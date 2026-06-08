import aiosmtplib
from email.message import EmailMessage
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationCreate, Notification
from app.db.models import Notification as NotificationModel, User
from app.core.config import settings
from app.core.cache import cache
from app.core.message_queue import message_queue
from typing import List
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    async def create_notification(self, notification_data: NotificationCreate) -> NotificationModel:
        notification = NotificationModel(
            message=notification_data.message,
            tenant_id=notification_data.tenant_id,
            user_id=notification_data.user_id
        )

        created_notification = await self.repo.create(notification)

        # Invalidate cache for this user
        await cache.delete(f"user_{notification_data.user_id}_notifications")

        # Queue email notification if user has email
        if notification_data.user_id:
            await self._queue_email_notification(created_notification)

        return created_notification

    async def get_user_notifications(self, user_id: int, limit: int = 50) -> List[NotificationModel]:
        """Get notifications for a user with caching"""
        cache_key = f"user_{user_id}_notifications_{limit}"

        async def fetch_notifications():
            # Use join to get user info efficiently
            query = select(NotificationModel).options(
                joinedload(NotificationModel.user)
            ).where(NotificationModel.user_id == user_id).order_by(
                NotificationModel.created_at.desc()
            ).limit(limit)

            result = await self.repo.session.execute(query)
            return result.scalars().unique().all()

        return await cache.get_or_set(cache_key, fetch_notifications)

    async def _queue_email_notification(self, notification: NotificationModel):
        """Queue email notification for async processing"""
        try:
            # Get user email
            query = select(User.email).where(User.id == notification.user_id)
            result = await self.repo.session.execute(query)
            user_email = result.scalar()

            if user_email:
                message_data = {
                    'to_email': user_email,
                    'subject': f'New Notification from {settings.app_name}',
                    'body': notification.message,
                    'notification_id': notification.id
                }

                await message_queue.publish_message(
                    'email_notifications',
                    message_data,
                    priority=1
                )
                logger.info(f"Queued email notification for user {notification.user_id}")
        except Exception as e:
            logger.error(f"Failed to queue email notification: {e}")

    @staticmethod
    async def send_email_notification(to_email: str, subject: str, body: str) -> bool:
        """Send email notification synchronously"""
        if not all([settings.smtp_server, settings.smtp_username, settings.smtp_password]):
            logger.warning("SMTP settings not configured")
            return False

        message = EmailMessage()
        message["From"] = settings.smtp_username
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.smtp_server,
                port=settings.smtp_port,
                username=settings.smtp_username,
                password=settings.smtp_password,
                use_tls=True
            )
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    @staticmethod
    async def process_email_queue(message_data: dict):
        """Process email notification from queue"""
        await NotificationService.send_email_notification(
            message_data['to_email'],
            message_data['subject'],
            message_data['body']
        )