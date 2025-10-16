# app/rag/vectorstore.py
import asyncio
from langchain_postgres import PGEngine, PGVectorStore
from app.rag.embedder import get_embedding_model
from app.core.config import settings

async def get_vectorstore():
    """
    Setup koneksi PGVectorStore tapi tetap non-blocking (async-compatible).
    """
    def init_store():
        CONNECTION_STRING = (
            f"postgresql+psycopg://{settings.DB_USER}:{settings.DB_PASSWORD}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )

        engine = PGEngine.from_connection_string(url=CONNECTION_STRING)

        embeddings = get_embedding_model()
        VECTOR_SIZE = 384
        TABLE_NAME = "knowledge_vectors"

        store = PGVectorStore.create_sync(
            engine=engine,
            table_name=TABLE_NAME,
            embedding_service=embeddings,
        )
        return store

    # Jalankan di thread terpisah agar tidak block event loop FastAPI
    store = await asyncio.to_thread(init_store)
    return store
