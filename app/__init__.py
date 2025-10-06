# app/__init__.py
from fastapi import FastAPI

app = FastAPI(title="RAG Chat Backend")

__all__ = ["app"]