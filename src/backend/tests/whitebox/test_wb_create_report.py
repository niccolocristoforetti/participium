from __future__ import annotations

from unittest.mock import Mock

import pytest

from participium.core.exceptions import ValidationError
from participium.models.enums import ReportStatus
from participium.services.report_service import ReportService


pytestmark = pytest.mark.whitebox


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_photo(filename: str = "photo.jpg", content_type: str = "image/jpeg") -> Mock:
    photo = Mock()
    photo.filename = filename
    photo.content_type = content_type
    return photo


def _make_empty_photo() -> Mock:
    """A FileStorage-like object with no filename (filtered out as invalid)."""
    photo = Mock()
    photo.filename = None
    return photo


def _make_reporter(reporter_id: int = 1) -> Mock:
    reporter = Mock()
    reporter.id = reporter_id
    return reporter


def _make_active_category(category_id: int = 10) -> Mock:
    category = Mock()
    category.id = category_id
    category.is_active = True
    category.name = "Roads"
    return category


def _make_inactive_category(category_id: int = 10) -> Mock:
    category = Mock()
    category.id = category_id
    category.is_active = False
    return category


# ---------------------------------------------------------------------------
# Base fixture — bundle
# ---------------------------------------------------------------------------

@pytest.fixture
def report_service_bundle() -> dict[str, object]:
    session = Mock()
    report_repository = Mock()
    category_repository = Mock()
    storage_service = Mock()
    notification_service = Mock()

    service = ReportService(
        session=session,
        report_repository=report_repository,
        category_repository=category_repository,
        storage_service=storage_service,
        notification_service=notification_service,
    )

    return {
        "service": service,
        "session": session,
        "report_repository": report_repository,
        "category_repository": category_repository,
        "storage_service": storage_service,
    }


# ---------------------------------------------------------------------------
# Derived fixture — happy-path baseline (active category + return value wired)
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_report_case(report_service_bundle: dict[str, object]) -> dict[str, object]:
    """All inputs valid: active category, title, description, coordinates, 1 photo."""
    category = _make_active_category()
    report_service_bundle["category_repository"].get_by_id.return_value = category

    saved_report = Mock()
    saved_report.id = 99
    report_service_bundle["report_repository"].get_by_id.return_value = saved_report
    report_service_bundle["storage_service"].save.return_value = "/uploads/photo.jpg"

    report_service_bundle["category"] = category
    report_service_bundle["saved_report"] = saved_report
    return report_service_bundle


# ---------------------------------------------------------------------------
# T1 – category_id is None → category = None → ValidationError
# ---------------------------------------------------------------------------

def test_create_report_raises_when_category_id_is_none(
    report_service_bundle: dict[str, object],
) -> None:
    """C_category (category_id is None) → False branch → category = None → ValidationError."""
    service = report_service_bundle["service"]
    report_service_bundle["category_repository"].get_by_id.return_value = None

    with pytest.raises(ValidationError, match="valid active category"):
        service.create_report(
            reporter=_make_reporter(),
            category_id=None,
            title="A title",
            description="A description",
            latitude=45.0,
            longitude=7.0,
            photos=[_make_photo()],
        )


# ---------------------------------------------------------------------------
# T2 – category_id is a non-parseable string → int() raises → ValidationError
# ---------------------------------------------------------------------------

def test_create_report_raises_when_category_id_not_parseable(
    report_service_bundle: dict[str, object],
) -> None:
    """int(category_id) raises ValueError → ValidationError ("valid active category")."""
    service = report_service_bundle["service"]

    with pytest.raises(ValidationError, match="valid active category"):
        service.create_report(
            reporter=_make_reporter(),
            category_id="not-a-number",
            title="A title",
            description="A description",
            latitude=45.0,
            longitude=7.0,
            photos=[_make_photo()],
        )


# ---------------------------------------------------------------------------
# T3 – valid category_id integer but category not found in DB → ValidationError
# ---------------------------------------------------------------------------

def test_create_report_raises_when_category_not_found(
    report_service_bundle: dict[str, object],
) -> None:
    """get_by_id returns None → not category → ValidationError."""
    service = report_service_bundle["service"]
    report_service_bundle["category_repository"].get_by_id.return_value = None

    with pytest.raises(ValidationError, match="valid active category"):
        service.create_report(
            reporter=_make_reporter(),
            category_id=10,
            title="A title",
            description="A description",
            latitude=45.0,
            longitude=7.0,
            photos=[_make_photo()],
        )


# ---------------------------------------------------------------------------
# T4 – category found but inactive → ValidationError
# ---------------------------------------------------------------------------

def test_create_report_raises_when_category_inactive(
    report_service_bundle: dict[str, object],
) -> None:
    """category.is_active == False → ValidationError."""
    service = report_service_bundle["service"]
    report_service_bundle["category_repository"].get_by_id.return_value = _make_inactive_category()

    with pytest.raises(ValidationError, match="valid active category"):
        service.create_report(
            reporter=_make_reporter(),
            category_id=10,
            title="A title",
            description="A description",
            latitude=45.0,
            longitude=7.0,
            photos=[_make_photo()],
        )


# ---------------------------------------------------------------------------
# T5 – title is empty string → ValidationError
# ---------------------------------------------------------------------------

def test_create_report_raises_when_title_missing(
    valid_report_case: dict[str, object],
) -> None:
    """not title → ValidationError ("Title and description")."""
    service = valid_report_case["service"]

    with pytest.raises(ValidationError, match="Title and description"):
        service.create_report(
            reporter=_make_reporter(),
            category_id=10,
            title="",
            description="A description",
            latitude=45.0,
            longitude=7.0,
            photos=[_make_photo()],
        )


# ---------------------------------------------------------------------------
# T6 – description is empty string → ValidationError
# ---------------------------------------------------------------------------

def test_create_report_raises_when_description_missing(
    valid_report_case: dict[str, object],
) -> None:
    """not description → ValidationError ("Title and description")."""
    service = valid_report_case["service"]

    with pytest.raises(ValidationError, match="Title and description"):
        service.create_report(
            reporter=_make_reporter(),
            category_id=10,
            title="A title",
            description="",
            latitude=45.0,
            longitude=7.0,
            photos=[_make_photo()],
        )


# ---------------------------------------------------------------------------
# T7 – latitude is None → ValidationError
# ---------------------------------------------------------------------------

def test_create_report_raises_when_latitude_is_none(
    valid_report_case: dict[str, object],
) -> None:
    """latitude is None → ValidationError ("Latitude and longitude are required")."""
    service = valid_report_case["service"]

    with pytest.raises(ValidationError, match="Latitude and longitude are required"):
        service.create_report(
            reporter=_make_reporter(),
            category_id=10,
            title="A title",
            description="A description",
            latitude=None,
            longitude=7.0,
            photos=[_make_photo()],
        )


# ---------------------------------------------------------------------------
# T8 – longitude is None → ValidationError
# ---------------------------------------------------------------------------

def test_create_report_raises_when_longitude_is_none(
    valid_report_case: dict[str, object],
) -> None:
    """longitude is None → ValidationError ("Latitude and longitude are required")."""
    service = valid_report_case["service"]

    with pytest.raises(ValidationError, match="Latitude and longitude are required"):
        service.create_report(
            reporter=_make_reporter(),
            category_id=10,
            title="A title",
            description="A description",
            latitude=45.0,
            longitude=None,
            photos=[_make_photo()],
        )


# ---------------------------------------------------------------------------
# T9 – latitude is non-numeric string → float() raises → ValidationError
# ---------------------------------------------------------------------------

def test_create_report_raises_when_latitude_not_numeric(
    valid_report_case: dict[str, object],
) -> None:
    """float(latitude) raises ValueError → ValidationError ("valid numbers")."""
    service = valid_report_case["service"]

    with pytest.raises(ValidationError, match="valid numbers"):
        service.create_report(
            reporter=_make_reporter(),
            category_id=10,
            title="A title",
            description="A description",
            latitude="not-a-float",
            longitude=7.0,
            photos=[_make_photo()],
        )


# ---------------------------------------------------------------------------
# T10 – longitude is non-numeric string → float() raises → ValidationError
# ---------------------------------------------------------------------------

def test_create_report_raises_when_longitude_not_numeric(
    valid_report_case: dict[str, object],
) -> None:
    """float(longitude) raises ValueError → ValidationError ("valid numbers")."""
    service = valid_report_case["service"]

    with pytest.raises(ValidationError, match="valid numbers"):
        service.create_report(
            reporter=_make_reporter(),
            category_id=10,
            title="A title",
            description="A description",
            latitude=45.0,
            longitude="not-a-float",
            photos=[_make_photo()],
        )


# ---------------------------------------------------------------------------
# T11 – photos list empty → valid_photos empty → ValidationError
# ---------------------------------------------------------------------------

def test_create_report_raises_when_no_valid_photos(
    valid_report_case: dict[str, object],
) -> None:
    """photos=[] → valid_photos=[] → ValidationError ("At least one photo")."""
    service = valid_report_case["service"]

    with pytest.raises(ValidationError, match="At least one photo"):
        service.create_report(
            reporter=_make_reporter(),
            category_id=10,
            title="A title",
            description="A description",
            latitude=45.0,
            longitude=7.0,
            photos=[],
        )


# ---------------------------------------------------------------------------
# T12 – all photos have no filename → all filtered → ValidationError
# ---------------------------------------------------------------------------

def test_create_report_raises_when_all_photos_have_no_filename(
    valid_report_case: dict[str, object],
) -> None:
    """All FileStorage objects have filename=None → valid_photos=[] → ValidationError."""
    service = valid_report_case["service"]

    with pytest.raises(ValidationError, match="At least one photo"):
        service.create_report(
            reporter=_make_reporter(),
            category_id=10,
            title="A title",
            description="A description",
            latitude=45.0,
            longitude=7.0,
            photos=[_make_empty_photo(), _make_empty_photo()],
        )


# ---------------------------------------------------------------------------
# T13 – 4 valid photos → len(valid_photos) > 3 → ValidationError
# ---------------------------------------------------------------------------

def test_create_report_raises_when_more_than_three_photos(
    valid_report_case: dict[str, object],
) -> None:
    """len(valid_photos) == 4 > 3 → ValidationError ("at most 3 photos")."""
    service = valid_report_case["service"]

    with pytest.raises(ValidationError, match="at most 3 photos"):
        service.create_report(
            reporter=_make_reporter(),
            category_id=10,
            title="A title",
            description="A description",
            latitude=45.0,
            longitude=7.0,
            photos=[_make_photo(f"p{i}.jpg") for i in range(4)],
        )


# ---------------------------------------------------------------------------
# T14 – happy path, exactly 1 photo (loop executed once)
# ---------------------------------------------------------------------------

def test_create_report_succeeds_with_one_photo(
    valid_report_case: dict[str, object],
) -> None:
    """All inputs valid with 1 photo: report persisted, session committed, return value correct."""
    service = valid_report_case["service"]
    session = valid_report_case["session"]
    report_repository = valid_report_case["report_repository"]
    storage_service = valid_report_case["storage_service"]
    saved_report = valid_report_case["saved_report"]

    photo = _make_photo()

    result = service.create_report(
        reporter=_make_reporter(),
        category_id=10,
        title="  Pothole on Via Roma  ",
        description="Large pothole near n. 5",
        latitude=45.07,
        longitude=7.67,
        photos=[photo],
    )

    assert result is saved_report
    report_repository.add.assert_called()
    session.flush.assert_called_once()
    storage_service.save.assert_called_once_with(photo)
    report_repository.add_photo.assert_called_once()
    report_repository.add_status_entry.assert_called_once()
    session.commit.assert_called_once()


# ---------------------------------------------------------------------------
# T15 – happy path, exactly 3 photos (loop executed 3 times)
# ---------------------------------------------------------------------------

def test_create_report_succeeds_with_three_photos(
    valid_report_case: dict[str, object],
) -> None:
    """3 valid photos: storage.save and add_photo each called exactly 3 times."""
    service = valid_report_case["service"]
    session = valid_report_case["session"]
    report_repository = valid_report_case["report_repository"]
    storage_service = valid_report_case["storage_service"]

    photos = [_make_photo(f"p{i}.jpg") for i in range(3)]

    service.create_report(
        reporter=_make_reporter(),
        category_id=10,
        title="Title",
        description="Description",
        latitude=45.07,
        longitude=7.67,
        photos=photos,
    )

    assert storage_service.save.call_count == 3
    assert report_repository.add_photo.call_count == 3
    session.commit.assert_called_once()


# ---------------------------------------------------------------------------
# T16 – mixed photos: invalid ones filtered, only valid ones saved
# ---------------------------------------------------------------------------

def test_create_report_filters_photos_without_filename(
    valid_report_case: dict[str, object],
) -> None:
    """Photos without filename are excluded; remaining valid photo is persisted."""
    service = valid_report_case["service"]
    storage_service = valid_report_case["storage_service"]
    report_repository = valid_report_case["report_repository"]

    valid_photo = _make_photo("real.jpg")
    photos = [_make_empty_photo(), valid_photo, _make_empty_photo()]

    service.create_report(
        reporter=_make_reporter(),
        category_id=10,
        title="Title",
        description="Description",
        latitude=45.07,
        longitude=7.67,
        photos=photos,
    )

    storage_service.save.assert_called_once_with(valid_photo)
    assert report_repository.add_photo.call_count == 1


# ---------------------------------------------------------------------------
# T17 – title and description are stripped of surrounding whitespace
# ---------------------------------------------------------------------------

def test_create_report_strips_title_and_description(
    valid_report_case: dict[str, object],
) -> None:
    """title.strip() and description.strip() are applied before persisting."""
    service = valid_report_case["service"]
    report_repository = valid_report_case["report_repository"]

    service.create_report(
        reporter=_make_reporter(),
        category_id=10,
        title="  spaced title  ",
        description="  spaced description  ",
        latitude=45.0,
        longitude=7.0,
        photos=[_make_photo()],
    )

    # First call to add() carries the newly-constructed Report instance
    added_report = report_repository.add.call_args_list[0][0][0]
    assert added_report.title == "spaced title"
    assert added_report.description == "spaced description"


# ---------------------------------------------------------------------------
# T18 – is_anonymous flag is propagated correctly
# ---------------------------------------------------------------------------

def test_create_report_propagates_is_anonymous_flag(
    valid_report_case: dict[str, object],
) -> None:
    """is_anonymous=True is stored on the Report object passed to add()."""
    service = valid_report_case["service"]
    report_repository = valid_report_case["report_repository"]

    service.create_report(
        reporter=_make_reporter(),
        category_id=10,
        title="Title",
        description="Description",
        latitude=45.0,
        longitude=7.0,
        photos=[_make_photo()],
        is_anonymous=True,
    )

    added_report = report_repository.add.call_args_list[0][0][0]
    assert added_report.is_anonymous is True


# ---------------------------------------------------------------------------
# T19 – initial status is always PENDING_APPROVAL
# ---------------------------------------------------------------------------

def test_create_report_initial_status_is_pending_approval(
    valid_report_case: dict[str, object],
) -> None:
    """Newly created Report is initialised with status=ReportStatus.PENDING_APPROVAL."""
    service = valid_report_case["service"]
    report_repository = valid_report_case["report_repository"]

    service.create_report(
        reporter=_make_reporter(),
        category_id=10,
        title="Title",
        description="Description",
        latitude=45.0,
        longitude=7.0,
        photos=[_make_photo()],
    )

    added_report = report_repository.add.call_args_list[0][0][0]
    assert added_report.status == ReportStatus.PENDING_APPROVAL


# ---------------------------------------------------------------------------
# T20 – category_id supplied as a numeric string (e.g. "10") → accepted
# ---------------------------------------------------------------------------

def test_create_report_accepts_category_id_as_numeric_string(
    valid_report_case: dict[str, object],
) -> None:
    """category_id='10' is coerced to int(10) and passed to get_by_id."""
    service = valid_report_case["service"]
    category_repository = valid_report_case["category_repository"]

    service.create_report(
        reporter=_make_reporter(),
        category_id="10",
        title="Title",
        description="Description",
        latitude=45.0,
        longitude=7.0,
        photos=[_make_photo()],
    )

    category_repository.get_by_id.assert_called_once_with(10)

