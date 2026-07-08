"""
Celery tasks for async AI generation: images, videos, captions.
Uses proper asyncio pattern for worker threads.
"""
import asyncio
import os
import uuid
from pathlib import Path
from datetime import datetime

from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.tasks.celery_app import celery_app
from backend.app.core.config import get_settings
from backend.app.services.comfyui_service import comfyui_service
from backend.app.services.ollama_service import ollama_service

settings = get_settings()

# Sync engine for Celery tasks
sync_engine = create_engine(settings.DATABASE_URL_SYNC)


def _run_async(coro):
    """Safely run an async coroutine from a sync Celery worker thread."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _save_image_record(character_id: str, file_path: str, prompt: str, negative_prompt: str, category: str):
    """Save generated image to database."""
    from backend.app.models.image import Image
    with Session(sync_engine) as session:
        img = Image(
            character_id=uuid.UUID(character_id),
            file_path=str(file_path),
            prompt=prompt,
            negative_prompt=negative_prompt,
            category=category,
            status="generated",
        )
        session.add(img)
        session.commit()


def _save_video_record(character_id: str, file_path: str, prompt: str, source_image_id: str = None):
    """Save generated video to database."""
    from backend.app.models.video import Video
    with Session(sync_engine) as session:
        vid = Video(
            character_id=uuid.UUID(character_id),
            file_path=str(file_path),
            prompt=prompt,
            source_image_id=uuid.UUID(source_image_id) if source_image_id else None,
            status="generated",
        )
        session.add(vid)
        session.commit()


@celery_app.task(bind=True, max_retries=3)
def generate_image_task(self, character_id: str, prompt: str, negative_prompt: str = "", category: str = "general"):
    """Async task to generate an image via ComfyUI."""
    try:
        workflow = comfyui_service.build_txt2img_workflow(
            prompt=prompt,
            negative_prompt=negative_prompt,
        )

        result = _run_async(comfyui_service.queue_prompt(workflow))
        prompt_id = result.get("prompt_id")
        if not prompt_id:
            raise ValueError("No prompt_id returned from ComfyUI")

        history = _run_async(comfyui_service.wait_for_generation(prompt_id))

        if history and "outputs" in history:
            for node_id, output in history["outputs"].items():
                if "images" in output:
                    for img_data in output["images"]:
                        filename = img_data["filename"]
                        subfolder = img_data.get("subfolder", "")
                        img_bytes = _run_async(
                            comfyui_service.download_output(filename, subfolder)
                        )

                        char_dir = Path(settings.MEDIA_ROOT) / "images" / character_id
                        char_dir.mkdir(parents=True, exist_ok=True)
                        file_path = char_dir / filename
                        file_path.write_bytes(img_bytes)

                        _save_image_record(character_id, str(file_path), prompt, negative_prompt, category)
                        return {"status": "completed", "file": str(file_path)}

        raise ValueError("Generation failed - no outputs received")

    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(bind=True, max_retries=3)
def generate_video_task(self, character_id: str, image_path: str = "", prompt: str = ""):
    """Async task to generate a video from an image via ComfyUI."""
    try:
        workflow = comfyui_service.build_img2vid_workflow(
            image_path=image_path,
            prompt=prompt,
        )

        result = _run_async(comfyui_service.queue_prompt(workflow))
        prompt_id = result.get("prompt_id")
        if not prompt_id:
            raise ValueError("No prompt_id returned from ComfyUI")

        history = _run_async(comfyui_service.wait_for_generation(prompt_id, max_wait=600))

        if history and "outputs" in history:
            for node_id, output in history["outputs"].items():
                if "images" in output:
                    for img_data in output["images"]:
                        filename = img_data["filename"]
                        subfolder = img_data.get("subfolder", "")
                        img_bytes = _run_async(
                            comfyui_service.download_output(filename, subfolder)
                        )

                        vid_dir = Path(settings.MEDIA_ROOT) / "videos" / character_id
                        vid_dir.mkdir(parents=True, exist_ok=True)
                        file_path = vid_dir / filename
                        file_path.write_bytes(img_bytes)

                        _save_video_record(character_id, str(file_path), prompt)
                        return {"status": "completed", "file": str(file_path)}

        raise ValueError("Video generation failed - no outputs received")

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=2)
def generate_caption_task(self, character_id: str, topic: str = "", tone: str = "casual"):
    """Async task to generate a social media caption via Ollama."""
    try:
        from backend.app.models.character import Character
        with Session(sync_engine) as session:
            char = session.query(Character).filter(Character.id == uuid.UUID(character_id)).first()
            if not char:
                raise ValueError(f"Character {character_id} not found")

            char_name = char.name
            char_bio = char.bio or ""

        result = _run_async(
            ollama_service.generate_caption(char_name, char_bio, topic, tone)
        )

        return {"status": "completed", "caption": result["caption"], "hashtags": result["hashtags"]}

    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)


@celery_app.task
def publish_content_task(post_id: str):
    """Publish a post to social media platforms."""
    from backend.app.models.post import Post
    with Session(sync_engine) as session:
        post = session.query(Post).filter(Post.id == uuid.UUID(post_id)).first()
        if not post:
            return {"status": "failed", "error": f"Post {post_id} not found"}

        post.status = "published"
        post.publish_date = datetime.utcnow()
        session.commit()

    return {"status": "completed", "post_id": post_id, "platform": post.platform}


@celery_app.task
def generate_daily_content():
    """Scheduled task to generate daily content for all active characters."""
    from backend.app.models.character import Character
    with Session(sync_engine) as session:
        characters = session.query(Character).filter(Character.status == "active").all()

        for char in characters:
            # Generate a new image
            prompts = [
                "casual lifestyle photo, natural lighting, beautiful smile",
                "fashion portrait, studio lighting, elegant outfit",
                "outdoor adventure, golden hour, warm tones",
            ]
            import random
            prompt = random.choice(prompts)

            generate_image_task.delay(
                str(char.id),
                prompt=prompt,
                category="daily",
            )

            # Generate caption for the image
            generate_caption_task.delay(
                str(char.id),
                topic="today's vibe",
            )

    return {"status": "completed", "characters_processed": len(characters)}