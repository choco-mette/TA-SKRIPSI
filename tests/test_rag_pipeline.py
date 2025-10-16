# tests/test_rag_pipeline.py
import asyncio
import logging
import os
import sys
import time
from datetime import datetime

# Fix event loop policy untuk Windows (psycopg async)
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.rag.rag_service import rag_chat
from app.rag.retriever_service import retrieve_context

# === Konfigurasi Logging === #
os.makedirs("logs", exist_ok=True)
log_filename = f"logs/rag_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

# === Main Test === #
async def main():
    query = "bagaimana cara mengatasi stres?"
    logging.info("=" * 80)
    logging.info("[TEST] Mulai pengujian RAG pipeline")
    logging.info(f"[USER INPUT] {query}")

    # --- Step 1: Retrieval (ingat: retrieve_context adalah async) ---
    logging.info("[STEP 1] Melakukan retrieval konteks dari vectorstore...")
    try:
        t0 = time.time()
        context_docs = await retrieve_context(query, top_k=5)  # <-- await di sini
        retrieval_time = time.time() - t0
        logging.info(f"[INFO] {len(context_docs)} konteks ditemukan (waktu: {retrieval_time:.2f} detik)")

        for i, ctx in enumerate(context_docs, 1):
            content_preview = (ctx.get("content") or "").replace("\n", " ")
            # ambil metadata penting jika ada
            meta = ctx.get("metadata") or {}
            meta_info = ", ".join(f"{k}: {v}" for k, v in meta.items() if k in ["file_path", "page", "source"])
            logging.info(f"\n--- Konteks {i} ---")
            logging.info(f"Isi (potongan): {content_preview}...")
            logging.info(f"Metadata: {meta_info if meta_info else 'Tidak ada metadata tambahan'}")

    except Exception as e:
        logging.exception(f"[ERROR] Gagal saat retrieval: {e}")
        return

    # --- Step 2: Kirim ke LLM (Ollama DeepSeek) ---
    logging.info("\n[STEP 2] Mengirim prompt ke LLM (Ollama DeepSeek)...")
    try:
        t1 = time.time()
        response = await rag_chat(query)
        llm_time = time.time() - t1

        logging.info(f"[STEP 3] Respons diterima dari LLM ✅ (waktu: {llm_time:.2f} detik)")
        logging.info(f"\n=== HASIL AKHIR ===\n{response}\n")

    except Exception as e:
        logging.exception(f"[ERROR] Gagal memproses RAG pipeline (LLM): {e}")
        return

    total_time = retrieval_time + llm_time
    logging.info(f"[DONE] Pengujian RAG pipeline selesai (total waktu: {total_time:.2f} detik).")
    logging.info("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
