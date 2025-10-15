# app/rag/preprocess_service.py
from app.rag.loader import load_pdf_documents
from app.rag.cleaner import clean_text
from app.rag.splitter import chunk_documents
from app.rag.vectorstore import get_vectorstore

def process_pdf_folder(folder_path: str):
    """
    Pipeline utama:
    1. Load semua PDF dari folder
    2. Clean teks
    3. Chunk dokumen
    4. Simpan ke database (pgvector)
    """
    print(f"[START] Proses folder PDF: {folder_path}")
    docs = load_pdf_documents(folder_path)
    if not docs:
        print("[STOP] Tidak ada dokumen untuk diproses.")
        return
    # cleaned = clean_text(docs)

    # chunks = chunk_documents(cleaned)
    chunks = chunk_documents(docs)
    cleaned = clean_text(chunks)
    store = get_vectorstore()
    print(f"[INFO] Menyimpan {len(cleaned)} chunks ke database...")

    store.add_documents(cleaned)

    print(f"[SUCCESS] {len(cleaned)} chunks berhasil disimpan ke database.")
