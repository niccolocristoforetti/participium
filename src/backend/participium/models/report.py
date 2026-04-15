from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from participium.models.base import Base, TimestampMixin
from participium.models.enums import ReportStatus


@dataclass
class Report(TimestampMixin, Base):
    id: int | None = None
    title: str = ""
    description: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    is_anonymous: bool = False
    status: ReportStatus = ReportStatus.PENDING_APPROVAL
    rejection_reason: str | None = None
    reporter_id: int | None = None
    category_id: int | None = None
    reporter: "User | None" = None
    category: "Category | None" = None
    photos: list["ReportPhoto"] = field(default_factory=list)
    status_history: list["ReportStatusHistory"] = field(default_factory=list)
    followers: list["ReportFollower"] = field(default_factory=list)
    messages: list["Message"] = field(default_factory=list)


@dataclass
class ReportPhoto(TimestampMixin, Base):
    id: int | None = None
    report_id: int | None = None
    file_path: str = ""
    original_filename: str = ""
    content_type: str | None = None
    report: Report | None = None


@dataclass
class ReportStatusHistory(Base):
    id: int | None = None
    report_id: int | None = None
    previous_status: ReportStatus | None = None
    new_status: ReportStatus = ReportStatus.PENDING_APPROVAL
    note: str | None = None
    changed_by_id: int | None = None
    created_at: datetime | None = None
    report: Report | None = None
    changed_by: "User | None" = None


@dataclass
class ReportFollower(Base):
    id: int | None = None
    report_id: int | None = None
    user_id: int | None = None
    created_at: datetime | None = None
    report: Report | None = None
    user: "User | None" = None
