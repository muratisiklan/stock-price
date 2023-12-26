import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
from src.utils import get_stock_data
"""
    Update Database (Load New Data)
"""


def update_db_sp500():
    # Connect to MongoDB (replace 'your_mongodb_uri' and 'your_database_name')
    with MongoClient('mongodb://127.0.0.1:27017/') as client:
        db = client['stockdata']
        collection = db['stock']

        # Read S&P 500 company data from the CSV file
        sp500_df = pd.read_csv("/Users/muratisiklan/Desktop/stock-price/Artifacts/constituents_csv.csv")

        # Get the tickers, company names, and create a dictionary for quick lookup
        sp500_data = sp500_df.set_index('Symbol')[['Name']].to_dict()['Name']

        # Take the top 500 companies
        top_500_symbols = sp500_df.head(500)['Symbol']

        # Find the most recent date in the MongoDB collection for any symbol
        latest_date_record = collection.find_one(sort=[('Date', -1)])
        latest_date = latest_date_record['Date'] if latest_date_record else datetime(2000, 1, 1)

        # Date range for the most recent data until now
        start_date = (latest_date + timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')

        # Iterate through top 500 symbols
        for symbol in top_500_symbols:
            data = get_stock_data(symbol, start_date, end_date)

            if data is not None:
                # Add 'Symbol' and 'Company' to each record
                data['Symbol'] = symbol
                data['Company'] = sp500_data.get(symbol, '')

                # Reset the index and convert to a list of dictionaries for insertion
                data_dict_list = data.reset_index().to_dict(orient='records')

                # Check if the list is not empty before insertion
                if data_dict_list:
                    # Insert the data into MongoDB
                    collection.insert_many(data_dict_list)

def update_db_bist():
    # Connect to MongoDB (replace 'your_mongodb_uri' and 'your_database_name')
    with MongoClient('mongodb://127.0.0.1:27017/') as client:
        db = client['stockdata']
        collection = db['bist']

        # Read S&P 500 company data from the CSV file
        bist_df = pd.read_csv("/Users/muratisiklan/Desktop/stock-price/Artifacts/bist_data.csv")

        bist_data = bist_df.set_index('Code')[['Name']].to_dict()['Name']

        top_500_symbols = bist_df.head(500)['Code']

        # Find the most recent date in the MongoDB collection for any symbol
        latest_date_record = collection.find_one(sort=[('Date', -1)])
        latest_date = latest_date_record['Date'] if latest_date_record else datetime(2000, 1, 1)

        # Date range for the most recent data until now
        start_date = (latest_date + timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')

        # Iterate through top 500 symbols
        for symbol in top_500_symbols:
            data = get_stock_data(symbol, start_date, end_date)

            if data is not None:
                # Add 'Symbol' and 'Company' to each record
                data['Code'] = symbol
                data['Company'] = bist_data.get(symbol, '')

                # Reset the index and convert to a list of dictionaries for insertion
                data_dict_list = data.reset_index().to_dict(orient='records')

                # Check if the list is not empty before insertion
                if data_dict_list:
                    # Insert the data into MongoDB
                    collection.insert_many(data_dict_list)
