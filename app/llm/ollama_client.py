# app/llm/ollama_client.py
import httpx
import asyncio
from app.core.config import settings

OLLAMA_URL = f"{settings.API_LLM_URL}/api/chat"

async def generate_response(messages):
    """
    Kirim prompt ke model Ollama (DeepSeek 14B) secara async.
    """
    payload = {
        "model": "deepseek-r1:14b",
        "messages": messages,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()

        # Handle kemungkinan field berbeda (misalnya `message.content`)
        if "message" in data and "content" in data["message"]:
            return data["message"]["content"]
        return data
