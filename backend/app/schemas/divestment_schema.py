from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class DivestmentRequest(BaseModel):
    investment_id: int
    date_divested: Optional[date]
    unit_price: float
    quantity: int

    class Config:
        from_attributes = True

