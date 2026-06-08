from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from .base import BaseRepository
from typing import Optional

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_tenant(self, tenant_id: int):
        result = await self.session.execute(select(User).where(User.tenant_id == tenant_id))
        return result.scalars().all()