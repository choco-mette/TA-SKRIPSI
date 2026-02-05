from fastapi import APIRouter
from app.routes.pages.auth import router as auth_router
from app.routes.pages.chat import router as chat_router
from app.routes.pages.admin import router as admin_router
from app.routes.pages.landing_page import router as landing_router

pages_router = APIRouter()

pages_router.include_router(auth_router)
pages_router.include_router(chat_router)
pages_router.include_router(admin_router)
pages_router.include_router(landing_router)