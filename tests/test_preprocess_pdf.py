import asyncio
import sys

# ✅ Fix untuk event loop Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.rag.preprocess_service import process_pdf_folder

if __name__ == "__main__":
    process_pdf_folder(r"C:\laragon\www\Backend AI\data\PDF")
