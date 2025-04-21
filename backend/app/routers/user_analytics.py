from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.user_analytics_service import get_user_analytics
from ..schemas.user_analytics_schema import AnalyticsResponse
from .auth import get_current_user

router = APIRouter(prefix="/user_analytics", tags=["user_analytics"])

user_dependency = Depends(get_current_user)
db_dependency = Depends(get_db)


@router.get("/", response_model=AnalyticsResponse, status_code=status.HTTP_200_OK)
async def get_data_last_month(
    db: Session = db_dependency,
    user: dict = user_dependency,
    last_month_start: Optional[date] = datetime.today().date(),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    return get_user_analytics(db, user, last_month_start)
