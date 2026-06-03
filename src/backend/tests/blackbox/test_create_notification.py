from __future__ import annotations

from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from participium.models.base import Base
from participium.models.category import Category
from participium.models.enums import NotificationType, ReportStatus, Role
from participium.models.notification import Notification
from participium.models.report import Report
from participium.models.user import User
from participium.repositories.notification_repository import NotificationRepository
from participium.services.notification_service import NotificationService


@pytest.fixture
def seed_notification_data():
    """
    Crea un DB SQLite in-memory con:
    - Categoria id=1  attiva
    - Utente id=1     (mario.rossi, email_notifications_enabled=False per evitare invio email)
    - Report id=1     associato all'utente e alla categoria
    Restituisce (service, user, report).
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        cat = Category(id=1, name="Viabilità", is_active=True)
        user = User(
            id=1,
            username="mario.rossi",
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            password_hash="hashed",
            role=Role.CITIZEN,
            is_active=True,
            is_email_verified=True,
            email_notifications_enabled=False,
        )
        report = Report(
            id=1,
            title="Buca in Via Roma",
            description="Grande buca pericolosa",
            latitude=45.0,
            longitude=9.0,
            status=ReportStatus.ASSIGNED,
            reporter_id=1,
            category_id=1,
        )
        session.add_all([cat, user, report])
        session.commit()

        service = NotificationService(
            session=session,
            notification_repository=NotificationRepository(session),
            email_gateway=Mock(),  # mock per evitare invio email reale
        )

        yield service, user, report


# Casi di successo: user valido con report

@pytest.mark.parametrize(
    "notification_type, title, body",
    [
        # CN1 – STATUS_CHANGE con report
        (NotificationType.STATUS_CHANGE, "Stato aggiornato", "Il report è stato assegnato"),
        # CN2 – MESSAGE con report
        (NotificationType.MESSAGE, "Nuovo messaggio", "Hai ricevuto un messaggio"),
        # CN3 – SYSTEM con report
        (NotificationType.SYSTEM, "Avviso di sistema", "Manutenzione programmata"),
    ],
)
def test_create_notification_with_report(
    seed_notification_data, notification_type, title, body,
) -> None:
    service, user, report = seed_notification_data

    result = service.create_notification(
        user=user,
        notification_type=notification_type,
        title=title,
        body=body,
        report=report,
    )

    assert isinstance(result, Notification)
    assert result.user_id == user.id
    assert result.report_id == report.id
    assert result.type == notification_type
    assert result.title == title
    assert result.body == body
    assert result.is_read is False



# Casi di successo: user valido senza report


@pytest.mark.parametrize(
    "notification_type, title, body",
    [
        # CN4 – STATUS_CHANGE senza report
        (NotificationType.STATUS_CHANGE, "Stato aggiornato", "Il report è stato risolto"),
        # CN5 – MESSAGE senza report
        (NotificationType.MESSAGE, "Nuovo messaggio", "Contenuto del messaggio"),
        # CN6 – SYSTEM senza report
        (NotificationType.SYSTEM, "Avviso di sistema", "Manutenzione programmata"),
    ],
)
def test_create_notification_no_report(
    seed_notification_data, notification_type, title, body,
) -> None:
    service, user, _report = seed_notification_data

    result = service.create_notification(
        user=user,
        notification_type=notification_type,
        title=title,
        body=body,
        report=None,
    )

    assert isinstance(result, Notification)
    assert result.user_id == user.id
    assert result.report_id is None
    assert result.type == notification_type



# Casi user=None → ritorna None


@pytest.mark.parametrize(
    "notification_type, title, body, use_report",
    [
        # CN7 – None, STATUS_CHANGE, con report
        (NotificationType.STATUS_CHANGE, "Stato aggiornato", "Il report è stato assegnato", True),
        # CN8 – None, MESSAGE, con report
        (NotificationType.MESSAGE, "Nuovo messaggio", "Hai ricevuto un messaggio", True),
        # CN9 – None, SYSTEM, senza report
        (NotificationType.SYSTEM, "Avviso di sistema", "Manutenzione programmata", False),
    ],
)
def test_create_notification_null_user(
    seed_notification_data, notification_type, title, body, use_report,
) -> None:
    service, _user, report = seed_notification_data

    result = service.create_notification(
        user=None,
        notification_type=notification_type,
        title=title,
        body=body,
        report=report if use_report else None,
    )

    assert result is None



# Boundary: stringhe vuote per titolo e corpo
# Il contratto non documenta eccezioni per stringhe vuote.

@pytest.mark.parametrize(
    "title, body",
    [
        # CNB1 – titolo vuoto
        ("", "Corpo valido"),
        # CNB2 – corpo vuoto
        ("Titolo valido", ""),
        # CNB3 – titolo e corpo vuoti
        ("", ""),
    ],
)
def test_create_notification_empty_strings(
    seed_notification_data, title, body,
) -> None:
    service, user, _report = seed_notification_data

    result = service.create_notification(
        user=user,
        notification_type=NotificationType.SYSTEM,
        title=title,
        body=body,
        report=None,
    )

    assert isinstance(result, Notification)
    assert result.title == title
    assert result.body == body