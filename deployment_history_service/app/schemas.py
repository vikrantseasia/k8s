from pydantic import BaseModel, Field, HttpUrl


class DeploymentDetails(BaseModel):
    envId: str
    # Comment: str
    url: HttpUrl
    desc: str


class DeploymentHistoryDetails(BaseModel):
    id: str = Field(alias='_id')
    project_id: str
    deployment_Details: DeploymentDetails

    class Config:
        allow_population_by_field_name = True
