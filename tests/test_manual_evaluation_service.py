import os
import sys

# Tambahkan path project root agar bisa import app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.models import RagEvaluationResult, RagEvaluationRougeDetail
from app.services.evaluation_service import EvaluationService


def main():
    db = SessionLocal()
    service = EvaluationService(db=db)

    try:
        print("=== BACKFILL ROUGE DETAIL (PRECISION/RECALL/F1) ===\n")

        evaluation_rows = db.query(RagEvaluationResult).order_by(RagEvaluationResult.id.asc()).all()

        if not evaluation_rows:
            print("Tidak ada data pada rag_evaluation_results.")
            return

        inserted_count = 0
        skipped_count = 0
        failed_count = 0

        print(f"{'EvalID':<8} | {'Status':<10} | {'R1-F1':<8} | {'R2-F1':<8} | {'RL-F1':<8}")
        print("-" * 60)

        for eval_row in evaluation_rows:
            try:
                existing_detail = db.query(RagEvaluationRougeDetail).filter(
                    RagEvaluationRougeDetail.evaluation_result_id == eval_row.id
                ).first()

                if existing_detail:
                    skipped_count += 1
                    print(f"{eval_row.id:<8} | {'SKIPPED':<10} | {'-':<8} | {'-':<8} | {'-':<8}")
                    continue

                if not eval_row.test_case or not eval_row.test_case.reference_answer or not eval_row.model_answer:
                    failed_count += 1
                    print(f"{eval_row.id:<8} | {'FAILED':<10} | {'-':<8} | {'-':<8} | {'-':<8}")
                    continue

                metrics = service.evaluate_text_metrics(
                    reference_text=eval_row.test_case.reference_answer,
                    generated_text=eval_row.model_answer
                )

                rouge_detail = RagEvaluationRougeDetail(
                    evaluation_result_id=eval_row.id,
                    rouge_1_precision=metrics["rouge"]["rouge1"]["precision"],
                    rouge_1_recall=metrics["rouge"]["rouge1"]["recall"],
                    rouge_1_f1=metrics["rouge"]["rouge1"]["f1"],
                    rouge_2_precision=metrics["rouge"]["rouge2"]["precision"],
                    rouge_2_recall=metrics["rouge"]["rouge2"]["recall"],
                    rouge_2_f1=metrics["rouge"]["rouge2"]["f1"],
                    rouge_l_precision=metrics["rouge"]["rougeL"]["precision"],
                    rouge_l_recall=metrics["rouge"]["rougeL"]["recall"],
                    rouge_l_f1=metrics["rouge"]["rougeL"]["f1"],
                )
                db.add(rouge_detail)
                db.commit()

                inserted_count += 1
                print(
                    f"{eval_row.id:<8} | {'INSERTED':<10} | "
                    f"{metrics['rouge']['rouge1']['f1']:<8.4f} | "
                    f"{metrics['rouge']['rouge2']['f1']:<8.4f} | "
                    f"{metrics['rouge']['rougeL']['f1']:<8.4f}"
                )

            except Exception:
                db.rollback()
                failed_count += 1
                print(f"{eval_row.id:<8} | {'FAILED':<10} | {'-':<8} | {'-':<8} | {'-':<8}")

        print("-" * 60)
        print(f"Inserted : {inserted_count}")
        print(f"Skipped  : {skipped_count}")
        print(f"Failed   : {failed_count}")
        print("\nSelesai backfill.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
