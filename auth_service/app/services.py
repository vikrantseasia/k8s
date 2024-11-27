from app.schemas import UserCreate, UserInDB
from core.security import get_password_hash, verify_password
from db.mongo import user_collection
from pymongo.errors import DuplicateKeyError
from typing import Union


def create_user(user: UserCreate):
    if user_collection.find_one({"email": user.email}):
        raise ValueError("Email already exists")

    if user_collection.find_one({"emp_id": user.emp_id}):
        raise ValueError("Employee ID already exists")

    hashed_password = get_password_hash(user.password)
    user_in_db = UserInDB(
        role=user.role,
        emp_id=user.emp_id,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone_number,
        department=user.department,
        hashed_password=hashed_password
    )
    try:
        user_collection.insert_one(user_in_db.dict(by_alias=True))
    except DuplicateKeyError:
        raise ValueError("User already exists")

def authenticate_user(email: str, password: str) -> Union[UserInDB, None]:
    user_data = user_collection.find_one({"email": email})
    if not user_data:
        return None

    user = UserInDB(**user_data)

    if not verify_password(password, user.hashed_password):
        return None

    return user
