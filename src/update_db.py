import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
from src.utils import get_stock_data
import yfinance as yf
import numpy as np
"""
    Update Database (Load New Data)
"""


def update_stocks_collection():
    # Constants
    MONGO_URI = "mongodb://127.0.0.1:27017/"
    DB_NAME = "stockdata"
    COLLECTION_NAME = "stocks"
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




def update_interest_collection():
    MONGO_URI = "mongodb://127.0.0.1:27017/"
    DB_NAME = "stockdata"
    COLLECTION_NAME = "interest"
    EXCEL_FILE_PATH = "/Users/muratisiklan/Desktop/stock-price/Artifacts/interest_rates.xlsx"

    with MongoClient(MONGO_URI) as client:
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Find the most recent entry in the collection
        most_recent_entry = collection.find_one(sort=[('_id', -1)])

        if most_recent_entry:
            most_recent_date_str = most_recent_entry.get("_id")
            most_recent_date = datetime.strptime(most_recent_date_str, "%Y-%m-%d")
        else:
            # If the collection is empty, set the most_recent_date to a reasonable default
            most_recent_date = datetime(2000, 1, 1)

        df = pd.read_excel(EXCEL_FILE_PATH, parse_dates=['Date'])
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

        most_recent_rate = df.loc[df['Date'].idxmax()]['Rate']

        # Check if the most recent entry is from today
        if most_recent_date.date() == datetime.now().date():
            print("Most recent entry is from today. No updates needed.")
            return

        # Calculate the number of days between most_recent_date and today
        days_difference = (datetime.now() - most_recent_date).days

        # Generate a date range based on the number of days
        date_range = [most_recent_date + timedelta(days=i) for i in range(1, days_difference + 1)]

        for date in date_range:
            date_str = date.strftime("%Y-%m-%d")

            # Create a document
            document = {
                "_id": date_str,
                "Rate": most_recent_rate
            }

            # Insert the document into the collection
            collection.insert_one(document)