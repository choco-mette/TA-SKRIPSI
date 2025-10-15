# app/rag/vectorstore.py
from langchain_core.documents import Document
from langchain_postgres import PGEngine, PGVectorStore
from app.rag.embedder import get_embedding_model
from app.core.config import settings


def get_vectorstore():
    """
    Setup koneksi dan inisialisasi vectorstore di PostgreSQL (PGVectorStore).
    """
    # 🔹 Buat connection string PostgreSQL
    CONNECTION_STRING = (
        f"postgresql+psycopg://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )

    # 🔹 Inisialisasi engine untuk koneksi
    engine = PGEngine.from_connection_string(url=CONNECTION_STRING)

    # 🔹 Tentukan model embedding
    embeddings = get_embedding_model()

    # 🔹 Ukuran vektor embedding yang kamu gunakan (all-MiniLM-L6-v2 = 384)
    VECTOR_SIZE = 384

    # 🔹 Nama tabel untuk penyimpanan embedding
    TABLE_NAME = "knowledge_vectors"

    # # 🔹 Buat tabel (hanya pertama kali)
    # engine.init_vectorstore_table(
    #     table_name=TABLE_NAME,
    #     vector_size=VECTOR_SIZE,
    # )

    # 🔹 Buat atau load vector store
    store = PGVectorStore.create_sync(
        engine=engine,
        table_name=TABLE_NAME,
        embedding_service=embeddings,
    )

    return store
