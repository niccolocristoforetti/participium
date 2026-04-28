from __future__ import annotations

import pytest

from unittest.mock import Mock
from participium.models.notification import Notification
from participium.services.notification_service import NotificationService


pytestmark = pytest.mark.whitebox


# Structural tests for NotificationService.count_unread_message_notifications_by_report
# belong here. The current runnable smoke check is kept in test_wb_task06_smoke.py.

def _notification(*, notification_id: int, user_id: int, report_id: int | None , is_read: bool = False) -> Notification:
    """
    Helper per creare istanze di notifica.
    """
    return Notification(
        id=notification_id,
        user_id=user_id,
        report_id=report_id,
        is_read=is_read,
    )


@pytest.fixture
def notification_service_bundle() -> dict[str, object]:
    """
    Inizializza il servizio mockando le sue dipendenze.
    """
    session = Mock()
    notification_repository = Mock()
    email_gateway = Mock()
    service = NotificationService(
        session=session,
        notification_repository=notification_repository,
        email_gateway=email_gateway,
    )
    return {
        "service": service,
        "session": session,
        "notification_repository": notification_repository,
    }


@pytest.fixture
def empty_notifications_case(notification_service_bundle: dict[str, object]) -> dict[str, object]:
    """Setup per T1 (L0): la repository restituisce una lista vuota."""
    notification_service_bundle["notification_repository"].list_unread_message_notifications.return_value = []
    return notification_service_bundle


@pytest.fixture
def single_notification_case(notification_service_bundle: dict[str, object]) -> dict[str, object]:
    """Setup per T2 (L1): la repository restituisce una notifica valida."""
    notification = _notification(notification_id=101, user_id=10, report_id=20)
    notification_service_bundle["notification_repository"].list_unread_message_notifications.return_value = [
        notification
    ]
    return notification_service_bundle


@pytest.fixture
def mixed_notifications_case(notification_service_bundle: dict[str, object]) -> dict[str, object]:
    """
    Setup per T3 (L2+): la repository restituisce due notifiche.
    La prima ha report_id=None (che innescherà il 'continue'),
    la seconda ha report_id=20 (valida).
    """
    notifications = [
        _notification(notification_id=201, user_id=10, report_id=None),
        _notification(notification_id=202, user_id=10, report_id=20),
    ]
    notification_service_bundle["notification_repository"].list_unread_message_notifications.return_value = (
        notifications
    )
    return notification_service_bundle


def test_count_unread_notifications_returns_empty_dict_without_matches(
    empty_notifications_case: dict[str, object],
) -> None:
    """Copre il Loop L0 (0 iterazioni)."""
    service: NotificationService = empty_notifications_case["service"]
    notification_repository: Mock = empty_notifications_case["notification_repository"]

    counts = service.count_unread_message_notifications_by_report(user_id=10)

    assert counts == {}
    notification_repository.list_unread_message_notifications.assert_called_once_with(user_id=10)


def test_count_unread_notifications_counts_single_notification(
    single_notification_case: dict[str, object],
) -> None:
    """Copre il Loop L1 (1 iterazione)."""
    service: NotificationService = single_notification_case["service"]
    notification_repository: Mock = single_notification_case["notification_repository"]

    counts = service.count_unread_message_notifications_by_report(user_id=10)

    # C'è una sola notifica con report_id 20
    assert counts == {20: 1}
    notification_repository.list_unread_message_notifications.assert_called_once_with(user_id=10)


def test_count_unread_notifications_skips_none_and_counts_valid(
    mixed_notifications_case: dict[str, object],
) -> None:
    """
    Copre Node, Edge, Condition e Path (approssimato).
    Copre il Loop L2+ con esecuzione di entrambi i rami interni (continue e assegnazione).
    """
    service: NotificationService = mixed_notifications_case["service"]
    notification_repository: Mock = mixed_notifications_case["notification_repository"]

    counts = service.count_unread_message_notifications_by_report(user_id=10)

    # La notifica con report_id=None viene saltata, conta solo quella con report_id=20
    assert counts == {20: 1}
    notification_repository.list_unread_message_notifications.assert_called_once_with(user_id=10)
