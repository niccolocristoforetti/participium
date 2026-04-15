from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from participium.models.base import Base, TimestampMixin


@dataclass
class EmailVerificationToken(TimestampMixin, Base):
    id: int | None = None
    user_id: int | None = None
    token: str = ""
    expires_at: datetime | None = None
    is_used: bool = False
    user: "User | None" = None
