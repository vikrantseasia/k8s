from fastapi import APIRouter, Depends
from app.services.addprojects import ProjectService
from app.schemas.addprojects import ProjectDetails
from db.mongo import project_collection, infra_collection, department_collection, technology_collection, domain_collection  # Import additional collections
from utils.dependencies import get_current_user, get_current_admin_user

router = APIRouter()
project_service = ProjectService(project_collection, infra_collection, department_collection, technology_collection, domain_collection)  # Pass additional collections

@router.post("/add_project", response_model=ProjectDetails)
def create_project_details(
    project_details: ProjectDetails,
    current_user: dict = Depends(get_current_user),
     current_admin: dict = Depends(get_current_admin_user)
):
    return project_service.create_project_details(project_details)
