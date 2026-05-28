from __future__ import annotations

from unittest.mock import Mock
import pytest

from participium.models.notification import Notification
from participium.services.notification_service import NotificationService


pytestmark = pytest.mark.whitebox



#  Helpers 


# Helper 

# crea istanze di notifica con parametri personalizzati.
def _notification(*, notification_id: int, user_id: int, report_id: int | None, is_read: bool = False) -> Notification:
    return Notification(
        id=notification_id,
        user_id=user_id,
        report_id=report_id,
        is_read=is_read,
    )



#  Fixtures 


# Inizializza il servizio mockando le sue dipendenze per l'isolamento dei test.
@pytest.fixture
def notification_service_bundle() -> dict[str, object]:
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


# caso limite vuoto: la repository restituisce una lista vuota di notifiche.
@pytest.fixture
def empty_notifications_case(notification_service_bundle: dict[str, object]) -> dict[str, object]:
    notification_service_bundle["notification_repository"].list_unread_message_notifications.return_value = []
    return notification_service_bundle


#  scenario base: la repository restituisce una singola notifica valida associata a un report.
@pytest.fixture
def single_notification_case(notification_service_bundle: dict[str, object]) -> dict[str, object]:
    notification = _notification(notification_id=101, user_id=10, report_id=20)
    notification_service_bundle["notification_repository"].list_unread_message_notifications.return_value = [
        notification
    ]
    return notification_service_bundle


#  scenario misto: la repository restituisce più notifiche, incluse alcune da scartare.
@pytest.fixture
def mixed_notifications_case(notification_service_bundle: dict[str, object]) -> dict[str, object]:
    notifications = [
        _notification(notification_id=201, user_id=10, report_id=None),
        _notification(notification_id=202, user_id=10, report_id=20),
        _notification(notification_id=203, user_id=10, report_id=20),
        _notification(notification_id=204, user_id=10, report_id=30),
    ]
    notification_service_bundle["notification_repository"].list_unread_message_notifications.return_value = notifications
    return notification_service_bundle



# --- Casi di Test ---


# NCB1 – Caso limite ciclo vuoto: verifica che con zero notifiche venga restituito un dizionario vuoto.
def test_ncb1_count_unread_notifications_returns_empty_dict_without_matches(
    empty_notifications_case: dict[str, object],
) -> None:
    service: NotificationService = empty_notifications_case["service"]
    notification_repository: Mock = empty_notifications_case["notification_repository"]

    counts = service.count_unread_message_notifications_by_report(user_id=10)

    assert counts == {}
    notification_repository.list_unread_message_notifications.assert_called_once_with(user_id=10)


# NC1 – Caso base singolo: verifica il corretto conteggio quando è presente una sola notifica valida (1 iterazione).
def test_nc1_count_unread_notifications_counts_single_notification(
    single_notification_case: dict[str, object],
) -> None:
    service: NotificationService = single_notification_case["service"]
    notification_repository: Mock = single_notification_case["notification_repository"]

    counts = service.count_unread_message_notifications_by_report(user_id=10)

    assert counts == {20: 1}
    notification_repository.list_unread_message_notifications.assert_called_once_with(user_id=10)


# NC2 – Flusso logico e rami interni: verifica che le notifiche con report_id pari a None vengano ignorate e che le restanti siano sommate correttamente.
def test_nc2_count_unread_notifications_skips_none_and_counts_valid(
    mixed_notifications_case: dict[str, object],
) -> None:
    service: NotificationService = mixed_notifications_case["service"]
    notification_repository: Mock = mixed_notifications_case["notification_repository"]

    counts = service.count_unread_message_notifications_by_report(user_id=10)

    assert counts == {20: 2, 30: 1}
    notification_repository.list_unread_message_notifications.assert_called_once_with(user_id=10)