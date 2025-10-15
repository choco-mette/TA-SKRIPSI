# app/rag/loader.py
from langchain_community.document_loaders import PyMuPDFLoader
from pathlib import Path

def load_pdf_documents(folder_path: str):
    """
    Membaca semua file PDF dari folder dan mengubahnya menjadi list dokumen LangChain.
    """
    folder = Path(folder_path)
    pdf_files = list(folder.glob("*.pdf"))

    if not pdf_files:
        print(f"[WARN] Tidak ada file PDF di folder: {folder_path}")
        return []

    all_docs = []
    for pdf_path in pdf_files:
        print(f"[INFO] Loading {pdf_path.name} ...")
        loader = PyMuPDFLoader(str(pdf_path))
        docs = loader.load()
        for doc in docs:
            doc.metadata["source_path"] = str(pdf_path)
        all_docs.extend(docs)

    print(f"[SUCCESS] Total {len(all_docs)} halaman dari {len(pdf_files)} file PDF.")
    return all_docs
