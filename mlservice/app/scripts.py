from .components.stage01data_ingestion import StockIngestion
from .components.stage02get_data import CompanyMetrics
from .database import mongo_uri
from .utils import is_up_to_date
from .exception import CustomException
import sys

# time_period = 100
# comp_filter = "DOAS.IS"


# if not is_up_to_date(mongo_uri):
#     try:
#         stock_ingestion = StockIngestion(mongo_uri)
#         stock_ingestion.initiate_stock_ingestion()
#     except Exception as e:
#         raise CustomException(e, sys)


# try:
#     comp_metrics = CompanyMetrics(mongo_uri)
#     metrics = comp_metrics.calculate_company_metrics(
#         comp_filter, time_period)
#     # data = metrics[comp_filter]

#     print(f"Metrics for {comp_filter}:")
#     for key, value in metrics.items():
#         print(f" {key} : {value}")
#         print()
# except Exception as e:
#     raise CustomException(e, sys)
