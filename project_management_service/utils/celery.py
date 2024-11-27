import os
import json
import logging
import subprocess

import requests
from celery import Celery
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
from urllib.parse import quote_plus

# Load environment variables
env_path = find_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path=env_path)

# Setup logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
logfile = os.path.join(log_dir, 'cronjob.log')
logging.basicConfig(filename=logfile, level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration
celery = Celery('tasks', broker='redis://localhost:6379/0')
celery.conf.result_backend = 'redis://localhost:6379/0'

# MongoDB connection
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_READ_PREFERENCE = os.getenv("MONGO_READ_PREFERENCE", "primaryPreferred")
MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE")

MONGO_PASSWORD_ENCODED = quote_plus(MONGO_PASSWORD)
MONGO_URL = (
    f"mongodb://{MONGO_USER}:{MONGO_PASSWORD_ENCODED}@{MONGO_HOST}:{MONGO_PORT}/"
    f"{MONGO_DB_NAME}?readPreference={MONGO_READ_PREFERENCE}&authSource={MONGO_AUTH_SOURCE}"
)

client = MongoClient(MONGO_URL)
db = client[MONGO_DB_NAME]
cronjob_domain_testing = db["domain_testing"]

# Task to run every 2 minutes
@celery.task
def fetch_and_store_data():
    try:
        # First API call to get the token using curl command
        curl_command = """
        curl -X POST "https://seasiaconnect.com/api/api/UserManagement/Login" \
        -H "accept: text/plain" \
        -H "Content-Type: application/json-patch+json" \
        -d '{"userName":"10000","password":"Mind@123","clientApp":false,"isTrackerLogin":true}'
        """
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"curl command failed with error: {result.stderr}")
            return

        login_data = json.loads(result.stdout)
        token = login_data.get("token")

        if not token:
            logger.error("Failed to fetch token")
            return

        logger.info(f"Fetched token: {token}")

        # Store the login data in MongoDB
        login_result = cronjob_domain_testing.insert_one(login_data)
        logger.info(f"Login data inserted with ID: {login_result.inserted_id}")

        # Second API call to get the data
        data_url = "https://seasiaconnect.com/api/api/v1/Master/DropdownData/GetByName"
        data_payload = {
            "module": 1,
            "status": "active"
        }

        headers = {
            "Authorization": f"Bearer {token}"
        }

        data_response = requests.post(data_url, json=data_payload, headers=headers)
        data_response.raise_for_status()

        data = data_response.json()

        # Store the response data in MongoDB
        response_result = cronjob_domain_testing.insert_one(data)
        logger.info(f"Response data inserted with ID: {response_result.inserted_id}")

    except subprocess.SubprocessError as e:
        logger.error(f"Subprocess error: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

# Add periodic task
from celery.schedules import crontab

celery.conf.beat_schedule = {
    'fetch-and-store-data-every-2-minutes': {
        'task': 'utils.celery.fetch_and_store_data',
        'schedule': crontab(minute='*/2'),  # Run every 2 minutes
    },
}

if __name__ == "__main__":
    celery.start()
