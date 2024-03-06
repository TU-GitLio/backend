from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
POSTGRES_ID = os.environ.get("POSTGRES_ID")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_ID}:{POSTGRES_PASSWORD}@gitlio.czdnm9iu9p2c.us-east-1.rds.amazonaws.com:5432"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()