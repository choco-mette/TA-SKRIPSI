from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db, SessionLocal
from app.core.dependencies import get_current_admin
from app.models.models import User
from app.services.evaluation_service import EvaluationService
from app.schemas.evaluation import EvaluationRunRequest, EvaluationResultResponse, RagTestCaseResponse, RagTestCaseCreate
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)

def run_evaluation_task(environment_id: int, limit: int = None):
    """
    Background task to run evaluation.
    Creates its own DB session to avoid detached instance issues.
    """
    db = SessionLocal()
    try:
        service = EvaluationService(db)
        service.run_evaluation(environment_id, limit)
    except Exception as e:
        logger.error(f"Background evaluation failed: {e}")
    finally:
        db.close()

@router.post("/run_generative", response_model=dict)
def run_evaluation(
    request: EvaluationRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Start RAG Evaluation process in background.
    """
    background_tasks.add_task(run_evaluation_task, request.environment_id, request.limit)
    return {"message": "Evaluation started in background. Check logs or results endpoint for progress."}

@router.get("/results_generative", response_model=List[EvaluationResultResponse])
def get_all_results_generative(
    page: int = 1,
    limit: int = 100,
    environment_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    offset = (page - 1) * limit
    service = EvaluationService(db)
    return service.get_all_results(limit, offset, environment_id, start_date, end_date)

@router.get("/results_generative/{environment_id}", response_model=List[EvaluationResultResponse])
def get_results(
    environment_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = EvaluationService(db)
    return service.get_results(environment_id)

@router.post("/test-cases/import", response_model=dict)
async def import_test_cases(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    
    content = await file.read()
    service = EvaluationService(db)
    try:
        count = service.import_test_cases_from_csv(content)
        return {"message": f"Successfully imported {count} test cases."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Import failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during import.")

@router.post("/test-cases", response_model=RagTestCaseResponse)
def create_test_case_api(
    test_case: RagTestCaseCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = EvaluationService(db)
    return service.create_test_case(test_case.question, test_case.reference_answer)

@router.put("/test-cases/{case_id}", response_model=RagTestCaseResponse)
def update_test_case_api(
    case_id: int,
    data: RagTestCaseCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = EvaluationService(db)
    updated = service.update_test_case(case_id, data.question, data.reference_answer)
    if not updated:
        raise HTTPException(status_code=404, detail="Test case not found")
    return updated

@router.delete("/test-cases/{case_id}", status_code=204)
def delete_test_case_api(
    case_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = EvaluationService(db)
    deleted = service.delete_test_case(case_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Test case not found")
    return

@router.get("/test-cases", response_model=List[RagTestCaseResponse])
def get_test_cases(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    service = EvaluationService(db)
    return service.get_all_test_cases()
