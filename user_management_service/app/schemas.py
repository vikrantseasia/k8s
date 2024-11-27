from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserDetails(BaseModel):
    id: str = Field(alias='_id')
    email: EmailStr
    full_name: str
    phone_number: str
    role: str = None
    emp_id: str = None
    department: str = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

