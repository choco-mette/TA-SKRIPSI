from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import uuid
import csv
import io
from datetime import datetime
from typing import List, Optional, Any
from nltk.translate.bleu_score import sentence_bleu, corpus_bleu, SmoothingFunction
from nltk.tokenize import word_tokenize
from rouge_score import rouge_scorer

# Ensure NLTK data (punkt) is downloaded. 
# This might need to happen at startup or in Dockerfile.
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

from app.models.models import RagTestCase, RagEvaluationResult, EnvironmentModel
from app.ai.rag_pipeline import RAGPipeline
from app.schemas.evaluation import EvaluationResultResponse
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class EvaluationService:
    def __init__(self, db: Session):
        self.db = db
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    def import_test_cases_from_csv(self, file_content: bytes) -> int:
        """
        Parses CSV and inserts RagTestCase records.
        Expected CSV format: question, reference_answer
        """
        try:
            decoded_content = file_content.decode('utf-8')
            # Use StringIO to simulate a file object for csv reader
            csv_file = io.StringIO(decoded_content)
            csv_reader = csv.DictReader(csv_file)
            
            count = 0
            for row in csv_reader:
                # Normalizing keys to lower case just in case
                row_lower = {k.lower(): v for k, v in row.items()}
                question = row_lower.get('question')
                reference = row_lower.get('reference_answer') or row_lower.get('answer')
                
                if not question or not reference:
                    continue
                
                # Check for duplicate question
                existing = self.db.query(RagTestCase).filter(RagTestCase.question == question).first()
                if existing:
                    existing.reference_answer = reference
                else:
                    new_case = RagTestCase(
                        question=question,
                        reference_answer=reference
                    )
                    self.db.add(new_case)
                count += 1
                
            self.db.commit()
            logger.info(f"Imported {count} test cases successfully.")
            return count
        except Exception as e:
            logger.error(f"Failed to import CSV: {e}")
            self.db.rollback()
            raise ValueError(f"Failed to parse CSV file: {str(e)}")

    def create_test_case(self, question: str, reference_answer: str) -> RagTestCase:
        existing = self.db.query(RagTestCase).filter(RagTestCase.question == question).first()
        if existing:
            existing.reference_answer = reference_answer
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        new_case = RagTestCase(question=question, reference_answer=reference_answer)
        self.db.add(new_case)
        self.db.commit()
        self.db.refresh(new_case)
        return new_case

    def update_test_case(self, case_id: int, question: str, reference_answer: str) -> Optional[RagTestCase]:
        case = self.db.query(RagTestCase).filter(RagTestCase.id == case_id).first()
        if not case:
            return None
        
        case.question = question
        case.reference_answer = reference_answer
        self.db.commit()
        self.db.refresh(case)
        return case

    def delete_test_case(self, case_id: int) -> bool:
        case = self.db.query(RagTestCase).filter(RagTestCase.id == case_id).first()
        if not case:
            return False
            
        self.db.delete(case)
        self.db.commit()
        return True

    def get_all_test_cases(self):
        return self.db.query(RagTestCase).all()


    def run_evaluation(self, environment_id: int, limit: int = None) -> List[RagEvaluationResult]:
        """
        Runs RAG evaluation on ALL test cases using the specified model environment.
        """
        logger.info(f"Starting Evaluation Run on Environment ID: {environment_id}")
        
        # 1. Fetch Environment Config
        env_model = self.db.query(EnvironmentModel).filter(EnvironmentModel.id == environment_id).first()
        if not env_model:
            raise ValueError(f"Environment Model ID {environment_id} not found.")

        # 2. Initialize RAG Pipeline with specific model
        # Note: We create a fresh instance to ensure clean state
        rag = RAGPipeline(self.db, environment_id=environment_id)

        # 3. Fetch All Test Cases
        query = self.db.query(RagTestCase)
        if limit:
            query = query.limit(limit)
        test_cases = query.all()
        
        logger.info(f"Found {len(test_cases)} test cases to evaluate.")

        results = []
        
        for case in test_cases:
            # Generate unique ID for isolated conversation
            session_id = str(uuid.uuid4())
            
            try:
                # 4. Generate Answer via RAG
                # We assume rag.run returns the answer text directly or a dict with 'answer'
                # Let's inspect rag_pipeline.run return value.
                # Assuming it returns a string based on previous knowledge of simple chains.
                # If it returns a dict, we extract 'answer' or 'output'.
                generated_response = rag.run(session_id, case.question)
                
                # Handling different return types if RAG implementation varies
                if isinstance(generated_response, dict):
                     generated_text = generated_response.get('answer', generated_response.get('output', str(generated_response)))
                else:
                    generated_text = str(generated_response)

                # 5. Calculate Metrics
                reference_text = case.reference_answer
                
                # BLEU-4
                # Tokenize
                ref_tokens = word_tokenize(reference_text.lower())
                gen_tokens = word_tokenize(generated_text.lower())
                
                # Use smooth function to handle short sentences (avoid 0 score when < 4 tokens)
                cc = SmoothingFunction()

                # # sentence_bleu expects list of references (list of lists of tokens)
                bleu = sentence_bleu([ref_tokens], gen_tokens)

                # sentence_bleu expects list of references (list of lists of tokens)
                # weights=(0.25, 0.25, 0.25, 0.25) is the default for BLEU-4, 
                # but explicit definition is clearer.
                # BLEU-4
                # bleu = sentence_bleu(
                #     [ref_tokens], 
                #     gen_tokens, 
                #     weights=(0.25, 0.25, 0.25, 0.25),
                #     smoothing_function=cc.method1
                # )

                # ROUGE
                rouge_scores = self.rouge_scorer.score(reference_text, generated_text)
                
                # 6. Save Result
                result = RagEvaluationResult(
                    test_case_id=case.id,
                    environment_id=environment_id,
                    model_answer=generated_text,
                    bleu_score=bleu,
                    rouge_1=rouge_scores['rouge1'].fmeasure,
                    rouge_2=rouge_scores['rouge2'].fmeasure,
                    rouge_l=rouge_scores['rougeL'].fmeasure
                )
                self.db.add(result)
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error evaluating test case {case.id}: {e}")
                continue

        self.db.commit()
        logger.info(f"Evaluation completed. Processed {len(results)} cases.")
        return results

    def get_results(self, environment_id: int) -> List[RagEvaluationResult]:
        # Uses explicit query to join tables and return flat dict for schema compatibility
        results = self.db.query(
            RagEvaluationResult,
            RagTestCase.question.label("question"),
            EnvironmentModel.models_name.label("env_name")
        ).join(
            RagTestCase, RagEvaluationResult.test_case_id == RagTestCase.id
        ).join(
            EnvironmentModel, RagEvaluationResult.environment_id == EnvironmentModel.id
        ).filter(
            RagEvaluationResult.environment_id == environment_id
        ).order_by(RagEvaluationResult.created_at.desc()).all()

        response = []
        for r, q, e_name in results:
            # Create a dict from the model and add extra fields
            r_dict = r.__dict__.copy()
            r_dict['question'] = q
            r_dict['environment_name'] = e_name 
            response.append(r_dict)
        return response

    def get_all_results(self, limit: int = 100, offset: int = 0, environment_id: Optional[int] = None, start_date: Optional[Any] = None, end_date: Optional[Any] = None) -> List[Any]:
        query = self.db.query(
            RagEvaluationResult,
            RagTestCase.question.label("question"),
            EnvironmentModel.models_name.label("env_name")
        ).join(
            RagTestCase, RagEvaluationResult.test_case_id == RagTestCase.id
        ).join(
            EnvironmentModel, RagEvaluationResult.environment_id == EnvironmentModel.id
        )

        if environment_id is not None:
             query = query.filter(RagEvaluationResult.environment_id == environment_id)
        
        if start_date:
             if isinstance(start_date, str):
                 try:
                     start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                 except ValueError:
                     pass
             query = query.filter(func.date(RagEvaluationResult.created_at) >= start_date)

        if end_date:
             if isinstance(end_date, str):
                 try:
                     end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                 except ValueError:
                     pass
             query = query.filter(func.date(RagEvaluationResult.created_at) <= end_date)

        results = query.order_by(RagEvaluationResult.created_at.desc()).offset(offset).limit(limit).all()

        response = []
        for r, q, e_name in results:
            r_dict = r.__dict__.copy()
            r_dict['question'] = q
            r_dict['environment_name'] = e_name 
            response.append(r_dict)
        return response
