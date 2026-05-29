from __future__ import annotations

from unittest.mock import Mock

import pytest

from participium.core.exceptions import ValidationError
from participium.models.enums import ReportStatus
from participium.services.report_service import ReportService


pytestmark = pytest.mark.whitebox



#  Helpers 


# Crea un oggetto FileStorage valido con filename e content_type impostati.
def _make_photo(filename: str = "photo.jpg", content_type: str = "image/jpeg") -> Mock:
    photo = Mock()
    photo.filename = filename
    photo.content_type = content_type
    return photo


# Crea un oggetto FileStorage senza filename (viene scartato in quanto non valido).
def _make_empty_photo() -> Mock:
    photo = Mock()
    photo.filename = None
    return photo


# Crea un mock dell'utente segnalatore con un id specifico.
def _make_reporter(reporter_id: int = 1) -> Mock:
    reporter = Mock()
    reporter.id = reporter_id
    return reporter


# Crea un mock di una categoria attiva nel sistema.
def _make_active_category(category_id: int = 10) -> Mock:
    category = Mock()
    category.id = category_id
    category.is_active = True
    category.name = "Strade"
    return category


# Crea un mock di una categoria disattivata nel sistema.
def _make_inactive_category(category_id: int = 10) -> Mock:
    category = Mock()
    category.id = category_id
    category.is_active = False
    return category



#  Fixtures 


# Crea un servizio con tutte le dipendenze mockate per l'isolamento dei test.
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


# Baseline di test con tutti gli input base validi e mock pre-configurati.
@pytest.fixture
def valid_report_case(report_service_bundle: dict[str, object]) -> dict[str, object]:
    category = _make_active_category()
    report_service_bundle["category_repository"].get_by_id.return_value = category

    saved_report = Mock()
    saved_report.id = 99
    report_service_bundle["report_repository"].get_by_id.return_value = saved_report
    report_service_bundle["storage_service"].save.return_value = "/uploads/photo.jpg"

    report_service_bundle["category"] = category
    report_service_bundle["saved_report"] = saved_report
    return report_service_bundle



# Casi di fallimento: categoria non valida (CR1: id None, CR2: non numerico, CR3: non trovata, CR4: inattiva) → ValidationError
@pytest.mark.parametrize(
    "category_id, mock_category_return, expected_match",
    [
        (None, _make_active_category(), "valid active category"),
        ("not-a-number", _make_active_category(), "valid active category"),
        (10, None, "valid active category"),
        (10, _make_inactive_category(), "valid active category"),
    ],
)
def test_create_report_invalid_category(
    report_service_bundle: dict[str, object],
    category_id,
    mock_category_return,
    expected_match,
) -> None:
    service = report_service_bundle["service"]
    report_service_bundle["category_repository"].get_by_id.return_value = mock_category_return

    with pytest.raises(ValidationError, match=expected_match):
        service.create_report(
            reporter=_make_reporter(),
            category_id=category_id,
            title="Titolo valido",
            description="Descrizione valida",
            latitude=45.0,
            longitude=7.0,
            photos=[_make_photo()],
        )


# Casi di fallimento: campi testo vuoti o coordinate non valide (CR5-CR10) → ValidationError
@pytest.mark.parametrize(
    "title, description, latitude, longitude, expected_match",
    [
        ("", "Descrizione valida", 45.0, 7.0, "Title and description"),
        ("Titolo valido", "", 45.0, 7.0, "Title and description"),
        ("Titolo valido", "Descrizione valida", None, 7.0, "Latitude and longitude are required"),
        ("Titolo valido", "Descrizione valida", 45.0, None, "Latitude and longitude are required"),
        ("Titolo valido", "Descrizione valida", "not-a-float", 7.0, "valid numbers"),
        ("Titolo valido", "Descrizione valida", 45.0, "not-a-float", "valid numbers"),
    ],
)
def test_create_report_invalid_fields(
    valid_report_case: dict[str, object],
    title,
    description,
    latitude,
    longitude,
    expected_match,
) -> None:
    service = valid_report_case["service"]

    with pytest.raises(ValidationError, match=expected_match):
        service.create_report(
            reporter=_make_reporter(),
            category_id=10,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            photos=[_make_photo()],
        )


# Casi di fallimento e limiti: validazione del numero di foto (CRB1: nessuna, CRB2: tutte vuote, CRB3: più di 3) → ValidationError
@pytest.mark.parametrize(
    "photos, expected_match",
    [
        ([], "At least one photo"),
        ([_make_empty_photo(), _make_empty_photo()], "At least one photo"),
        ([_make_photo(f"p{i}.jpg") for i in range(4)], "at most 3 photos"),
    ],
)
def test_create_report_invalid_photos(
    valid_report_case: dict[str, object],
    photos,
    expected_match,
) -> None:
    service = valid_report_case["service"]

    with pytest.raises(ValidationError, match=expected_match):
        service.create_report(
            reporter=_make_reporter(),
            category_id=10,
            title="Titolo valido",
            description="Descrizione valida",
            latitude=45.0,
            longitude=7.0,
            photos=photos,
        )


# CR11 –  la creazione ha successo con esattamente una foto valida e persistenza corretta.
def test_cr11_succeeds_with_one_photo(valid_report_case: dict[str, object]) -> None:
    service = valid_report_case["service"]
    session = valid_report_case["session"]
    report_repository = valid_report_case["report_repository"]
    storage_service = valid_report_case["storage_service"]
    saved_report = valid_report_case["saved_report"]

    photo = _make_photo()

    result = service.create_report(
        reporter=_make_reporter(),
        category_id=10,
        title="  Buca in Via Roma  ",
        description="Larga buca vicino al civico 5",
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


# CRB4 – Caso limite di successo: la creazione ha successo con esattamente 3 foto valide (limite massimo).
def test_crb4_succeeds_with_three_photos(valid_report_case: dict[str, object]) -> None:
    service = valid_report_case["service"]
    session = valid_report_case["session"]
    report_repository = valid_report_case["report_repository"]
    storage_service = valid_report_case["storage_service"]

    photos = [_make_photo(f"p{i}.jpg") for i in range(3)]

    service.create_report(
        reporter=_make_reporter(),
        category_id=10,
        title="Titolo",
        description="Descrizione",
        latitude=45.07,
        longitude=7.67,
        photos=photos,
    )

    assert storage_service.save.call_count == 3
    assert report_repository.add_photo.call_count == 3
    session.commit.assert_called_once()


# CR12 – Filtro foto: gli oggetti foto privi di filename vengono scartati e non salvati su storage.
def test_cr12_filters_photos_without_filename(valid_report_case: dict[str, object]) -> None:
    service = valid_report_case["service"]
    storage_service = valid_report_case["storage_service"]
    report_repository = valid_report_case["report_repository"]

    valid_photo = _make_photo("real.jpg")
    photos = [_make_empty_photo(), valid_photo, _make_empty_photo()]

    service.create_report(
        reporter=_make_reporter(),
        category_id=10,
        title="Titolo",
        description="Descrizione",
        latitude=45.07,
        longitude=7.67,
        photos=photos,
    )

    storage_service.save.assert_called_once_with(valid_photo)
    assert report_repository.add_photo.call_count == 1


# CR13 – gli spazi bianchi all'inizio e alla fine di titolo e descrizione vengono rimossi.
def test_cr13_strips_title_and_description(valid_report_case: dict[str, object]) -> None:
    service = valid_report_case["service"]
    report_repository = valid_report_case["report_repository"]

    service.create_report(
        reporter=_make_reporter(),
        category_id=10,
        title="  titolo spaziato  ",
        description="  descrizione spaziata  ",
        latitude=45.0,
        longitude=7.0,
        photos=[_make_photo()],
    )

    added_report = report_repository.add.call_args_list[0][0][0]
    assert added_report.title == "titolo spaziato"
    assert added_report.description == "descrizione spaziata"


# CR14 – l'opzione is_anonymous viene correttamente passata e assegnata al modello del report.
def test_cr14_propagates_is_anonymous_flag(valid_report_case: dict[str, object]) -> None:
    service = valid_report_case["service"]
    report_repository = valid_report_case["report_repository"]

    service.create_report(
        reporter=_make_reporter(),
        category_id=10,
        title="Titolo",
        description="Descrizione",
        latitude=45.0,
        longitude=7.0,
        photos=[_make_photo()],
        is_anonymous=True,
    )

    added_report = report_repository.add.call_args_list[0][0][0]
    assert added_report.is_anonymous is True


# CR15 – ogni nuovo report creato assume tassativamente lo stato iniziale PENDING_APPROVAL.
def test_cr15_initial_status_is_pending_approval(valid_report_case: dict[str, object]) -> None:
    service = valid_report_case["service"]
    report_repository = valid_report_case["report_repository"]

    service.create_report(
        reporter=_make_reporter(),
        category_id=10,
        title="Titolo",
        description="Descrizione",
        latitude=45.0,
        longitude=7.0,
        photos=[_make_photo()],
    )

    added_report = report_repository.add.call_args_list[0][0][0]
    assert added_report.status == ReportStatus.PENDING_APPROVAL


# CR16 – un category_id fornito come stringa numerica viene convertito correttamente in intero.
def test_cr16_accepts_category_id_as_numeric_string(valid_report_case: dict[str, object]) -> None:
    service = valid_report_case["service"]
    category_repository = valid_report_case["category_repository"]

    service.create_report(
        reporter=_make_reporter(),
        category_id="10",
        title="Titolo",
        description="Descrizione",
        latitude=45.0,
        longitude=7.0,
        photos=[_make_photo()],
    )

    category_repository.get_by_id.assert_called_once_with(10)