from datetime import date
from typing import Optional

from pydantic import BaseModel, Field




class DivestmentRequest(BaseModel):
    #?come from dropdwn menu?
    investment_id:int
    quantity: int
    unit_price: float
    date_divested = Optional[date]
