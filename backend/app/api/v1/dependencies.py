from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token
from app.domain.entities.user import User
from app.infrastructure.database.models import UserModel, WorkspaceMemberModel
from app.infrastructure.repositories.user_repository import UserRepository

security_bearer = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    auth: HTTPAuthorizationCredentials | None = Depends(security_bearer),
    session: AsyncSession = Depends(get_db_session),
) -> User | None:
    """Dependency attempting to resolve authenticated User context from JWT bearer token."""
    if not auth or not auth.credentials:
        return None
    try:
        payload = decode_token(auth.credentials)
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        repo = UserRepository(session)
        return await repo.get_by_id(UUID(user_id_str))
    except Exception:
        return None


async def get_current_user(
    user: User | None = Depends(get_current_user_optional),
) -> User:
    if user is None:
        raise UnauthorizedException()
    return user


async def get_workspace_id_header(
    x_workspace_id: str | None = Header(None, alias="X-Workspace-ID"),
) -> UUID | None:
    """Dependency extracting tenant X-Workspace-ID header."""
    if not x_workspace_id:
        return None
    try:
        return UUID(x_workspace_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-Workspace-ID header UUID format",
        ) from exc


async def ensure_workspace_membership(
    workspace_id: UUID,
    user_id: UUID,
    session: AsyncSession,
    allowed_roles: set[str] | None = None,
) -> WorkspaceMemberModel:
    result = await session.execute(
        select(WorkspaceMemberModel).where(
            WorkspaceMemberModel.workspace_id == workspace_id,
            WorkspaceMemberModel.user_id == user_id,
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise ForbiddenException("You are not a member of this workspace")
    if allowed_roles and membership.role not in allowed_roles:
        raise ForbiddenException("Insufficient role for this workspace action")
    return membership


async def validate_user_exists(session: AsyncSession, user_id: UUID) -> UserModel:
    result = await session.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
