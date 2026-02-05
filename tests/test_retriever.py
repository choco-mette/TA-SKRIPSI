import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import SessionLocal
from app.services.embedding_service import EmbeddingConfigService

def test_similarity_search(query_text: str, top_k: int = 3):
    print(f"🔍 Testing Similarity Search for: '{query_text}'")
    
    db = SessionLocal()
    try:
        # 1. Get Embedder Service
        embedding_service = EmbeddingConfigService(db)
        embedder = embedding_service.get_embedding_model()
        
        print("🧠 Generating query embedding...")
        query_vector = embedder.embed_query(query_text)
        
        # 2. Perform Cosine Similarity Search via pgvector
        # Operator <=> stands for Cosine Distance in pgvector
        # Order by distance ASC means most similar first
        sql = text(f"""
            SELECT 
                bk.content, 
                d.title,
                1 - (bk.embedding <=> :query_vector) as similarity
            FROM base_knowledge bk
            JOIN document d ON bk.doc_id = d.id
            ORDER BY bk.embedding <=> :query_vector ASC
            LIMIT :top_k
        """)
        
        results = db.execute(sql, {
            "query_vector": str(query_vector), # pgvector needs string representation often
            "top_k": top_k
        }).fetchall()
        
        print(f"\n✅ Found {len(results)} relevant chunks:\n")
        
        for i, row in enumerate(results):
            score = row.similarity
            print(f"[{i+1}] Score: {score:.4f} | Source: {row.title}")
            print(f"    Content Preview: {row.content[:200000]}...")
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_query = sys.argv[1]
    else:
        user_query = "Apa ciri-ciri depresi?"
        
    test_similarity_search(user_query)
