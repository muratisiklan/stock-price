from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, date
from typing import Optional
from ..components.stage02get_data import CompanyMetrics
from ..database import mongo_uri
from ..utils.utils import sanitize_for_json

router = APIRouter(prefix="/recommendation", tags=["recommendation"])


@router.get("/",  status_code=status.HTTP_200_OK)
async def get_company_metrics(
    symbol: str = Query(default="ASELS.IS",
                        description="Stock symbol of the company"),

):

    #TODO: Fetch data for every company with close prices (Last 365 rows for each company)


    #TODO: Calculate additional metrics for companies

    # Some Metrics that are used in metrics.py can be used 

    #Todo: İmpute missing values etc (data cleaning)


    #TODO: create clustering with optimal K clusters


    #TODO: Randomly select 3 company where symbol is in same cluster

    #TODO: Return selected 3 company symbols as recommendation


    return None
