from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import SocialPostModel


async def publish_instagram_post(session: AsyncSession, post_id: UUID) -> SocialPostModel | None:
    result = await session.execute(select(SocialPostModel).where(SocialPostModel.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        return None

    if post.status not in {"SCHEDULED", "APPROVED", "PENDING_REVIEW"}:
        return post

    post.status = "PUBLISHED"
    post.published_at = datetime.now(UTC)
    post.external_post_id = f"ig_{uuid4().hex[:12]}"
    post.error_message = None
    await session.commit()
    await session.refresh(post)
    return post


async def publish_due_posts(session: AsyncSession, now: datetime | None = None) -> int:
    now_utc = now or datetime.now(UTC)
    result = await session.execute(
        select(SocialPostModel).where(
            and_(
                SocialPostModel.platform == "instagram",
                SocialPostModel.status == "SCHEDULED",
                or_(
                    SocialPostModel.scheduled_for.is_(None),
                    SocialPostModel.scheduled_for <= now_utc,
                ),
            )
        )
    )
    posts = result.scalars().all()
    for post in posts:
        post.status = "PUBLISHED"
        post.published_at = now_utc
        post.external_post_id = f"ig_{uuid4().hex[:12]}"
        post.error_message = None

    await session.commit()
    return len(posts)
