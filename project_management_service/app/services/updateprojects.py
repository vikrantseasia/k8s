from bson import ObjectId
from pymongo.collection import Collection
from fastapi import HTTPException, status
from app.schemas.addprojects import ProjectDetails
from app.schemas.updateprojects import ProjectDetails as UpdateProjectDetails
import logging
import random
import string
import json
from utils.redis_client import redis_client  # Import the Redis client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectService:
    def __init__(self, project_collection: Collection, infra_collection: Collection, department_collection: Collection, technology_collection: Collection, domain_collection: Collection):
        self.project_collection = project_collection
        self.infra_collection = infra_collection
        self.department_collection = department_collection
        self.technology_collection = technology_collection
        self.domain_collection = domain_collection

    def update_project_details(self, project_id: str, project_details: UpdateProjectDetails) -> UpdateProjectDetails:
        try:
            if not ObjectId.is_valid(project_id):
                logger.error(f"Invalid project ID: {project_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid project ID '{project_id}'"
                )

            project_obj_id = ObjectId(project_id)
            logger.info(f"Converted project ID to ObjectId: {project_obj_id}")

            # Check if the project exists in the database
            project = self.project_collection.find_one({"_id": project_obj_id})
            if not project:
                logger.warning(f"Project with ID '{project_id}' not found in collection")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with ID '{project_id}' not found"
                )

            project_dict = project_details.dict(by_alias=True, exclude_unset=True)
            logger.info(f"Updating project details: {project_dict}")

            # Check if isViewEdited is set to true
            if 'isViewEdited' in project_dict and project_dict['isViewEdited']:
                logger.error("isViewEdited value is true")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="isViewEdited value should be false"
                )

            # Set isViewEdited to false
            project_dict['isViewEdited'] = False

            # Convert infra_type, department, and technologyName ids to ObjectId
            if 'infra_type' in project_dict and 'id' in project_dict['infra_type']:
                project_dict['infra_type']['id'] = ObjectId(project_dict['infra_type']['id'])
            if 'department' in project_dict and 'id' in project_dict['department']:
                project_dict['department']['id'] = ObjectId(project_dict['department']['id'])
            if 'domain' in project_dict and 'id' in project_dict['domain']:
                project_dict['domain']['id'] = ObjectId(project_dict['domain']['id'])
            for tech in project_dict['technologyName']:
                tech['id'] = ObjectId(tech['id'])

            # Convert nested infra_type id in application environments to ObjectId
            for app in project_dict['application']:
                for env in app['environments'].values():
                    env['infra_type']['id'] = ObjectId(env['infra_type']['id'])
                    env['env_id'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

            logger.info(f"Final project dict to update: {project_dict}")

            update_result = self.project_collection.update_one(
                {"_id": project_obj_id},
                {"$set": project_dict}
            )

            if update_result.matched_count == 0:
                logger.warning(f"No project matched for ID '{project_id}' during update")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with ID '{project_id}' not found"
                )

            updated_project = self.project_collection.find_one({"_id": project_obj_id})
            updated_project['_id'] = str(updated_project['_id'])

            # Convert all ObjectId instances to strings
            def convert_object_ids(doc):
                for key, value in doc.items():
                    if isinstance(value, ObjectId):
                        doc[key] = str(value)
                    elif isinstance(value, dict):
                        convert_object_ids(value)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                convert_object_ids(item)

            convert_object_ids(updated_project)

            # Update the cache with the new project details
            cache_key = f"project:{project_id}:admin=False"
            try:
                redis_client.set(cache_key, json.dumps(updated_project))
                logger.info(f"Cache updated for project ID: {project_id}")
            except Exception as redis_error:
                logger.error(f"Error setting Redis cache entry: {redis_error}")
                # Continue even if cache set fails

            # Invalidate the specific project cache in get_all_project_details
            self.invalidate_project_cache()

            return UpdateProjectDetails(**updated_project)
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Unexpected error updating project details: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating project details"
            )

    def invalidate_project_cache(self):
        try:
            keys = redis_client.keys("projects:*")
            if keys:
                redis_client.delete(*keys)
            logger.info("Invalidated project cache keys")

            specific_keys = redis_client.keys("project:*")
            if specific_keys:
                redis_client.delete(*specific_keys)
            logger.info("Invalidated specific project cache keys")
        except Exception as e:
            logger.error(f"Error invalidating cache keys: {e}")
            # Log the error but do not disrupt the process
