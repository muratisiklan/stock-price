import yfinance as yf
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import numpy as np


def get_data_from_yfinance(symbol, start_date, end_date):
    # Includes start, excludes end date
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    try:
        # Fetch historical stock data for the specified symbol and date range from Yahoo Finance
        stock_data = yf.download(symbol, start=start_date, end=end_date)

        # Reset the index and format the '_id' field as a string
        stock_data.reset_index(inplace=True)

        return stock_data
    except Exception as e:
        print(
            f"Error fetching data for {symbol} from {start_date} to {end_date}: {e}")


def create_update_collections(connection_string, database, symbols_list):
    """cretes data frame for given symbol list starting from 2015-01-01 to now+1 (now is included)
    """
    client = MongoClient(connection_string)
    db = client[database]

    for symbol in symbols_list:

        collection = db[symbol]
        most_recent_document = collection.find_one({}, sort=[('_id', -1)])
        if most_recent_document:
            most_recent_id = most_recent_document["_id"]
            most_recent_date = datetime.strptime(most_recent_id, "%Y-%m-%d")
            one_day_later = most_recent_date + timedelta(days=1)
            start_date = one_day_later.strftime("%Y-%m-%d")

            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            end_date = tomorrow.strftime("%Y-%m-%d")
        else:
            start_date = "2015-01-01"
            tomorrow = datetime.now() + timedelta(days=1)
            end_date = tomorrow.strftime("%Y-%m-%d")

        data = get_data_from_yfinance(symbol, start_date, end_date)

        if data.empty:
            print(f"No data retrieved for {symbol}")
            continue

        data['_id'] = pd.to_datetime(data['Date']).dt.strftime("%Y-%m-%d")

        # Drop the original 'Date' column
        data = data.drop(columns=['Date'])

        # Convert the DataFrame to a list of dictionaries
        data_list = data.to_dict(orient='records')

        # Insert the data into the MongoDB collection
        collection.insert_many(data_list)

    client.close()


def update_interest_collection():
    MONGO_URI = "mongodb://127.0.0.1:27017/"
    DB_NAME = "stockdata"
    COLLECTION_NAME = "interest"
    EXCEL_FILE_PATH = "/Users/muratisiklan/Desktop/stock-price/Artifacts/base_data/interest_rates.xlsx"

    with MongoClient(MONGO_URI) as client:
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Find the most recent entry in the collection
        most_recent_entry = collection.find_one(sort=[('_id', -1)])

        most_recent_date_str = most_recent_entry.get("_id")
        most_recent_date = datetime.strptime(
            most_recent_date_str, "%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")

        if today == most_recent_date:
            print("Interest collection is up to date")

        else:

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
            date_range = [most_recent_date +
                          timedelta(days=i) for i in range(1, days_difference + 1)]

            for date in date_range:
                date_str = date.strftime("%Y-%m-%d")

                # Create a document
                document = {
                    "_id": date_str,
                    "Rate": most_recent_rate
                }

                # Insert the document into the collection
                collection.insert_one(document)
