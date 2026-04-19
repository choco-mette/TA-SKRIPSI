import os
import sys
import nltk
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.tokenize import word_tokenize

# Tambahkan path root project agar bisa import app.core.config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.core.config import settings
except ImportError:
    # Fallback jika config tidak bisa diimport, ganti dengan database URL Anda manual
    # Contoh: "postgresql://user:password@localhost/dbname"
    print("Warning: Could not import settings. Using default DB URL.")
    DATABASE_URL = "postgresql://aichatbot:password98765@localhost/ai_chatbotdb" 
else:
    DATABASE_URL = str(settings.SQLALCHEMY_DATABASE_URI)

# Download dictionary nltk jika belum ada
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading nltk punkt...")
    nltk.download('punkt')

def calculate_bleu(reference, candidate):
    """
    Menghitung BLEU score.
    """
    if not reference or not candidate:
        return 0.0

    ref_tokens = word_tokenize(reference.lower())
    cand_tokens = word_tokenize(candidate.lower())
    
    # Smoothing function useful for short sentences
    cc = SmoothingFunction()
    
    return sentence_bleu([ref_tokens], cand_tokens, smoothing_function=cc.method1)

def main():
    print("=== MENGHITUNG BLEU SCORE DARI DATABASE ===\n")
    
    # Setup Database Connection
    if not DATABASE_URL:
        print("Database URL not found.")
        return

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # SQL Query Pure (Sesuai diskusi sebelumnya)
        query = text("""
            SELECT 
                re.id AS evaluation_id,
                rt.question,
                rt.reference_answer,
                re.model_answer,
                em.models_name
            FROM 
                rag_evaluation_results re
            JOIN 
                rag_test_cases rt ON re.test_case_id = rt.id
            LEFT JOIN 
                environment_models em ON re.environment_id = em.id
            WHERE 
                re.model_answer IS NOT NULL 
                AND rt.reference_answer IS NOT NULL
        """)

        result = db.execute(query)
        rows = result.fetchall()

        if not rows:
            print("Tidak ada data ditemukan di tabel rag_evaluation_results.")
            return

        print(f"{'ID':<4} | {'BLEU':<6} | {'Model':<15} | {'Ref (Short)':<30} | {'Ans (Short)':<30}")
        print("-" * 100)

        total_score = 0
        count = 0

        for row in rows:
            # Akses kolom berdasarkan nama kolom (SQLAlchemy row mapping)
            # row: (evaluation_id, question, reference_answer, model_answer, models_name)
            # Perhatikan: cara akses row bisa berbeda tergantung versi SQLAlchemy.
            # Menggunakan mapping (row._mapping) atau akses indeks jika tuple.
            
            # Akses aman untuk SQLAlchemy terbaru:
            eval_id = row.evaluation_id
            reference = row.reference_answer
            answer = row.model_answer
            model_name = row.models_name or "Unknown"

            score = calculate_bleu(reference, answer)
            
            total_score += score
            count += 1
            
            # Truncate string for display
            ref_display = (reference[:27] + '..') if len(reference) > 27 else reference
            ans_display = (answer[:27] + '..') if len(answer) > 27 else answer
            model_display = (model_name[:12] + '..') if len(model_name) > 12 else model_name

            print(f"{eval_id:<4} | {score:.4f} | {model_display:<15} | {ref_display:<30} | {ans_display:<30}")

        if count > 0:
            avg_score = total_score / count
            print("-" * 100)
            print(f"Rata-rata BLEU Score: {avg_score:.4f} (dari {count} data)")
        
    except Exception as e:
        print(f"Terjadi error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
