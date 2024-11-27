from pymongo import MongoClient
from core.config import settings

client = MongoClient(settings.MONGO_URL)
db = client[settings.MONGO_DB_NAME]
user_collection = db["users"]
