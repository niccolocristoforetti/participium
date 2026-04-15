from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


class Base:
    pass


@dataclass
class TimestampMixin:
    created_at: datetime | None = None
    updated_at: datetime | None = None
