from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, List
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

class Infra(BaseModel):
    id: str
    name: Optional[str] = None

class Department(BaseModel):
    id: str = None  # Make id optional
    department_name: Optional[str] = None

class TechnologyName(BaseModel):
    id: ObjectIdStr
    name: Optional[str] = None

class DeploymentHistory(BaseModel):
    url: HttpUrl
    Date: str

class SourceDetails(BaseModel):
    Type: str
    url: HttpUrl

class ProjectStatus(BaseModel):
    Status : str

class ProjectType(BaseModel):
    Type: str

class Environment(BaseModel):
    url: HttpUrl
    # comments: str
    description: str
    deploymentHistory: DeploymentHistory
    infra_type: Infra
    env_id: str

class Application(BaseModel):
    name: str
    environments: Dict[str, Environment]  # Changed to Dict for dynamic environments

class Domain(BaseModel):
    id: str
    Domain: str
    Name: str
    Description: Optional[str] = None
    Examples: Optional[str] = None
    Synonym: Optional[str] = None
class ProjectDetails(BaseModel):
    id: str = Field(alias='_id')
    name: str
    image: HttpUrl
    projectdocs: ProjectDocs
    clientName: str
    ownerName: str
    department: Department
    technologyName: List[TechnologyName]
    domain: Domain
    infra_type: Infra
    desc: str
    source_details: SourceDetails
    feature_project: bool
    project_display: bool
    isViewEdited: bool
    projectType: ProjectType
    projectStatus: ProjectStatus
    application: List[Application]

class ProjectDetailsResponse(BaseModel):
    limit: int
    current_page: int
    total_pages: int
    projects: List[ProjectDetails]
