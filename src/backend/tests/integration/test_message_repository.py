from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from participium.models.message import Message


@pytest.mark.integration
def test_add_message_persists_in_database(message_repository, db_session):
    """add() persiste il messaggio e restituisce l'oggetto con l'id generato."""
    # Arrange
    # Su SQLite in memoria le FK non sono vincolanti senza PRAGMA foreign_keys=ON,
    # quindi possiamo usare ID fittizi per report_id, sender_id e recipient_id.
    new_message = Message(
        report_id=1,
        sender_id=2,
        recipient_id=3,
        body="Test message body",
    )

    # Act
    added_message = message_repository.add(new_message)
    db_session.commit()

    # Assert
    assert added_message.id is not None
    assert added_message.body == "Test message body"
    assert added_message.report_id == 1
    assert added_message.sender_id == 2
    assert added_message.recipient_id == 3


@pytest.mark.integration
def test_list_for_report_returns_only_messages_of_that_report(message_repository, db_session):
    """list_for_report() filtra correttamente per report_id."""
    # Arrange: 2 messaggi per il report 10, 1 per il report 99
    now = datetime.now()
    msg1 = Message(report_id=10, body="First message",  created_at=now - timedelta(seconds=2))
    msg2 = Message(report_id=10, body="Second message", created_at=now - timedelta(seconds=1))
    msg3 = Message(report_id=99, body="Other report message", created_at=now)

    message_repository.add(msg1)
    message_repository.add(msg2)
    message_repository.add(msg3)
    db_session.commit()

    # Act
    messages = message_repository.list_for_report(10)

    # Assert: solo i messaggi del report 10
    assert len(messages) == 2
    assert all(m.report_id == 10 for m in messages)


@pytest.mark.integration
def test_list_for_report_returns_messages_ordered_by_created_at_asc(message_repository, db_session):
    """list_for_report() restituisce i messaggi ordinati per created_at ASC.

    I created_at vengono impostati esplicitamente con timedelta per garantire
    un ordinamento deterministico indipendente dalla velocità di SQLite.
    """
    # Arrange
    now = datetime.now()
    msg_first  = Message(report_id=20, body="Prima nel tempo",   created_at=now - timedelta(minutes=5))
    msg_second = Message(report_id=20, body="Seconda nel tempo", created_at=now - timedelta(minutes=2))
    msg_third  = Message(report_id=20, body="Terza nel tempo",   created_at=now)

    # Inseriamo intenzionalmente in ordine invertito per verificare che sia
    # l'ORDER BY a determinare il risultato, non l'ordine di inserimento.
    message_repository.add(msg_third)
    message_repository.add(msg_first)
    message_repository.add(msg_second)
    db_session.commit()

    # Act
    messages = message_repository.list_for_report(20)

    # Assert
    assert len(messages) == 3
    assert messages[0].body == "Prima nel tempo"
    assert messages[1].body == "Seconda nel tempo"
    assert messages[2].body == "Terza nel tempo"


@pytest.mark.integration
def test_list_for_report_returns_empty_list_when_no_messages(message_repository):
    """list_for_report() restituisce una lista vuota senza sollevare eccezioni
    quando non esistono messaggi per il report richiesto."""
    # Act
    messages = message_repository.list_for_report(999)

    # Assert
    assert messages == []