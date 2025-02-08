from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from typing import Optional
from ..components.stage02get_data import CompanyMetrics
from ..database import mongo_uri
from fastapi.responses import StreamingResponse
import matplotlib.pyplot as plt
import pandas as pd
import io

# This API is responsible for returning a chart related to customer's company shares for a period of time.

router = APIRouter(prefix="/charts", tags=["charts"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_company_charts(
    symbol: str = Query(default="ASELS.IS",
                        description="Stock symbol of the company"),
    start_date: Optional[str] = Query(datetime.today().strftime("%Y-%m-%d"),
                                      lt=datetime.today().strftime("%Y-%m-%d"),
                                      description="Stock symbol of the company"),
):

    # Initialize the CompanyMetrics instance
    cm = CompanyMetrics(mongo_uri)

    # Attempt to calculate the company metrics
    try:
        data = cm.calculate_company_metrics(
            symbol, start_date, return_data=True)
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

    data['_id'] = pd.to_datetime(data['_id'])

    # Plotting the data
    plt.figure(figsize=(10, 5))
    plt.plot(data['_id'], data['Close'], marker='o')
    plt.title(f'Closing Prices Since {start_date} for Company {symbol}')
    plt.xlabel('Date')
    plt.ylabel('Closing Price')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    # Save the plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return StreamingResponse(buf, media_type="image/png")
