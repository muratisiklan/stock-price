from datetime import date
from typing import List

from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from ..models import Divestment, Investment, DivestmentMain
from ..schemas.user_analytics_schema import AnalyticsResponse, CompanyDetail


def get_user_analytics(db: Session, user: dict, start_date: date) -> AnalyticsResponse:
    user_id = user["id"]

    # Common filters
    investment_filter = (
        Investment.owner_id == user_id,
        Investment.date_invested >= start_date
    )
    divestment_filter = (
        Divestment.owner_id == user_id,
        Divestment.date_invested >= start_date
    )

    # Helper for None safety
    def safe(value, default=0):
        return value if value is not None else default

    # Investment aggregation
    inv = db.query(
        func.count(Investment.id),
        func.sum(Investment.quantity * Investment.unit_price),
        func.count(distinct(Investment.company)),
        func.sum(Investment.quantity),
        func.sum(Investment.quantity_remaining),
        (func.sum(Investment.quantity * Investment.unit_price) /
         func.nullif(func.sum(Investment.quantity), 0)),
    ).filter(*investment_filter).first()

    (
        num_investments,
        total_invested,
        distinct_companies_invested,
        quantity_invested,
        quantity_nonrealized_investment,
        average_cost,
    ) = inv

    # Divestment aggregation
    div = db.query(
        func.count(Divestment.id),
        func.sum(Divestment.revenue),
        func.count(distinct(Divestment.company)),
        func.sum(Divestment.quantity),
        func.sum(Divestment.cost_of_investment),
        func.sum(Divestment.revenue),
        func.sum(Divestment.net_return),
        (func.sum(Divestment.quantity * Divestment.unit_price) /
         func.nullif(func.sum(Divestment.quantity), 0)),
    ).filter(*divestment_filter).first()

    (
        _,
        total_divested,
        distinct_companies_divested,
        quantity_divested,
        cost_of_realized_investment,
        revenue_from_realized_investment,
        net_return,
        average_revenue,
    ) = div

    # div_main optimized
    div_main = db.query(
        Divestment.company,
        func.count(func.distinct(Divestment.divestmentmain_id))
    ).filter(*divestment_filter).group_by(Divestment.company).all()

    div_main_dict = {company: count for company, count in div_main}
    total_num_div_mains = sum(div_main_dict.values())

    # Per-company investment metrics
    inv_subq = db.query(
        Investment.company.label("company"),
        func.count(Investment.id).label("num_investments"),
        func.sum(Investment.quantity * Investment.unit_price).label("total_invested"),
        func.sum(Investment.quantity).label("quantity_invested"),
        func.sum(Investment.quantity_remaining).label("quantity_nonrealized_investment"),
        (func.sum(Investment.quantity * Investment.unit_price) /
         func.nullif(func.sum(Investment.quantity), 0)).label("average_cost"),
    ).filter(*investment_filter).group_by(Investment.company).subquery()

    # Per-company divestment metrics
    div_subq = db.query(
        Divestment.company.label("company"),
        func.count(Divestment.id).label("num_divestments"),
        func.sum(Divestment.quantity * Divestment.unit_price).label("total_divested"),
        func.sum(Divestment.quantity).label("quantity_divested"),
        func.sum(Divestment.cost_of_investment).label("cost_of_realized_investment"),
        func.sum(Divestment.revenue).label("revenue_from_realized_investment"),
        func.sum(Divestment.net_return).label("net_return"),
        (func.sum(Divestment.quantity * Divestment.unit_price) /
         func.nullif(func.sum(Divestment.quantity), 0)).label("average_revenue"),
    ).filter(*divestment_filter).group_by(Divestment.company).subquery()

    # Outer join both subqueries
    company_rows = db.query(
        inv_subq.c.company,
        inv_subq.c.num_investments,
        inv_subq.c.total_invested,
        inv_subq.c.quantity_invested,
        inv_subq.c.quantity_nonrealized_investment,
        inv_subq.c.average_cost,
        div_subq.c.num_divestments,
        div_subq.c.total_divested,
        div_subq.c.quantity_divested,
        div_subq.c.cost_of_realized_investment,
        div_subq.c.revenue_from_realized_investment,
        div_subq.c.net_return,
        div_subq.c.average_revenue,
    ).outerjoin(div_subq, inv_subq.c.company == div_subq.c.company, full=True).all()

    # Assemble response
    company_details: List[CompanyDetail] = []
    for row in company_rows:
        avg_profit = safe(row.average_revenue, 0.0) - safe(row.average_cost, 0.0)
        company_details.append(CompanyDetail(
            company_name=row.company,
            num_investments=row.num_investments or 0,
            total_invested=safe(row.total_invested, 0.0),
            quantity_invested=row.quantity_invested or 0,
            quantity_nonrealized_investment=row.quantity_nonrealized_investment or 0,
            average_cost=safe(row.average_cost, 0.0),
            num_divestments=div_main_dict.get(row.company, 0),
            total_divested=safe(row.total_divested, 0.0),
            quantity_divested=row.quantity_divested or 0,
            cost_of_realized_investment=safe(row.cost_of_realized_investment),
            revenue_from_realized_investment=safe(row.revenue_from_realized_investment),
            net_return=safe(row.net_return, 0.0),
            average_revenue=safe(row.average_revenue, 0.0),
            average_profit=avg_profit,
        ))

    return AnalyticsResponse(
        from_date=start_date,
        num_investments=num_investments or 0,
        total_invested=safe(total_invested, 0.0),
        distinct_companies_invested=distinct_companies_invested or 0,
        quantity_invested=quantity_invested or 0,
        quantity_nonrealized_investment=quantity_nonrealized_investment or 0,
        average_cost=safe(average_cost, 0.0),
        num_divestments=total_num_div_mains,
        total_divested=safe(total_divested, 0.0),
        distinct_companies_divested=distinct_companies_divested or 0,
        quantity_divested=quantity_divested or 0,
        cost_of_realized_investment=safe(cost_of_realized_investment),
        revenue_from_realized_investment=safe(revenue_from_realized_investment),
        net_return=safe(net_return, 0.0),
        average_revenue=safe(average_revenue, 0.0),
        average_profit=(safe(average_revenue, 0.0) - safe(average_cost, 0.0)),
        investments_by_company=company_details,
    )
