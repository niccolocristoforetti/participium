from __future__ import annotations

from dataclasses import dataclass, field

from participium.models.base import Base, TimestampMixin
from participium.models.enums import Role


@dataclass
class User(TimestampMixin, Base):
    id: int | None = None
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    password_hash: str = ""
    role: Role = Role.CITIZEN
    category_id: int | None = None
    is_active: bool = True
    is_email_verified: bool = False
    email_notifications_enabled: bool = True
    profile_picture_path: str | None = None
    category: "Category | None" = None
    reports: list["Report"] = field(default_factory=list)
    notifications: list["Notification"] = field(default_factory=list)
    verification_tokens: list["EmailVerificationToken"] = field(default_factory=list)
