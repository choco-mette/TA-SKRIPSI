
from fastapi import APIRouter 
from app.routes.api.auth import router as auth_router
from app.routes.api.admin.rules import router as admin_rules_router
from app.routes.api.admin.personality import router as admin_personality_router
from app.routes.api.admin.enviroment import router as admin_environment_router
from app.routes.api.admin.documents import router as admin_documents_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(admin_rules_router, prefix="/admin/rules", tags=["admin-rules"])
api_router.include_router(admin_personality_router, prefix="/admin/personality", tags=["admin-personality"])
api_router.include_router(admin_environment_router, prefix="/admin/environments", tags=["admin-environments"])
api_router.include_router(admin_documents_router, prefix="/admin/documents", tags=["admin-documents"])