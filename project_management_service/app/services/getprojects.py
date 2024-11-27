from fastapi import HTTPException, status
from bson import ObjectId
from pymongo.collection import Collection
from typing import List, Optional
from math import ceil
import json
import logging
from utils.redis_client import redis_client
from app.schemas.getprojects import ProjectDetails

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

    def get_all_project_details(self, limit: int, page: int, infra_type_id: Optional[List[str]] = None, department_id: Optional[List[str]] = None, technology_id: Optional[List[str]] = None, domain_id: Optional[List[str]] = None, name: Optional[str] = None, is_admin: bool = False) -> dict:
        try:
            cache_key = f"projects:limit={limit}:page={page}:infra={infra_type_id}:dept={department_id}:tech={technology_id}:domain={domain_id}:name={name}:admin={is_admin}"
            cached_data = redis_client.get(cache_key)

            if cached_data:
                logger.info("Cache hit for all project details")
                return json.loads(cached_data)
            else:
                logger.info("Cache miss for all project details, querying database")

            skip = (page - 1) * limit

            query = {}
            if not is_admin:
                query['project_display'] = True
            if infra_type_id:
                query['infra_type.id'] = {'$in': [ObjectId(id) for id in infra_type_id]}
            if department_id:
                query['department.id'] = {'$in': [ObjectId(id) for id in department_id]}
            if technology_id:
                query['technologyName.id'] = {'$in': [ObjectId(id) for id in technology_id]}
            if domain_id:
                query['domain.id'] = {'$in': [ObjectId(id) for id in domain_id]}
            if name:
                if isinstance(name, str) and name.strip():
                    query['name'] = {'$regex': name, '$options': 'i'}
                else:
                    logger.warning("Invalid name parameter passed for regex")

            total_projects = self.project_collection.count_documents(query)
            total_pages = ceil(total_projects / limit)

            projects = list(self.project_collection.find(query).skip(skip).limit(limit).sort([("feature_project", -1), ("name", 1)]))

            if not projects:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No project details found"
                )

            for project in projects:
                project['_id'] = str(project['_id'])

                if 'department' in project and 'id' in project['department']:
                    department_id = project['department']['id']
                    if isinstance(department_id, dict) and '$oid' in department_id:
                        department_id = department_id['$oid']
                    if department_id:
                        department = self.department_collection.find_one({"_id": ObjectId(department_id), 'department_name': {'$ne': None}})
                        if department:
                            project['department'] = {'id': str(department['_id']), 'department_name': department.get('department_name', '')}
                        else:
                            project['department'] = {'id': '', 'department_name': ''}

                if 'technologyName' not in project:
                    project['technologyName'] = []
                elif isinstance(project['technologyName'], dict):
                    project['technologyName'] = [project['technologyName']]
                elif isinstance(project['technologyName'], list):
                    for tech in project['technologyName']:
                        technology_id = tech['id']
                        if isinstance(technology_id, dict) and '$oid' in technology_id:
                            technology_id = technology_id['$oid']
                        if technology_id:
                            technology = self.technology_collection.find_one({"_id": ObjectId(technology_id), 'name': {'$ne': None}})
                            if technology:
                                tech['id'] = str(technology['_id'])
                                tech['name'] = technology.get('name', '')
                            else:
                                tech['id'] = ''
                                tech['name'] = ''

                if 'infra_type' in project and 'id' in project['infra_type']:
                    infra_id = project['infra_type']['id']
                    if isinstance(infra_id, dict) and '$oid' in infra_id:
                        infra_id = infra_id['$oid']
                    if infra_id:
                        infra = self.infra_collection.find_one({"_id": ObjectId(infra_id), 'name': {'$ne': None}})
                        if infra:
                            project['infra_type'] = {'id': str(infra['_id']), 'name': infra.get('name', '')}
                        else:
                            project['infra_type'] = {'id': '', 'name': ''}

                if 'domain' in project and 'id' in project['domain']:
                    domain_id = project['domain']['id']
                    if isinstance(domain_id, dict) and '$oid' in domain_id:
                        domain_id = domain_id['$oid']
                    if domain_id:
                        domain = self.domain_collection.find_one({"_id": ObjectId(domain_id)})
                        if domain:
                            project['domain'] = {'id': str(domain['_id']), 'Domain': domain.get('Domain', ''), 'Name': domain.get('Name', ''), 'Description': domain.get('Description', ''), 'Examples': domain.get('Examples', '')}
                        else:
                            project['domain'] = {'id': '', 'Domain': '', 'Name': '', 'Description': '', 'Examples': ''}

                if 'application' in project:
                    for app in project['application']:
                        environments = {
                            k: v for k, v in app.get('environments', {}).items()
                            if isinstance(v, dict) and 'env_id' in v
                        }
                        for env in environments.values():
                            if 'deploymentHistory' in env:
                                env['deploymentHistory'] = env.pop('deploymentHistory')
                            if 'infra_type' in env and 'id' in env['infra_type']:
                                infra_id = env['infra_type']['id']
                                if isinstance(infra_id, dict) and '$oid' in infra_id:
                                    infra_id = infra_id['$oid']
                                if infra_id:
                                    infra = self.infra_collection.find_one({"_id": ObjectId(infra_id), 'name': {'$ne': None}})
                                    if infra:
                                        env['infra_type']['id'] = str(infra['_id'])
                                        env['infra_type']['name'] = infra.get('name', '')
                                    else:
                                        env['infra_type'] = {'id': '', 'name': ''}
                        app['environments'] = environments

            response = {
                "limit": limit,
                "current_page": page,
                "total_pages": total_pages,
                "projects": projects
            }

            try:
                redis_client.set(cache_key, json.dumps(response, default=str))
                logger.info("Data cached for all project details")
            except Exception as redis_error:
                logger.error(f"Error setting Redis cache entry: {redis_error}")
                # Continue even if cache set fails

            return response
        except HTTPException as http_exc:
            if http_exc.status_code == status.HTTP_404_NOT_FOUND:
                return {
                    "limit": limit,
                    "current_page": page,
                    "total_pages": 0,
                    "projects": []
                }
            else:
                logger.error(f"HTTP error occurred: {http_exc.detail}")
                raise http_exc
        except Exception as e:
            logger.error(f"Unexpected error fetching all project details: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while fetching all project details"
            )

    def get_project_details_by_id(self, project_id: str, is_admin: bool = False) -> ProjectDetails:
        try:
            cache_key = f"project:{project_id}:admin={is_admin}"
            cached_data = redis_client.get(cache_key)

            if cached_data:
                logger.info(f"Cache hit for project details with id: {project_id}")
                project = json.loads(cached_data)
            else:
                logger.info(f"Cache miss for project details with id: {project_id}, querying database")
                query = {"_id": ObjectId(project_id)}

                if not is_admin:
                    query['project_display'] = True

                project = self.project_collection.find_one(query)

                if not project:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Project details not found"
                    )

                project['_id'] = str(project['_id'])

                if 'department' in project and 'id' in project['department']:
                    department_id = project['department']['id']
                    if isinstance(department_id, dict) and '$oid' in department_id:
                        department_id = department_id['$oid']
                    if department_id:
                        department = self.department_collection.find_one({"_id": ObjectId(department_id), 'department_name': {'$ne': None}})
                        if department:
                            project['department'] = {'id': str(department['_id']), 'department_name': department.get('department_name', '')}
                        else:
                            project['department'] = {'id': '', 'department_name': ''}

                if 'technologyName' not in project:
                    project['technologyName'] = []
                elif isinstance(project['technologyName'], dict):
                    project['technologyName'] = [project['technologyName']]
                elif isinstance(project['technologyName'], list):
                    for tech in project['technologyName']:
                        technology_id = tech['id']
                        if isinstance(technology_id, dict) and '$oid' in technology_id:
                            technology_id = technology_id['$oid']
                        if technology_id:
                            technology = self.technology_collection.find_one({"_id": ObjectId(technology_id), 'name': {'$ne': None}})
                            if technology:
                                tech['id'] = str(technology['_id'])
                                tech['name'] = technology.get('name', '')
                            else:
                                tech['id'] = ''
                                tech['name'] = ''

                if 'infra_type' in project and 'id' in project['infra_type']:
                    infra_id = project['infra_type']['id']
                    if isinstance(infra_id, dict) and '$oid' in infra_id:
                        infra_id = infra_id['$oid']
                    if infra_id:
                        infra = self.infra_collection.find_one({"_id": ObjectId(infra_id), 'name': {'$ne': None}})
                        if infra:
                            project['infra_type'] = {'id': str(infra['_id']), 'name': infra.get('name', '')}
                        else:
                            project['infra_type'] = {'id': '', 'name': ''}

                if 'domain' in project and 'id' in project['domain']:
                    domain_id = project['domain']['id']
                    if isinstance(domain_id, dict) and '$oid' in domain_id:
                        domain_id = domain_id['$oid']
                    if domain_id:
                        domain = self.domain_collection.find_one({"_id": ObjectId(domain_id)})
                        if domain:
                            project['domain'] = {'id': str(domain['_id']), 'Domain': domain.get('Domain', ''), 'Name': domain.get('Name', ''), 'Description': domain.get('Description', ''), 'Examples': domain.get('Examples', '')}
                        else:
                            project['domain'] = {'id': '', 'Domain': '', 'Name': '', 'Description': '', 'Examples': ''}

                if 'application' in project:
                    for app in project['application']:
                        environments = {
                            k: v for k, v in app.get('environments', {}).items()
                            if isinstance(v, dict) and 'env_id' in v
                        }
                        for env in environments.values():
                            if 'deploymentHistory' in env:
                                env['deploymentHistory'] = env.pop('deploymentHistory')
                            if 'infra_type' in env and 'id' in env['infra_type']:
                                infra_id = env['infra_type']['id']
                                if isinstance(infra_id, dict) and '$oid' in infra_id:
                                    infra_id = infra_id['$oid']
                                if infra_id:
                                    infra = self.infra_collection.find_one({"_id": ObjectId(infra_id), 'name': {'$ne': None}})
                                    if infra:
                                        env['infra_type']['id'] = str(infra['_id'])
                                        env['infra_type']['name'] = infra.get('name', '')
                                    else:
                                        env['infra_type'] = {'id': '', 'name': ''}
                        app['environments'] = environments

                try:
                    redis_client.set(cache_key, json.dumps(project, default=str))
                    logger.info(f"Data cached for project details with id: {project_id}")
                except Exception as redis_error:
                    logger.error(f"Error setting Redis cache entry: {redis_error}")
                    # Continue even if cache set fails

            return ProjectDetails(**project)
        except HTTPException as http_exc:
            logger.error(f"HTTP error occurred: {http_exc.detail}")
            raise http_exc
        except Exception as e:
            logger.error(f"Unexpected error fetching project details by id: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while fetching project details"
            )
