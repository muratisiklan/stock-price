from .components.stage01data_ingestion import StockIngestion
from .components.stage02get_data import CompanyMetrics
from .database import mongo_uri
from .utils.utils import is_up_to_date
from .utils.exception import CustomException
import sys

comp_filter = "ASELS.IS"
start_date = "2024-05-05"


if not is_up_to_date(mongo_uri):
    try:
        stock_ingestion = StockIngestion(mongo_uri)
        #stock_ingestion.ingest_all_data("2024-06-06")
        stock_ingestion.initiate_stock_ingestion()
    except Exception as e:
        raise CustomException(e, sys)


# try:
#     comp_metrics = CompanyMetrics(mongo_uri)
#     metrics = comp_metrics.calculate_company_metrics(
#         comp_filter, start_date)
#     # data = metrics[comp_filter]

#     print(f"Metrics for {comp_filter}:")
#     for key, value in metrics.items():
#         print(f" {key} : {value}")
#         print()
# except Exception as e:
#     raise CustomException(e, sys)
