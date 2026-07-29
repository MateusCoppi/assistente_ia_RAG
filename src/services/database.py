from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.models import Base
from sqlalchemy import text


DATABASE_URL = (
    "postgresql+psycopg://admin:admin123456@localhost:5432/rag_db"
)

engine = create_engine(DATABASE_URL)

# Instala a extensao para vetores
with engine.begin() as conn:
    conn.execute(
        text("CREATE EXTENSION IF NOT EXISTS vector")
    )

SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(engine)