from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime
from sqlalchemy import func, distinct
from typing import Optional, List
import pydantic

from ..database import get_db
from ..models import User, Divestment, Investment
from .auth import get_current_user
from ..config import settings_api
from ..schemas.company_analytics_schema import CompanyMetrics, CompanyAnalyticsResponse
import requests

# Analytics calculations are based on transactions (both investment and divestment) made in the specified date interval.
# If a divestment is included in the specified interval, yet the associated investment is before that date, such
# divestment is not accounted for while calculating analytics.
# ie: Analytics are calculated for investments (and associated divestments) made inside the specified time interval.

router = APIRouter(prefix="/company_analytics", tags=["company_analytics"])

user_dependency = Depends(get_current_user)
db_dependency = Depends(get_db)
# response_model = CompanyAnalyticsResponse,


@router.get("/", response_model=CompanyAnalyticsResponse, status_code=status.HTTP_200_OK)
async def get_company_metrics(
    db: Session = db_dependency,
    user: dict = user_dependency,
    start_from: Optional[date] = datetime.today().date()
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed!")

    comp_query = db.query(distinct(Investment.company)).filter(
        Investment.is_active == True,
        Investment.owner_id == user.get("id"),
        Investment.date_invested >= start_from
    ).all()

    companies = [company[0] for company in comp_query]

    company_metrics_list: List[CompanyMetrics] = []

    for symbol in companies:
        url = f'{settings_api.ml_svc_url}metrics/'
        params = {
            'symbol': symbol,
            'start_date': start_from,
        }

        try:
            res = requests.get(url, params=params)
            res.raise_for_status()

            data = res.json()  # Assuming the response is JSON
            print(data)

            metrics = CompanyMetrics(**data)
            company_metrics_list.append(metrics)

        except requests.exceptions.RequestException as e:
            print(f"Error sending request to {url}: {e}")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail=f"Error fetching metrics for {symbol}")

    response = CompanyAnalyticsResponse(
        holding_companies=companies,
        company_metrics=company_metrics_list
    )

    return response
