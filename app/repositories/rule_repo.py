from sqlalchemy.orm import Session
from app.models.models import Rule
from typing import List, Optional

class RuleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, rule: Rule) -> Rule:
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Rule]:
        return self.db.query(Rule).offset(skip).limit(limit).all()

    def get_by_id(self, rule_id: int) -> Optional[Rule]:
        return self.db.query(Rule).filter(Rule.id == rule_id).first()

    def update(self, rule: Rule) -> Rule:
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete(self, rule: Rule):
        self.db.delete(rule)
        self.db.commit()
