from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Event
from .base import BaseRepository

class EventRepository(BaseRepository[Event]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Event)

    async def get_by_tenant(self, tenant_id: int):
        result = await self.session.execute(select(Event).where(Event.tenant_id == tenant_id))
        return result.scalars().all()