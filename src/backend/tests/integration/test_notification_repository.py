"""
Test di integrazione per NotificationRepository.

Copertura al 100% dei metodi pubblici:
  - add()
  - get_by_id()
  - list_for_user()
  - list_unread_message_notifications()  — branch con e senza report_id
  - delete_for_user()

La fixture notification_repository è definita in conftest.py e non viene
ridefinita qui per evitare duplicazione.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from participium.models.enums import NotificationType
from participium.models.notification import Notification


@pytest.mark.integration
def test_add_and_get_by_id_found(notification_repository, db_session):
    """add() persiste la notifica; get_by_id() la recupera correttamente."""
    # Arrange
    new_notification = Notification(
        user_id=1,
        type=NotificationType.SYSTEM,
        title="Test",
        body="Body",
    )

    # Act
    added = notification_repository.add(new_notification)
    db_session.commit()

    # Assert
    fetched = notification_repository.get_by_id(added.id)
    assert fetched is not None
    assert fetched.title == "Test"
    assert fetched.body == "Body"
    assert fetched.user_id == 1
    assert fetched.is_read is False  # default


@pytest.mark.integration
def test_get_by_id_returns_none_when_not_found(notification_repository):
    """get_by_id() restituisce None per un id inesistente."""
    assert notification_repository.get_by_id(999) is None


@pytest.mark.integration
def test_list_for_user_orders_by_created_at_desc(notification_repository, db_session):
    """list_for_user() ordina le notifiche dalla più recente alla più vecchia."""
    # Arrange: created_at espliciti per ordine deterministico
    now = datetime.now()
    n_old = Notification(
        user_id=2, type=NotificationType.SYSTEM,
        title="Old", body="...", created_at=now - timedelta(days=2),
    )
    n_new = Notification(
        user_id=2, type=NotificationType.SYSTEM,
        title="New", body="...", created_at=now,
    )

    # Inseriamo intenzionalmente prima il più recente per verificare che
    # sia l'ORDER BY e non l'ordine di inserimento a determinare il risultato.
    notification_repository.add(n_new)
    notification_repository.add(n_old)
    db_session.commit()

    # Act
    notifications = notification_repository.list_for_user(2)

    # Assert
    assert len(notifications) == 2
    assert notifications[0].title == "New"
    assert notifications[1].title == "Old"


@pytest.mark.integration
def test_list_for_user_returns_empty_list_for_unknown_user(notification_repository):
    """list_for_user() restituisce una lista vuota per un utente senza notifiche."""
    assert notification_repository.list_for_user(999) == []


@pytest.mark.integration
def test_list_unread_message_notifications_excludes_read(notification_repository, db_session):
    """list_unread_message_notifications() senza report_id esclude le notifiche lette."""
    # Arrange
    n_unread = Notification(user_id=1, type=NotificationType.MESSAGE, title="U", body="B", is_read=False)
    n_read   = Notification(user_id=1, type=NotificationType.MESSAGE, title="R", body="B", is_read=True)

    notification_repository.add(n_unread)
    notification_repository.add(n_read)
    db_session.commit()

    # Act
    results = notification_repository.list_unread_message_notifications(user_id=1)

    # Assert: solo quella non letta
    assert len(results) == 1
    assert results[0].id == n_unread.id
    assert results[0].is_read is False


@pytest.mark.integration
def test_list_unread_message_notifications_excludes_other_types(notification_repository, db_session):
    """list_unread_message_notifications() non restituisce notifiche di tipo != MESSAGE."""
    # Arrange
    n_msg    = Notification(user_id=3, type=NotificationType.MESSAGE, title="M", body="B", is_read=False)
    n_system = Notification(user_id=3, type=NotificationType.SYSTEM,  title="S", body="B", is_read=False)

    notification_repository.add(n_msg)
    notification_repository.add(n_system)
    db_session.commit()

    # Act
    results = notification_repository.list_unread_message_notifications(user_id=3)

    # Assert: solo quella di tipo MESSAGE
    assert len(results) == 1
    assert results[0].type == NotificationType.MESSAGE


@pytest.mark.integration
def test_list_unread_message_notifications_filters_by_report_id(notification_repository, db_session):
    """list_unread_message_notifications() con report_id filtra per quel report."""
    # Arrange
    n_report_10 = Notification(user_id=1, report_id=10, type=NotificationType.MESSAGE, title="T", body="B", is_read=False)
    n_report_20 = Notification(user_id=1, report_id=20, type=NotificationType.MESSAGE, title="T", body="B", is_read=False)

    notification_repository.add(n_report_10)
    notification_repository.add(n_report_20)
    db_session.commit()

    # Act
    results = notification_repository.list_unread_message_notifications(user_id=1, report_id=10)

    # Assert: solo quella con report_id=10
    assert len(results) == 1
    assert results[0].report_id == 10


@pytest.mark.integration
def test_delete_for_user_removes_only_that_users_notifications(notification_repository, db_session):
    """delete_for_user() elimina tutte le notifiche dell'utente specificato
    senza toccare quelle degli altri utenti."""
    # Arrange
    n_user5  = Notification(user_id=5, type=NotificationType.SYSTEM, title="T", body="B")
    n_user6  = Notification(user_id=6, type=NotificationType.SYSTEM, title="T", body="B")

    notification_repository.add(n_user5)
    notification_repository.add(n_user6)
    db_session.commit()

    # Salviamo l'id dell'utente 6 prima del commit per verificarlo dopo la delete
    id_user6 = n_user6.id

    # Act
    notification_repository.delete_for_user(5)
    db_session.commit()

    # Assert: utente 5 non ha più notifiche
    assert notification_repository.list_for_user(5) == []

    # Assert: la notifica dell'utente 6 è intatta e recuperabile tramite get_by_id
    assert notification_repository.get_by_id(id_user6) is not None
    assert len(notification_repository.list_for_user(6)) == 1