from pydantic import BaseModel
from typing import Any, Dict
from datetime import datetime

class EventBase(BaseModel):
    event_type: str
    data: Dict[str, Any]

class EventCreate(EventBase):
    tenant_id: int
    user_id: int

class Event(EventBase):
    id: int
    tenant_id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True