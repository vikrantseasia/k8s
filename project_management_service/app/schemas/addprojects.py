from typing import List, Dict, Optional
from pydantic import BaseModel, Field, HttpUrl, validator
from bson import ObjectId

class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return str(v)

class ProjectDocs(BaseModel):
    Figma_url: Optional[HttpUrl]
    Dam_Link: Optional[HttpUrl]

class InfraType(BaseModel):
    id: ObjectIdStr

class Department(BaseModel):
    id: ObjectIdStr

class TechnologyName(BaseModel):
    id: ObjectIdStr

class Domain(BaseModel):
    id: ObjectIdStr

class DeploymentHistory(BaseModel):
    url: HttpUrl
    Date: str

class SourceDetails(BaseModel):
    Type: str
    url: HttpUrl

    @validator('Type')
    def validate_type(cls, v):
        valid_types = ['github', 'gitLab', 'bitbucket', 'internal-git']
        if v not in valid_types:
            raise ValueError(f'Type must be one of {valid_types}')
        return v

class ProjectStatus(BaseModel):
    Status : str

    @validator('Status')
    def validate_status(cls, v):
        valid_status = ['in-progress', 'completed', 'on-hold']
        if v not in valid_status:
            raise ValueError(f'Type must be one of {valid_status}')
        return v

class ProjectType(BaseModel):
    Type: str

    @validator('Type')
    def validate_type(cls, v):
        valid_types = ['in-house', 'client',]
        if v not in valid_types:
            raise ValueError(f'Type must be one of {valid_types}')
        return v

class Environment(BaseModel):
    url: HttpUrl
    description: str
    deploymentHistory: DeploymentHistory
    infra_type: InfraType
    env_id: str = None

class Application(BaseModel):
    name: str
    environments: Dict[str, Environment]

class ProjectDetails(BaseModel):
    name: str
    image: HttpUrl
    projectdocs: ProjectDocs
    clientName: str
    ownerName: str
    department: Department
    technologyName: List[TechnologyName]
    domain: Domain
    infra_type: InfraType
    desc: str
    source_details: SourceDetails
    feature_project: bool
    project_display: bool
    isViewEdited: bool
    projectType: ProjectType
    projectStatus: ProjectStatus
    application: List[Application]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: lambda x: str(x)
        }
