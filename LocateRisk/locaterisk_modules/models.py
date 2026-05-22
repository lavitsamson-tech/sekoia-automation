from pydantic import BaseModel, Field


class LocateriskModuleConfiguration(BaseModel):
    api_key: str = Field(..., description="API Key", json_schema_extra={"secret": True})
    scan_id: str = Field(..., description="Scan ID", json_schema_extra={"secret": True})
    report_url: str = "https://app.locaterisk.com/api/rest/report/export"
