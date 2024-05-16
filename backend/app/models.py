from .database import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, String, Boolean, Date, Float
from datetime import datetime


def default_date():
    return datetime.today().date()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="pleb")
    phone_number = Column(String)


class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String)
    company = Column(String)
    description = Column(String)
    complete = Column(Boolean, default=False)
    date_invested = Column(Date, default=default_date)
    unit_price = Column(Float)
    quantity = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))
