from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=2)
