# tests/test_rag_service.py
import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.rag.rag_service import rag_chat

async def main():
    print("[TEST] Menjalankan RAG Chat (async)...")
    user_message = "Bagaimana cara mengatasi stres?"
    response = await rag_chat(user_message)
    print("\n[HASIL]:", response)

if __name__ == "__main__":
    asyncio.run(main())
