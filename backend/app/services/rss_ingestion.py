from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import feedparser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import ArticleModel, NewsSourceModel


def _parse_published_at(entry: dict[str, Any]) -> datetime | None:
    value = entry.get("published_parsed")
    if value is None:
        return None
    try:
        return datetime(*value[:6], tzinfo=UTC)
    except (TypeError, ValueError):
        return None


def _normalize_entry(entry: dict[str, Any], fallback_category: str) -> dict[str, Any]:
    title = str(entry.get("title", "")).strip() or "Untitled article"
    url = str(entry.get("link", "")).strip()
    summary = str(entry.get("summary", "")).strip() or None

    media = entry.get("media_content") or []
    image_url = None
    if isinstance(media, list) and media:
        first = media[0]
        if isinstance(first, dict):
            image_url = first.get("url")

    category = fallback_category
    tags = entry.get("tags")
    if isinstance(tags, list) and tags:
        first_tag = tags[0]
        if isinstance(first_tag, dict) and first_tag.get("term"):
            category = str(first_tag["term"]).lower().strip()

    return {
        "title": title,
        "url": url,
        "summary": summary,
        "content": summary,
        "image_url": image_url,
        "category": category,
        "published_at": _parse_published_at(entry),
    }


async def ingest_source(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    source_id: UUID,
    max_entries: int = 30,
) -> dict[str, int]:
    source_result = await session.execute(
        select(NewsSourceModel).where(
            NewsSourceModel.id == source_id,
            NewsSourceModel.workspace_id == workspace_id,
            NewsSourceModel.is_active.is_(True),
        )
    )
    source = source_result.scalar_one_or_none()
    if source is None:
        return {"processed": 0, "created": 0, "skipped": 0}

    parsed_feed = feedparser.parse(source.url)
    entries = parsed_feed.entries[:max_entries]

    urls = [str(item.get("link", "")).strip() for item in entries if item.get("link")]
    existing_urls: set[str] = set()
    if urls:
        existing_result = await session.execute(
            select(ArticleModel.url).where(
                ArticleModel.workspace_id == workspace_id,
                ArticleModel.url.in_(urls),
            )
        )
        existing_urls = set(existing_result.scalars().all())

    created = 0
    skipped = 0

    for raw_entry in entries:
        normalized = _normalize_entry(raw_entry, source.category)
        if not normalized["url"] or normalized["url"] in existing_urls:
            skipped += 1
            continue

        session.add(
            ArticleModel(
                workspace_id=workspace_id,
                source_id=source.id,
                title=normalized["title"],
                url=normalized["url"],
                summary=normalized["summary"],
                content=normalized["content"],
                image_url=normalized["image_url"],
                category=normalized["category"],
                published_at=normalized["published_at"],
            )
        )
        existing_urls.add(normalized["url"])
        created += 1

    source.last_fetched_at = datetime.now(UTC)
    await session.commit()

    return {
        "processed": len(entries),
        "created": created,
        "skipped": skipped,
    }
