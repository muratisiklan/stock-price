from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, date
from typing import Optional
from ..components.stage02get_data import CompanyMetrics
from ..database import mongo_uri
from ..utils.utils import sanitize_for_json
from fastapi.responses import StreamingResponse

# Analytics calculations are based on transactions(both investment and divestment) made in specified date interval
# if a divestment is included in specified interval; yet associated investment is before that date; such
# divestment is not accounted while calculated analytics
# ie: Analytics calculated for Investments(and associated divestments) made inside specified time interval


router = APIRouter(prefix="/chart", tags=["chart"])


@router.get("/",  status_code=status.HTTP_200_OK)
async def get_company_charts(
    symbol: str = Query(default="ASELS.IS",
                        description="Stock symbol of the company"),
    start_date: Optional[str] = Query(datetime.today().strftime("%Y-%m-%d"),
                                      lt=datetime.today().strftime("%Y-%m-%d"),
                                      description="Stock symbol of the company"),
):

    # figure = company_data
    # figure.savefig("tofile.png")
    # file = open("file.png",mode="rb")
    # response = StreamingResponse(file,media_type="image/png")

    # Initialize the CompanyMetrics instance
    cm = CompanyMetrics(mongo_uri)

    # Attempt to calculate the company metrics
    try:
        data = cm.calculate_company_metrics(symbol, start_date,data=True)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while calculating data."
        )

    print(data)


    return {"response": "hello world"}
