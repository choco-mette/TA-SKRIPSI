# app/rag/embedder.py
from langchain_community.embeddings import SentenceTransformerEmbeddings

from langchain_huggingface import HuggingFaceEmbeddings

def get_embedding_model():
    """
    Mengembalikan model embedding ringan dan cepat untuk Bahasa Indonesia.
    """
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
