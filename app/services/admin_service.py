from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.rule_repo import RuleRepository
from app.schemas.rule import RuleCreate, RuleUpdate
from app.models.models import Rule, User

class AdminService:
    def __init__(self, db: Session):
        self.rule_repo = RuleRepository(db)

    def create_rule(self, data: RuleCreate, current_user: User) -> Rule:
        new_rule = Rule(
            content=data.content,
            is_active=data.is_active,
            created_by=current_user.id
        )
        return self.rule_repo.create(new_rule)

    def get_rules(self, skip: int = 0, limit: int = 100):
        return self.rule_repo.get_all(skip, limit)

    def update_rule(self, rule_id: int, data: RuleUpdate) -> Rule:
        rule = self.rule_repo.get_by_id(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        if data.content is not None:
            rule.content = data.content
        if data.is_active is not None:
            rule.is_active = data.is_active
            
        return self.rule_repo.update(rule)

    def delete_rule(self, rule_id: int):
        rule = self.rule_repo.get_by_id(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        self.rule_repo.delete(rule)
