from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, User
from app.core.security import get_password_hash
from app.db.models import User
from typing import Optional

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, user_data: UserCreate) -> User:
        hashed = get_password_hash(user_data.password)
        user = User(email=user_data.email, hashed_password=hashed, tenant_id=user_data.tenant_id)
        return await self.repo.create(user)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.repo.get_by_email(email)