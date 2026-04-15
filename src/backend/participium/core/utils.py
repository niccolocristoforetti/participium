from __future__ import annotations

from datetime import datetime


def parse_date(value: str | None) -> datetime | None:
    """Parse an ISO-8601 datetime string.

    Inputs:
        value: ISO-8601 datetime string, or `None`.

    Returns:
        Parsed `datetime` when `value` is non-empty, otherwise `None`.

    Raises:
        ValueError: if `value` is non-empty but not a valid ISO-8601 datetime.
    """
    raise NotImplementedError
