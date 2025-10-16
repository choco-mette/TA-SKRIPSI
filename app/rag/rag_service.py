# app/rag/rag_service.py
from app.rag.retriever_service import retrieve_context
from app.llm.ollama_client import generate_response

async def rag_chat(user_message: str):
    """
    Jalankan pipeline RAG async:
    - Ambil konteks dari vector database
    - Kirim ke model Ollama DeepSeek
    """
    context_docs = await retrieve_context(user_message, top_k=3)
    context_text = "\n\n".join([doc["content"] for doc in context_docs])

    system_prompt = (
        "Kamu adalah asisten AI yang membantu menjawab berdasarkan dokumen lokal berikut.\n"
        "Jawaban harus relevan dan menggunakan bahasa yang sopan.\n"
        "Jika konteks tidak ditemukan, jawab 'Saya tidak menemukan informasi terkait.'\n\n"
        f"=== KONTEKS ===\n{context_text}\n\n"
        f"=== PERTANYAAN ===\n{user_message}"
    )

    messages = [
        {"role": "system", "content": "Kamu adalah asisten cerdas untuk topik kesehatan mental."},
        {"role": "user", "content": system_prompt}
    ]

    response = await generate_response(messages)
    return response
