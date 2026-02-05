from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from app.models.models import EnvironmentModel

class LLMService:
    def __init__(self, db: Session):
        self.db = db

    def get_llm_model(self, temperature: float = 0.7):
        """
        Factories the LangChain ChatOpenAI Model based on active DB configuration.
        Compatible with Deepseek, Sumopod, OpenAI, etc.
        """
        # Fetch active chat model config
        config = self.db.query(EnvironmentModel).filter(
            EnvironmentModel.model_type == 'chat', 
            EnvironmentModel.is_active == True
        ).first()

        if not config:
            raise ValueError("No active chat model configuration found in Admin Settings.")

        # Initialize ChatOpenAI
        return ChatOpenAI(
            model=config.models_name,
            openai_api_key=config.api_key,
            openai_api_base=config.base_url,
            temperature=temperature
        )
