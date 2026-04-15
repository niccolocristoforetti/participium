from __future__ import annotations

from dataclasses import dataclass

from participium.models.base import Base, TimestampMixin


@dataclass
class Message(TimestampMixin, Base):
    id: int | None = None
    report_id: int | None = None
    sender_id: int | None = None
    recipient_id: int | None = None
    body: str = ""
    report: "Report | None" = None
    sender: "User | None" = None
    recipient: "User | None" = None
