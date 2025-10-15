import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_HOST: str = os.getenv("DB_HOST")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_PORT: str = os.getenv("DB_PORT")
    API_LLM_URL: str = os.getenv("API_LLM_URL")
    MODEL_LLM_NAME: str = os.getenv("MODEL_LLM_NAME")

settings = Settings()
