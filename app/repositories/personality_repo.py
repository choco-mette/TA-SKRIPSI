from sqlalchemy.orm import Session
from app.models.models import PersonalityAI
from typing import Optional

class PersonalityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_first(self) -> Optional[PersonalityAI]:
        return self.db.query(PersonalityAI).first()

    def create(self, personality: PersonalityAI) -> PersonalityAI:
        self.db.add(personality)
        self.db.commit()
        self.db.refresh(personality)
        return personality

    def update(self, personality: PersonalityAI) -> PersonalityAI:
        self.db.commit()
        self.db.refresh(personality)
        return personality
