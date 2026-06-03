from __future__ import annotations

from unittest.mock import Mock

import pytest

from participium.core.exceptions import AuthorizationError, ValidationError
from participium.models.enums import Role
from participium.models.message import Message
from participium.models.report import Report
from participium.models.user import User


# Helper

def _make_user(*, user_id=1, role=Role.CITIZEN, category_id=None):
    """Helper per creare un Mock di User con attributi di ruolo."""
    user = Mock(spec=User)
    user.id = user_id
    user.role = role
    user.category_id = category_id
    user.first_name = "Test"
    user.last_name = "User"
    user.username = "testuser"
    return user


def _make_report(*, reporter_id=10, category_id=1):
    """Helper per creare un Mock di Report con reporter e category."""
    report = Mock(spec=Report)
    report.id = 1
    report.reporter_id = reporter_id
    report.category_id = category_id
    report.reporter = _make_user(user_id=reporter_id)
    report.status_history = []
    return report


class TestCanAccessThread:
    """Test suite per il metodo can_access_thread."""

    def test_none_user_returns_false(self, messaging_service):
        """Un utente None non ha accesso al thread."""
        # Arrange
        report = _make_report()

        # Act
        result = messaging_service.can_access_thread(report, None)

        # Assert
        assert result is False

    def test_admin_always_has_access(self, messaging_service):
        """Un admin ha sempre accesso al thread."""
        # Arrange
        report = _make_report()
        admin = _make_user(user_id=99, role=Role.ADMIN)

        # Act
        result = messaging_service.can_access_thread(report, admin)

        # Assert
        assert result is True

    def test_operator_same_category_has_access(self, messaging_service):
        """Un operator della stessa categoria ha accesso."""
        # Arrange
        report = _make_report(category_id=5)
        operator = _make_user(user_id=99, role=Role.OPERATOR, category_id=5)

        # Act
        result = messaging_service.can_access_thread(report, operator)

        # Assert
        assert result is True

    def test_operator_different_category_no_access(self, messaging_service):
        """Un operator di una categoria diversa non ha accesso."""
        # Arrange
        report = _make_report(reporter_id=10, category_id=5)
        operator = _make_user(user_id=99, role=Role.OPERATOR, category_id=99)

        # Act
        result = messaging_service.can_access_thread(report, operator)

        # Assert
        assert result is False

    def test_reporter_has_access(self, messaging_service):
        """Il reporter del report ha accesso al thread."""
        # Arrange
        report = _make_report(reporter_id=10)
        citizen = _make_user(user_id=10, role=Role.CITIZEN)

        # Act
        result = messaging_service.can_access_thread(report, citizen)

        # Assert
        assert result is True

    def test_other_citizen_no_access(self, messaging_service):
        """Un citizen non reporter non ha accesso."""
        # Arrange
        report = _make_report(reporter_id=10)
        stranger = _make_user(user_id=99, role=Role.CITIZEN)

        # Act
        result = messaging_service.can_access_thread(report, stranger)

        # Assert
        assert result is False


class TestEnsureAccess:
    """Test suite per il metodo _ensure_access (chiamato tramite send_message)."""

    def test_ensure_access_raises_for_unauthorized_user(self, messaging_service):
        """Errore se un utente non autorizzato prova a inviare un messaggio."""
        # Arrange
        report = _make_report(reporter_id=10, category_id=1)
        stranger = _make_user(user_id=99, role=Role.CITIZEN)

        # Act & Assert
        with pytest.raises(AuthorizationError) as exc_info:
            messaging_service.send_message(report, stranger, "hello")

        assert "do not have access" in str(exc_info.value)


class TestListMessages:
    """Test suite per il metodo list_messages."""

    def test_list_messages_returns_repository_result(
        self, messaging_service, mock_message_repository,
    ):
        """list_messages() verifica l'accesso e delega al repository."""
        # Arrange
        report = _make_report(reporter_id=10)
        citizen = _make_user(user_id=10, role=Role.CITIZEN)
        msg = Mock(spec=Message)
        mock_message_repository.list_for_report.return_value = [msg]

        # Act
        result = messaging_service.list_messages(report, citizen)

        # Assert
        mock_message_repository.list_for_report.assert_called_once_with(report.id)
        assert result == [msg]

    def test_list_messages_raises_for_unauthorized_user(self, messaging_service):
        """list_messages() solleva AuthorizationError per utente non autorizzato."""
        # Arrange
        report = _make_report(reporter_id=10)
        stranger = _make_user(user_id=99, role=Role.CITIZEN)

        # Act & Assert
        with pytest.raises(AuthorizationError):
            messaging_service.list_messages(report, stranger)


class TestSendMessage:
    """Test suite per il metodo send_message."""

    def test_send_message_empty_body_raises(self, messaging_service):
        """Errore se il body è vuoto o composto solo da spazi."""
        # Arrange
        report = _make_report(reporter_id=10)
        citizen = _make_user(user_id=10, role=Role.CITIZEN)

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            messaging_service.send_message(report, citizen, "   ")

        assert "empty" in str(exc_info.value)

    def test_send_message_no_recipient_raises(self, messaging_service, mock_message_repository):
        """Errore se non è possibile risolvere un recipient."""
        # Arrange
        report = _make_report(reporter_id=10)
        report.reporter = None  # nessun reporter a cui rispondere
        report.status_history = []
        citizen = _make_user(user_id=10, role=Role.CITIZEN)
        mock_message_repository.list_for_report.return_value = []

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            messaging_service.send_message(report, citizen, "hello")

        assert "No recipient" in str(exc_info.value)

    def test_admin_sends_to_reporter(
        self, messaging_service, mock_message_repository, mock_session,
    ):
        """Un admin invia al reporter del report."""
        # Arrange
        report = _make_report(reporter_id=10)
        admin = _make_user(user_id=2, role=Role.ADMIN)

        # Act
        messaging_service.send_message(report, admin, "Hello citizen")

        # Assert
        mock_message_repository.add.assert_called_once()
        created_msg = mock_message_repository.add.call_args[0][0]
        assert created_msg.recipient_id == 10
        mock_session.commit.assert_called_once()

    def test_citizen_resolves_recipient_from_messages(
        self, messaging_service, mock_message_repository,
    ):
        """Un citizen risolve il recipient dall'ultimo messaggio di un operator."""
        # Arrange
        report = _make_report(reporter_id=10)
        citizen = _make_user(user_id=10, role=Role.CITIZEN)

        operator = _make_user(user_id=2, role=Role.OPERATOR, category_id=1)
        prev_msg = Mock(spec=Message)
        prev_msg.sender = operator
        mock_message_repository.list_for_report.return_value = [prev_msg]

        # Act
        messaging_service.send_message(report, citizen, "Thanks")

        # Assert
        created_msg = mock_message_repository.add.call_args[0][0]
        assert created_msg.recipient_id == operator.id

    def test_citizen_resolves_recipient_from_status_history(
        self, messaging_service, mock_message_repository,
    ):
        """Un citizen risolve il recipient dallo status_history del report."""
        # Arrange
        operator = _make_user(user_id=2, role=Role.OPERATOR, category_id=1)
        status_event = Mock()
        status_event.changed_by = operator

        report = _make_report(reporter_id=10)
        report.status_history = [status_event]
        citizen = _make_user(user_id=10, role=Role.CITIZEN)
        mock_message_repository.list_for_report.return_value = []

        # Act
        messaging_service.send_message(report, citizen, "Question")

        # Assert
        created_msg = mock_message_repository.add.call_args[0][0]
        assert created_msg.recipient_id == operator.id


class TestSenderName:
    """Test suite per il metodo statico _sender_name."""

    def test_full_name(self):
        """Restituisce 'first_name last_name' se presenti."""
        # Arrange
        user = Mock(spec=User)
        user.first_name = "John"
        user.last_name = "Doe"
        user.username = "jdoe"

        # Act & Assert
        from participium.services.messaging_service import MessagingService
        assert MessagingService._sender_name(user) == "John Doe"

    def test_falls_back_to_username(self):
        """Se first/last name sono vuoti, usa lo username."""
        # Arrange
        user = Mock(spec=User)
        user.first_name = ""
        user.last_name = ""
        user.username = "jdoe"

        # Act & Assert
        from participium.services.messaging_service import MessagingService
        assert MessagingService._sender_name(user) == "jdoe"