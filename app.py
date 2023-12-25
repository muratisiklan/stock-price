from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from datetime import datetime, timedelta

app = FastAPI()

# Connect to MongoDB
client = MongoClient('mongodb://127.0.0.1:27017/')
db = client['stockdata']
collection = db['stock']

# Serve the frontend app
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/stock/{symbol}", response_class=HTMLResponse)
def get_stock_data(request: Request, symbol: str, start_date: datetime = None, end_date: datetime = None):
    # Your logic to retrieve stock data from MongoDB based on symbol and date range
    # You can use start_date and end_date parameters for filtering data

    # Example: Fetch data for the last 30 days
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)

    if not end_date:
        end_date = datetime.now()

    stock_data = collection.find({
        'Symbol': symbol,
        'Date': {'$gte': start_date, '$lte': end_date}
    })

    # Convert MongoDB cursor to a list of dictionaries
    stock_data_list = list(stock_data)

    return templates.TemplateResponse("stock_chart.html", {"request": request, "symbol": symbol, "stock_data": stock_data_list})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
