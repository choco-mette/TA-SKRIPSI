from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
templates = Jinja2Templates(directory=templates_dir)

@router.get("/admin", tags=["Pages"])
@router.get("/admin/{section}", tags=["Pages"])
async def admin_page(request: Request, section: str = "overview"):
    return templates.TemplateResponse("admin/index.html", {"request": request, "initial_section": section})

