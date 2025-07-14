from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
#MYSQL_USER = os.getenv("MYSQL_USER", "root")
#MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")  # no default, required
#MYSQL_HOST = os.getenv("MYSQL_HOST", "sql")
#MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
#MYSQL_DB = os.getenv("MYSQL_DB", "auto_agent_evaluation")
POSTGRES_URI = os.getenv("POSTGRES_URI")
if not POSTGRES_URI:
    raise RuntimeError("❌ Environment variable POSTGRES_URI is not set.")

#SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

engine = create_engine(POSTGRES_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get DB session in FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()