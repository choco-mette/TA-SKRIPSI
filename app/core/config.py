import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_URL: str = os.getenv("DATABASE_URL")
    API_LLM_URL: str = os.getenv("API_LLM_URL")
    MODEL_LLM_NAME: str = os.getenv("MODEL_LLM_NAME")

settings = Settings()
