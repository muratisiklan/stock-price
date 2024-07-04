import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import datetime as dt
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


def is_up_to_date(mongo_uri: str) -> bool:
    """returns true if db is up to date
    returns false if db is not up to date
    

    Args:
        mongo_uri (str): _description_

    Raises:
        CustomException: _description_

    Returns:
        bool: _description_
    """

    try:

        with MongoClient(mongo_uri) as client:
            static_symbol = "ASELS.IS"
            db = client.stockdata
            collection = db[static_symbol]
            cursor = collection.find().sort("_id", -1).limit(1)
            data = list(cursor)

            entry_date = data[0]["_id"]
            hour_now = datetime.now().time()
            today = datetime.today()
            yesterday = today - timedelta(days=1)

            # saat 18.15 ile 23.59 arasındaysa son entry bugünün tarihi olacak
            if hour_now > dt.time(18, 15) and hour_now < dt.time(0, 0):
                return entry_date == today.strftime("%Y-%m-%d")
            # saat 00.00 ile 18.14 arasındaysa son entry dünün tarihi olacak
            else:
                return entry_date == yesterday.strftime("%Y-%m-%d")
    except Exception as e:
        raise CustomException(e, sys)
    finally:
        client.close()
