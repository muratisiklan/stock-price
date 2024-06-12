from typing import Annotated, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func

from ..database import get_db
from ..models import User, Divestment, Investment
from ..schemas.divestment_schema import DivestmentRequest
from .auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_data_last_month(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    last_month_start = datetime.now() - timedelta(days=30)

    # Calculate metrics for investments
    num_investments = db.query(func.count(Investment.id)).filter(
        Investment.owner_id == user.get("id"),
        Investment.date_invested >= last_month_start
    ).scalar()

    distinct_companies_invested = db.query(Investment.company).filter(
        Investment.owner_id == user.get("id"),
        Investment.date_invested >= last_month_start
    ).distinct().count()

    total_invested = db.query(func.sum(Investment.quantity * Investment.unit_price)).filter(
        Investment.owner_id == user.get("id"),
        Investment.date_invested >= last_month_start
    ).scalar()

    # Calculate metrics for divestments
    num_divestments = db.query(func.count(Divestment.id)).filter(
        Divestment.owner_id == user.get("id"),
        Divestment.date_divested >= last_month_start
    ).scalar()

    # Assuming divestment relates to company through investment
    #! distinct_companies_divested = db.query(Divestment.investment_company).filter(
    #     Divestment.owner_id == user.get("id"),
    #     Divestment.date_divested >= last_month_start
    # ).distinct().count()

    total_divested = db.query(func.sum(Divestment.quantity * Divestment.unit_price)).filter(
        Divestment.owner_id == user.get("id"),
        Divestment.date_divested >= last_month_start
    ).scalar()

    # Prepare the response
    response = {
        "num_investments": num_investments or 0,
        "distinct_companies_invested": distinct_companies_invested or 0,
        "total_invested": total_invested or 0.0,
        "num_divestments": num_divestments or 0,
        "total_divested": total_divested or 0.0,
    }

    return response
