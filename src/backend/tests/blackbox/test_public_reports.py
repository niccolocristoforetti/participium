from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from participium.models.base import Base
from participium.models.category import Category
from participium.models.enums import ReportStatus, Role
from participium.models.report import Report
from participium.models.user import User
from participium.repositories.category_repository import CategoryRepository
from participium.repositories.report_repository import ReportRepository
from participium.services.report_service import ReportService


@pytest.fixture
def seed_public_reports_data():
    """
    Crea un DB SQLite in-memory e lo popola con un dataset per i report pubblici.
    Risolve il vincolo NOT NULL inserendo coordinate  valide.
    - Utente reporter (id=1) per soddisfare i vincoli di integrità referenziale
    - Categoria 1 (Attiva) e Categoria 2 (Attiva)
    - Report 1: Categoria 1, Status ASSIGNED, Data: 2024-06-01
    - Report 2: Categoria 2, Status IN_PROGRESS, Data: 2024-01-01
    - Report 3: Categoria 1, Status RESOLVED, Data: 2024-12-31
    Restituisce il ReportService pronto all'uso e chiude la sessione alla fine di ogni test.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # 1. Creazione dell'utente di supporto per evitare violazioni di Foreign Key (reporter_id)
        reporter = User(
            id=1,
            username="test.user",
            first_name="Test",
            last_name="User",
            email="test.user@example.com",
            password_hash="hashed",
            role=Role.CITIZEN,
            is_active=True,
            is_email_verified=True,
        )
        session.add(reporter)

        # 2. Creazione delle categorie
        session.add_all([
            Category(id=1, name="Categoria1", is_active=True),
            Category(id=2, name="Categoria2", is_active=True),
        ])
        session.flush()

        # 3. Creazione dei report con coordinate obbligatorie (latitude, longitude) valorizzate
        session.add_all([
            # R1: Cat 1, Assigned, 2024-06-01
            Report(
                id=1, 
                category_id=1, 
                reporter_id=1,
                status=ReportStatus.ASSIGNED, 
                created_at=datetime(2024, 6, 1),
                latitude=45.0,
                longitude=9.0,
                is_anonymous=False,
                title="Buca", description="Desc"
            ),
            # R2: Cat 2, In Progress, 2024-01-01
            Report(
                id=2, 
                category_id=2, 
                reporter_id=1,
                status=ReportStatus.IN_PROGRESS, 
                created_at=datetime(2024, 1, 1),
                latitude=45.1,
                longitude=9.1,
                is_anonymous=False,
                title="Ramo caduto", description="Desc"
            ),
            # R3: Cat 1, Resolved, 2024-12-31
            Report(
                id=3, 
                category_id=1, 
                reporter_id=1,
                status=ReportStatus.RESOLVED, 
                created_at=datetime(2024, 12, 31),
                latitude=45.2,
                longitude=9.2,
                is_anonymous=False,
                title="Semaforo rotto", description="Desc"
            ),
        ])
        session.commit()

        yield ReportService(
            session=session,
            report_repository=ReportRepository(session),
            category_repository=CategoryRepository(session),
            storage_service=None,
        )
        
        # Pulisce esplicitamente la sessione per prevenire i ResourceWarning dei thread di sqlite
        session.close()


@pytest.mark.parametrize(
    "category_id, status, date_from, date_to, sort, expected_ids, expected_length",
    [
        # PR1 – parametri nominali: tutti i report pubblici ordinati desc (R3 -> R1 -> R2)
        (None, None, None, None, "desc", [3, 1, 2], 3),
        
        # PR2 – category_id invalido/non esistente -> lista vuota
        (9999, None, None, None, "desc", [], 0),
        
        # PR3 – status invalido -> lista vuota
        (None, "Stato invalido", None, None, "desc", [], 0),
        
        # PR4 – date_from invalido -> lista vuota
        (None, None, "data invalida", None, "desc", [], 0),
        
        # PR5 – date_to invalido 
        # xfail: Il backend non valida la stringa malformata per date_to, ignorandola e restituendo 3 elementi invece di 0.
        pytest.param(None, None, None, "data invalida", "desc", [], 0,
                     marks=pytest.mark.xfail(strict=True, reason="Il service ignora sileniziosamente il date_to non valido invece di filtrare vuoto")),
        
        # PR6 – sort invalido o None -> ricade sul comportamento di default (desc)
        (None, None, None, None, "invalid", [3, 1, 2], 3),
        (None, None, None, None, None, [3, 1, 2], 3),
        
        # PR7 – status valido (Assigned) -> trova solo R1
        (None, ReportStatus.ASSIGNED, None, None, "desc", [1], 1),
        
        # --- Boundary: ordinamento e logica delle date ---
        # PRB8 – date_from e date_to coincidenti -> trova solo R1 (created_at == 2024-06-01)
        (None, None, datetime(2024, 6, 1), datetime(2024, 6, 1), "desc", [1], 1),
        
        # PRB9 – date_to precedente a date_from -> lista vuota
        (None, None, datetime(2024, 6, 1), datetime(2024, 5, 31), "desc", [], 0),
        
        # Caso aggiuntivo di controllo per l'ordinamento "asc" (R2 -> R1 -> R3)
        (None, None, None, None, "asc", [2, 1, 3], 3),
    ],
)
def test_list_public_reports(
    seed_public_reports_data: ReportService,
    category_id,
    status,
    date_from,
    date_to,
    sort,
    expected_ids: list[int],
    expected_length: int,
) -> None:
    report_service = seed_public_reports_data

    
    result = report_service.list_public_reports(
        category_id=category_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        sort=sort,
    )

    
    assert isinstance(result, list)
    assert len(result) == expected_length

    
    actual_ids = [r.id for r in result]
    assert actual_ids == expected_ids