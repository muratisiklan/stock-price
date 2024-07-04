from .components.stage01data_ingestion import StockIngestion
from .exception import CustomException
from .logger import logging
from .components.stage02get_data import calculate_company_metrics
from pymongo import MongoClient
import asyncio
from .database import client

bist_db = client.stockdata
# Example usage
# try:
#     stock_ingestion = StockIngestion()
#     stock_ingestion.initiate_stock_ingestion()
# except CustomException as e:
#     logging.error(f"Failed to ingest stock data: {e}")
# except Exception as e:
#     logging.error(f"Unexpected error: {e}")





# Calculate company metrics


# Example usage: calculate metrics for the last 100 days
async def main():
    try:
        # Example usage: calculate metrics for the last 100 days
        metrics = await calculate_company_metrics(100)

        for symbol, metric in metrics.items():
            print(f"Metrics for {symbol}:")
            for key, value in metric.items():
                print(f"  {key}: {value}")
            print()

    except Exception as e:
        print(f"Error: {e}")


asyncio.run(main())

#TODO: Check if data base i up to date, if not initiate stock ingestion


#TODO: For each company, make predictions short mid long term


#TODO: Save predictions to mongodb

