from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class GlobalRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    USER = "USER"


@dataclass
class User:
    """Pure domain entity representing a User."""
    id: UUID
    email: str
    full_name: str
    role: GlobalRole
    is_active: bool = True
    is_mfa_enabled: bool = False
    created_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        email: str,
        full_name: str,
        role: GlobalRole = GlobalRole.USER,
    ) -> "User":
        return cls(
            id=uuid4(),
            email=email.lower().strip(),
            full_name=full_name.strip(),
            role=role,
            is_active=True,
            is_mfa_enabled=False,
            created_at=datetime.utcnow(),
        )
