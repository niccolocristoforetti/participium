from __future__ import annotations

from datetime import datetime

import pytest

pytestmark = pytest.mark.skip(reason="Disabled.")

from participium.core.utils import parse_date


def test_pd1_none_returns_none() -> None:
    assert parse_date(None) is None


def test_pd2_empty_string_returns_none() -> None:
    assert parse_date("") is None


def test_pd3_valid_iso_with_time() -> None:
    assert parse_date("2024-01-15T10:30:00") == datetime(2024, 1, 15, 10, 30, 0)


def test_pd4_invalid_string_raises_value_error() -> None:
    with pytest.raises(ValueError):
        parse_date("not-a-date")


def test_pdb1_date_only() -> None:
    assert parse_date("2023-10-25") == datetime(2023, 10, 25, 0, 0, 0)


def test_pdb2_hour_only() -> None:
    assert parse_date("2023-10-25T10") == datetime(2023, 10, 25, 10, 0, 0)


def test_pdb3_hour_and_minutes() -> None:
    assert parse_date("2023-10-25T10:01") == datetime(2023, 10, 25, 10, 1, 0)


def test_pdb4_wrong_separator() -> None:
    with pytest.raises(ValueError):
        parse_date("2023/10/25T10:00")


def test_pdb5_month_zero() -> None:
    with pytest.raises(ValueError):
        parse_date("2023-00-25T10:00:00")


def test_pdb6_month_thirteen() -> None:
    with pytest.raises(ValueError):
        parse_date("2023-13-25T10:00:00")


def test_pdb7_day_zero() -> None:
    with pytest.raises(ValueError):
        parse_date("2023-10-00T10:00:00")


def test_pdb8_day_thirty_two() -> None:
    with pytest.raises(ValueError):
        parse_date("2023-10-32T10:00:00")


def test_pdb9_year_month_only() -> None:
    with pytest.raises(ValueError):
        parse_date("2023-10")


def test_pdb10_hour_twenty_four() -> None:
    with pytest.raises(ValueError):
        parse_date("2024-01-15T24:00:00")


def test_pdb11_negative_seconds() -> None:
    with pytest.raises(ValueError):
        parse_date("2024-01-15T00:00:-1")


def test_pdb12_feb29_non_leap_year() -> None:
    with pytest.raises(ValueError):
        parse_date("2023-02-29T10:00:00")
