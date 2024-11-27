from pymongo import MongoClient
from core.config import settings

client = MongoClient(settings.MONGO_URL)
db = client[settings.MONGO_DB_NAME]
deployment_history_collection = db["deployment"]
user_collection = db["users"]


