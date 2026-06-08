from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Report
from .base import BaseRepository

class ReportRepository(BaseRepository[Report]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Report)

    async def get_by_user(self, user_id: int):
        result = await self.session.execute(select(Report).where(Report.user_id == user_id))
        return result.scalars().all()

    async def get_by_tenant(self, tenant_id: int):
        result = await self.session.execute(select(Report).where(Report.tenant_id == tenant_id))
        return result.scalars().all()