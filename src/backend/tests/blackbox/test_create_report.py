from __future__ import annotations

import pytest
from werkzeug.datastructures import FileStorage

from participium.core.exceptions import ValidationError
from participium.models.category import Category
from participium.models.enums import ReportStatus
from participium.models.user import User


VALID_PHOTO   = FileStorage(filename="buca_1.jpg")
VALID_PHOTO_2 = FileStorage(filename="buca_2.jpg")
VALID_PHOTO_3 = FileStorage(filename="buca_3.jpg")
VALID_PHOTO_4 = FileStorage(filename="buca_4.jpg")
INVALID_PHOTO = FileStorage(filename="")


@pytest.fixture
def seed_create_report_data(db_session):
    cat_active   = Category(name="Viabilità", is_active=True)
    cat_inactive = Category(name="Inattiva",  is_active=False)
    db_session.add(cat_active)
    db_session.add(cat_inactive)
    db_session.flush()
    # cat_active.id == 1, cat_inactive.id == 2 (SQLite autoincrement da 1)


VALID_REPORTER = User(id=1, username="mario.rossi", is_active=True)


@pytest.mark.parametrize(
    "category_id, title, description, latitude, longitude, photos, is_anonymous",
    [
        # CR1 – parametri nominali, int + float
        (1,   "Buca", "Descrizione", 45.0,   9.0,   [VALID_PHOTO], False),
        # CR2 – category_id e coordinate come stringhe convertibili
        ("1", "Buca", "Descrizione", "45.0", "9.0", [VALID_PHOTO], False),
        # CR3 – segnalazione anonima
        (1,   "Buca", "Descrizione", 45.0,   9.0,   [VALID_PHOTO], True),
        # CR4 – latitude come stringa, longitude come float
        (1,   "Buca", "Descrizione", "45.0", 9.0,   [VALID_PHOTO], False),
        # CR5 – latitude come float, longitude come stringa
        (1,   "Buca", "Descrizione", 45.0,   "9.0", [VALID_PHOTO], False),
        # CRB2 – esattamente 1 foto valida (minimo)
        (1, "Buca", "Descrizione", 45.0, 9.0, [VALID_PHOTO], False),
        # CRB3 – esattamente 3 foto valide (massimo)
        (1, "Buca", "Descrizione", 45.0, 9.0, [VALID_PHOTO, VALID_PHOTO_2, VALID_PHOTO_3], False),
        # CRB6 – 4 elementi ma solo 2 con filename
        (1, "Buca", "Descrizione", 45.0, 9.0, [VALID_PHOTO, VALID_PHOTO_2, INVALID_PHOTO, INVALID_PHOTO], False),
        # CRB12 – latitudine al minimo consentito (-90)
        (1, "Buca", "Descrizione", -90.0, 0.0, [VALID_PHOTO], False),
        # CRB14 – latitudine al massimo consentito (+90)
        (1, "Buca", "Descrizione",  90.0, 0.0, [VALID_PHOTO], False),
        # CRB16 – longitudine al minimo consentito (-180)
        (1, "Buca", "Descrizione", 0.0, -180.0, [VALID_PHOTO], False),
        # CRB18 – longitudine al massimo consentito (+180)
        (1, "Buca", "Descrizione", 0.0,  180.0, [VALID_PHOTO], False),
    ],
)
def test_create_report_success(
    seed_create_report_data,
    report_service,
    category_id,
    title,
    description,
    latitude,
    longitude,
    photos,
    is_anonymous,
) -> None:
    report = report_service.create_report(
        reporter=VALID_REPORTER,
        category_id=category_id,
        title=title,
        description=description,
        latitude=latitude,
        longitude=longitude,
        photos=photos,
        is_anonymous=is_anonymous,
    )

    from participium.models.report import Report
    assert isinstance(report, Report)
    assert report.is_anonymous == is_anonymous
    assert report.status == ReportStatus.PENDING_APPROVAL


@pytest.mark.parametrize(
    "category_id, title, description, latitude, longitude, photos, is_anonymous",
    [
        # CR6  – category_id mancante (None)
        (None,   "Buca", "Descrizione", 45.0, 9.0, [VALID_PHOTO], False),
        # CR7  – category_id malformato
        ("abc",  "Buca", "Descrizione", 45.0, 9.0, [VALID_PHOTO], False),
        # CR8  – category_id sconosciuto
        (9999,   "Buca", "Descrizione", 45.0, 9.0, [VALID_PHOTO], False),
        # CR9  – categoria inattiva (ID 2)
        (2,      "Buca", "Descrizione", 45.0, 9.0, [VALID_PHOTO], False),
        # CR10 – title None
        (1, None,   "Descrizione", 45.0, 9.0, [VALID_PHOTO], False),
        # CR11 – description None
        (1, "Buca", None,          45.0, 9.0, [VALID_PHOTO], False),
        # CR12 – latitude None
        (1, "Buca", "Descrizione", None,  9.0,  [VALID_PHOTO], False),
        # CR13 – longitude None
        (1, "Buca", "Descrizione", 45.0,  None, [VALID_PHOTO], False),
        # CR14 – latitude malformata
        (1, "Buca", "Descrizione", "abc", 9.0,  [VALID_PHOTO], False),
        # CR15 – longitude malformata
        (1, "Buca", "Descrizione", 45.0,  "abc",[VALID_PHOTO], False),
        # CR16 – unico FileStorage senza filename
        (1, "Buca", "Descrizione", 45.0, 9.0, [INVALID_PHOTO], False),
        # CRB1 – 0 foto valide
        (1, "Buca", "Descrizione", 45.0, 9.0, [INVALID_PHOTO, INVALID_PHOTO], False),
        # CRB4 – 4 foto tutte valide (oltre il massimo)
        (1, "Buca", "Descrizione", 45.0, 9.0, [VALID_PHOTO, VALID_PHOTO_2, VALID_PHOTO_3, VALID_PHOTO_4], False),
        # CRB5 – lista vuota
        (1, "Buca", "Descrizione", 45.0, 9.0, [], False),
        # CRB7  – title stringa vuota
        (1, "",     "Descrizione", 45.0, 9.0, [VALID_PHOTO], False),
        # CRB8  – description stringa vuota
        (1, "Buca", "",            45.0, 9.0, [VALID_PHOTO], False),
        # CRB9  – latitude stringa vuota
        (1, "Buca", "Descrizione", "",   9.0, [VALID_PHOTO], False),
        # CRB10 – longitude stringa vuota
        (1, "Buca", "Descrizione", 45.0, "",  [VALID_PHOTO], False),
        # CRB11 – category_id stringa vuota
        ("", "Buca", "Descrizione", 45.0, 9.0, [VALID_PHOTO], False),
    ],
)
def test_create_report_invalid(
    seed_create_report_data,
    report_service,
    category_id,
    title,
    description,
    latitude,
    longitude,
    photos,
    is_anonymous,
) -> None:
    with pytest.raises(ValidationError):
        report_service.create_report(
            reporter=VALID_REPORTER,
            category_id=category_id,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            photos=photos,
            is_anonymous=is_anonymous,
        )
