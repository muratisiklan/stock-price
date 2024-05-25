from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import DATE, TIMESTAMP
from sqlalchemy.types import Boolean, Float, Integer, String

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    role = Column(String, default="pleb")
    phone_number = Column(String)
    # ? number of investments and total investment is incremented in Investment post request
    number_of_investments = Column(Integer, nullable=False, default=0)
    total_investment = Column(Integer, nullable=False, default=0)


class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String)
    company = Column(String)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    date_invested = Column(DATE, nullable=False, server_default=text("now()"))
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    unit_price = Column(Float)
    quantity = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))


# class Company(Base):
#     __tablename__ = "companies"

#     id = Column(Integer, primary_key=True,index=True,autoincrement=True)
#     name = Column(String,nullable=False)
#     times_invested = Column(Integer,nullable=False,default=0)
#     amount_invested =Column(Integer,nullable=False,default=0)
