from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=100)


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    owner_id: UUID
    plan_tier: str


class WorkspaceMemberAddRequest(BaseModel):
    user_id: UUID
    role: str = Field(pattern="^(OWNER|ADMIN|EDITOR|VIEWER)$")


class WorkspaceMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    user_id: UUID
    role: str


class NewsSourceCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    url: str = Field(min_length=5, max_length=1024)
    category: str = Field(min_length=2, max_length=60)


class NewsSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    name: str
    url: str
    category: str
    is_active: bool
    last_fetched_at: datetime | None


class ArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID
    workspace_id: UUID
    title: str
    url: str
    summary: str | None
    category: str
    image_url: str | None
    published_at: datetime | None


class IngestSourceResponse(BaseModel):
    task_id: str
    status: str


class GeneratePostRequest(BaseModel):
    platform: str = Field(default="instagram", pattern="^(instagram)$")


class SocialPostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    article_id: UUID
    platform: str
    status: str
    caption: str
    image_prompt: str | None
    image_url: str | None
    scheduled_for: datetime | None
    published_at: datetime | None
    external_post_id: str | None


class QueueApproveRequest(BaseModel):
    caption: str | None = Field(default=None, max_length=2000)
    scheduled_for: datetime | None = None
