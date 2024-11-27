from fastapi import APIRouter, Depends, HTTPException
from app.services.deleteproduct import ProjectService
from app.schemas.deleteproduct import ProjectDetails
from db.mongo import project_collection, infra_collection, department_collection, technology_collection  # Import additional collections
from utils.dependencies import get_current_user , get_current_admin_user

router = APIRouter()
project_service = ProjectService(project_collection, infra_collection, department_collection, technology_collection)  # Pass additional collections


@router.delete("/delete_project/{project_id}", response_model=dict)
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
     current_admin: dict = Depends(get_current_admin_user)
):
    return project_service.delete_project_details(project_id)
