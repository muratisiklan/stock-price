from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

""""""
# models for investments
""""""
# For investment Post requests


class InvestmenRequest(BaseModel):
    title: str = Field(min_length=3)
    company: str = Field(min_length=2)
    description: str = Field(min_length=3, max_length=100)
    date_invested: Optional[date]
    unit_price: float
    quantity: int




""""""
# Models fo Divestments
""""""
# class DivestmentRequest(BaseModel):
#     #?come from dropdwn menu?
#     quantity: int
#     unit_price: float
#     investment_id:int
#     date_divested = Optional[date]



""""""
# Models for Auath
""""""


class UserCreateRequest(BaseModel):
    username: str = Field(..., description="Username of the user")
    email: str = Field(..., description="Email address of the user")
    first_name: str = Field(..., description="First name of the user")
    last_name: str = Field(..., description="Last name of the user")
    password: str = Field(..., description="Password of the user")
    phone_number: str = Field(..., description="Phone number of the user")


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


""""""
# For user verification
""""""
class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=2)
