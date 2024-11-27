from fastapi import APIRouter, Query, Depends, HTTPException, status, Body
from typing import List, Optional
from app.services.getprojects import ProjectService
from app.schemas.getprojects import ProjectDetailsResponse, ProjectDetails
from db.mongo import project_collection, infra_collection, department_collection, technology_collection, domain_collection  # Import additional collections
from utils.dependencies import get_current_user, get_current_admin_user

router = APIRouter()
project_service = ProjectService(project_collection, infra_collection, department_collection, technology_collection, domain_collection)  # Pass additional collections

@router.get("/project_details", response_model=ProjectDetailsResponse)
def get_all_project_details(
    limit: int = Query(default=10, ge=1),
    page: int = Query(default=1, ge=1),
    infra_type_id: Optional[List[str]] = Query(None),
    department_id: Optional[List[str]] = Query(None),
    technology_id: Optional[List[str]] = Query(None),
    domain_id: Optional[List[str]] = Query(None),
    name: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    is_admin = current_user.get("role") == "admin"
    return project_service.get_all_project_details(limit, page, infra_type_id, department_id, technology_id, domain_id, name, is_admin)

@router.get("/project_details/{project_id}", response_model=ProjectDetails)
def get_project_details_by_id(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    is_admin = current_user.get("role") == "admin"
    return project_service.get_project_details_by_id(project_id, is_admin)


