from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.rule_repo import RuleRepository
from app.repositories.personality_repo import PersonalityRepository
from app.schemas.rule import RuleCreate, RuleUpdate
from app.schemas.personality import PersonalityCreate, PersonalityUpdate
from app.models.models import Rule, User, PersonalityAI

class AdminService:
    def __init__(self, db: Session):
        self.rule_repo = RuleRepository(db)
        self.personality_repo = PersonalityRepository(db)

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

    # ==========================
    # PERSONALITY AI MANAGEMENT
    # ==========================

    def get_personality(self):
        return self.personality_repo.get_first()

    def create_personality(self, data: PersonalityCreate, current_user: User) -> PersonalityAI:
        existing = self.personality_repo.get_first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Personality already exists. Only one record allowed."
            )
        
        new_personality = PersonalityAI(
            content=data.content,
            created_by=current_user.id
        )
        return self.personality_repo.create(new_personality)

    def update_personality(self, data: PersonalityUpdate) -> PersonalityAI:
        personality = self.personality_repo.get_first()
        if not personality:
            raise HTTPException(status_code=404, detail="Personality not found")
        
        personality.content = data.content
        return self.personality_repo.update(personality)
