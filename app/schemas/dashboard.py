from pydantic import BaseModel
from typing import Any, Dict

class DashboardBase(BaseModel):
    name: str
    data: Dict[str, Any]

class DashboardCreate(DashboardBase):
    tenant_id: int
    user_id: int

class Dashboard(DashboardBase):
    id: int
    tenant_id: int
    user_id: int

    class Config:
        from_attributes = True