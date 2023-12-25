import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
from src.utils import get_stock_data
"""
    Update Database (Load New Data)
"""


def update_db():
    # Connect to MongoDB (replace 'your_mongodb_uri' and 'your_database_name')
    client = MongoClient('mongodb://127.0.0.1:27017/')
    db = client['stockdata']
    collection = db['stock']

    # Read S&P 500 company data from the CSV file
    sp500_df = pd.read_csv(
        "/Users/muratisiklan/Desktop/stock-price/Artifacts/constituents_csv.csv")

    # Get the tickers, company names, and create a dictionary for quick lookup
    sp500_data = sp500_df.set_index('Symbol')[['Name']].to_dict()['Name']

    # Take the top 100 companies
    top_500_symbols = sp500_df.head(500)['Symbol']

    # Find the most recent date in the MongoDB collection for any symbol
    latest_date_record = collection.find_one(sort=[('Date', -1)])
    if latest_date_record:
        latest_date = latest_date_record['Date']
    else:
        # If the collection is empty, set the start date to a specific point in the past
        latest_date = datetime(2000, 1, 1)

    # Date range for the most recent data until now
    start_date = (latest_date + timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    # Iterate through top 100 symbols
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

    # Close the MongoDB connection
    client.close()
