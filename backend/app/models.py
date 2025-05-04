from sqlalchemy import Column, ForeignKey, func, Enum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import DATE, TIMESTAMP
from sqlalchemy.types import Boolean, Float, Integer, String

from .database import Base
from .enums.user_enum import UserRole


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    role = Column(Enum(UserRole, name="user_role"),
                  nullable=False, default=UserRole.PLEB)
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
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=True, onupdate=func.now())
    is_active = Column(Boolean, default=True)
    title = Column(String)
    company = Column(String, nullable=False)

    description = Column(String)
    unit_price = Column(Float)
    quantity = Column(Integer)
    quantity_remaining = Column(Integer)

    owner_id = Column(Integer, ForeignKey("user.id"))
    # company = Column(String, ForeignKey("company.name")) # Ticker of corresponding company with .market


class DivestmentMain(Base):
    __tablename__ = "divestment_main"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    # From Request
    unit_price = Column(Float)
    quantity = Column(Integer)
    date_divested = Column(DATE, nullable=False, server_default=text("now()"))
    company = Column(String, nullable=False)

    # Will be calculated at insert or update
    revenue = Column(Float)
    owner_id = Column(Integer, ForeignKey("user.id"))


class Divestment(Base):
    __tablename__ = "divestment"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    # From Rquest
    unit_price = Column(Float)
    quantity = Column(Integer)
    date_divested = Column(DATE, nullable=False, server_default=text("now()"))

    # Will be calculated at insert or update
    revenue = Column(Float)
    net_return = Column(Float)

    # From Respective Investment (with query param)
    date_invested = Column(DATE)  # TODO: Oldest Investment related with
    cost_of_investment = Column(Float)
    company = Column(String, nullable=False)

    divestmentmain_id = Column(Integer, ForeignKey("divestment_main.id"))
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
    name = Column(String, nullable=False, unique=False)
    ticker = Column(String, nullable=False, unique=False)

    # pred_short = Column(Float, nullable=True)
    # pred_mid = Column(Float, nullable=True)
    # pred_long = Column(Float, nullable=True)

    # # risk indexes
    # risk_short = Column(Float, nullable=True)
    # risk_mid = Column(Float, nullable=True)
    # risk_long = Column(Float, nullable=True)

    # For now only İstanbul Stock Exchange
    market_id = Column(Integer, ForeignKey("market.id"), nullable=True)


class Country(Base):
    __tablename__ = "country"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country_code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    region = Column(String, nullable=True)
    income_level = Column(Integer, nullable=True)

    # credit_rating = Column(Integer, nullable=True)
    # credit_status = Column(Integer, nullable=True)
    # gdp = Column(Float, nullable=True)


class Market(Base):
    __tablename__ = "market"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    country = Column(String, nullable=True)
    currency = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    mic_code = Column(String, nullable=True)
    yahoo_suffix = Column(String, nullable=True)

    index_30 = Column(Float, nullable=True)
    index_50 = Column(Float, nullable=True)
    index_100 = Column(Float, nullable=True)

    # country_id = Column(Integer, ForeignKey("country.id"), nullable=True)
