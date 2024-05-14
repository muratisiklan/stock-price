from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# from fastapi import Depends

## change databse
## "DBMS://USERNAME:PASSWORD@HOST:PORT/DBNAME"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/InvestmentAppDB"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


