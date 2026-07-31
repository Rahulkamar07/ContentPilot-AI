from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.user import User
from app.domain.entities.workspace import Workspace, WorkspaceMember


class UserRepositoryInterface(ABC):
    """Abstract contract enforcing user repository isolation."""

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def save(self, user: User, password_hash: str) -> User:
        pass


class WorkspaceRepositoryInterface(ABC):
    """Abstract contract enforcing workspace repository isolation."""

    @abstractmethod
    async def get_by_id(self, workspace_id: UUID) -> Workspace | None:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Workspace | None:
        pass

    @abstractmethod
    async def save(self, workspace: Workspace) -> Workspace:
        pass

    @abstractmethod
    async def add_member(self, member: WorkspaceMember) -> WorkspaceMember:
        pass
