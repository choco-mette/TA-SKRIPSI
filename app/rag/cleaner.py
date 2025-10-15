# app/rag/cleaner.py
import re
from langchain.docstore.document import Document

def clean_text(docs):
    """
    Membersihkan teks dari karakter aneh, bullet, newline berlebih, dan spasi ganda.
    Cocok digunakan sebelum proses embedding agar hasil retrieval lebih konsisten.
    """
    cleaned = []
    bullet_pattern = r'[\u2022•·●-]'  # deteksi simbol bullet umum

    for doc in docs:
        text = doc.page_content

        # Hilangkan karakter bullet dan simbol aneh
        text = re.sub(bullet_pattern, ' ', text)

        # Hilangkan karakter null dan newline berlebih
        text = text.replace('\x00', ' ')
        text = re.sub(r'\s+', ' ', text)

        # Trim spasi di awal/akhir
        text = text.strip()

        cleaned.append(Document(page_content=text, metadata=doc.metadata))

    print(f"[INFO] Cleaned {len(cleaned)} documents.")
    return cleaned
