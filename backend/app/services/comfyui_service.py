"""
ComfyUI service for image and video generation.
Communicates with ComfyUI server running in Docker via HTTP API.
"""
import json
import uuid
import time
import httpx
from pathlib import Path
from typing import Optional

from app.core.config import get_settings

settings = get_settings()

COMFYUI_URL = settings.COMFYUI_URL


class ComfyUIService:
    """Handles communication with ComfyUI for image and video generation."""

    @staticmethod
    def load_workflow_json(workflow_name: str) -> dict:
        """Load a workflow JSON file from the comfyui workflows directory."""
        workflow_path = Path(__file__).parent.parent.parent.parent / "comfyui" / "workflows" / workflow_name
        if workflow_path.exists():
            return json.loads(workflow_path.read_text())
        # Default empty workflow
        return {}

    @staticmethod
    async def queue_prompt(prompt: dict, client_id: str = None) -> dict:
        """Submit a workflow prompt to ComfyUI and return the prompt_id."""
        if client_id is None:
            client_id = str(uuid.uuid4())

        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"prompt": prompt, "client_id": client_id}
            response = await client.post(f"{COMFYUI_URL}/prompt", json=payload)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_history(prompt_id: str) -> dict:
        """Retrieve generation history for a given prompt_id."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{COMFYUI_URL}/history/{prompt_id}")
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def wait_for_generation(prompt_id: str, max_wait: int = 300) -> Optional[dict]:
        """Poll ComfyUI until generation completes or timeout is reached."""
        start_time = time.time()

        async with httpx.AsyncClient(timeout=300.0) as client:
            while (time.time() - start_time) < max_wait:
                try:
                    history = await ComfyUIService.get_history(prompt_id)
                    if prompt_id in history:
                        return history[prompt_id]
                except Exception:
                    pass
                time.sleep(2)
        return None

    @staticmethod
    async def download_output(filename: str, subfolder: str = "", output_type: str = "output") -> bytes:
        """Download a generated file from ComfyUI."""
        params = {"filename": filename, "subfolder": subfolder, "type": output_type}
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(f"{COMFYUI_URL}/view", params=params)
            response.raise_for_status()
            return response.content

    @staticmethod
    def build_txt2img_workflow(
        prompt: str,
        negative_prompt: str = "",
        width: int = 768,
        height: int = 1024,
        steps: int = 25,
        cfg: float = 7.0,
        seed: int = -1,
        model_name: str = "flux_dev.safetensors",
    ) -> dict:
        """Build a basic FLUX txt2img workflow."""
        if seed == -1:
            import random
            seed = random.randint(1, 2**31)

        workflow = {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0],
                },
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": model_name},
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": width, "height": height, "batch_size": 1},
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": f"photorealistic, high quality, 8k, {prompt}",
                    "clip": ["4", 1],
                },
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": negative_prompt or "blurry, low quality, distorted, ugly, bad anatomy",
                    "clip": ["4", 1],
                },
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2],
                },
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["8", 0],
                    "filename_prefix": "aifactory",
                },
            },
        }
        return workflow

    @staticmethod
    def build_img2vid_workflow(
        image_path: str,
        prompt: str = "",
        length: int = 25,
    ) -> dict:
        """Build a basic image-to-video workflow using CogVideoX or Wan."""
        import random
        seed = random.randint(1, 2**31)

        workflow = {
            "1": {
                "class_type": "LoadImage",
                "inputs": {"image": image_path},
            },
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": 25,
                    "cfg": 7.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0],
                },
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "wan_2_1.safetensors"},
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": 512, "height": 512, "batch_size": length},
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": f"smooth motion, cinematic, {prompt}",
                    "clip": ["4", 1],
                },
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "static, still, jittery, deformed",
                    "clip": ["4", 1],
                },
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {"images": ["8", 0], "filename_prefix": "aifactory_vid"},
            },
        }
        return workflow


comfyui_service = ComfyUIService()