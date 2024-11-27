from pydantic import BaseModel
from typing import Optional, List

class Infra(BaseModel):
    id: str
    name: Optional[str] = None

class Department(BaseModel):
    id: str = None  # Make id optional
    department_name: Optional[str] = None

class TechnologyName(BaseModel):
    id: str = None  # Make id optional
    name: Optional[str] = None

class Domain(BaseModel):
    id: str = None  # Make id optional
    Domain: Optional[str] = None

class CombinedDetails(BaseModel):
    infra: List[Infra]
    department: List[Department]
    technology: List[TechnologyName]
    domain: List[Domain]

class CombinedDetailsResponse(BaseModel):
    details: CombinedDetails
    class Config:
        allow_population_by_field_name = True