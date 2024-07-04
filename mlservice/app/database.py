from pymongo.errors import ConnectionFailure
from motor.motor_asyncio import AsyncIOMotorClient


# app/database.py

MONGO_DETAILS = "mongodb://127.0.0.1:27017/"  # Replace with your MongoDB URI

client = AsyncIOMotorClient(MONGO_DETAILS)

try:
    # Test the connection
    client.admin.command('ping')
    print("MongoDB connection successful")
except ConnectionFailure:
    print("MongoDB connection failed")
