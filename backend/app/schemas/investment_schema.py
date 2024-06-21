from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class InvestmentRequest(BaseModel):
    title: str = Field(min_length=3)
    company: str = Field(min_length=2)
    description: str = Field(min_length=3, max_length=100)
    date_invested: Optional[date]
    unit_price: float
    quantity: int

    class Config:
        orm_mode = True
