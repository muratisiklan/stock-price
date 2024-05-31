from datetime import date
from typing import Optional

from pydantic import BaseModel


class DivestmentRequest(BaseModel):
    # ?come from dropdwn menu?
    investment_id: int
    unit_price: float
    quantity: int
    date_divested : Optional[date]
