from pydantic import BaseModel, Field


class LocateriskModuleConfiguration(BaseModel):
    api_key: str = Field(..., description="API Key", secret=True)
    scan_id: str = Field(..., description="Scan ID", secret=True)
    report_url: str = "https://app.locaterisk.com/api/rest/report/export"
