from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import ArticleModel, SocialPostModel


def summarize_text(text: str) -> str:
    compact = " ".join(text.split())
    if not compact:
        return "No summary available."
    return compact[:280] if len(compact) > 280 else compact


def build_caption(title: str, summary: str, category: str) -> str:
    hashtag = f"#{category.replace(' ', '').lower()}" if category else "#news"
    title_part = title.strip()[:120]
    summary_part = summary.strip()[:220]
    return f"{title_part}\n\n{summary_part}\n\n{hashtag} #contentpilot"


def vision_prompt_from_article(title: str, summary: str, category: str) -> str:
    return (
        "Create an original editorial illustration. "
        f"Topic: {category}. Headline context: {title}. "
        f"Key scene cues: {summary[:200]}. "
        "Use bold composition, modern lighting, and avoid logos/text from source image."
    )


async def generate_social_post(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    article_id: UUID,
    platform: str = "instagram",
) -> SocialPostModel | None:
    article_result = await session.execute(
        select(ArticleModel).where(
            ArticleModel.id == article_id,
            ArticleModel.workspace_id == workspace_id,
        )
    )
    article = article_result.scalar_one_or_none()
    if article is None:
        return None

    summary = summarize_text(article.summary or article.content or article.title)
    article.summary = summary
    caption = build_caption(article.title, summary, article.category)
    prompt = vision_prompt_from_article(article.title, summary, article.category)

    post = SocialPostModel(
        workspace_id=workspace_id,
        article_id=article.id,
        platform=platform,
        status="PENDING_REVIEW",
        caption=caption,
        image_prompt=prompt,
        image_url=article.image_url,
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post
