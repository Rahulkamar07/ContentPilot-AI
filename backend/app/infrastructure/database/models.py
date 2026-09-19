from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
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
    mfa_secret: Mapped[str | None] = mapped_column(String(128), nullable=True)

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
    __table_args__ = (UniqueConstraint("workspace_id", "user_id", name="uq_workspace_user"),)

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


class NewsSourceModel(Base, UUIDMixin, TimestampMixin):
    """Configured RSS/news source per workspace."""

    __tablename__ = "news_sources"
    __table_args__ = (UniqueConstraint("workspace_id", "url", name="uq_news_source_workspace_url"),)

    workspace_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False, default="general")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ArticleModel(Base, UUIDMixin, TimestampMixin):
    """Normalized article record ingested from sources."""

    __tablename__ = "articles"
    __table_args__ = (UniqueConstraint("workspace_id", "url", name="uq_article_workspace_url"),)

    workspace_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("news_sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    category: Mapped[str] = mapped_column(String(60), nullable=False, default="general")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SocialPostModel(Base, UUIDMixin, TimestampMixin):
    """Queue item generated from articles and published to social channels."""

    __tablename__ = "social_posts"

    workspace_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    article_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    platform: Mapped[str] = mapped_column(String(30), nullable=False, default="instagram")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING_REVIEW")
    caption: Mapped[str] = mapped_column(Text, nullable=False)
    image_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    external_post_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class SocialAccountModel(Base, UUIDMixin, TimestampMixin):
    """Workspace social account connection details."""

    __tablename__ = "social_accounts"
    __table_args__ = (
        UniqueConstraint("workspace_id", "platform", "account_identifier", name="uq_social_account"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    platform: Mapped[str] = mapped_column(String(30), nullable=False)
    account_identifier: Mapped[str] = mapped_column(String(120), nullable=False)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
