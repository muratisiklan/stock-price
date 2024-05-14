from pydantic import BaseModel, Field

""""""
# models for investments
""""""
# For investment Post requests


class InvestmenRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    company: str = Field(min_length=2)
    complete: bool

""""""
# Models for Auath
""""""

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str


""""""
# For user verification

""""""

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=2)
