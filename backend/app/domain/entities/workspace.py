from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class WorkspaceRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"


class PlanTier(str, Enum):
    STARTER = "STARTER"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


@dataclass
class Workspace:
    """Pure domain entity representing a multi-tenant Workspace."""
    id: UUID
    name: str
    slug: str
    owner_id: UUID
    plan_tier: PlanTier = PlanTier.STARTER
    settings: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None

    @classmethod
    def create(cls, name: str, slug: str, owner_id: UUID) -> "Workspace":
        return cls(
            id=uuid4(),
            name=name.strip(),
            slug=slug.lower().strip(),
            owner_id=owner_id,
            plan_tier=PlanTier.STARTER,
            settings={},
            created_at=datetime.utcnow(),
        )


@dataclass
class WorkspaceMember:
    """Pure domain entity linking Users to Workspaces with RBAC roles."""
    id: UUID
    workspace_id: UUID
    user_id: UUID
    role: WorkspaceRole
    created_at: datetime | None = None
