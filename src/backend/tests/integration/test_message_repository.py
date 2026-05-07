#aaaaaaaaaaaaa
"""
Test di integrazione per MessageRepository.

Copertura al 100% dei metodi pubblici:
  - add()
  - list_for_report()  — filtro per report_id, ordinamento ASC, lista vuota

Ogni test dipende esclusivamente dalla fixture ``message_repository``
(e ``db_session`` quando serve il commit) definita in conftest.py.
SQLite in memoria non applica i vincoli FK di default, quindi si usano
ID fittizi per report_id, sender_id e recipient_id.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from participium.models.message import Message


# ---------------------------------------------------------------------------
# add()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_add_assigns_primary_key(message_repository, db_session):
    """add() persiste il messaggio nel database: dopo il commit l'id è valorizzato."""
    msg = Message(report_id=1, sender_id=2, recipient_id=3, body="Hello")

    message_repository.add(msg)
    db_session.commit()

    assert msg.id is not None


@pytest.mark.integration
def test_add_persists_all_fields(message_repository, db_session):
    """add() salva correttamente body, report_id, sender_id e recipient_id."""
    msg = Message(report_id=10, sender_id=20, recipient_id=30, body="Payload")

    message_repository.add(msg)
    db_session.commit()

    db_session.expire(msg)
    assert msg.body == "Payload"
    assert msg.report_id == 10
    assert msg.sender_id == 20
    assert msg.recipient_id == 30


@pytest.mark.integration
def test_add_with_nullable_sender_and_recipient(message_repository, db_session):
    """add() accetta sender_id e recipient_id nulli (campi nullable nel modello)."""
    msg = Message(report_id=5, sender_id=None, recipient_id=None, body="Anonymous")

    message_repository.add(msg)
    db_session.commit()

    db_session.expire(msg)
    assert msg.sender_id is None
    assert msg.recipient_id is None


@pytest.mark.integration
def test_add_returns_the_same_object(message_repository, db_session):
    """add() restituisce l'oggetto passato (identità, non copia)."""
    msg = Message(report_id=1, body="Return check")

    result = message_repository.add(msg)
    db_session.commit()

    assert result is msg


# ---------------------------------------------------------------------------
# list_for_report()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_list_for_report_returns_only_messages_of_that_report(message_repository, db_session):
    """list_for_report() filtra esclusivamente per report_id."""
    now = datetime.now()
    msg_target = Message(report_id=10, body="Belongs here", created_at=now)
    msg_other  = Message(report_id=99, body="Other report", created_at=now)

    message_repository.add(msg_target)
    message_repository.add(msg_other)
    db_session.commit()

    results = message_repository.list_for_report(10)

    assert len(results) == 1
    assert results[0].body == "Belongs here"
    assert all(m.report_id == 10 for m in results)


@pytest.mark.integration
def test_list_for_report_orders_by_created_at_asc(message_repository, db_session):
    """list_for_report() ordina i messaggi dal più vecchio al più recente (ASC).

    I messaggi vengono inseriti in ordine inverso per verificare che sia
    l'ORDER BY della query a determinare il risultato.
    """
    now = datetime.now()
    msg_first  = Message(report_id=20, body="First",  created_at=now - timedelta(minutes=5))
    msg_second = Message(report_id=20, body="Second", created_at=now - timedelta(minutes=2))
    msg_third  = Message(report_id=20, body="Third",  created_at=now)

    # Inserimento in ordine inverso: ordine di inserimento ≠ ordine atteso
    message_repository.add(msg_third)
    message_repository.add(msg_first)
    message_repository.add(msg_second)
    db_session.commit()

    results = message_repository.list_for_report(20)

    assert len(results) == 3
    assert results[0].body == "First"
    assert results[1].body == "Second"
    assert results[2].body == "Third"


@pytest.mark.integration
def test_list_for_report_returns_empty_list_when_no_messages(message_repository):
    """list_for_report() restituisce una lista vuota per un report senza messaggi."""
    results = message_repository.list_for_report(999)

    assert results == []


@pytest.mark.integration
def test_list_for_report_does_not_return_messages_of_other_reports(message_repository, db_session):
    """list_for_report() non include messaggi di report diversi anche se presenti nel DB."""
    now = datetime.now()
    for i, rid in enumerate([1, 2, 3]):
        message_repository.add(Message(report_id=rid, body=f"msg {i}", created_at=now))
    db_session.commit()

    results = message_repository.list_for_report(2)

    assert len(results) == 1
    assert results[0].report_id == 2