from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from werkzeug.datastructures import FileStorage

from participium.core.exceptions import ValidationError
from participium.models.base import Base
from participium.models.category import Category
from participium.models.enums import Role
from participium.models.report import Report, ReportFollower, ReportPhoto, ReportStatusHistory  # noqa: F401
from participium.models.user import User
from participium.repositories.category_repository import CategoryRepository
from participium.repositories.report_repository import ReportRepository
from participium.services.report_service import ReportService
from participium.services.storage_service import StorageService


# --- foto per i test ---
VALID_PHOTO   = FileStorage(filename="buca_1.jpg")
VALID_PHOTO_2 = FileStorage(filename="buca_2.jpg")
VALID_PHOTO_3 = FileStorage(filename="buca_3.jpg")
VALID_PHOTO_4 = FileStorage(filename="buca_4.jpg")
INVALID_PHOTO = FileStorage(filename="")


@pytest.fixture
def seed_create_report_data():
    """
    Crea un DB SQLite in-memory con:
    - Utente reporter  (id=1)
    - Categoria id=1   attiva
    - Categoria id=2   inattiva
    Restituisce un ReportService pronto all'uso.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all([
            Category(id=1, name="Viabilità",  is_active=True),
            Category(id=2, name="Archiviata", is_active=False),
            User(
                id=1,
                username="mario.rossi",
                first_name="Mario",
                last_name="Rossi",
                email="mario.rossi@example.com",
                password_hash="hashed",
                role=Role.CITIZEN,
                is_active=True,
                is_email_verified=True,
            ),
        ])
        session.commit()

        yield ReportService(
            session=session,
            report_repository=ReportRepository(session),
            category_repository=CategoryRepository(session),
            storage_service=StorageService(),
        )


# reporter da passare a create_report (stesso id del DB)
VALID_REPORTER = User(
    id=1,
    username="mario.rossi",
    first_name="Mario",
    last_name="Rossi",
    email="mario.rossi@example.com",
    password_hash="hashed",
    role=Role.CITIZEN,
    is_active=True,
    is_email_verified=True,
)


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

        # --- Boundary: numero di foto valide ---
        # CRB2 – esattamente 1 foto valida (minimo)
        (1, "Buca", "Descrizione", 45.0, 9.0, [VALID_PHOTO], False),
        # CRB3 – esattamente 3 foto valide (massimo)
        (1, "Buca", "Descrizione", 45.0, 9.0,
         [VALID_PHOTO, VALID_PHOTO_2, VALID_PHOTO_3], False),
        # CRB6 – 4 elementi ma solo 2 con filename → 2 foto valide, entro i limiti
        (1, "Buca", "Descrizione", 45.0, 9.0,
         [VALID_PHOTO, VALID_PHOTO_2, INVALID_PHOTO, INVALID_PHOTO], False),

        # --- Boundary: limiti geografici ---
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
    seed_create_report_data: ReportService,
    category_id,
    title,
    description,
    latitude,
    longitude,
    photos,
    is_anonymous,
) -> None:
    report_service = seed_create_report_data

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

    assert isinstance(report, Report)
    assert report.is_anonymous == is_anonymous


@pytest.mark.parametrize(
    "category_id, title, description, latitude, longitude, photos, is_anonymous",
    [
        # --- Casi base: category_id non valido ---
        # CR6  – category_id mancante (None)
        (None,   "Buca", "Descrizione", 45.0, 9.0, [VALID_PHOTO], False),
        # CR7  – category_id malformato (stringa non numerica)
        ("abc",  "Buca", "Descrizione", 45.0, 9.0, [VALID_PHOTO], False),
        # CR8  – category_id sconosciuto
        (9999,   "Buca", "Descrizione", 45.0, 9.0, [VALID_PHOTO], False),
        # CR9  – categoria inattiva (ID 2)
        (2,      "Buca", "Descrizione", 45.0, 9.0, [VALID_PHOTO], False),

        # --- Casi base: title / description mancanti ---
        # CR10 – title None
        (1, None,   "Descrizione", 45.0, 9.0, [VALID_PHOTO], False),
        # CR11 – description None
        (1, "Buca", None,          45.0, 9.0, [VALID_PHOTO], False),

        # --- Casi base: coordinate mancanti o malformate ---
        # CR12 – latitude None
        (1, "Buca", "Descrizione", None,  9.0,  [VALID_PHOTO], False),
        # CR13 – longitude None
        (1, "Buca", "Descrizione", 45.0,  None, [VALID_PHOTO], False),
        # CR14 – latitude malformata ("abc")
        (1, "Buca", "Descrizione", "abc", 9.0,  [VALID_PHOTO], False),
        # CR15 – longitude malformata ("abc")
        (1, "Buca", "Descrizione", 45.0,  "abc",[VALID_PHOTO], False),

        # --- Casi base: foto non valide ---
        # CR16 – unico FileStorage senza filename
        (1, "Buca", "Descrizione", 45.0, 9.0, [INVALID_PHOTO], False),

        # --- Boundary: numero di foto valide ---
        # CRB1 – 2 elementi entrambi senza filename → 0 foto valide
        (1, "Buca", "Descrizione", 45.0, 9.0,
         [INVALID_PHOTO, INVALID_PHOTO], False),
        # CRB4 – 4 foto tutte valide (oltre il massimo di 3)
        (1, "Buca", "Descrizione", 45.0, 9.0,
         [VALID_PHOTO, VALID_PHOTO_2, VALID_PHOTO_3, VALID_PHOTO_4], False),
        # CRB5 – lista vuota (0 foto)
        (1, "Buca", "Descrizione", 45.0, 9.0, [], False),

        # --- Boundary: campi testo vuoti ---
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

        # --- Boundary: limiti geografici superati ---
        # xfail: il service non valida i boundary geografici, la ValidationError non viene sollevata
        # CRB13 – latitudine sotto il minimo (-90.1)
        pytest.param(1, "Buca", "Descrizione", -90.1, 0.0,  [VALID_PHOTO], False,
                     marks=pytest.mark.xfail(strict=True, reason="boundary geografico non validato dal service")),
        # CRB15 – latitudine sopra il massimo (90.1)
        pytest.param(1, "Buca", "Descrizione",  90.1, 0.0,  [VALID_PHOTO], False,
                     marks=pytest.mark.xfail(strict=True, reason="boundary geografico non validato dal service")),
        # CRB17 – longitudine sotto il minimo (-180.1)
        pytest.param(1, "Buca", "Descrizione", 0.0, -180.1, [VALID_PHOTO], False,
                     marks=pytest.mark.xfail(strict=True, reason="boundary geografico non validato dal service")),
        # CRB19 – longitudine sopra il massimo (180.1)
        pytest.param(1, "Buca", "Descrizione", 0.0,  180.1, [VALID_PHOTO], False,
                     marks=pytest.mark.xfail(strict=True, reason="boundary geografico non validato dal service")),
    ],
)
def test_create_report_invalid(
    seed_create_report_data: ReportService,
    category_id,
    title,
    description,
    latitude,
    longitude,
    photos,
    is_anonymous,
) -> None:
    report_service = seed_create_report_data

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