from src.components.stock_ingestion import StockIngestion 
# main.py

# stock_price/main.py
# stock_price_app/main.py


from fastapi import FastAPI, HTTPException,Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class StockPrice(BaseModel):
    _id: str
    Open: float
    High: float
    Low: float
    Close: float
    Adj_Close: float
    Volume: int

class StockInvestment(BaseModel):
    stock_symbol: str
    start_date: str
    end_date: str

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient("mongodb://your_mongo_db_connection_string")
    app.mongodb = app.mongodb_client.your_database_name

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/calculate_roi/{stock_symbol}")
async def calculate_roi(stock_symbol: str, investment: StockInvestment):
    db_collection = app.mongodb[stock_symbol]
    stock_prices = list(db_collection.find({
        "_id": {"$gte": investment.start_date, "$lte": investment.end_date}
    }))

    if not stock_prices:
        raise HTTPException(status_code=404, detail="Stock prices not found")

    total_investment = calculate_total_investment(stock_prices)
    total_return = calculate_total_return(stock_prices)

    return {"total_investment": total_investment, "total_return": total_return}

def calculate_total_investment(stock_prices: List[StockPrice]) -> float:
    return sum(price['Close'] * price['Volume'] for price in stock_prices)

def calculate_total_return(stock_prices: List[StockPrice]) -> float:
    return sum(price['Close'] * price['Volume'] for price in stock_prices) * 1.1



# if __name__ == "__main__":
#     stock_ingestion = StockIngestion()
#     stock_ingestion.initiate_stock_ingestion()