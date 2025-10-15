# app/rag/splitter.py
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_documents(docs, chunk_size=1000, overlap=150):
    """
    Memecah teks jadi potongan kecil agar cocok untuk embedding dan retrieval.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(docs)
    print(f"[INFO] Split into {len(chunks)} chunks.")
    return chunks
