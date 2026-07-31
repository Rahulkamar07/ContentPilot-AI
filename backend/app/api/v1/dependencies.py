from typing import Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db_session
from app.core.security import decode_token
from app.domain.entities.user import User
from app.infrastructure.repositories.user_repository import UserRepository

security_bearer = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    session: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """Dependency attempting to resolve authenticated User context from JWT Bearer token."""
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


async def get_workspace_id_header(
    x_workspace_id: Optional[str] = Header(None, alias="X-Workspace-ID")
) -> Optional[UUID]:
    """Dependency extracting tenant X-Workspace-ID header."""
    if not x_workspace_id:
        return None
    try:
        return UUID(x_workspace_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-Workspace-ID header UUID format"
        )
