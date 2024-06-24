from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func,distinct

from ..database import get_db
from ..models import User, Divestment, Investment
from ..schemas.analytics_schema import AnalyticsResponse, CompanyDetail
from .auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=AnalyticsResponse, status_code=status.HTTP_200_OK)
async def get_data_last_month(
    db: db_dependency,
    user: user_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    # Calculate the start of last month
    last_month_start = datetime.now() - timedelta(days=30)

    # Query to fetch aggregated investment and divestment data per company

    # number of investments last month
    num_investments = db.query(func.count(Investment.id)).filter(
        Investment.owner_id == user["id"],
        Investment.date_invested >= last_month_start
    ).scalar()
    total_invested = db.query(func.sum(Investment.quantity * Investment.unit_price)).filter(
        Investment.owner_id == user["id"],
        Investment.date_invested >= last_month_start
    ).scalar()

    distinct_companies_invested = db.query(func.count(distinct(Investment.company))).filter(
        Investment.owner_id == user["id"],
        Investment.date_invested >= last_month_start
    ).scalar()

    num_divestments = db.query(func.count(Divestment.id)).filter(
        Divestment.owner_id == user["id"],
        Divestment.date_invested >= last_month_start
    ).scalar()
    total_divested = db.query(func.sum(Divestment.quantity * Divestment.unit_price)).filter(
        Divestment.owner_id == user["id"],
        Divestment.date_invested >= last_month_start
    ).scalar()

    distinct_companies_divested = db.query(func.count(distinct(Divestment.company))).filter(
        Divestment.owner_id == user["id"],
        Divestment.date_invested >= last_month_start
    ).scalar()








    combined_query = db.query(
        Investment.company.label("company_name"),
        func.count(Investment.id).label("num_investments"),
        func.sum(Investment.quantity *
                 Investment.unit_price).label("total_invested"),
        func.sum(Investment.quantity).label("quantity_invested"),
        func.count(Divestment.id).label("num_divestments"),
        func.sum(Divestment.quantity *
                 Divestment.unit_price).label("total_divested"),
        func.sum(Divestment.quantity).label("quantity_divested")
    ).outerjoin(
        Divestment, (Investment.company == Divestment.company) &
                    (Divestment.owner_id == user["id"]) &
                    (Divestment.date_divested >= last_month_start)
    ).filter(
        Investment.owner_id == user["id"],
        Investment.date_invested >= last_month_start
    ).group_by(Investment.company).all()

    # Initialize variables for aggregating totals and distinct companies
    total_investments = 0
    total_divestments = 0
    total_amount_invested = 0.0
    total_amount_divested = 0.0
    distinct_companies_invested = 0
    distinct_companies_divested = 0
    company_details = []

    # Construct the final AnalyticsResponse object
    response = AnalyticsResponse(
        num_investments=total_investments,
        distinct_companies_invested=distinct_companies_invested,
        total_invested=total_amount_invested,
        num_divestments=total_divestments,
        distinct_companies_divested=distinct_companies_divested,
        total_divested=total_amount_divested,
        investments_by_company=company_details
    )

    return response
