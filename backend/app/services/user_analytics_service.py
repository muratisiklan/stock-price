from datetime import date
from typing import Dict

import requests
from sqlalchemy import distinct, func
from sqlalchemy.orm import Session, aliased

from ..config import settings_api
from ..models import Divestment, Investment
from ..schemas.user_analytics_schema import AnalyticsResponse, CompanyDetail


def get_user_analytics(db: Session, user: dict, last_month_start: date) -> AnalyticsResponse:
    # Query for investments
    investment_data = (
        db.query(
            func.count(Investment.id).label("num_investments"),
            func.sum(Investment.quantity * Investment.unit_price).label(
                "total_invested"
            ),
            func.count(distinct(Investment.company)).label(
                "distinct_companies_invested"
            ),
            func.sum(Investment.quantity).label("quantity_invested"),
            func.sum(Investment.quantity_remaining).label(
                "quantity_nonrealized_investment"
            ),
        )
        .filter(
            Investment.owner_id == user["id"],
            Investment.date_invested >= last_month_start,
        )
        .first()
    )

    # Query for divestments
    divestment_data = (
        db.query(
            func.count(Divestment.id).label("num_divestments"),
            func.sum(Divestment.quantity * Divestment.unit_price).label(
                "total_divested"
            ),
            func.count(distinct(Divestment.company)).label(
                "distinct_companies_divested"
            ),
            func.sum(Divestment.quantity).label("quantity_divested"),
            func.sum(Divestment.cost_of_investment).label(
                "cost_of_realized_investment"
            ),
            func.sum(Divestment.revenue).label("revenue_from_realized_investment"),
            func.sum(Divestment.net_return).label("net_return"),
        )
        .filter(
            Divestment.owner_id == user["id"],
            Divestment.date_invested >= last_month_start,
        )
        .first()
    )

    # Subqueries for specific company investment and divestment metrics
    investment_subquery = (
        db.query(
            Investment.company.label("company_name"),
            func.count(Investment.id).label("num_investments"),
            func.sum(Investment.quantity * Investment.unit_price).label(
                "total_invested"
            ),
            func.sum(Investment.quantity).label("quantity_invested"),
            func.sum(Investment.quantity_remaining).label(
                "quantity_nonrealized_investment"
            ),
        )
        .filter(
            Investment.owner_id == user["id"],
            Investment.date_invested >= last_month_start,
        )
        .group_by(Investment.company)
        .subquery()
    )

    divestment_subquery = (
        db.query(
            Divestment.company.label("company_name"),
            func.count(Divestment.id).label("num_divestments"),
            func.sum(Divestment.quantity * Divestment.unit_price).label(
                "total_divested"
            ),
            func.sum(Divestment.quantity).label("quantity_divested"),
            func.sum(Divestment.cost_of_investment).label(
                "cost_of_realized_investment"
            ),
            func.sum(Divestment.revenue).label("revenue_from_realized_investment"),
            func.sum(Divestment.net_return).label("net_return"),
        )
        .filter(
            Divestment.owner_id == user["id"],
            Divestment.date_invested >= last_month_start,
        )
        .group_by(Divestment.company)
        .subquery()
    )

    # Alias the subqueries for clarity
    investment_alias = aliased(investment_subquery)
    divestment_alias = aliased(divestment_subquery)

    # Perform the join on company_name
    query = (
        db.query(
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
            divestment_alias.c.net_return,
        )
        .join(
            divestment_alias,
            investment_alias.c.company_name == divestment_alias.c.company_name,
            isouter=True,
        )
        .all()
    )

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
            cost_of_realized_investment=row.cost_of_realized_investment or 0,
            revenue_from_realized_investment=row.revenue_from_realized_investment or 0,
            net_return=row.net_return or 0.0,
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
        quantity_nonrealized_investment=investment_data.quantity_nonrealized_investment or 0,
        quantity_divested=divestment_data.quantity_divested or 0,
        cost_of_realized_investment=divestment_data.cost_of_realized_investment or 0,
        revenue_from_realized_investment=divestment_data.revenue_from_realized_investment or 0,
        net_return=divestment_data.net_return or 0.0,
        investments_by_company=company_details,
    )

    return response
