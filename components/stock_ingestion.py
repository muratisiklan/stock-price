import os
import pandas as pd
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pymongo import MongoClient
from src.utils import get_data_from_yfinance
from src.exception import CustomException
from src.logger import logging

@dataclass
class StockIngestionConfig:
    connection_string: str = "mongodb://127.0.0.1:27017/"
    database_name: str = "stockdata"
    symbols_list = list(pd.read_csv("/Users/muratisiklan/Desktop/stock-price/Artifacts/base_data/bist_data.csv")["Symbol"])

class StockIngestion:
    def __init__(self) -> None:
        self.ingestion_config = StockIngestionConfig()

    def initiate_stock_ingestion(self) -> None:
        client = MongoClient(self.ingestion_config.connection_string)
        db = client[self.ingestion_config.database_name]

        for symbol in self.ingestion_config.symbols_list:
            collection = db[symbol]
            try:
                logging.info(f"Data Ingestion is Started for Symbol: {symbol}")

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
                    logging.warning(f"No data retrieved for {symbol}")
                    continue

                data['_id'] = pd.to_datetime(data['Date']).dt.strftime("%Y-%m-%d")
                data = data.drop(columns=['Date'])

                data_list = data.to_dict(orient='records')
                collection.insert_many(data_list)

            except Exception as e:
                raise CustomException(e,sys)
            

        client.close()

