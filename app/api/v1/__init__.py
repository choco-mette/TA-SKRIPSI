from fastapi import APIRouter
from . import routes_users, routes_chat, routes_auth

router_v1 = APIRouter()
router_v1.include_router(routes_users.router, prefix="/users", tags=["Users"])
router_v1.include_router(routes_chat.router, prefix="/chat", tags=["Chat"])
router_v1.include_router(routes_auth.router, prefix="/auth", tags=["Auth"])