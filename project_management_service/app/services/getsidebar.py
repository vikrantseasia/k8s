from pymongo.collection import Collection
from fastapi import HTTPException, status
import logging
import json
from utils.redis_client import redis_client  # Import the Redis client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SidebarService:
    def __init__(self, infra_collection: Collection, department_collection: Collection, technology_collection: Collection, domain_collection: Collection):
        self.infra_collection = infra_collection
        self.department_collection = department_collection
        self.technology_collection = technology_collection
        self.domain_collection = domain_collection

    def get_combined_details(self) -> dict:
        cache_key = "sidebar:combined_details"

        try:
            # Check cache
            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for sidebar combined details")
                return json.loads(cached_data)

            logger.info(f"Cache miss for sidebar combined details. Fetching from database.")

            infra_docs = list(self.infra_collection.find())
            department_docs = list(self.department_collection.find())
            technology_docs = list(self.technology_collection.find())
            domain_docs = list(self.domain_collection.find())

            infra_details = [{'id': str(doc['_id']), 'name': doc['name']} for doc in infra_docs]
            department_details = [{'id': str(doc['_id']), 'department_name': doc['department_name']} for doc in department_docs]
            technology_details = [{'id': str(doc['_id']), 'name': doc['name']} for doc in technology_docs]
            domain_details = [{'id': str(doc['_id']), 'Domain': doc['Domain']} for doc in domain_docs]

            combined_details = {
                "details": {
                    "infra": infra_details,
                    "department": department_details,
                    "technology": technology_details,
                    "domain": domain_details
                }
            }

            # Update cache
            try:
                redis_client.set(cache_key, json.dumps(combined_details))
                logger.info(f"Cache updated for sidebar combined details")
            except Exception as redis_error:
                logger.error(f"Error setting Redis cache entry: {redis_error}")
                # Continue even if cache set fails

            return combined_details
        except Exception as e:
            logger.error(f"Unexpected error fetching combined details: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while fetching sidebar combined details"
            )
