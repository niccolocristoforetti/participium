from __future__ import annotations

import pytest

from participium.core.exceptions import AuthorizationError, ValidationError
from participium.models.enums import Role
from participium.models.message import Message
from participium.models.report import Report
from participium.models.user import User
from participium.services.messaging_service import MessagingService


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

# Cittadino autore del report
REPORTER = User(id=10, username="mario.rossi", role=Role.CITIZEN, is_active=True)

# Operatore
OPERATOR = User(id=20, username="op.verdi", role=Role.OPERATOR, is_active=True)

# Utente estraneo al report
STRANGER = User(id=99, username="estraneo", role=Role.CITIZEN, is_active=True)

# Report con reporter valorizzato e status_history con operatore
# (garantisce che _resolve_recipient trovi un destinatario per REPORTER)
REPORT_WITH_REPORTER = Report(
    id=1,
    title="Buca in strada",
    reporter_id=REPORTER.id,
    reporter=REPORTER,
)

# Report orfano: reporter=None, nessun messaggio precedente da operatori,
# nessun status_history con operatori → _resolve_recipient restituisce None
# anche per un mittente OPERATOR (che viene comunque autorizzato)
REPORT_ORPHAN = Report(
    id=2,
    title="Report orfano",
    reporter_id=None,
    reporter=None,
    status_history=[],
)


@pytest.fixture
def seed_send_message_data() -> None:
    # Popola il sistema con i prerequisiti di `send_message`.
    #
    # Dataset suggerito:
    # - `REPORTER` persistito e attivo (id=10, role=CITIZEN)
    # - `OPERATOR` persistito e attivo (id=20, role=OPERATOR)
    # - `STRANGER` persistito e attivo (id=99, role=CITIZEN)
    # - `REPORT_WITH_REPORTER` persistito, reporter_id=10, con almeno un evento
    #   in status_history il cui changed_by ha role=OPERATOR (per rendere
    #   risolvibile il destinatario quando mittente è REPORTER)
    # - `REPORT_ORPHAN` persistito, reporter_id=None, senza messaggi precedenti
    #   da operatori e senza status_history con operatori
    pass


# ---------------------------------------------------------------------------
# MSG1 – Happy path: reporter invia messaggio, destinatario risolvibile
# EC covered: EC1 × EC3 × EC5
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_msg1_reporter_sends_message(seed_send_message_data: None) -> None:
    service = MessagingService()

    msg = service.send_message(
        report=REPORT_WITH_REPORTER,
        sender=REPORTER,
        body="Ciao, il problema persiste.",
    )

    assert isinstance(msg, Message)


# ---------------------------------------------------------------------------
# MSG2 – Mittente estraneo → AuthorizationError
# EC covered: EC2 × EC3 × EC5
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_msg2_unauthorized_sender(seed_send_message_data: None) -> None:
    service = MessagingService()

    with pytest.raises(AuthorizationError):
        service.send_message(
            report=REPORT_WITH_REPORTER,
            sender=STRANGER,
            body="Ciao",
        )


# ---------------------------------------------------------------------------
# MSG3 – Body composto solo da spazi → ValidationError
# EC covered: EC1 × EC4 × EC5
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_msg3_blank_body(seed_send_message_data: None) -> None:
    service = MessagingService()

    with pytest.raises(ValidationError):
        service.send_message(
            report=REPORT_WITH_REPORTER,
            sender=REPORTER,
            body="   ",
        )


# ---------------------------------------------------------------------------
# MSG4 – Body stringa vuota → ValidationError
# EC covered: EC1 × EC4 × EC5
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_msg4_empty_body(seed_send_message_data: None) -> None:
    service = MessagingService()

    with pytest.raises(ValidationError):
        service.send_message(
            report=REPORT_WITH_REPORTER,
            sender=REPORTER,
            body="",
        )


# ---------------------------------------------------------------------------
# MSG5 – Nessun destinatario risolvibile → ValidationError
#        Mittente OPERATOR autorizzato, ma report.reporter è None:
#        _resolve_recipient ritorna None per la branch OPERATOR.
# EC covered: EC1 × EC3 × EC6
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_msg5_no_resolvable_recipient(seed_send_message_data: None) -> None:
    service = MessagingService()

    with pytest.raises(ValidationError):
        service.send_message(
            report=REPORT_ORPHAN,
            sender=OPERATOR,
            body="Aggiornamento.",
        )


# ---------------------------------------------------------------------------
# MSG6 – Happy path: operatore invia messaggio, reporter è il destinatario
# EC covered: EC1 × EC3 × EC5
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_msg6_operator_sends_message(seed_send_message_data: None) -> None:
    service = MessagingService()

    msg = service.send_message(
        report=REPORT_WITH_REPORTER,
        sender=OPERATOR,
        body="Abbiamo preso in carico la segnalazione.",
    )

    assert isinstance(msg, Message)


# ---------------------------------------------------------------------------
# Boundary: body dopo trimming
# ---------------------------------------------------------------------------

# MSGB1 – Singolo spazio → ValidationError
# EC covered: EC1 × EC4 × EC5
@pytest.mark.skip(reason="Disabled.")
def test_msgb1_single_space_body(seed_send_message_data: None) -> None:
    service = MessagingService()

    with pytest.raises(ValidationError):
        service.send_message(
            report=REPORT_WITH_REPORTER,
            sender=REPORTER,
            body=" ",
        )


# MSGB2 – Tab e newline → ValidationError
# EC covered: EC1 × EC4 × EC5
@pytest.mark.skip(reason="Disabled.")
def test_msgb2_whitespace_only_body(seed_send_message_data: None) -> None:
    service = MessagingService()

    with pytest.raises(ValidationError):
        service.send_message(
            report=REPORT_WITH_REPORTER,
            sender=REPORTER,
            body="\t\n",
        )