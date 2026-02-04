from fastapi import FastAPI
from app.routes.api import api_router
from app.routes.pages import pages_router

app = FastAPI(title="Mental Health Chatbot")
app.include_router(api_router, prefix="/api/v1")
app.include_router(pages_router)