from .components.stage01data_ingestion import StockIngestion
from .database import mongo_uri
from .components.stage02get_data import calculate_company_metrics
from pymongo import MongoClient


# ingestion = StockIngestion(mongo_uri)
# ingestion.initiate_stock_ingestion()


try:
# Example usage: calculate metrics for the last 100 days
    metrics = calculate_company_metrics(100)

    for symbol, metric in metrics.items():
        print(f"Metrics for {symbol}:")
        for key, value in metric.items():
            print(f"  {key}: {value}")
        print()

except Exception as e:
    print(f"Error: {e}")



# TODO: Check if data base i up to date, if not initiate stock ingestion


# TODO: For each company, make predictions short mid long term


# TODO: Save predictions to mongodb
