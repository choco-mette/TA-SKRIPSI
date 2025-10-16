# app/rag/retriever_service.py
import asyncio
from app.rag.vectorstore import get_vectorstore

async def retrieve_context(query: str, top_k: int = 3):
    """
    Ambil potongan teks paling relevan dari vector database secara async.
    """
    store = await get_vectorstore()

    def run_retrieve():
        retriever = store.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
        return retriever.invoke(query)

    results = await asyncio.to_thread(run_retrieve)

    contexts = [
        {"content": doc.page_content, "metadata": doc.metadata}
        for doc in results
    ]
    return contexts
