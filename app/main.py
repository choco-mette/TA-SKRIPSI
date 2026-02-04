from fastapi import FastAPI
from app.routes import routes

app = FastAPI(title="RAG Backend")
app.include_router(routes.router, prefix="/api/v1")
