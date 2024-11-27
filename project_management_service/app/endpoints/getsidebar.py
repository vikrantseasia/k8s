from fastapi import APIRouter, Depends
from app.services.getsidebar import SidebarService
from app.schemas.getsidebar import CombinedDetailsResponse
from db.mongo import  infra_collection, department_collection, technology_collection , domain_collection
from utils.dependencies import get_current_user

router = APIRouter()
sidebar_service = SidebarService( infra_collection, department_collection, technology_collection, domain_collection)


@router.get("/get_sidebar", response_model=CombinedDetailsResponse)
def get_combined_details(
    current_user: dict = Depends(get_current_user)
):
    return sidebar_service.get_combined_details()