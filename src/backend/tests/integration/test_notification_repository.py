"""
Test di integrazione per NotificationRepository.

Copertura al 100% dei metodi pubblici:
  - add()
  - get_by_id()
  - list_for_user()
  - list_unread_message_notifications()  — branch con e senza report_id
  - delete_for_user()                    — branch lista piena e lista vuota

La fixture ``notification_repository`` è definita in conftest.py.
SQLite in memoria non applica i vincoli FK di default: user_id e report_id
fittizi sono accettati senza errori.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from participium.models.enums import NotificationType
from participium.models.notification import Notification


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_notification(user_id: int, **kwargs) -> Notification:
    """Factory che produce una Notification con valori di default sensati."""
    defaults = dict(
        type=NotificationType.SYSTEM,
        title="Default title",
        body="Default body",
    )
    defaults.update(kwargs)
    return Notification(user_id=user_id, **defaults)


# ---------------------------------------------------------------------------
# add()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_add_assigns_primary_key(notification_repository, db_session):
    """add() persiste la notifica: dopo il commit l'id è valorizzato."""
    n = _make_notification(user_id=1)

    notification_repository.add(n)
    db_session.commit()

    assert n.id is not None


@pytest.mark.integration
def test_add_returns_the_notification_object(notification_repository, db_session):
    """add() restituisce l'oggetto notifica (il type hint dice None, ma il codice fa return)."""
    n = _make_notification(user_id=1)

    result = notification_repository.add(n)
    db_session.commit()

    # Il metodo esegue ``return notification`` nonostante l'annotazione sia None.
    # Il test documenta il comportamento reale dell'implementazione.
    assert result is n


@pytest.mark.integration
def test_add_persists_all_fields(notification_repository, db_session):
    """add() salva correttamente type, title, body, report_id e il default is_read=False."""
    n = _make_notification(
        user_id=5,
        type=NotificationType.MESSAGE,
        title="Titolo specifico",
        body="Corpo specifico",
        report_id=99,
    )

    notification_repository.add(n)
    db_session.commit()
    db_session.expire(n)

    assert n.type == NotificationType.MESSAGE
    assert n.title == "Titolo specifico"
    assert n.body == "Corpo specifico"
    assert n.report_id == 99
    assert n.is_read is False


# ---------------------------------------------------------------------------
# get_by_id()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_get_by_id_returns_correct_notification(notification_repository, db_session):
    """get_by_id() recupera la notifica con l'id corretto."""
    n = _make_notification(user_id=2, title="Specific", body="Body")

    notification_repository.add(n)
    db_session.commit()

    fetched = notification_repository.get_by_id(n.id)

    assert fetched is not None
    assert fetched.title == "Specific"
    assert fetched.user_id == 2


@pytest.mark.integration
def test_get_by_id_returns_none_for_unknown_id(notification_repository):
    """get_by_id() restituisce None per un id inesistente."""
    assert notification_repository.get_by_id(99999) is None


# ---------------------------------------------------------------------------
# list_for_user()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_list_for_user_returns_only_that_users_notifications(notification_repository, db_session):
    """list_for_user() non include notifiche di altri utenti."""
    notification_repository.add(_make_notification(user_id=10, title="User10"))
    notification_repository.add(_make_notification(user_id=11, title="User11"))
    db_session.commit()

    results = notification_repository.list_for_user(10)

    assert len(results) == 1
    assert results[0].user_id == 10


@pytest.mark.integration
def test_list_for_user_orders_by_created_at_desc(notification_repository, db_session):
    """list_for_user() ordina dalla notifica più recente alla più vecchia (DESC).

    I messaggi vengono inseriti in ordine inverso per verificare che sia
    l'ORDER BY e non l'ordine di inserimento a determinare il risultato.
    """
    now = datetime.now()
    n_old = _make_notification(user_id=3, title="Old", created_at=now - timedelta(days=2))
    n_new = _make_notification(user_id=3, title="New", created_at=now)

    # Inserimento: prima il più recente, poi il più vecchio
    notification_repository.add(n_new)
    notification_repository.add(n_old)
    db_session.commit()

    results = notification_repository.list_for_user(3)

    assert len(results) == 2
    assert results[0].title == "New"
    assert results[1].title == "Old"


@pytest.mark.integration
def test_list_for_user_returns_empty_list_for_user_without_notifications(notification_repository):
    """list_for_user() restituisce una lista vuota per un utente senza notifiche."""
    assert notification_repository.list_for_user(99999) == []


# ---------------------------------------------------------------------------
# list_unread_message_notifications()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_list_unread_message_notifications_excludes_read(notification_repository, db_session):
    """Esclude le notifiche di tipo MESSAGE già lette."""
    notification_repository.add(_make_notification(
        user_id=1, type=NotificationType.MESSAGE, title="Unread", is_read=False,
    ))
    notification_repository.add(_make_notification(
        user_id=1, type=NotificationType.MESSAGE, title="Read", is_read=True,
    ))
    db_session.commit()

    results = notification_repository.list_unread_message_notifications(user_id=1)

    assert len(results) == 1
    assert results[0].title == "Unread"
    assert results[0].is_read is False


@pytest.mark.integration
def test_list_unread_message_notifications_excludes_non_message_types(notification_repository, db_session):
    """Esclude notifiche non lette di tipo diverso da MESSAGE."""
    notification_repository.add(_make_notification(
        user_id=2, type=NotificationType.MESSAGE, title="Msg", is_read=False,
    ))
    notification_repository.add(_make_notification(
        user_id=2, type=NotificationType.SYSTEM, title="Sys", is_read=False,
    ))
    notification_repository.add(_make_notification(
        user_id=2, type=NotificationType.STATUS_CHANGE, title="StatusChg", is_read=False,
    ))
    db_session.commit()

    results = notification_repository.list_unread_message_notifications(user_id=2)

    assert len(results) == 1
    assert results[0].type == NotificationType.MESSAGE


@pytest.mark.integration
def test_list_unread_message_notifications_with_and_without_report_id(
    notification_repository, db_session
):
    """Verifica entrambi i branch: senza report_id restituisce tutto, con report_id filtra.

    Un unico test che copre le due varianti mettendo in evidenza la differenza
    di comportamento senza duplicare il setup.
    """
    for rid in [10, 20, 30]:
        notification_repository.add(_make_notification(
            user_id=4, type=NotificationType.MESSAGE, title=f"R{rid}", report_id=rid, is_read=False,
        ))
    db_session.commit()

    # Branch senza report_id: restituisce tutte e 3 le notifiche non lette
    all_results = notification_repository.list_unread_message_notifications(user_id=4)
    assert len(all_results) == 3

    # Branch con report_id: filtra al solo report_id=10
    filtered = notification_repository.list_unread_message_notifications(user_id=4, report_id=10)
    assert len(filtered) == 1
    assert filtered[0].report_id == 10


@pytest.mark.integration
def test_list_unread_message_notifications_returns_empty_when_none(notification_repository):
    """Restituisce lista vuota se non esistono notifiche MESSAGE non lette per l'utente."""
    results = notification_repository.list_unread_message_notifications(user_id=99999)

    assert results == []


# ---------------------------------------------------------------------------
# delete_for_user()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_delete_for_user_removes_all_notifications_of_that_user(notification_repository, db_session):
    """delete_for_user() elimina tutte le notifiche dell'utente specificato."""
    for i in range(3):
        notification_repository.add(_make_notification(user_id=6, title=f"N{i}"))
    db_session.commit()

    notification_repository.delete_for_user(6)
    db_session.commit()

    assert notification_repository.list_for_user(6) == []


@pytest.mark.integration
def test_delete_for_user_does_not_affect_other_users(notification_repository, db_session):
    """delete_for_user() non rimuove le notifiche degli altri utenti."""
    n_keep = _make_notification(user_id=7, title="Keep")
    notification_repository.add(_make_notification(user_id=6, title="Delete me"))
    notification_repository.add(n_keep)
    db_session.commit()

    kept_id = n_keep.id

    notification_repository.delete_for_user(6)
    db_session.commit()

    assert notification_repository.get_by_id(kept_id) is not None
    assert len(notification_repository.list_for_user(7)) == 1


@pytest.mark.integration
def test_delete_for_user_is_idempotent_on_empty_user(notification_repository, db_session):
    """delete_for_user() su un utente senza notifiche non solleva eccezioni."""
    notification_repository.delete_for_user(99)
    db_session.commit()  # nessuna eccezione = test passato