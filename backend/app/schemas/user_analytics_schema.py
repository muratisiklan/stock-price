from pydantic import BaseModel, Field
from typing import List
from datetime import date


class CompanyDetail(BaseModel):
    company_name: str = Field(...,
                              description="Name of the company")
    num_investments: int = Field(...,
                                 description="Number of investments made in the company")
    num_divestments: int = Field(...,
                                 description="Number of divestments made in the company")
    total_invested: float = Field(...,
                                  description="Total amount invested in the company")
    total_divested: float = Field(...,
                                  description="Total amount divested from the company")

    quantity_invested: int = Field(...,
                                   description="Total quantity invested in specific company")
    quantity_nonrealized_investment: int = Field(...,
                                                 description="Total quantity invested yet not realized for each company")
    quantity_divested: int = Field(...,
                                   description="Total quantity divested in specific company")

    cost_of_realized_investment: float = Field(...,
                                               description="Total cost of realized investments per company")
    revenue_from_realized_investment: float = Field(...,
                                                    description="Total revenue gained(realized) by divestments for each company")
    net_return: float = Field(...,
                              description="Total net return in last month by each company")
    average_cost: float = Field(...,
                                description="Total net return in last month by each company")
    average_revenue: float = Field(...,
                                description="Total net return in last month by each company")
    average_profit: float = Field(...,
                                description="Total net return in last month by each company")

    # class Config:
    #     json_schema_extra = {
    #         "example": {
    #             "company_name": "Company A",
    #             "num_investments": 2,
    #             "num_divestments": 1,
    #             "total_invested": 10000.00,
    #             "total_divested": 5000.00,
    #             "quantity_invested": 10,
    #             "quantity_divested": 10,
    #             "net_return": 100.25
    #         }
    #     }


class AnalyticsResponse(BaseModel):
    from_date: date = Field(...,
                            description="Analytics starting from this date")

    num_investments: int = Field(...,
                                 description="Total number of investments in the last month")
    num_divestments: int = Field(...,
                                 description="Total number of divestments in the last month")

    distinct_companies_invested: int = Field(
        ..., description="Number of distinct companies invested in the last month")
    distinct_companies_divested: int = Field(
        ..., description="Number of distinct companies divested in the last month")

    total_invested: float = Field(...,
                                  description="Total amount invested in the last month")
    total_divested: float = Field(...,
                                  description="Total amount divested in the last month")

    quantity_invested: int = Field(...,
                                   description="Total quantity invested in the last month")
    quantity_nonrealized_investment: int = Field(...,
                                                 description="Total quantity nonrealized  ivestments in the last month")
    quantity_divested: int = Field(...,
                                   description="Total quantity divested in the last month")

    cost_of_realized_investment: float = Field(...,
                                               description="Total cost of investments which are realized by divestments in the last month")
    revenue_from_realized_investment: float = Field(...,
                                                    description="Total revenue gained(realized) by divestments in the last month")
    net_return: float = Field(...,
                              description="Total net return in last month")
    average_cost: float = Field(...,
                                description="Total net return in last month by each company")
    average_revenue: float = Field(...,
                                description="Total net return in last month by each company")
    average_profit: float = Field(...,
                                description="Total net return in last month by each company")

    investments_by_company: List[CompanyDetail] = Field(
        ..., description="Detailed information for each company")

    class Config:
        json_schema_extra = {
            "example": {
                "from_date": "2024-12-12",
                "num_investments": 5,
                "num_divestments": 2,
                "distinct_companies_invested": 3,
                "distinct_companies_divested": 2,
                "total_invested": 15000.50,
                "total_divested": 8000.75,
                "quantity_invested": 5,
                "quantity_nonrealized_investment": 3,
                "quantity_divested": 2,
                "cost_of_realized_investment": 1200.00,
                "revenue_from_realized_investment": 1323.00,
                "net_return": 123.00,
                "average_cost": 500.00,
                "average_revenue":600.00,
                "average_profit":100.00,


                "investments_by_company": [
                    {
                        "company_name": "Company A",
                        "num_investments": 2,
                        "num_divestments": 1,
                        "total_invested": 10000.00,
                        "total_divested": 5000.00,
                        "quantity_invested": 10,
                        "quantity_nonrealized_investment": 10,
                        "quantity_divested": 10,
                        "cost_of_realized_investment": 150.00,
                        "revenue_from_realized_investment": 250.00,
                        "net_return": 100.00,
                        "average_cost": 500.00,
                        "average_revenue":600.00,
                        "average_profit":100.00,

                    },
                    {
                        "company_name": "Company B",
                        "num_investments": 2,
                        "num_divestments": 1,
                        "total_invested": 10000.00,
                        "total_divested": 5000.00,
                        "quantity_invested": 10,
                        "quantity_nonrealized_investment": 10,
                        "quantity_divested": 10,
                        "cost_of_realized_investment": 150.00,
                        "revenue_from_realized_investment": 250.00,
                        "net_return": 100.00,
                        "average_cost": 500.00,
                        "average_revenue":600.00,
                        "average_profit":100.00,
                    },
                    {
                        "company_name": "Company C",
                        "num_investments": 2,
                        "num_divestments": 1,
                        "total_invested": 10000.00,
                        "total_divested": 5000.00,
                        "quantity_invested": 10,
                        "quantity_nonrealized_investment": 10,
                        "quantity_divested": 10,
                        "cost_of_realized_investment": 150.00,
                        "revenue_from_realized_investment": 250.00,
                        "net_return": 100.00,
                        "average_cost": 500.00,
                        "average_revenue":600.00,
                        "average_profit":100.00,


                    }
                ]
            }
        }

        from_attributes = True


# Total investments last month
# Total Divestments last month
# Distinct companies invested last month
# Distinct companies divested last month
# Total amount invested last month
# Total amount divested last month

# For Investments, number of investments for each company last month
# For Divestments, number of divestments for each company last month

# For each company,some detailed infor regarding last month
