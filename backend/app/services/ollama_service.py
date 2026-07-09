"""
Ollama service for LLM text generation - descriptions, captions, hashtags.
"""
import json
import httpx
from typing import Optional

from app.core.config import get_settings

settings = get_settings()


class OllamaService:
    """Handles LLM text generation via Ollama API."""

    OLLAMA_URL = settings.OLLAMA_URL
    MODEL = settings.LLM_MODEL

    @staticmethod
    async def generate(
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        """Generate text using Ollama."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {
                "model": OllamaService.MODEL,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }
            response = await client.post(f"{OllamaService.OLLAMA_URL}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")

    @staticmethod
    async def generate_caption(
        character_name: str,
        character_bio: str,
        topic: str = "",
        tone: str = "casual",
        language: str = "english",
    ) -> dict:
        """Generate a social media caption and hashtags for a character."""
        system_prompt = (
            "You are a social media expert and professional copywriter. "
            "You write engaging captions for Instagram and TikTok posts."
        )

        topic_hint = f"about: {topic}" if topic else "showing off today's lifestyle"
        prompt = (
            f"Write an engaging {tone} social media caption for an influencer named {character_name}.\n"
            f"Character bio: {character_bio}\n"
            f"Post is {topic_hint}.\n"
            f"Language: {language}\n\n"
            f"Output as JSON with fields: 'caption' (the post text), 'hashtags' (list of 5-10 relevant hashtags)."
        )

        result = await OllamaService.generate(prompt, system_prompt)
        try:
            # Try to parse JSON, fallback to raw text
            parsed = json.loads(result.strip())
            return {
                "caption": parsed.get("caption", result),
                "hashtags": parsed.get("hashtags", []),
            }
        except json.JSONDecodeError:
            return {
                "caption": result.strip(),
                "hashtags": ["#aiinfluencer", "#lifestyle", "#trending"],
            }

    @staticmethod
    async def generate_bio(character_name: str, appearance: dict, style: str) -> str:
        """Generate a character bio."""
        system_prompt = "You are a creative writer creating bios for AI influencers."
        prompt = (
            f"Write a short, appealing bio for an AI influencer named {character_name}.\n"
            f"Appearance: {json.dumps(appearance)}\n"
            f"Style: {style}\n"
            f"Keep it under 150 characters, engaging and fun."
        )
        return await OllamaService.generate(prompt, system_prompt, max_tokens=200)


ollama_service = OllamaService()