from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional, List
import requests

from ..database import get_db
from ..models import User, Divestment, Investment
from .auth import get_current_user
from ..config import settings_api
from ..schemas.company_analytics_schema import CompanyMetrics, CompanyAnalyticsResponse
from ..services.company_analytics_service import get_company_metrics_service

router = APIRouter(prefix="/company_analytics", tags=["company_analytics"])

user_dependency = Depends(get_current_user)
db_dependency = Depends(get_db)


@router.get("/", response_model=CompanyAnalyticsResponse, status_code=status.HTTP_200_OK)
async def get_company_metrics(
    db: Session = db_dependency,
    user: dict = user_dependency,
    start_from: Optional[date] = datetime.today().date()
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed!")

    try:
        response = get_company_metrics_service(db, user, start_from)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=str(e))
