from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import ensure_workspace_membership, get_current_user, get_workspace_id_header
from app.api.v1.schemas import (
    ArticleResponse,
    GeneratePostRequest,
    IngestSourceResponse,
    NewsSourceCreateRequest,
    NewsSourceResponse,
    QueueApproveRequest,
    SocialPostResponse,
)
from app.core.database import get_db_session
from app.domain.entities.user import User
from app.infrastructure.database.models import ArticleModel, NewsSourceModel, SocialPostModel
from app.services.ai_pipeline import generate_social_post
from app.services.publishing import publish_instagram_post
from app.workers.tasks import ingest_rss_source_task

router = APIRouter(tags=["Content Pipeline"])


@router.post("/sources", response_model=NewsSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_news_source(
    payload: NewsSourceCreateRequest,
    workspace_id: UUID | None = Depends(get_workspace_id_header),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> NewsSourceResponse:
    if workspace_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Workspace-ID header required")
    await ensure_workspace_membership(workspace_id, current_user.id, session, {"OWNER", "ADMIN", "EDITOR"})

    existing = await session.execute(
        select(NewsSourceModel).where(
            NewsSourceModel.workspace_id == workspace_id,
            NewsSourceModel.url == payload.url,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Source URL already exists")

    source = NewsSourceModel(
        workspace_id=workspace_id,
        name=payload.name.strip(),
        url=payload.url.strip(),
        category=payload.category.lower().strip(),
        is_active=True,
    )
    session.add(source)
    await session.commit()
    await session.refresh(source)
    return NewsSourceResponse.model_validate(source)


@router.get("/sources", response_model=list[NewsSourceResponse])
async def list_news_sources(
    workspace_id: UUID | None = Depends(get_workspace_id_header),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[NewsSourceResponse]:
    if workspace_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Workspace-ID header required")
    await ensure_workspace_membership(workspace_id, current_user.id, session)

    result = await session.execute(
        select(NewsSourceModel)
        .where(NewsSourceModel.workspace_id == workspace_id)
        .order_by(NewsSourceModel.created_at.desc())
    )
    return [NewsSourceResponse.model_validate(item) for item in result.scalars().all()]


@router.post("/sources/{source_id}/ingest", response_model=IngestSourceResponse)
async def ingest_source(
    source_id: UUID,
    workspace_id: UUID | None = Depends(get_workspace_id_header),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> IngestSourceResponse:
    if workspace_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Workspace-ID header required")
    await ensure_workspace_membership(workspace_id, current_user.id, session, {"OWNER", "ADMIN", "EDITOR"})

    task_result = ingest_rss_source_task.delay(str(workspace_id), str(source_id))
    return IngestSourceResponse(task_id=task_result.id, status="QUEUED")


@router.get("/articles", response_model=list[ArticleResponse])
async def list_articles(
    workspace_id: UUID | None = Depends(get_workspace_id_header),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[ArticleResponse]:
    if workspace_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Workspace-ID header required")
    await ensure_workspace_membership(workspace_id, current_user.id, session)

    result = await session.execute(
        select(ArticleModel)
        .where(ArticleModel.workspace_id == workspace_id)
        .order_by(ArticleModel.created_at.desc())
        .limit(200)
    )
    return [ArticleResponse.model_validate(item) for item in result.scalars().all()]


@router.post("/articles/{article_id}/ai-process", response_model=SocialPostResponse)
async def process_article_with_ai(
    article_id: UUID,
    payload: GeneratePostRequest,
    workspace_id: UUID | None = Depends(get_workspace_id_header),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> SocialPostResponse:
    if workspace_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Workspace-ID header required")
    await ensure_workspace_membership(workspace_id, current_user.id, session, {"OWNER", "ADMIN", "EDITOR"})

    post = await generate_social_post(
        session,
        workspace_id=workspace_id,
        article_id=article_id,
        platform=payload.platform,
    )
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    return SocialPostResponse.model_validate(post)


@router.get("/queue/posts", response_model=list[SocialPostResponse])
async def list_queue_posts(
    workspace_id: UUID | None = Depends(get_workspace_id_header),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[SocialPostResponse]:
    if workspace_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Workspace-ID header required")
    await ensure_workspace_membership(workspace_id, current_user.id, session)

    result = await session.execute(
        select(SocialPostModel)
        .where(SocialPostModel.workspace_id == workspace_id)
        .order_by(SocialPostModel.created_at.desc())
        .limit(200)
    )
    return [SocialPostResponse.model_validate(item) for item in result.scalars().all()]


@router.post("/queue/posts/{post_id}/approve", response_model=SocialPostResponse)
async def approve_queue_post(
    post_id: UUID,
    payload: QueueApproveRequest,
    workspace_id: UUID | None = Depends(get_workspace_id_header),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> SocialPostResponse:
    if workspace_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Workspace-ID header required")
    await ensure_workspace_membership(workspace_id, current_user.id, session, {"OWNER", "ADMIN", "EDITOR"})

    result = await session.execute(
        select(SocialPostModel).where(
            SocialPostModel.id == post_id,
            SocialPostModel.workspace_id == workspace_id,
        )
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if payload.caption is not None:
        post.caption = payload.caption.strip()

    post.status = "SCHEDULED"
    post.scheduled_for = payload.scheduled_for
    await session.commit()
    await session.refresh(post)

    if post.scheduled_for is None or post.scheduled_for <= datetime.now(UTC):
        published = await publish_instagram_post(session, post.id)
        if published is not None:
            post = published

    return SocialPostResponse.model_validate(post)
