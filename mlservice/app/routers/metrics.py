from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, date
from typing import Optional
from ..components.stage02get_data import CompanyMetrics
from ..database import mongo_uri
from ..utils.utils import sanitize_for_json

# Analytics calculations are based on transactions(both investment and divestment) made in specified date interval
# if a divestment is included in specified interval; yet associated investment is before that date; such
# divestment is not accounted while calculated analytics
# ie: Analytics calculated for Investments(and associated divestments) made inside specified time interval


router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/",  status_code=status.HTTP_200_OK)
async def get_company_metrics(
    symbol: str = Query(default="ASELS.IS",
                        description="Stock symbol of the company"),
    start_date: Optional[str] = Query(datetime.today().strftime("%Y-%m-%d"),
                                      lt=datetime.today().strftime("%Y-%m-%d"),
                                      description="Will calculate metrics starting from this date"),
):

    # if start_date >= datetime.today().strftime("%Y-%m-%d"):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Start date cannot be in the future."
    #     )

    # Initialize the CompanyMetrics instance
    cm = CompanyMetrics(mongo_uri)

    # Attempt to calculate the company metrics
    try:
        metrics = cm.calculate_company_metrics(symbol, start_date)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while calculating metrics."
        )
    response = sanitize_for_json(metrics)

    return response

