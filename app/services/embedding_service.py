from langchain_openai import OpenAIEmbeddings
from sqlalchemy.orm import Session
from app.models.models import EnvironmentModel

class EmbeddingConfigService:
    def __init__(self, db: Session):
        self.db = db

    def get_embedding_model(self):
        """
        Factories the LangChain Embedding Model based on active DB configuration.
        """
        # Fetch active embedding config
        config = self.db.query(EnvironmentModel).filter(
            EnvironmentModel.model_type == 'embedding', 
            EnvironmentModel.is_active == True
        ).first()

        if not config:
            # Fallback or Error? For now raising error to enforce config
            raise ValueError("No active embedding model configuration found in Admin Settings.")

        # Initialize OpenAIEmbeddings (SumoPod/Deepseek compatible)
        # Note: 'model' parameter usually required by OpenAIEmbeddings, 
        # using the 'models_name' from DB.
        return OpenAIEmbeddings(
            model=config.models_name,
            openai_api_key=config.api_key,
            openai_api_base=config.base_url,
            check_embedding_ctx_length=False # prevent checks if using non-standard models
        )
