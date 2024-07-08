from pymongo import MongoClient
from ..exception import CustomException
from ..logger import logging
import sys
from datetime import datetime


class SaveCompanyMetrics():

    """Will not be used for now ------- !!!!!!!

    Raises:
        CustomException: _description_
    """

    def __init__(self) -> None:
        self.collection_name = "metrics"

    def db_save_metrics(self, mongo_uri: str, data: dict) -> None:
        """Saves metrics to mongo db data base with specified mongo uri and given data

        Raises:
            CustomException: _description_
        """

        today = datetime.today().strftime("%Y-%m-%d")  # Corrected date format
        documents = [{"_id": today, **data}]

        try:
            with MongoClient(mongo_uri) as client:
                db = client.metricdata
                collection = db[self.collection_name]

                # Check if document with today's _id already exists
                if collection.find_one({"_id": today}):
                    logging.warning(
                        f"A document with _id '{today}' already exists. It will be updated.")
                    collection.update_one({"_id": today}, {"$set": data})
                else:
                    collection.insert_many(documents)

                logging.info("Metrics saved or updated successfully.")

        except Exception as e:
            logging.error(f"An error occurred while saving metrics: {e}")
            raise CustomException(e, sys)

        finally:
            client.close()
