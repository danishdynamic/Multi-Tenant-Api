from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Notification
from .base import BaseRepository

class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Notification)

    async def get_by_user(self, user_id: int):
        result = await self.session.execute(select(Notification).where(Notification.user_id == user_id))
        return result.scalars().all()

    async def get_unsent(self):
        result = await self.session.execute(select(Notification).where(Notification.sent == False))
        return result.scalars().all()