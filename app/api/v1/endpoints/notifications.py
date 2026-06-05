from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.notification_repository import NotificationRepository
from app.services.notification_service import NotificationService
from app.schemas.notification import NotificationCreate, Notification
from app.core.dependencies import get_current_user
from app.db.models import User
from typing import List, cast

router = APIRouter()

@router.post("/", response_model=Notification)
async def create_notification(
    notification: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if notification.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized for this tenant")
    
    repo = NotificationRepository(db)
    service = NotificationService(repo)
    return await service.create_notification(notification)

@router.get("/", response_model=List[Notification])
async def get_user_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = cast(int, current_user.id)
    repo = NotificationRepository(db)
    service = NotificationService(repo)
    return await service.get_user_notifications(user_id)