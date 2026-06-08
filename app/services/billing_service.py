import stripe
from datetime import datetime, timedelta
from typing import Optional
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas.subscription import SubscriptionCreate, Subscription
from app.db.models import Subscription
from app.core.config import settings

stripe.api_key = settings.stripe_secret_key

class BillingService:
    def __init__(self, repo: Optional[SubscriptionRepository] = None):
        self.repo = repo

    async def create_subscription(self, subscription_data: SubscriptionCreate) -> Subscription:
        if not self.repo:
            raise ValueError("Repository required for subscription operations")
        subscription = Subscription(
            plan=subscription_data.plan,
            status="active",
            start_date=subscription_data.start_date,
            end_date=subscription_data.end_date,
            tenant_id=subscription_data.tenant_id
        )
        return await self.repo.create(subscription)

    async def get_tenant_subscriptions(self, tenant_id: int):
        if not self.repo:
            raise ValueError("Repository required for subscription operations")
        return await self.repo.get_by_tenant(tenant_id)

    async def get_active_subscription(self, tenant_id: int):
        if not self.repo:
            raise ValueError("Repository required for subscription operations")
        return await self.repo.get_active_by_tenant(tenant_id)

    @staticmethod
    def create_stripe_customer(email: str, name: str):
        return stripe.Customer.create(
            email=email,
            name=name
        )

    def create_stripe_subscription(self, customer_id: str, price_id: str):
        return stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"]
        )

    def cancel_stripe_subscription(self, subscription_id: str):
        return stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )

    @staticmethod
    def get_stripe_prices():
        return stripe.Price.list(active=True)