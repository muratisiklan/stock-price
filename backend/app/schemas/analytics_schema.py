from pydantic import BaseModel, Field


class AnalyticsResponse(BaseModel):
    num_investments: int = Field(...,
                                 description="Total number of investments in the last month")
    distinct_companies_invested: int = Field(
        ..., description="Number of distinct companies invested in the last month")
    total_invested: float = Field(...,
                                  description="Total amount invested in the last month")
    num_divestments: int = Field(...,
                                 description="Total number of divestments in the last month")
    distinct_companies_divested: int = Field(
        ..., description="Number of distinct companies divested in the last month")
    total_divested: float = Field(...,
                                  description="Total amount divested in the last month")

    class Config:
        schema_extra = {
            "example": {
                "num_investments": 5,
                "distinct_companies_invested": 3,
                "total_invested": 15000.50,
                "num_divestments": 2,
                "distinct_companies_divested": 2,
                "total_divested": 8000.75
            }
        }
