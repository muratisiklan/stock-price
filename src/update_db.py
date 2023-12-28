import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
from src.utils import get_stock_data
import yfinance as yf
"""
    Update Database (Load New Data)
"""
    

def update_database(collection_name):
    # Constants
    MONGO_URI = "mongodb://127.0.0.1:27017/"
    DB_NAME = "stockdata"
    COLLECTION_NAME = collection_name
    bist_data = pd.read_csv(
        "/Users/muratisiklan/Desktop/stock-price/Artifacts/bist_data.csv")

    # Connect to MongoDB
    with MongoClient(MONGO_URI) as client:
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Get the most recent date in the database
        most_recent_entry = collection.find_one({}, sort=[("_id", -1)])

        if most_recent_entry:
            most_recent_date = datetime.strptime(
                most_recent_entry["_id"], "%Y-%m-%d")
        else:
            # If the database is empty, set the most recent date to a specific start date
            most_recent_date = datetime.strptime("2015-01-01", "%Y-%m-%d")

        # Calculate the date range to fetch data
        today = datetime.now()
        date_range_start = (most_recent_date).strftime("%Y-%m-%d")
        date_range_end = (today+timedelta(days=1)).strftime("%Y-%m-%d")

        for index, row in bist_data.iterrows():
            symbol = row['Symbol']
            company = row['Name']

            # Fetch stock data
            stock_data = yf.download(
                symbol, start=date_range_start, end=date_range_end)

            if not stock_data.empty:
                # Organize stock data by date
                for date_str, data in stock_data.iterrows():
                    date_str = date_str.strftime('%Y-%m-%d')
                    document = {
                        "Symbol": symbol,
                        "Company": company,
                        "Open": data['Open'],
                        "High": data['High'],
                        "Low": data['Low'],
                        "Close": data['Close'],
                        "AdjClose": data['Adj Close'],
                        "Volume": data['Volume']
                    }
                    # Insert document into MongoDB collection
                    collection.update_one({"_id": date_str}, {
                                          "$push": {"bist": document}}, upsert=True)
