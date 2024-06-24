from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    username: str = Field(..., description="Username of the user")
    email: str = Field(..., description="Email address of the user")
    first_name: str = Field(..., description="First name of the user")
    last_name: str = Field(..., description="Last name of the user")
    password: str = Field(..., description="Password of the user")
    phone_number: str = Field(..., description="Phone number of the user")

    class Config:
        from_attributes = True

