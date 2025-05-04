from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class DivestmentMainRequest(BaseModel):
    date_divested: Optional[date]
    unit_price: float
    quantity: int
    company: str

    class Config:
        from_attributes = True
