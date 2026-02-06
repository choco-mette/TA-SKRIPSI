from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any

from app.services.embedding_service import EmbeddingConfigService

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class Retriever:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingConfigService(db)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves top_k most relevant document chunks for the given query using Cosine Similarity.
        """
        try:
            logger.info(f"Generating embedding for query: '{query}'")
            # 1. Generate Embedding for the User Query
            embedder = self.embedding_service.get_embedding_model()
            query_vector = embedder.embed_query(query)

            # 2. Vector Search (Cosine Similarity)
            # Using pgvector operator <=> for cosine distance
            # Similarity = 1 - Distance
            logger.info("Executing vector search in database...")
            sql = text("""
                SELECT 
                    bk.content, 
                    bk.doc_id,
                    d.title,
                    1 - (bk.embedding <=> :query_vector) as similarity
                FROM base_knowledge bk
                JOIN document d ON bk.doc_id = d.id
                ORDER BY bk.embedding <=> :query_vector ASC
                LIMIT :top_k
            """)

            results = self.db.execute(sql, {
                "query_vector": str(query_vector),
                "top_k": top_k
            }).fetchall()
            
            logger.info(f"Vector search returned {len(results)} matches.")

            # 3. Format Results
            documents = []
            for row in results:
                documents.append({
                    "content": row.content,
                    "metadata": {
                        "doc_id": row.doc_id,
                        "title": row.title,
                        "similarity_score": float(row.similarity)
                    }
                })

            return documents

        except Exception as e:
            # Log error properly in production
            print(f"Retrieval Error: {str(e)}")
            return []
