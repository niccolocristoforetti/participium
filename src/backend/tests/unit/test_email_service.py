from __future__ import annotations

from unittest.mock import Mock, MagicMock, patch

import pytest

from participium.services.email_service import (
    BaseEmailGateway,
    ConsoleEmailGateway,
    SmtpEmailGateway,
    build_email_gateway,
)


class TestBaseEmailGateway:
    """Test suite per BaseEmailGateway."""

    def test_send_does_not_raise(self):
        """Il metodo send della classe base esegue senza errori."""
        # Arrange
        gateway = BaseEmailGateway()

        # Act & Assert — nessuna eccezione
        gateway.send("to@test.com", "Subject", "Body")


class TestConsoleEmailGateway:
    """Test suite per ConsoleEmailGateway."""

    def test_send_writes_file_to_outbox(self, tmp_path):
        """send() scrive un file nella directory outbox con i dati dell'email."""
        # Arrange
        outbox = tmp_path / "outbox"
        gateway = ConsoleEmailGateway(outbox_dir=outbox, sender="noreply@test.com")

        # Act
        gateway.send("user@test.com", "Welcome", "Hello!")

        # Assert
        files = list(outbox.iterdir())
        assert len(files) == 1
        content = files[0].read_text(encoding="utf-8")
        assert "TO: user@test.com" in content
        assert "SUBJECT: Welcome" in content
        assert "Hello!" in content


class TestSmtpEmailGateway:
    """Test suite per SmtpEmailGateway."""

    @patch("participium.services.email_service.smtplib.SMTP")
    def test_send_with_tls_and_credentials(self, mock_smtp_class):
        """Invio con TLS e credenziali attiva starttls e login."""
        # Arrange
        smtp_instance = MagicMock()
        mock_smtp_class.return_value.__enter__ = Mock(return_value=smtp_instance)
        mock_smtp_class.return_value.__exit__ = Mock(return_value=False)

        gateway = SmtpEmailGateway(
            host="smtp.test.com", port=587,
            username="user", password="pass",
            sender="noreply@test.com", use_tls=True,
        )

        # Act
        gateway.send("to@test.com", "Subject", "Body")

        # Assert
        smtp_instance.starttls.assert_called_once()
        smtp_instance.login.assert_called_once_with("user", "pass")
        smtp_instance.send_message.assert_called_once()

    @patch("participium.services.email_service.smtplib.SMTP")
    def test_send_without_tls_and_without_credentials(self, mock_smtp_class):
        """Invio senza TLS e senza credenziali salta starttls e login."""
        # Arrange
        smtp_instance = MagicMock()
        mock_smtp_class.return_value.__enter__ = Mock(return_value=smtp_instance)
        mock_smtp_class.return_value.__exit__ = Mock(return_value=False)

        gateway = SmtpEmailGateway(
            host="smtp.test.com", port=25,
            username=None, password=None,
            sender="noreply@test.com", use_tls=False,
        )

        # Act
        gateway.send("to@test.com", "Subject", "Body")

        # Assert
        smtp_instance.starttls.assert_not_called()
        smtp_instance.login.assert_not_called()
        smtp_instance.send_message.assert_called_once()


class TestBuildEmailGateway:
    """Test suite per la factory build_email_gateway."""

    def test_builds_smtp_gateway_when_backend_is_smtp(self):
        """Con mail_backend='smtp' e smtp_host valorizzato, costruisce SmtpEmailGateway."""
        # Arrange
        settings = Mock()
        settings.mail_backend = "smtp"
        settings.smtp_host = "smtp.example.com"
        settings.smtp_port = 587
        settings.smtp_username = "user"
        settings.smtp_password = "pass"
        settings.mail_from = "noreply@test.com"
        settings.smtp_use_tls = True

        # Act
        gateway = build_email_gateway(settings)

        # Assert
        assert isinstance(gateway, SmtpEmailGateway)

    def test_falls_back_to_console_when_backend_is_console(self, tmp_path):
        """Con mail_backend='console' costruisce ConsoleEmailGateway."""
        # Arrange
        settings = Mock()
        settings.mail_backend = "console"
        settings.smtp_host = None
        settings.mail_outbox_dir = tmp_path / "outbox"
        settings.mail_from = "noreply@test.com"

        # Act
        gateway = build_email_gateway(settings)

        # Assert
        assert isinstance(gateway, ConsoleEmailGateway)

    def test_falls_back_to_console_when_smtp_host_is_empty(self, tmp_path):
        """Con smtp_host vuoto, anche se backend è 'smtp', usa ConsoleEmailGateway."""
        # Arrange
        settings = Mock()
        settings.mail_backend = "smtp"
        settings.smtp_host = ""
        settings.mail_outbox_dir = tmp_path / "outbox"
        settings.mail_from = "noreply@test.com"

        # Act
        gateway = build_email_gateway(settings)

        # Assert
        assert isinstance(gateway, ConsoleEmailGateway)
