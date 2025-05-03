from sqlalchemy.orm import Session
from sqlalchemy import distinct
import requests

from ..models import Investment
from ..config import settings_api
from ..schemas.company_analytics_schema import CompanyMetrics, CompanyAnalyticsResponse


def get_company_metrics_service(db: Session, user: dict, start_from: str) -> CompanyAnalyticsResponse:
    # Get distinct companies associated with the user's investments after the start date
    comp_query = db.query(distinct(Investment.company)).filter(
        #Investment.is_active == True,
        Investment.owner_id == user.get("id"),
        Investment.date_invested >= start_from
    ).all()

    companies = [company[0] for company in comp_query]

    company_metrics_list: List[CompanyMetrics] = []

    for symbol in companies:
        url = f'{settings_api.ml_svc_url}metrics/'
        params = {
            'symbol': symbol,
            'start_date': start_from,
        }

        try:
            res = requests.get(url, params=params)
            res.raise_for_status()

            data = res.json()  # Assuming the response is JSON
            print(data)

            metrics = CompanyMetrics(**data)
            company_metrics_list.append(metrics)

        except requests.exceptions.RequestException as e:
            print(f"Error sending request to {url}: {e}")
            raise Exception(f"Error fetching metrics for {symbol}")

    # Return the response object with company metrics
    response = CompanyAnalyticsResponse(
        holding_companies=companies,
        company_metrics=company_metrics_list
    )
    return response
