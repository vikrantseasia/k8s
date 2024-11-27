from pymongo.collection import Collection
from fastapi import HTTPException, status
from app.schemas import UserDetails
import logging
import json
from utils.redis_client import redis_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, user_collection: Collection):
        self.user_collection = user_collection

    def get_user_by_emp_id(self, emp_id: str) -> UserDetails:
        try:
            # Generate cache key
            cache_key = f"user:{emp_id}"

            # Check cache first
            cached_user = redis_client.get(cache_key)
            if cached_user:
                logger.info(f"Cache hit for user with emp_id: {emp_id}")
                return UserDetails(**json.loads(cached_user))

            logger.info(f"Cache miss for user with emp_id: {emp_id}. Fetching from database.")

            # Fetch user details from MongoDB
            user = self.user_collection.find_one({"emp_id": emp_id})
            if not user:
                logger.warning(f"User with emp_id {emp_id} not found.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            # Convert ObjectId to str for JSON serialization
            user['_id'] = str(user['_id'])

            # Cache user details
            try:
                redis_client.set(cache_key, json.dumps(user))
                logger.info(f"Cache updated for user with emp_id: {emp_id}")
            except Exception as redis_error:
                logger.error(f"Error setting Redis cache entry: {redis_error}")
                # Continue even if cache set fails

            return UserDetails(**user)
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Unexpected error fetching user details by emp_id {emp_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error while fetching user details")