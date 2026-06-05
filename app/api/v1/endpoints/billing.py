from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.billing_service import BillingService
from app.schemas.subscription import SubscriptionCreate, Subscription
from app.core.dependencies import get_current_user
from app.db.models import User
from typing import List, cast

router = APIRouter()

@router.post("/", response_model=Subscription)
async def create_subscription(
    subscription: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if subscription.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized for this tenant")
    
    repo = SubscriptionRepository(db)
    service = BillingService(repo)
    return await service.create_subscription(subscription)

@router.get("/", response_model=List[Subscription])
async def get_tenant_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = SubscriptionRepository(db)
    service = BillingService(repo)
    tenant_id = cast(int, current_user.tenant_id)  # Explicit type cast for Pylance
    return await service.get_tenant_subscriptions(tenant_id)

@router.get("/active", response_model=Subscription)
async def get_active_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = SubscriptionRepository(db)
    service = BillingService(repo)
    tenant_id = cast(int, current_user.tenant_id)  # Explicit type cast for Pylance
    subscription = await service.get_active_subscription(tenant_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    return subscription

@router.post("/stripe/customer")
async def create_stripe_customer(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BillingService()  # No repo needed for Stripe operations
    email = cast(str, current_user.email)  # Explicit type cast for Pylance
    tenant_id = cast(int, current_user.tenant_id)  # Explicit type cast for Pylance
    customer = service.create_stripe_customer(email, f"Tenant {tenant_id}")
    return {"customer_id": customer.id, "customer": customer}

@router.get("/stripe/prices")
async def get_stripe_prices(
    current_user: User = Depends(get_current_user)
):
    prices = BillingService.get_stripe_prices()  # Static method call
    return {"prices": prices.data}