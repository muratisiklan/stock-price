from sqlalchemy import Column, ForeignKey, column, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import DATE, TIMESTAMP
from sqlalchemy.types import Boolean, Float, Integer, String

from .database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    role = Column(String, default="pleb")
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    phone_number = Column(String)
    # ? number of investments and total investment is incremented in Investment post request
    number_of_investments = Column(Integer, nullable=False, default=0)
    total_investment = Column(Integer, nullable=False, default=0)
    number_of_divestments = Column(Integer, nullable=False, default=0)
    total_divestment = Column(Integer, nullable=False, default=0)

    is_premium = Column(Boolean, nullable=False, default=False)


class Investment(Base):
    __tablename__ = "investment"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date_invested = Column(DATE, nullable=False, server_default=text("now()"))
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=func.now())
    is_active = Column(Boolean, default=True)
    title = Column(String)
    company = Column(String)  # Ticker of corresponding company with .market
    description = Column(String)
    unit_price = Column(Float)
    quantity = Column(Integer)
    quantity_remaining = Column(Integer)

    owner_id = Column(Integer, ForeignKey("user.id"))


class Divestment(Base):
    __tablename__ = "divestment"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date_divested = Column(DATE, nullable=False, server_default=text("now()"))
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    date_invested = Column(DATE)
    company = Column(String)  # Ticker of corresponding company with .market

    unit_price = Column(Float)
    quantity = Column(Integer)

    cost_of_investment = Column(Float)
    revenue = Column(Float)
    net_return = Column(Float)

    investment_id = Column(Integer, ForeignKey("investment.id"))
    owner_id = Column(Integer, ForeignKey("user.id"))


class Process(Base):
    __tablename__ = "process"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    explanation = Column(String, nullable=False)


class Log(Base):
    __tablename__ = "log"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    request_message = Column(JSON, nullable=False, default=dict)
    response_message = Column(JSON, nullable=False, default=dict)

    # TODO: For Now process id can be nullable
    process_id = Column(Integer, ForeignKey("process.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)


class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    ticker = Column(String, nullable=False)
    # For now only İstanbul Stock Exchange
    market = Column(String, nullable=False, default="bist")

    full_name = Column(String, nullable=True)

    # pred_short = Column(Float,nullable=True)
    # pred_mid = Column(Float, nullable=True)
    # pred_long = Column(Float,nullable=True)
    #
    # # risk indexes
    # risk_short = Column(Float,nullable=True)
    # risk_mid = Column(Float, nullable=True)
    # risk_long = Column(Float,nullable=True)
