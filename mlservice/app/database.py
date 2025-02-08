from pymongo import MongoClient
from .config import settings_api


#mongo_uri = "mongodb://127.0.0.1:27017/"


mongo_uri = f"{settings_api.mongo_url}"
