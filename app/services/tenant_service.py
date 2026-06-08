from app.repositories.tenant_repository import TenantRepository
from app.schemas.tenant import TenantCreate, Tenant
from app.db.models import Tenant

class TenantService:
    def __init__(self, repo: TenantRepository):
        self.repo = repo

    async def create_tenant(self, tenant_data: TenantCreate) -> Tenant:
        tenant = Tenant(name=tenant_data.name)
        return await self.repo.create(tenant)

    async def get_tenant_by_name(self, name: str) -> Tenant:
        return await self.repo.get_by_name(name)