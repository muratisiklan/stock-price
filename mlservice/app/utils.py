import pandas as pd
import yfinance as yf
from datetime import datetime
from .logger import logging
from .exception import CustomException
import sys
from pymongo import MongoClient


def get_data_from_yfinance(symbol: str, start_date: str, end_date: str):
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


def get_historical_data(mongo_uri: str, symbol: str, last_n: int) -> pd.DataFrame:
    """
    Retrieves historical data for a specific stock symbol from MongoDB.

    Args:
        mongo_uri (str): MongoDB connection URI.
        symbol (str): Stock symbol (ticker) to retrieve data for.
        last_n (int): Number of days of historical data to retrieve.

    Returns:
        pd.DataFrame: DataFrame containing the historical data for the specified symbol.
    """
    with MongoClient(mongo_uri) as client:
        try:
            # Connect to MongoDB and select the collection
            db = client.stockdata
            collection = db[symbol]

            # Retrieve the last N documents for the given symbol
            cursor = collection.find().sort("_id", -1).limit(last_n)

            # Convert cursor to list of documents
            data_list = list(cursor)

            # Convert the selected documents into a DataFrame
            df = pd.DataFrame(data_list)

            return df

        except Exception as e:
            logging.error(
                f"Error retrieving historical data for {symbol}: {e}")
            raise CustomException(
                f"Error retrieving historical data for {symbol}: {e}", sys)
        finally:
            client.close()
