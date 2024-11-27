from typing import List, Optional
from pymongo.collection import Collection
from pymongo.errors import InvalidId, OperationFailure
from fastapi import HTTPException, status
from app.schemas import DeploymentHistoryDetails
import logging
import json
from utils.redis_client import redis_client
from bson import ObjectId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentHistoryService:
    def __init__(self, deployment_history_collection: Collection):
        self.deployment_history_collection = deployment_history_collection

    def get_deployment_history_by_project_id(self, project_id: str, env_id: Optional[str] = None) -> List[DeploymentHistoryDetails]:
        try:
            # Validate project_id format
            if not ObjectId.is_valid(project_id):
                logger.warning(f"Invalid project ID format: {project_id}")
                return []

            # Generate the cache key
            cache_key = f"deployment_history:{project_id}"
            if env_id:
                cache_key += f":{env_id}"

            # Check the cache first
            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    logger.info(f"Cache hit for key: {cache_key}")
                    return [DeploymentHistoryDetails(**item) for item in json.loads(cached_data)]
            except Exception as redis_error:
                logger.error(f"Redis error: {redis_error}")
                # Continue to fetch from the database even if Redis has an issue

            query = {"project_id": project_id}
            if env_id:
                query["deployment_Details.envId"] = env_id

            try:
                deployment_history = list(self.deployment_history_collection.find(query))
            except InvalidId as inv_id_error:
                logger.error(f"Invalid ID error while querying MongoDB: {inv_id_error}")
                return []
            except OperationFailure as op_fail_error:
                logger.error(f"Operation failure error while querying MongoDB: {op_fail_error}")
                return []

            if not deployment_history:
                logger.warning(f"Deployment history for project_id {project_id} not found.")
                return []

            # Convert ObjectId to str for JSON serialization
            for item in deployment_history:
                item['_id'] = str(item['_id'])

            # Cache the result
            try:
                redis_client.set(cache_key, json.dumps(deployment_history))
                logger.info(f"Cache updated for key: {cache_key}")
            except Exception as redis_error:
                logger.error(f"Error updating Redis cache: {redis_error}")
                # Continue even if caching fails

            return [DeploymentHistoryDetails(**item) for item in deployment_history]
        except HTTPException as http_exc:
            logger.error(f"HTTP error occurred: {http_exc.detail}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching deployment history details: {e}")
            return []

