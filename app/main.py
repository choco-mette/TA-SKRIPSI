from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes.api import api_router
from app.routes.pages import pages_router
import os

app = FastAPI(title="Mental Health Chatbot")

# Mount Static Files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates Configuration
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

app.include_router(api_router, prefix="/api/v1")
app.include_router(pages_router)