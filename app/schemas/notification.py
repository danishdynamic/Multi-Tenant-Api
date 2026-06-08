from pydantic import BaseModel

class NotificationBase(BaseModel):
    message: str

class NotificationCreate(NotificationBase):
    tenant_id: int
    user_id: int

class Notification(NotificationBase):
    id: int
    tenant_id: int
    user_id: int
    sent: bool

    class Config:
        from_attributes = True