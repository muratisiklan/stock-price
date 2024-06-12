from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status

from ..database import get_db
from ..models import User, Divestment, Investment
from ..schemas.divestment_schema import DivestmentRequest
from .auth import get_current_user
from datetime import datetime
from datetime import timedelta
from sqlalchemy import func
router = APIRouter(prefix="/analytics", tags=["analytics"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_data_last_month(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    last_month = datetime.now() - timedelta(30)

    investment_model = db.query(Investment).filter(Investment.owner_id == user.get(
        "id"), Investment.date_invested >= last_month).first()
    divestment_model = db.query(Divestment).filter(Divestment.owner_id == user.get(
        "id"), Divestment.date_divested <= last_month).first()
    if investment_model:
        # Calculate total number of investments last month
        num_investments = db.query(func.count).filter(
            Investment.owner_id == user.get("id"), Investment.date_invested <= last_month).scalar()
    # Calculate number of distinct companies invested last month
        distinct_companies_invested = len(db.query(Investment.company).filter(Investment.owner_id == user.get("id"),
                                                                              Investment.date_invested >= last_month).distinct().all())

    # Claculate Total amount invested last month
        total_invested = db.query(func.sum(Investment.quantity * Investment.unit_price)).filter(
            Investment.owner_id == user.get(
                "id"), Investment.date_invested >= last_month
        )

    if divestment_model:
        # Calculate total number of divestments last month
        num_divestment = db.query(func.count).filter(
            Divestment.owner_id == user.get("id"), Divestment.date_divested <= last_month).scalar()

    # Calculate total number of distinct companies divested last month
    #! Might some problems divestment table doesnt have company field

    # Calculate total amount divested last month
    total_divested = db.query(func.sum(Divestment.quantity * Divestment.unit_price)).filter(
        Divestment.owner_id == user.get(
            "id"), Divestment.date_divested >= last_month
    )


    return total_divested
