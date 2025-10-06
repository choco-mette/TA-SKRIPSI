from fastapi import FastAPI
from app.api import router_v1

app = FastAPI(title="RAG Backend")
app.include_router(router_v1, prefix="/api/v1")
