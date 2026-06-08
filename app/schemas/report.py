from pydantic import BaseModel

class ReportBase(BaseModel):
    title: str
    content: str

class ReportCreate(ReportBase):
    tenant_id: int
    user_id: int

class Report(ReportBase):
    id: int
    tenant_id: int
    user_id: int

    class Config:
        from_attributes = True