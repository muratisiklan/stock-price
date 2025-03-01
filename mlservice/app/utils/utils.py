import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import datetime as dt
from .logger import logging
from .exception import CustomException
import sys
from pymongo import MongoClient
import numpy as np


def get_data_from_yfinance(symbol: str, start_date: str, end_date: str):
    # Includes start, excludes end date
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    try:
        # Fetch historical stock data for the specified symbol and date range from Yahoo Finance
        stock_data = yf.download(symbol, start=start_date, end=end_date)
        
        stock_data.columns = stock_data.columns.droplevel(1)
        stock_data = stock_data.iloc[1:].copy()
        stock_data.reset_index(inplace=True)
        stock_data.columns.name =None

        return stock_data
    except Exception as e:
        print(
            f"Error fetching data for {symbol} from {start_date} to {end_date}: {e}")


def get_historical_data(mongo_uri: str, symbol: str, start_date: str) -> pd.DataFrame:
    """
    Retrieves historical data for a specific stock symbol from MongoDB.

    Args:
        mongo_uri (str): MongoDB connection URI.
        symbol (str): Stock symbol (ticker) to retrieve data for.
        start_date (str): Data to be retrieved from date

    Returns:
        pd.DataFrame: DataFrame containing the historical data for the specified symbol.
    """
    with MongoClient(mongo_uri) as client:
        try:
            # Connect to MongoDB and select the collection
            db = client.stockdata
            collection = db[symbol]
            query = {"_id": {"$gte": start_date}}

            # Retrieve the last N documents for the given symbol
            cursor = collection.find(query).sort("_id", -1)

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
        mongo_uri (str): mongo connetion string

    Raises:
        CustomException: _description_

    Returns:
        bool: true if db is up to date false otherwise
    """

    try:
        # If database not exist or empty return false

        with MongoClient(mongo_uri) as client:
            if "stockdata" not in client.list_database_names():
                return False
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


def sanitize_for_json(data):
    if isinstance(data, dict):
        return {k: sanitize_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_for_json(i) for i in data]
    elif isinstance(data, float):
        if np.isfinite(data):
            return data
        else:
            return None  # or a default value
    else:
        return data


def get_data_as_data_frame(mongo_uri, days) -> pd.DataFrame:

    with MongoClient(mongo_uri) as client:
        try:
            database = client.stockdata
            all_data = []
            for collection_name in database.list_collection_names():
                collection = database[collection_name]
                # Fetch last 365 entries
                last_entries = list(
                    collection.find()
                    .sort("_id", -1)  # Sort by `_id` in descending order
                    .limit(days)
                )
                # Add collection name to each document
                for entry in last_entries:
                    entry['collection_name'] = collection_name
                    all_data.append(entry)

            # Convert to Pandas DataFrame
            df = pd.DataFrame(all_data)
            return df
        except Exception:
            raise CustomException(
                f"Error retrieving historical data", sys)
        finally:
            client.close()
