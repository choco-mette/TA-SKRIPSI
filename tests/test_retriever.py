# tests/test_retriever.py
import asyncio
import sys

# Fix untuk Windows event loop (psycopg3 async)
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.rag.retriever_service import retrieve_context

if __name__ == "__main__":
    query = "Bagaimana cara mengatasi stres?"
    results = retrieve_context(query, top_k=5)

    print("\n[RESULTS]")
    for i, res in enumerate(results, 1):
        print(f"\n--- Hasil {i} ---")
        print("Konten:", res["content"])
        print("Metadata:", res["metadata"])
