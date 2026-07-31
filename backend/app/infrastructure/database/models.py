from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.user import GlobalRole, User
from app.domain.entities.workspace import PlanTier, Workspace, WorkspaceMember, WorkspaceRole
from app.infrastructure.database.base import Base, TimestampMixin, UUIDMixin


class UserModel(Base, UUIDMixin, TimestampMixin):
    """SQLAlchemy ORM model for Users."""
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=GlobalRole.USER.value)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_mfa_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mfa_secret: Mapped[str] = mapped_column(String(128), nullable=True)

    def to_entity(self) -> User:
        return User(
            id=self.id,
            email=self.email,
            full_name=self.full_name,
            role=GlobalRole(self.role),
            is_active=self.is_active,
            is_mfa_enabled=self.is_mfa_enabled,
            created_at=self.created_at,
        )


class WorkspaceModel(Base, UUIDMixin, TimestampMixin):
    """SQLAlchemy ORM model for Workspaces."""
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    owner_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_tier: Mapped[str] = mapped_column(String(20), nullable=False, default=PlanTier.STARTER.value)
    settings: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    def to_entity(self) -> Workspace:
        return Workspace(
            id=self.id,
            name=self.name,
            slug=self.slug,
            owner_id=self.owner_id,
            plan_tier=PlanTier(self.plan_tier),
            settings=self.settings or {},
            created_at=self.created_at,
        )


class WorkspaceMemberModel(Base, UUIDMixin, TimestampMixin):
    """SQLAlchemy ORM model for Workspace RBAC Memberships."""
    __tablename__ = "workspace_members"
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_user"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=WorkspaceRole.EDITOR.value)

    def to_entity(self) -> WorkspaceMember:
        return WorkspaceMember(
            id=self.id,
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            role=WorkspaceRole(self.role),
            created_at=self.created_at,
        )
