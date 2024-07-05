from .components.stage01data_ingestion import StockIngestion
from .components.stage02get_data import CompanyMetrics
from .components.stage03save_metrics import SaveCompanyMetrics
from .database import mongo_uri
from .utils import is_up_to_date
from .exception import CustomException
import sys

specified_time_period = 100
comp_filter = "DOAS.IS"


if True:
    try:
        comp_metrics = CompanyMetrics(mongo_uri)
        metrics = comp_metrics.calculate_company_metrics(specified_time_period)
        #data = metrics[comp_filter]


        save = SaveCompanyMetrics()
        save.db_save_metrics(mongo_uri, metrics)

        print(f"Metrics for {comp_filter}:")
        for key, value in metrics.items():
            print(f" {key} : {value}")
            print()
    except Exception as e:
        raise CustomException(e, sys)

else:
    try:
        stock_ingestion = StockIngestion(mongo_uri)
        stock_ingestion.initiate_stock_ingestion()
    except Exception as e:
        raise CustomException(e, sys)




