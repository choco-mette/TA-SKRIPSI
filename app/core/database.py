from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine
from app.core.config import settings

# Membuat engine koneksi ke database
engine: Engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

# Factory untuk membuat database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class untuk semua ORM model
Base = declarative_base()


# Dependency database session untuk FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
