from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.interfaces.repositories import UserRepositoryInterface
from app.infrastructure.database.models import UserModel


class UserRepository(UserRepositoryInterface):
    """SQLAlchemy Async implementation of UserRepositoryInterface."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email.lower().strip())
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def save(self, user: User, password_hash: str) -> User:
        model = UserModel(
            id=user.id,
            email=user.email,
            password_hash=password_hash,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            is_mfa_enabled=user.is_mfa_enabled,
        )
        self._session.add(model)
        await self._session.flush()
        return model.to_entity()
