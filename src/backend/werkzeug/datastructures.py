from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FileStorage:
    filename: str | None = None
    content_type: str | None = None
