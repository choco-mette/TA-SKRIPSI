from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RagTestCaseCreate(BaseModel):
    question: str
    reference_answer: str

class RagTestCaseResponse(BaseModel):

    id: int
    question: str
    reference_answer: str

    class Config:
        from_attributes = True

class EvaluationRunRequest(BaseModel):
    environment_id: int
    limit: Optional[int] = None 

class EvaluationResultResponse(BaseModel):
    id: int
    test_case_id: int
    environment_id: int
    question: Optional[str] = None
    environment_name: Optional[str] = None
    model_answer: str
    bleu_score: Optional[float]
    rouge_1: Optional[float]
    rouge_2: Optional[float]
    rouge_l: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True
