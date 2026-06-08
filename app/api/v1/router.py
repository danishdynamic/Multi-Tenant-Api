from fastapi import APIRouter
from app.api.v1.endpoints import auth, tenants, dashboards, health, analytics, notifications, reports, billing

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
router.include_router(dashboards.router, prefix="/dashboards", tags=["dashboards"])
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
router.include_router(reports.router, prefix="/reports", tags=["reports"])
router.include_router(billing.router, prefix="/billing", tags=["billing"])
router.include_router(health.router, prefix="/health", tags=["health"])