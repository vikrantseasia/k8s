from bson import ObjectId
from pymongo.collection import Collection
from fastapi import HTTPException, status
import logging
from utils.redis_client import redis_client  # Import the Redis client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectService:
    def __init__(self, project_collection: Collection, infra_collection: Collection, department_collection: Collection, technology_collection: Collection):
        self.project_collection = project_collection
        self.infra_collection = infra_collection
        self.department_collection = department_collection
        self.technology_collection = technology_collection

    def delete_project_details(self, project_id: str) -> dict:
        try:
            if not ObjectId.is_valid(project_id):
                logger.error(f"Invalid project ID: {project_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid project ID '{project_id}'"
                )

            project_obj_id = ObjectId(project_id)
            logger.info(f"Converted project ID to ObjectId: {project_obj_id}")

            delete_result = self.project_collection.delete_one({"_id": project_obj_id})

            if delete_result.deleted_count == 0:
                logger.warning(f"Project with ID '{project_id}' not found for deletion")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with ID '{project_id}' not found"
                )

            # Delete the corresponding cache entry from Redis
            cache_key = f"projects:{project_id}"
            try:
                redis_client.delete(cache_key)
                logger.info(f"Cache entry deleted for project ID: {project_id}")
            except Exception as redis_error:
                logger.error(f"Error deleting Redis cache entry: {redis_error}")
                # Continue even if cache deletion fails

            logger.info(f"Successfully deleted project with ID: {project_id}")
            self.invalidate_project_cache()
            return {"message": "Project deleted successfully"}
        except HTTPException as http_exc:
            logger.error(f"HTTP error occurred: {http_exc.detail}")
            raise http_exc
        except Exception as e:
            logger.error(f"Unexpected error deleting project: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting the project"
            )

    def invalidate_project_cache(self):
        try:
            keys = redis_client.keys("projects:*")
            if keys:
                redis_client.delete(*keys)
            logger.info("Invalidated project cache keys")
        except Exception as e:
            logger.error(f"Error invalidating project cache: {e}")
            # Continue even if cache invalidation fails
