from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import ensure_workspace_membership, get_current_user, validate_user_exists
from app.api.v1.schemas import (
    WorkspaceCreateRequest,
    WorkspaceMemberAddRequest,
    WorkspaceMemberResponse,
    WorkspaceResponse,
)
from app.core.database import get_db_session
from app.domain.entities.user import User
from app.infrastructure.database.models import WorkspaceMemberModel, WorkspaceModel

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> WorkspaceResponse:
    slug = payload.slug.lower().strip()
    existing = await session.execute(select(WorkspaceModel).where(WorkspaceModel.slug == slug))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Workspace slug already exists")

    workspace = WorkspaceModel(
        name=payload.name.strip(),
        slug=slug,
        owner_id=current_user.id,
        plan_tier="STARTER",
        settings={},
    )
    session.add(workspace)
    await session.flush()

    membership = WorkspaceMemberModel(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role="OWNER",
    )
    session.add(membership)
    await session.commit()
    await session.refresh(workspace)

    return WorkspaceResponse.model_validate(workspace)


@router.get("", response_model=list[WorkspaceResponse])
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[WorkspaceResponse]:
    result = await session.execute(
        select(WorkspaceModel)
        .join(WorkspaceMemberModel, WorkspaceMemberModel.workspace_id == WorkspaceModel.id)
        .where(WorkspaceMemberModel.user_id == current_user.id)
        .order_by(WorkspaceModel.created_at.desc())
    )
    return [WorkspaceResponse.model_validate(item) for item in result.scalars().all()]


@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberResponse])
async def list_workspace_members(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[WorkspaceMemberResponse]:
    await ensure_workspace_membership(workspace_id, current_user.id, session)

    result = await session.execute(
        select(WorkspaceMemberModel).where(WorkspaceMemberModel.workspace_id == workspace_id)
    )
    return [WorkspaceMemberResponse.model_validate(item) for item in result.scalars().all()]


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse)
async def add_workspace_member(
    workspace_id: UUID,
    payload: WorkspaceMemberAddRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> WorkspaceMemberResponse:
    await ensure_workspace_membership(workspace_id, current_user.id, session, {"OWNER", "ADMIN"})
    await validate_user_exists(session, payload.user_id)

    existing = await session.execute(
        select(WorkspaceMemberModel).where(
            WorkspaceMemberModel.workspace_id == workspace_id,
            WorkspaceMemberModel.user_id == payload.user_id,
        )
    )
    model = existing.scalar_one_or_none()
    if model is not None:
        model.role = payload.role
    else:
        model = WorkspaceMemberModel(
            workspace_id=workspace_id,
            user_id=payload.user_id,
            role=payload.role,
        )
        session.add(model)

    await session.commit()
    await session.refresh(model)
    return WorkspaceMemberResponse.model_validate(model)
