# app/rag/retriever_service.py
from langchain_core.documents import Document
from app.rag.vectorstore import get_vectorstore


def retrieve_context(query: str, top_k: int = 3):
    """
    Ambil potongan teks paling relevan dari database berdasarkan query user.
    """
    # Ambil koneksi vectorstore
    store = get_vectorstore()

    # Buat retriever
    retriever = store.as_retriever(search_type="similarity", search_kwargs={"k": top_k})

    # Jalankan pencarian
    results = retriever.invoke(query)

    # Format hasil agar lebih mudah dibaca/log
    contexts = [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,
        }
        for doc in results
    ]

    return contexts
