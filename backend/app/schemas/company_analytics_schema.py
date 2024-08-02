from pydantic import BaseModel, Field
from typing import List
from datetime import date


class CompanyMetrics(BaseModel):

    symbol: str = Field(..., description="company symnol")
    from_date: date = Field(...,
                           description="Company metrics calculated from starting this date")
    max_value: float = Field(
        ..., description=" maximum value companies stock price reached starting from date specified")
    min_value: float = Field(
        ..., description=" minimum value companies stock price reached starting from date specified")
    standard_deviation: float = Field(
        ..., description="standard deviation of stock prices starting from given time")
    price_interval: float = Field(
        ..., description=" difference between min and maximum values of company stock from given starting date")
    percentage_change: float = Field(
        ..., description="percentege change from starting price and ending price(most current cloing) of given stock")
    volatility: float = Field(...,
                              description="volatility of company for given time")
    rsi: float = Field(...,
                       description="volatility of company for given time period")
    bollinger_up:float = Field(...,
                         description="bollinger upper band for given time period for company")
    bollinger_low:float = Field(...,
                          description="bollinger lower band for company in specific time")
    sharpe_ratio:float = Field(...,
                         description="sharpe ratio for company in given time")
    

class CompanyAnalyticsResponse(BaseModel):
    holding_companies: List[str] = Field(...,description= "Company symbols current user holds")
    company_metrics: List[CompanyMetrics] = Field(...,description="For each company current user holds list of analytics for each")
