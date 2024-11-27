from pymongo import MongoClient
from core.config import settings


client = MongoClient(settings.MONGO_URL)
db = client[settings.MONGO_DB_NAME]
user_collection = db["users"]
project_collection = db["projects"]

deployment_history_collection = db["deployment"]
department_collection = db["department_db"]
technology_collection = db["technology_db"]
infra_collection = db["infra_db"]
domain_collection = db["domains"]
cronjob_collection = db["testing"]
cronjob_domain_testing = db["domain_testing"]
cronjob_department_testing = db["department_testing"]