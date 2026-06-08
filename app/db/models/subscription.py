from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), index=True)
    plan = Column(String)
    status = Column(String, default="active")
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))

    tenant = relationship("Tenant")