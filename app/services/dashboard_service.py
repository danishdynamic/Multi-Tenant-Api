from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import DashboardCreate, Dashboard
from app.db.models import Dashboard as DashboardModel, User
from app.core.cache import cache
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class DashboardService:
    def __init__(self, repo: DashboardRepository):
        self.repo = repo

    async def create_dashboard(self, dashboard_data: DashboardCreate) -> DashboardModel:
        dashboard = DashboardModel(
            name=dashboard_data.name,
            data=dashboard_data.data,
            tenant_id=dashboard_data.tenant_id,
            user_id=dashboard_data.user_id
        )

        created_dashboard = await self.repo.create(dashboard)

        # Invalidate cache for this tenant
        await cache.invalidate_tenant_cache(dashboard_data.tenant_id)

        return created_dashboard

    async def get_user_dashboards(self, user_id: int) -> List[DashboardModel]:
        """Get dashboards for a user with caching"""
        cache_key = f"user_{user_id}_dashboards"

        async def fetch_dashboards():
            # Use join to get user info efficiently
            query = select(DashboardModel).options(
                joinedload(DashboardModel.user)
            ).where(DashboardModel.user_id == user_id)

            result = await self.repo.session.execute(query)
            return result.scalars().unique().all()

        return await cache.get_or_set(cache_key, fetch_dashboards)

    async def get_tenant_dashboards(self, tenant_id: int) -> List[DashboardModel]:
        """Get all dashboards for a tenant with caching"""
        cache_key = f"tenant_{tenant_id}_dashboards"

        async def fetch_dashboards():
            # Use join to get user info for all dashboards in tenant
            query = select(DashboardModel).options(
                joinedload(DashboardModel.user)
            ).where(DashboardModel.tenant_id == tenant_id)

            result = await self.repo.session.execute(query)
            return result.scalars().unique().all()

        return await cache.get_or_set(cache_key, fetch_dashboards)

    async def get_dashboard_with_user(self, dashboard_id: int, tenant_id: int) -> Optional[DashboardModel]:
        """Get a specific dashboard with user info using join"""
        cache_key = f"dashboard_{dashboard_id}_tenant_{tenant_id}"

        async def fetch_dashboard():
            query = select(DashboardModel).options(
                joinedload(DashboardModel.user)
            ).where(
                and_(
                    DashboardModel.id == dashboard_id,
                    DashboardModel.tenant_id == tenant_id
                )
            )

            result = await self.repo.session.execute(query)
            return result.scalars().first()

        return await cache.get_or_set(cache_key, fetch_dashboard)