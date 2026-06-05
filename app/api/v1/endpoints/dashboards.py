from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.dashboard_repository import DashboardRepository
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardCreate, Dashboard
from app.core.dependencies import get_current_user
from app.db.models import User
from typing import List, cast

router = APIRouter()

@router.post("/", response_model=Dashboard)
async def create_dashboard(
    dashboard: DashboardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if dashboard.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized for this tenant")
    
    repo = DashboardRepository(db)
    service = DashboardService(repo)
    return await service.create_dashboard(dashboard)

@router.get("/", response_model=List[Dashboard])
async def get_user_dashboards(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = cast(int, current_user.id)
    repo = DashboardRepository(db)
    service = DashboardService(repo)
    return await service.get_user_dashboards(user_id)

@router.get("/{dashboard_id}", response_model=Dashboard)
async def get_dashboard(
    dashboard_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = cast(int, current_user.tenant_id)
    repo = DashboardRepository(db)
    service = DashboardService(repo)
    dashboard = await service.get_dashboard_with_user(dashboard_id, tenant_id)

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    return dashboard