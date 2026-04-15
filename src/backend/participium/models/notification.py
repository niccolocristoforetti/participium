from __future__ import annotations

from dataclasses import dataclass

from participium.models.base import Base, TimestampMixin
from participium.models.enums import NotificationType


@dataclass
class Notification(TimestampMixin, Base):
    id: int | None = None
    user_id: int | None = None
    report_id: int | None = None
    type: NotificationType = NotificationType.SYSTEM
    title: str = ""
    body: str = ""
    is_read: bool = False
    user: "User | None" = None
    report: "Report | None" = None
