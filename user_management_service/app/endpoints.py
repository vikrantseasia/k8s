from fastapi import APIRouter, HTTPException, Depends,status
from app.schemas import UserDetails
from app.services import UserService
from db.mongo import user_collection
from utils.dependencies import get_current_user

router = APIRouter()
user_service = UserService(user_collection)

@router.get("/user_details", response_model=UserDetails)
def get_user_details_by_emp_id(current_user: dict = Depends(get_current_user)):
    emp_id = current_user.get('emp_id')
    if not emp_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee ID not found in token")
    try:
        return user_service.get_user_by_emp_id(emp_id)
    except HTTPException as e:
        raise e
