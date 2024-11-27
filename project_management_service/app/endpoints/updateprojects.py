from fastapi import APIRouter, Depends
from app.services.updateprojects import ProjectService
from app.schemas.updateprojects import ProjectDetails
from db.mongo import project_collection, infra_collection, department_collection, technology_collection, domain_collection
from utils.dependencies import get_current_user, get_current_admin_user

router = APIRouter()
project_service = ProjectService(project_collection, infra_collection, department_collection, technology_collection, domain_collection )  # Pass additional collections

@router.put("/update_project/{project_id}", response_model=ProjectDetails)
async def update_project(
    project_id: str,
    project_details: ProjectDetails,
    current_user: dict = Depends(get_current_user),
     current_admin: dict = Depends(get_current_admin_user)
):
    return project_service.update_project_details(project_id, project_details)
