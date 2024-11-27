from pydantic import BaseModel, Field, validator
from bson import ObjectId
from typing import Optional, Dict

class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return str(v)

class InfraType(BaseModel):
    id: Optional[ObjectIdStr]

class Department(BaseModel):
    id: Optional[ObjectIdStr]

class TechnologyName(BaseModel):
    id: Optional[ObjectIdStr]

class ApplicationProd(BaseModel):
    url: Optional[str]
    comments: Optional[str]
    description: Optional[str]
    infra_type: Optional[InfraType]
    deploymentHistory: Optional[Dict]
    env_id: Optional[str]

class Application(BaseModel):
    name: Optional[str]
    prod: Optional[ApplicationProd]

class ProjectDetails(BaseModel):
    name: Optional[str]
    image: Optional[str]
    projectdocs: Optional[Dict]
    clientName: Optional[str]
    ownerName: Optional[str]
    infra_type: Optional[InfraType]
    department: Optional[Department]
    technologyName: Optional[TechnologyName]
    desc: Optional[str]
    source_details: Optional[Dict]
    feature_project: Optional[bool]
    project_display: Optional[bool]
    application: Optional[Application]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: lambda x: str(x)
        }
