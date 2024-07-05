from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from typing import Optional
from ..components.stage02get_data import get_historical_data

# Analytics calculations are based on transactions(both investment and divestment) made in specified date interval
# if a divestment is included in specified interval; yet associated investment is before that date; such
# divestment is not accounted while calculated analytics
# ie: Analytics calculated for Investments(and associated divestments) made inside specified time interval


router = APIRouter(prefix="/metrics", tags=["metrics"])



@router.get("/",  status_code=status.HTTP_200_OK)
async def get_data_last_month(
    last_month_start: Optional[date] = datetime.today().date()
):
    today = datetime.today().date()
    
    
    response = None


    return response
