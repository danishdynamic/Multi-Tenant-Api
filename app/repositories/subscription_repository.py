from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Subscription
from .base import BaseRepository

class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Subscription)

    async def get_by_tenant(self, tenant_id: int):
        result = await self.session.execute(select(Subscription).where(Subscription.tenant_id == tenant_id))
        return result.scalars().all()

    async def get_active_by_tenant(self, tenant_id: int):
        result = await self.session.execute(
            select(Subscription).where(
                Subscription.tenant_id == tenant_id,
                Subscription.status == "active"
            )
        )
        return result.scalars().first()