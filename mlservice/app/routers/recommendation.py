from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..components.stage02get_data import CompanyMetrics
from ..database import mongo_uri
from ..utils.utils import get_data_as_data_frame, sanitize_for_json

router = APIRouter(prefix="/recommendation", tags=["recommendation"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_company_data(
    symbol: str = Query(default="ASELS.IS", description="Stock symbol of the company"),
    start_date: Optional[str] = Query(
        datetime.today().strftime("%Y-%m-%d"),
        lt=datetime.today().strftime("%Y-%m-%d"),
        description="Will get company data starting from this date!",
    ),
):
    cm = CompanyMetrics(mongo_uri)
    company_data = []

    for ticker in cm.symbols_list:
        data = cm.calculate_company_metrics(ticker, start_date)
        company_data.append(data)

    print(company_data)
    print(type(company_data))

    # TODO: Fetch data for every company with close prices (Last 365 rows for each company)

    # TODO: Calculate additional metrics for companies

    # Some Metrics that are used in metrics.py can be used

    # Todo: İmpute missing values etc (data cleaning)

    # TODO: create clustering with optimal K clusters

    # TODO: Randomly select 3 company where symbol is in same cluster

    # TODO: Return selected 3 company symbols as recommendation

    return None
