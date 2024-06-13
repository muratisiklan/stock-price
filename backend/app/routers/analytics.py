from typing import Annotated, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func, or_
import logging

from ..database import get_db
from ..models import User, Divestment, Investment
from ..schemas.analytics_schema import AnalyticsResponse
from .auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/", response_model=AnalyticsResponse, status_code=status.HTTP_200_OK)
async def get_data_last_month(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    last_month_start = datetime.now() - timedelta(days=30)

    # Check if the user has any investment or divestment
    has_investments = db.query(Investment).filter(
        Investment.owner_id == user.get("id")).first()
    has_divestments = db.query(Divestment).filter(
        Divestment.owner_id == user.get("id")).first()

    if not has_investments and not has_divestments:
        logger.info(
            f"User {user.get('id')} has no investments or divestments.")
        return AnalyticsResponse(
            num_investments=0,
            distinct_companies_invested=0,
            total_invested=0.0,
            num_divestments=0,
            distinct_companies_divested=0,
            total_divested=0.0
        )

    response = AnalyticsResponse(
        num_investments=0,
        distinct_companies_invested=0,
        total_invested=0.0,
        num_divestments=0,
        distinct_companies_divested=0,
        total_divested=0.0
    )

    if has_investments:
        investments_data = db.query(
            func.count(Investment.id).label("num_investments"),
            func.count(func.distinct(Investment.company)).label(
                "distinct_companies_invested"),
            func.sum(Investment.quantity *
                     Investment.unit_price).label("total_invested")
        ).filter(
            Investment.owner_id == user.get("id"),
            Investment.date_invested >= last_month_start
        ).first()

        if investments_data:
            response.num_investments = investments_data.num_investments or 0
            response.distinct_companies_invested = investments_data.distinct_companies_invested or 0
            response.total_invested = investments_data.total_invested or 0.0

    if has_divestments:
        divestments_data = db.query(
            func.count(Divestment.id).label("num_divestments"),
            func.count(func.distinct(Divestment.company)).label(
                "distinct_companies_divested"),
            func.sum(Divestment.quantity *
                     Divestment.unit_price).label("total_divested")
        ).filter(
            Divestment.owner_id == user.get("id"),
            Divestment.date_divested >= last_month_start
        ).first()

        if divestments_data:
            response.num_divestments = divestments_data.num_divestments or 0
            response.distinct_companies_divested = divestments_data.distinct_companies_divested or 0
            response.total_divested = divestments_data.total_divested or 0.0

    return response
