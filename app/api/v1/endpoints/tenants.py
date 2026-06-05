from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.tenant_repository import TenantRepository
from app.services.tenant_service import TenantService
from app.schemas.tenant import TenantCreate, Tenant

router = APIRouter()

@router.post("/", response_model=Tenant)
async def create_tenant(tenant: TenantCreate, db: AsyncSession = Depends(get_db)):
    repo = TenantRepository(db)
    service = TenantService(repo)
    return await service.create_tenant(tenant)

@router.get("/{tenant_id}", response_model=Tenant)
async def get_tenant(tenant_id: int, db: AsyncSession = Depends(get_db)):
    repo = TenantRepository(db)
    tenant = await repo.get_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant