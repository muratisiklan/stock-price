from .components.stage01data_ingestion import StockIngestion
from .exception import CustomException
from .logger import logging
from .database import client


bist_db = client.stockdata
# Example usage
try:
    stock_ingestion = StockIngestion()
    stock_ingestion.initiate_stock_ingestion()
except CustomException as e:
    logging.error(f"Failed to ingest stock data: {e}")
except Exception as e:
    logging.error(f"Unexpected error: {e}")




#TODO: Check if data base i up to date, if not initiate stock ingestion


#TODO: For each company, make predictions short mid long term


#TODO: Save predictions to mongodb

