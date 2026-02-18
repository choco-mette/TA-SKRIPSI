from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from app.models.models import EnvironmentModel
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class LLMService:
    def __init__(self, db: Session):
        self.db = db

    def get_llm_model(self, temperature: float = 0.7, environment_id: int = None):
        """
        Factories the LangChain ChatOpenAI Model based on active DB configuration.
        Compatible with Deepseek, Sumopod, OpenAI, etc.
        """
        # Fetch model config
        if environment_id:
            config = self.db.query(EnvironmentModel).filter(
                EnvironmentModel.id == environment_id
            ).first()
            if not config:
                error_msg = f"Environment Model ID {environment_id} not found."
                logger.error(error_msg)
                raise ValueError(error_msg)
        else:
            # Fetch default active chat model config
            config = self.db.query(EnvironmentModel).filter(
                EnvironmentModel.model_type == 'chat', 
                EnvironmentModel.is_active == True
            ).first()

        if not config:
            error_msg = "No active chat model configuration found in Admin Settings."
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"Initializing LLM Request -> Base URL: {config.base_url} | Model: {config.models_name}")

        # Initialize ChatOpenAI
        return ChatOpenAI(
            model=config.models_name,
            openai_api_key=config.api_key,
            openai_api_base=config.base_url,
            temperature=temperature
        )
