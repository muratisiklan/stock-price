from pymongo import MongoClient
import pandas as pd

def fetch_stock_data_from_mongo(symbol, start, end):
    """
    Fetches stock data for a specific stock symbol within a specific time interval from MongoDB.
    Includes Rate values from the 'interest' collection.

    Parameters:
    - symbol (str): Stock symbol (e.g., "BINHO.IS").
    - start (str): Start date in the format "%Y-%m-%d".
    - end (str): End date in the format "%Y-%m-%d".

    Returns:
    - pd.DataFrame: Pandas DataFrame containing the fetched stock data and Rate values.
    """
    # Constants
    MONGO_URI = "mongodb://127.0.0.1:27017/"
    DB_NAME = "stockdata"
    COLLECTION_NAME_STOCKS = "stocks"
    COLLECTION_NAME_INTEREST = "interest"

    # Connect to MongoDB
    with MongoClient(MONGO_URI) as client:
        db = client[DB_NAME]
        collection_stocks = db[COLLECTION_NAME_STOCKS]
        collection_interest = db[COLLECTION_NAME_INTEREST]

        # Query MongoDB collection for the specified symbol and time interval in 'stocks'
        query_stocks = {
            "_id": {"$gte": start, "$lte": end},
            "bist.Symbol": symbol
        }

        cursor_stocks = collection_stocks.find(query_stocks, {"bist.$": 1})

        # Extract stock data from the cursor and convert it to a DataFrame
        data_list = []
        for document in cursor_stocks:
            for entry in document["bist"]:
                if entry["Symbol"] == symbol:
                    data_list.append({
                        "Date": document["_id"],
                        "Symbol": entry["Symbol"],
                        "Company": entry["Company"],
                        "Open": entry["Open"],
                        "High": entry["High"],
                        "Low": entry["Low"],
                        "Close": entry["Close"],
                        "AdjClose": entry["AdjClose"],
                        "Volume": entry["Volume"]
                    })

        # Query MongoDB collection for Rate values in 'interest'
        query_interest = {
            "_id": {"$gte": start, "$lte": end}
        }

        cursor_interest = collection_interest.find(query_interest)

        # Create a dictionary to store Rate values by date
        rate_dict = {document["_id"]: document["Rate"] for document in cursor_interest}

        if data_list:
            # Convert the list of stock data to a DataFrame
            df = pd.DataFrame(data_list)

            # Add a 'Rate' column based on the 'Date' in the DataFrame
            df["Rate"] = df["Date"].map(rate_dict)

            return df
        else:
            print(f"No data found for {symbol} in the specified time interval.")
            return pd.DataFrame()
