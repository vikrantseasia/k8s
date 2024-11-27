from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: str
    role: str
    emp_id: str
    department: str

class UserCreate(UserBase):
    password: str
    confirm_password: str

class UserInDB(UserBase):
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    hashed_password: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
        }

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: Optional[str] = None

    class Config:
        # This ensures fields with None values are excluded from the response
        orm_mode = True
        json_encoders = {
            None: lambda v: v if v is not None else "",
        }
        use_enum_values = True
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        min_anystr_length = 1
        exclude_none = True


class TokenData(BaseModel):
    emp_id: Optional[str] = None
