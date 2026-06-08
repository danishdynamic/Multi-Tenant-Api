from pydantic import BaseModel
from datetime import datetime

class SubscriptionBase(BaseModel):
    plan: str
    status: str
    start_date: datetime
    end_date: datetime

class SubscriptionCreate(SubscriptionBase):
    tenant_id: int

class Subscription(SubscriptionBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True