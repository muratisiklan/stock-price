from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings_api

# from fastapi import Depends

# change databse
# "DBMS://USERNAME:PASSWORD@HOST:PORT/DBNAME"
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings_api.database_username}:{settings_api.database_password}@{settings_api.database_hostname}:{settings_api.database_port}/{settings_api.database_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
