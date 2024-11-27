import json
from bson import ObjectId
from pymongo.collection import Collection
from fastapi import HTTPException, status
from app.schemas.addprojects import ProjectDetails
import logging
import random
import string
from utils.redis_client import redis_client

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

    def create_project_details(self, project_details: ProjectDetails) -> ProjectDetails:
        try:
            # Check if project name already exists
            if self.project_collection.find_one({"name": project_details.name}):
                logger.warning(f"Project name '{project_details.name}' already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Project name '{project_details.name}' already exists"
                )

            # Check if isViewEdited is set to true
            if project_details.isViewEdited:
                logger.warning("isViewEdited value should be false")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="isViewEdited value should be false"
                )

            project_dict = project_details.dict(by_alias=True)
            project_dict['_id'] = ObjectId()  # Generate a new ObjectId for the project

            # Set isViewEdited to false
            project_dict['isViewEdited'] = False

            # Convert infra_type and department ids to ObjectId
            try:
                project_dict['infra_type']['id'] = ObjectId(project_dict['infra_type']['id'])
                project_dict['department']['id'] = ObjectId(project_dict['department']['id'])
                project_dict['domain']['id'] = ObjectId(project_dict['domain']['id'])

                # Convert technologyName ids to ObjectId
                for tech in project_dict['technologyName']:
                    tech['id'] = ObjectId(tech['id'])

                # Convert nested infra_type id in application environments to ObjectId
                for app in project_dict['application']:
                    for env in app['environments'].values():
                        env['infra_type']['id'] = ObjectId(env['infra_type']['id'])
                        env['env_id'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            except Exception as conversion_error:
                logger.error(f"Error converting IDs to ObjectId: {conversion_error}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Error converting IDs to ObjectId"
                )

            self.project_collection.insert_one(project_dict)
            project_dict['_id'] = str(project_dict['_id'])

            # Convert ObjectIds to strings for caching
            def convert_object_ids(d):
                for k, v in d.items():
                    if isinstance(v, ObjectId):
                        d[k] = str(v)
                    elif isinstance(v, dict):
                        convert_object_ids(v)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict):
                                convert_object_ids(item)
                return d

            project_dict = convert_object_ids(project_dict)

            # Update cache
            cache_key = f"projects:{project_dict['_id']}"
            try:
                redis_client.set(cache_key, json.dumps(project_dict))
                logger.info(f"Cache updated for project ID: {project_dict['_id']}")
            except Exception as redis_error:
                logger.error(f"Error updating Redis cache: {redis_error}")
                # Continue even if caching fails

            self.invalidate_project_cache()

            return ProjectDetails(**project_dict)

        except HTTPException as http_exc:
            logger.error(f"HTTP error occurred: {http_exc.detail}")
            raise http_exc
        except Exception as e:
            logger.error(f"Unexpected error creating project details: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating project details"
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
