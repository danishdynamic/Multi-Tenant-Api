from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Tenant
from .base import BaseRepository
from typing import Optional

class TenantRepository(BaseRepository[Tenant]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Tenant)

    async def get_by_name(self, name: str) -> Optional[Tenant]:
        result = await self.session.execute(select(Tenant).where(Tenant.name == name))
        return result.scalar_one_or_none()