from __future__ import annotations

import pytest

from participium.core.exceptions import AuthorizationError, ValidationError
from participium.models.category import Category
from participium.models.enums import ReportStatus, Role
from participium.models.report import Report, ReportStatusHistory
from participium.models.user import User


@pytest.fixture
def seed_send_message_data(db_session):
    cat = Category(name="Test", is_active=True)
    db_session.add(cat)
    db_session.flush()

    reporter = User(
        username="mario.rossi", first_name="Mario", last_name="Rossi",
        email="reporter@test.com", password_hash="hash",
        role=Role.CITIZEN, is_active=True, is_email_verified=True,
    )
    operator = User(
        username="op.verdi", first_name="Op", last_name="Verdi",
        email="operator@test.com", password_hash="hash",
        role=Role.OPERATOR, is_active=True, is_email_verified=True,
        category_id=cat.id,
    )
    stranger = User(
        username="estraneo", first_name="Estraneo", last_name="Utente",
        email="stranger@test.com", password_hash="hash",
        role=Role.CITIZEN, is_active=True, is_email_verified=True,
    )
    db_session.add_all([reporter, operator, stranger])
    db_session.flush()

    report_with_reporter = Report(
        title="Buca in strada", description="Buca",
        latitude=45.0, longitude=9.0,
        status=ReportStatus.PENDING_APPROVAL,
        reporter_id=reporter.id,
        category_id=cat.id,
    )
    db_session.add(report_with_reporter)
    db_session.flush()

    # Evento di storia con operatore: permette a _resolve_recipient di trovare
    # un destinatario quando il mittente è un cittadino (REPORTER)
    db_session.add(ReportStatusHistory(
        report_id=report_with_reporter.id,
        previous_status=None,
        new_status=ReportStatus.PENDING_APPROVAL,
        changed_by_id=operator.id,
    ))

    report_orphan = Report(
        title="Report orfano", description="Orfano",
        latitude=45.0, longitude=9.0,
        status=ReportStatus.PENDING_APPROVAL,
        reporter_id=None,
        category_id=cat.id,
    )
    db_session.add(report_orphan)
    db_session.flush()

    return {
        "reporter": reporter,
        "operator": operator,
        "stranger": stranger,
        "report_with_reporter": report_with_reporter,
        "report_orphan": report_orphan,
    }


# MSG1 – Happy path: reporter invia messaggio, destinatario risolvibile
def test_msg1_reporter_sends_message(seed_send_message_data, messaging_service) -> None:
    data = seed_send_message_data
    from participium.models.message import Message

    msg = messaging_service.send_message(
        report=data["report_with_reporter"],
        sender=data["reporter"],
        body="Ciao, il problema persiste.",
    )

    assert isinstance(msg, Message)
    assert msg.sender_id == data["reporter"].id
    assert msg.body == "Ciao, il problema persiste."


# MSG2 – Mittente estraneo → AuthorizationError
def test_msg2_unauthorized_sender(seed_send_message_data, messaging_service) -> None:
    data = seed_send_message_data

    with pytest.raises(AuthorizationError):
        messaging_service.send_message(
            report=data["report_with_reporter"],
            sender=data["stranger"],
            body="Ciao",
        )


# MSG3 – Body composto solo da spazi → ValidationError
def test_msg3_blank_body(seed_send_message_data, messaging_service) -> None:
    data = seed_send_message_data

    with pytest.raises(ValidationError):
        messaging_service.send_message(
            report=data["report_with_reporter"],
            sender=data["reporter"],
            body="   ",
        )


# MSG4 – Body stringa vuota → ValidationError
def test_msg4_empty_body(seed_send_message_data, messaging_service) -> None:
    data = seed_send_message_data

    with pytest.raises(ValidationError):
        messaging_service.send_message(
            report=data["report_with_reporter"],
            sender=data["reporter"],
            body="",
        )


# MSG5 – Nessun destinatario risolvibile → ValidationError
#        OPERATOR autorizzato (stessa categoria), report.reporter è None
def test_msg5_no_resolvable_recipient(seed_send_message_data, messaging_service) -> None:
    data = seed_send_message_data

    with pytest.raises(ValidationError):
        messaging_service.send_message(
            report=data["report_orphan"],
            sender=data["operator"],
            body="Aggiornamento.",
        )


# MSG6 – Happy path: operatore invia messaggio, reporter è il destinatario
def test_msg6_operator_sends_message(seed_send_message_data, messaging_service) -> None:
    data = seed_send_message_data
    from participium.models.message import Message

    msg = messaging_service.send_message(
        report=data["report_with_reporter"],
        sender=data["operator"],
        body="Abbiamo preso in carico la segnalazione.",
    )

    assert isinstance(msg, Message)
    assert msg.sender_id == data["operator"].id
    assert msg.recipient_id == data["reporter"].id


# MSGB1 – Singolo spazio → ValidationError
def test_msgb1_single_space_body(seed_send_message_data, messaging_service) -> None:
    data = seed_send_message_data

    with pytest.raises(ValidationError):
        messaging_service.send_message(
            report=data["report_with_reporter"],
            sender=data["reporter"],
            body=" ",
        )


# MSGB2 – Tab e newline → ValidationError
def test_msgb2_whitespace_only_body(seed_send_message_data, messaging_service) -> None:
    data = seed_send_message_data

    with pytest.raises(ValidationError):
        messaging_service.send_message(
            report=data["report_with_reporter"],
            sender=data["reporter"],
            body="\t\n",
        )
