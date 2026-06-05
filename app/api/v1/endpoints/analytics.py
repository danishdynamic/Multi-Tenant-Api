from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.event_repository import EventRepository
from app.services.event_service import EventService
from app.schemas.event import EventCreate, Event
from app.core.dependencies import get_current_user
from app.db.models import User
from typing import List, cast

router = APIRouter()

@router.post("/", response_model=Event)
async def create_event(
    event: EventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if event.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized for this tenant")

    repo = EventRepository(db)
    service = EventService(repo)
    return await service.create_event(event)

@router.get("/", response_model=List[Event])
async def get_tenant_events(
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = cast(int, current_user.tenant_id)
    repo = EventRepository(db)
    service = EventService(repo)
    return await service.get_tenant_events(tenant_id, limit)

@router.get("/stats")
async def get_tenant_event_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get event statistics for the current user's tenant"""
    tenant_id = cast(int, current_user.tenant_id)
    repo = EventRepository(db)
    service = EventService(repo)
    return await service.get_tenant_event_stats(tenant_id)