from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes.api import api_router
from app.routes.pages import pages_router
from app.utils.logger import setup_logger
import os
import time

logger = setup_logger("api_access")

app = FastAPI(title="Mental Health Chatbot")

# Global Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log Request
    logger.info(f"Incoming Request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        
        # Log Response
        process_time = (time.time() - start_time) * 1000
        logger.info(f"Request Completed: {request.method} {request.url} - Status: {response.status_code} - Duration: {process_time:.2f}ms")
        
        return response
    except Exception as e:
        logger.error(f"Request Failed: {request.method} {request.url} - Error: {str(e)}", exc_info=True)
        raise e

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