from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobBase(BaseModel):
    task: str

class JobCreate(JobBase):
    tenant_id: int

class Job(JobBase):
    id: int
    tenant_id: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True