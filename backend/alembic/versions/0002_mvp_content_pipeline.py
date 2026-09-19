"""0002_mvp_content_pipeline

Revision ID: 0002_mvp_content_pipeline
Revises: 0001_initial_baseline
Create Date: 2026-09-19 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002_mvp_content_pipeline"
down_revision: str | None = "0001_initial_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "news_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("category", sa.String(length=60), nullable=False, server_default="general"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "url", name="uq_news_source_workspace_url"),
    )
    op.create_index("idx_news_sources_workspace", "news_sources", ["workspace_id"], unique=False)

    op.create_table(
        "articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=1024), nullable=True),
        sa.Column("category", sa.String(length=60), nullable=False, server_default="general"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["news_sources.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "url", name="uq_article_workspace_url"),
    )
    op.create_index("idx_articles_workspace", "articles", ["workspace_id"], unique=False)
    op.create_index("idx_articles_source", "articles", ["source_id"], unique=False)

    op.create_table(
        "social_posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("article_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("platform", sa.String(length=30), nullable=False, server_default="instagram"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING_REVIEW"),
        sa.Column("caption", sa.Text(), nullable=False),
        sa.Column("image_prompt", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=1024), nullable=True),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("external_post_id", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_social_posts_workspace", "social_posts", ["workspace_id"], unique=False)
    op.create_index("idx_social_posts_article", "social_posts", ["article_id"], unique=False)
    op.create_index("idx_social_posts_scheduled_for", "social_posts", ["scheduled_for"], unique=False)

    op.create_table(
        "social_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("platform", sa.String(length=30), nullable=False),
        sa.Column("account_identifier", sa.String(length=120), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "platform", "account_identifier", name="uq_social_account"),
    )
    op.create_index("idx_social_accounts_workspace", "social_accounts", ["workspace_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_social_accounts_workspace", table_name="social_accounts")
    op.drop_table("social_accounts")

    op.drop_index("idx_social_posts_scheduled_for", table_name="social_posts")
    op.drop_index("idx_social_posts_article", table_name="social_posts")
    op.drop_index("idx_social_posts_workspace", table_name="social_posts")
    op.drop_table("social_posts")

    op.drop_index("idx_articles_source", table_name="articles")
    op.drop_index("idx_articles_workspace", table_name="articles")
    op.drop_table("articles")

    op.drop_index("idx_news_sources_workspace", table_name="news_sources")
    op.drop_table("news_sources")
