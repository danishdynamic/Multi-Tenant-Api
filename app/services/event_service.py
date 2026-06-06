from sqlalchemy import select, and_, func
from sqlalchemy.orm import joinedload
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate, Event
from app.db.models import Event as EventModel, User
from app.core.cache import cache
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class EventService:
    def __init__(self, repo: EventRepository):
        self.repo = repo

    async def create_event(self, event_data: EventCreate) -> EventModel:
        event = EventModel(
            event_type=event_data.event_type,
            data=event_data.data,
            tenant_id=event_data.tenant_id,
            user_id=event_data.user_id
        )

        created_event = await self.repo.create(event)

        # Invalidate analytics cache for this tenant
        await cache.invalidate_tenant_cache(event_data.tenant_id)

        return created_event

    async def get_tenant_events(self, tenant_id: int, limit: int = 100) -> List[EventModel]:
        """Get events for a tenant with caching and user info"""
        cache_key = f"analytics_tenant_{tenant_id}_events_{limit}"

        async def fetch_events():
            # Use join to get user info efficiently
            query = select(EventModel).options(
                joinedload(EventModel.user)
            ).where(EventModel.tenant_id == tenant_id).order_by(
                EventModel.created_at.desc()
            ).limit(limit)

            result = await self.repo.session.execute(query)
            return result.scalars().unique().all()

        return await cache.get_or_set(cache_key, fetch_events, ttl=300)  # 5 min cache

    async def get_tenant_event_stats(self, tenant_id: int) -> dict:
        """Get event statistics for a tenant with aggregation"""
        cache_key = f"analytics_tenant_{tenant_id}_stats"

        async def fetch_stats():
            # Use SQL aggregation for better performance
            query = select(
                EventModel.event_type,
                func.count(EventModel.id).label('count'),
                func.max(EventModel.created_at).label('last_event')
            ).where(EventModel.tenant_id == tenant_id).group_by(EventModel.event_type)

            result = await self.repo.session.execute(query)
            stats = {}
            for row in result:
                stats[row.event_type] = {
                    'count': row.count,
                    'last_event': row.last_event
                }

            # Get total events count
            total_query = select(func.count(EventModel.id)).where(EventModel.tenant_id == tenant_id)
            total_result = await self.repo.session.execute(total_query)
            total_events = total_result.scalar()

            return {
                'total_events': total_events,
                'event_types': stats
            }

        return await cache.get_or_set(cache_key, fetch_stats, ttl=600)  # 10 min cache