from fastapi import APIRouter, Query,Depends
from typing import List
from app.schemas import DeploymentHistoryDetails
from app.services import DeploymentHistoryService
from db.mongo import deployment_history_collection
from utils.dependencies import get_current_user, get_current_admin_user


router = APIRouter()

@router.get("/deployment_history", response_model=List[DeploymentHistoryDetails])
def get_deployment_history(project_id: str = Query(..., description="Project ID"),
                           env_id: str = Query(None, description="Environment ID"),current_user: dict = Depends(get_current_user)):
    deployment_history_service = DeploymentHistoryService(deployment_history_collection)
    deployment_history = deployment_history_service.get_deployment_history_by_project_id(project_id, env_id)

    return deployment_history
