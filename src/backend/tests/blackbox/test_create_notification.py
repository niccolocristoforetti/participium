from __future__ import annotations

import pytest

from participium.models.enums import NotificationType, ReportStatus
from participium.models.notification import Notification
from participium.models.report import Report
from participium.models.user import User
from participium.services.notification_service import NotificationService


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

VALID_USER = User(id=201, username="mario.rossi", is_active=True, is_email_verified=True)

VALID_REPORT = Report(
    id=301,
    title="Buca in Via Roma",
    status=ReportStatus.ASSIGNED,
    reporter_id=VALID_USER.id,
    category_id=1,
)


@pytest.fixture
def seed_notification_data() -> None:
    # Popola il sistema con i prerequisiti di `create_notification`.
    #
    # Dataset suggerito:
    # - `VALID_USER` persistito e attivo (id=201)
    # - `VALID_REPORT` persistito (id=301, reporter_id=201)
    pass


# ---------------------------------------------------------------------------
# CN1 – STATUS_CHANGE con report valido
# EC covered: EC1 × EC3 × EC6
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_cn1_status_change_with_report(seed_notification_data: None) -> None:
    service = NotificationService()

    result = service.create_notification(
        user=VALID_USER,
        notification_type=NotificationType.STATUS_CHANGE,
        title="Stato aggiornato",
        body="Il report è stato assegnato",
        report=VALID_REPORT,
    )

    assert isinstance(result, Notification)
    assert result.user_id == VALID_USER.id
    assert result.report_id == VALID_REPORT.id
    assert result.type == NotificationType.STATUS_CHANGE
    assert result.title == "Stato aggiornato"
    assert result.body == "Il report è stato assegnato"
    assert result.is_read is False


# ---------------------------------------------------------------------------
# CN2 – MESSAGE con report valido
# EC covered: EC1 × EC4 × EC6
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_cn2_message_with_report(seed_notification_data: None) -> None:
    service = NotificationService()

    result = service.create_notification(
        user=VALID_USER,
        notification_type=NotificationType.MESSAGE,
        title="Nuovo messaggio",
        body="Hai ricevuto un messaggio",
        report=VALID_REPORT,
    )

    assert isinstance(result, Notification)
    assert result.type == NotificationType.MESSAGE
    assert result.report_id == VALID_REPORT.id


# ---------------------------------------------------------------------------
# CN3 – SYSTEM con report valido
# EC covered: EC1 × EC5 × EC6
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_cn3_system_with_report(seed_notification_data: None) -> None:
    service = NotificationService()

    result = service.create_notification(
        user=VALID_USER,
        notification_type=NotificationType.SYSTEM,
        title="Avviso di sistema",
        body="Manutenzione programmata",
        report=VALID_REPORT,
    )

    assert isinstance(result, Notification)
    assert result.type == NotificationType.SYSTEM
    assert result.report_id == VALID_REPORT.id


# ---------------------------------------------------------------------------
# CN4 – STATUS_CHANGE senza report
# EC covered: EC1 × EC3 × EC7
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_cn4_status_change_no_report(seed_notification_data: None) -> None:
    service = NotificationService()

    result = service.create_notification(
        user=VALID_USER,
        notification_type=NotificationType.STATUS_CHANGE,
        title="Stato aggiornato",
        body="Il report è stato risolto",
        report=None,
    )

    assert isinstance(result, Notification)
    assert result.user_id == VALID_USER.id
    assert result.report_id is None
    assert result.type == NotificationType.STATUS_CHANGE


# ---------------------------------------------------------------------------
# CN5 – MESSAGE senza report
# EC covered: EC1 × EC4 × EC7
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_cn5_message_no_report(seed_notification_data: None) -> None:
    service = NotificationService()

    result = service.create_notification(
        user=VALID_USER,
        notification_type=NotificationType.MESSAGE,
        title="Nuovo messaggio",
        body="Contenuto del messaggio",
        report=None,
    )

    assert isinstance(result, Notification)
    assert result.type == NotificationType.MESSAGE
    assert result.report_id is None


# ---------------------------------------------------------------------------
# CN6 – SYSTEM senza report
# EC covered: EC1 × EC5 × EC7
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_cn6_system_no_report(seed_notification_data: None) -> None:
    service = NotificationService()

    result = service.create_notification(
        user=VALID_USER,
        notification_type=NotificationType.SYSTEM,
        title="Avviso di sistema",
        body="Manutenzione programmata",
        report=None,
    )

    assert isinstance(result, Notification)
    assert result.type == NotificationType.SYSTEM
    assert result.user_id == VALID_USER.id
    assert result.report_id is None


# ---------------------------------------------------------------------------
# CN7 – user=None, STATUS_CHANGE con report → None
# EC covered: EC2 × EC3 × EC6
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_cn7_null_user_status_change(seed_notification_data: None) -> None:
    service = NotificationService()

    result = service.create_notification(
        user=None,
        notification_type=NotificationType.STATUS_CHANGE,
        title="Stato aggiornato",
        body="Il report è stato assegnato",
        report=VALID_REPORT,
    )

    assert result is None


# ---------------------------------------------------------------------------
# CN8 – user=None, MESSAGE con report → None
# EC covered: EC2 × EC4 × EC6
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_cn8_null_user_message(seed_notification_data: None) -> None:
    service = NotificationService()

    result = service.create_notification(
        user=None,
        notification_type=NotificationType.MESSAGE,
        title="Nuovo messaggio",
        body="Hai ricevuto un messaggio",
        report=VALID_REPORT,
    )

    assert result is None


# ---------------------------------------------------------------------------
# CN9 – user=None, SYSTEM senza report → None
# EC covered: EC2 × EC5 × EC7
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_cn9_null_user_system(seed_notification_data: None) -> None:
    service = NotificationService()

    result = service.create_notification(
        user=None,
        notification_type=NotificationType.SYSTEM,
        title="Avviso di sistema",
        body="Manutenzione programmata",
        report=None,
    )

    assert result is None


# ---------------------------------------------------------------------------
# Boundary: stringhe vuote per titolo e corpo
# Il contratto non documenta eccezioni per stringhe vuote.
# ---------------------------------------------------------------------------

# CNB1 – Titolo vuoto
# EC covered: EC1 × EC5 × EC7
@pytest.mark.skip(reason="Disabled.")
def test_cnb1_empty_title(seed_notification_data: None) -> None:
    service = NotificationService()

    result = service.create_notification(
        user=VALID_USER,
        notification_type=NotificationType.SYSTEM,
        title="",
        body="Corpo valido",
        report=None,
    )

    assert isinstance(result, Notification)
    assert result.title == ""


# CNB2 – Corpo vuoto
# EC covered: EC1 × EC5 × EC7
@pytest.mark.skip(reason="Disabled.")
def test_cnb2_empty_body(seed_notification_data: None) -> None:
    service = NotificationService()

    result = service.create_notification(
        user=VALID_USER,
        notification_type=NotificationType.SYSTEM,
        title="Titolo valido",
        body="",
        report=None,
    )

    assert isinstance(result, Notification)
    assert result.body == ""


# CNB3 – Titolo e corpo vuoti
# EC covered: EC1 × EC5 × EC7
@pytest.mark.skip(reason="Disabled.")
def test_cnb3_empty_title_and_body(seed_notification_data: None) -> None:
    service = NotificationService()

    result = service.create_notification(
        user=VALID_USER,
        notification_type=NotificationType.SYSTEM,
        title="",
        body="",
        report=None,
    )

    assert isinstance(result, Notification)
    assert result.title == ""
    assert result.body == ""
