from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

database_url = f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
