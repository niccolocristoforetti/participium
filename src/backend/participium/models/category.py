from __future__ import annotations

from dataclasses import dataclass

from participium.models.base import Base, TimestampMixin


@dataclass
class Category(TimestampMixin, Base):
    id: int | None = None
    name: str = ""
    is_active: bool = True
