from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, aliased
from datetime import datetime, timedelta
from sqlalchemy import func, distinct

from ..database import get_db
from ..models import User, Divestment, Investment
from ..schemas.analytics_schema import AnalyticsResponse, CompanyDetail
from .auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

user_dependency = Depends(get_current_user)
db_dependency = Depends(get_db)


@router.get("/", response_model=AnalyticsResponse, status_code=status.HTTP_200_OK)
async def get_data_last_month(
    db: Session = db_dependency,
    user: dict = user_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    # Calculate the start of last month in UTC
    last_month_start = datetime.now() - timedelta(days=30)

    # Query for investments
    investment_data = db.query(
        func.count(Investment.id).label("num_investments"),
        func.sum(Investment.quantity *
                 Investment.unit_price).label("total_invested"),
        func.count(distinct(Investment.company)).label(
            "distinct_companies_invested")
    ).filter(
        Investment.owner_id == user["id"],
        Investment.date_invested >= last_month_start
    ).first()

    # Query for divestments
    divestment_data = db.query(
        func.count(Divestment.id).label("num_divestments"),
        func.sum(Divestment.quantity *
                 Divestment.unit_price).label("total_divested"),
        func.count(distinct(Divestment.company)).label(
            "distinct_companies_divested"),
        func.sum(Divestment.net_return).label("net_return")
    ).filter(
        Divestment.owner_id == user["id"],
        Divestment.date_divested >= last_month_start
    ).first()

    # investment metrics for specific company
    investment_subquery = db.query(Investment.company.label("company_name"),
                                   func.count(Investment.id).label(
        "num_investments"),
        func.sum(Investment.quantity *
                 Investment.unit_price).label("total_invested"),
        func.sum(Investment.quantity).label(
        "quantity_invested"),
    ).filter(
        Investment.owner_id == user["id"],
        Investment.date_invested >= last_month_start).group_by(Investment.company).subquery()

    divestment_subquery = db.query(Divestment.company.label("company_name"),
                                   func.count(Divestment.id).label(
        "num_divestments"),
        func.sum(Divestment.quantity *
                 Divestment.unit_price).label("total_divested"),
        func.sum(Divestment.quantity).label(
        "quantity_divested"),
        func.sum(Divestment.net_return).label(
        "net_return")
    ).filter(
        Divestment.owner_id == user["id"],
        Divestment.date_divested >= last_month_start).group_by(Divestment.company).subquery()


# Alias the subqueries for clarity
    investment_alias = aliased(investment_subquery)
    divestment_alias = aliased(divestment_subquery)

    # Perform the join on company_name
    query = db.query(
        investment_alias.c.company_name,
        investment_alias.c.num_investments,
        investment_alias.c.total_invested,
        investment_alias.c.quantity_invested,
        divestment_alias.c.num_divestments,
        divestment_alias.c.total_divested,
        divestment_alias.c.quantity_divested,
        divestment_alias.c.net_return
    ).join(
        divestment_alias, investment_alias.c.company_name == divestment_alias.c.company_name, isouter=True
    ).all()

    # Populate company details with handling for None values
    company_details = []
    for row in query:
        company_detail = CompanyDetail(
            company_name=row.company_name,
            num_investments=row.num_investments or 0,
            num_divestments=row.num_divestments or 0,
            total_invested=row.total_invested or 0.0,
            total_divested=row.total_divested or 0.0,
            quantity_invested=row.quantity_invested or 0,
            quantity_divested=row.quantity_divested or 0,
            net_return=row.net_return or 0.0
        )
        company_details.append(company_detail)

    # Construct the final AnalyticsResponse object
    response = AnalyticsResponse(
        num_investments=investment_data.num_investments or 0,
        distinct_companies_invested=investment_data.distinct_companies_invested or 0,
        total_invested=investment_data.total_invested or 0.0,
        num_divestments=divestment_data.num_divestments or 0,
        distinct_companies_divested=divestment_data.distinct_companies_divested or 0,
        total_divested=divestment_data.total_divested or 0.0,
        net_return=divestment_data.net_return or 0.0,
        investments_by_company=company_details
    )

    return response
