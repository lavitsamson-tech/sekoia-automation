from pydantic import BaseModel, Field


class LocateriskModuleConfiguration(BaseModel):
    api_key: str = Field(..., description="API Key", secret=True)
