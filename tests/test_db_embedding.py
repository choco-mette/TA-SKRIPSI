"""
Test script untuk memastikan koneksi database PostgreSQL aktif
dan ekstensi pgvector sudah tersedia.
"""

from sqlalchemy import text
from app.db.database import engine, SessionLocal


def test_database_connection():
    print("🔌 Menguji koneksi ke database PostgreSQL...\n")

    try:
        # Buat session
        session = SessionLocal()

        # Uji query dasar
        result = session.execute(text("SELECT version();")).fetchone()
        print(f"✅ Koneksi berhasil!")
        print(f"🧠 PostgreSQL Version: {result[0]}\n")

        # Cek apakah ekstensi pgvector tersedia
        print("🔍 Mengecek ekstensi pgvector...")
        ext_check = session.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        ).fetchone()

        if ext_check:
            print("✅ Ekstensi pgvector terpasang.")
        else:
            print("⚠️  Ekstensi pgvector belum ada. Jalankan perintah berikut di database Anda:")
            print("    CREATE EXTENSION IF NOT EXISTS vector;")

        # Cek apakah tabel knowledge_vectors ada
        print("\n📦 Mengecek tabel knowledge_vectors...")
        table_check = session.execute(
            text("""
                SELECT to_regclass('public.knowledge_vectors');
            """)
        ).fetchone()

        if table_check and table_check[0]:
            print("✅ Tabel knowledge_vectors ditemukan.")
        else:
            print("⚠️  Tabel knowledge_vectors belum dibuat. Jalankan migrasi terlebih dahulu.")

        session.close()

    except Exception as e:
        print("❌ Gagal terhubung ke database!")
        print("Error detail:", e)


if __name__ == "__main__":
    test_database_connection()
