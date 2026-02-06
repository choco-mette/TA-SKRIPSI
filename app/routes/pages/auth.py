from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

# Setup templates (Adjust path relative to this file)
# app/routes/pages/auth.py -> app/templates
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
templates = Jinja2Templates(directory=templates_dir)

@router.get("/register", tags=["Pages"])
async def register_page(request: Request):
    return templates.TemplateResponse("login/register.html", {"request": request})

@router.get("/login", tags=["Pages"])
async def login_page(request: Request):
    return templates.TemplateResponse("login/login.html", {"request": request})
