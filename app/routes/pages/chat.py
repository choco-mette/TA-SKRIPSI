from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
templates = Jinja2Templates(directory=templates_dir)

@router.get("/chat", tags=["Pages"])
async def chat_page(request: Request):
    return templates.TemplateResponse("chat/index.html", {"request": request})

@router.get("/chat/{conversation_id}", tags=["Pages"])
async def chat_conversation_page(request: Request, conversation_id: str):
    return templates.TemplateResponse("chat/index.html", {"request": request, "conversation_id": conversation_id})

