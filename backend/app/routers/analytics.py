from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, aliased
from datetime import datetime,date
from sqlalchemy import func, distinct
from dateutil.relativedelta import relativedelta
from typing import Optional

from ..database import get_db
from ..models import User, Divestment, Investment
from ..schemas.analytics_schema import AnalyticsResponse, CompanyDetail
from .auth import get_current_user

# Analytics calculations are based on transactions(both investment and divestment) made in specified date interval
# if a divestment is included in specified interval; yet associated investment is before that date; such
# divestment is not accounted while calculated analytics
# ie: Analytics calculated for Investments(and associated divestments) made inside specified time interval



router = APIRouter(prefix="/analytics", tags=["analytics"])

user_dependency = Depends(get_current_user)
db_dependency = Depends(get_db)


@router.get("/", response_model=AnalyticsResponse, status_code=status.HTTP_200_OK)
async def get_data_last_month(
    db: Session = db_dependency,
    user: dict = user_dependency,
    last_month_start:Optional[date] = datetime.today().date()
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

 
    # Query for investments
    investment_data = db.query(
        func.count(Investment.id).label("num_investments"),
        func.sum(Investment.quantity *
                 Investment.unit_price).label("total_invested"),
        func.count(distinct(Investment.company)).label(
            "distinct_companies_invested"),
        func.sum(Investment.quantity).label("quantity_invested"),
        func.sum(Investment.quantity_remaining).label("quantity_nonrealized_investment"),
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
        func.sum(Divestment.quantity).label("quantity_divested"),
        func.sum(Divestment.cost_of_investment).label("cost_of_realized_investment"),
        func.sum(Divestment.revenue).label("revenue_from_realized_investment"),
        func.sum(Divestment.net_return).label("net_return")
    ).filter(
        Divestment.owner_id == user["id"],
        Divestment.date_invested >= last_month_start
    ).first()

    # Subqueries for specific company investment and divestment metrics
    investment_subquery = db.query(
        Investment.company.label("company_name"),
        func.count(Investment.id).label("num_investments"),
        func.sum(Investment.quantity *
                 Investment.unit_price).label("total_invested"),
        func.sum(Investment.quantity).label("quantity_invested"),
        func.sum(Investment.quantity_remaining).label("quantity_nonrealized_investment")
    ).filter(
        Investment.owner_id == user["id"],
        Investment.date_invested >= last_month_start
    ).group_by(Investment.company).subquery()

    divestment_subquery = db.query(
        Divestment.company.label("company_name"),
        func.count(Divestment.id).label("num_divestments"),
        func.sum(Divestment.quantity *
                 Divestment.unit_price).label("total_divested"),
        func.sum(Divestment.quantity).label("quantity_divested"),
        func.sum(Divestment.cost_of_investment).label("cost_of_realized_investment"),
        func.sum(Divestment.revenue).label("revenue_from_realized_investment"),
        func.sum(Divestment.net_return).label("net_return")
    ).filter(
        Divestment.owner_id == user["id"],
        Divestment.date_invested >= last_month_start
    ).group_by(Divestment.company).subquery()

    # Alias the subqueries for clarity
    investment_alias = aliased(investment_subquery)
    divestment_alias = aliased(divestment_subquery)

    # Perform the join on company_name
    query = db.query(
        investment_alias.c.company_name,
        investment_alias.c.num_investments,
        investment_alias.c.total_invested,
        investment_alias.c.quantity_invested,
        investment_alias.c.quantity_nonrealized_investment,
        divestment_alias.c.num_divestments,
        divestment_alias.c.total_divested,
        divestment_alias.c.quantity_divested,
        divestment_alias.c.cost_of_realized_investment,
        divestment_alias.c.revenue_from_realized_investment,
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
            quantity_nonrealized_investment=row.quantity_nonrealized_investment or 0,
            quantity_divested=row.quantity_divested or 0,
            cost_of_realized_investment= row.cost_of_realized_investment or 0,
            revenue_from_realized_investment= row.revenue_from_realized_investment or 0,
            net_return=row.net_return or 0.0
        )
        company_details.append(company_detail)

    # Construct the final AnalyticsResponse object
    response = AnalyticsResponse(
        from_date=last_month_start,
        num_investments=investment_data.num_investments or 0,
        num_divestments=divestment_data.num_divestments or 0,
        distinct_companies_invested=investment_data.distinct_companies_invested or 0,
        distinct_companies_divested=divestment_data.distinct_companies_divested or 0,
        total_invested=investment_data.total_invested or 0.0,
        total_divested=divestment_data.total_divested or 0.0,
        quantity_invested=investment_data.quantity_invested or 0,
        quantity_nonrealized_investment = investment_data.quantity_nonrealized_investment or 0,
        quantity_divested=divestment_data.quantity_divested or 0,
        cost_of_realized_investment = divestment_data.cost_of_realized_investment or 0,
        revenue_from_realized_investment= divestment_data.revenue_from_realized_investment or 0,
        net_return=divestment_data.net_return or 0.0,
        investments_by_company=company_details
    )

    return response
