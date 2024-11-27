from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from app.schemas import UserCreate, Token
from app.services import create_user, authenticate_user
from core.security import create_access_token
from db.mongo import user_collection

router = APIRouter()

class OAuth2PasswordRequestFormEmailOrUsername(OAuth2PasswordBearer):
    def __init__(self, tokenUrl: str):
        super().__init__(tokenUrl=tokenUrl)

    async def __call__(self, email: str = Form(...), password: str = Form(...)):
        return {"email": email, "password": password}

oauth2_scheme = OAuth2PasswordRequestFormEmailOrUsername(tokenUrl="login")

@router.post("/register", response_model=Token)
def register(user: UserCreate):
    if user.password != user.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )
    try:
        create_user(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    access_token = create_access_token(data={"emp_id": user.emp_id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(form_data: dict = Depends(oauth2_scheme)):
    user_data = user_collection.find_one({"email": form_data["email"]})

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist",
        )

    user = authenticate_user(form_data["email"], form_data["password"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    access_token = create_access_token(data={"emp_id": user.emp_id, "role": user.role})

    response = {
        "access_token": access_token,
        "token_type": "bearer",
    }

    if user.role == "admin":
        response["role"] = user.role

    # Remove role if it is None or empty
    if "role" in response and response["role"] is None:
        del response["role"]

    return response

