from __future__ import annotations

from datetime import timedelta
from unittest.mock import Mock, patch, call

import pytest

from participium.core.exceptions import AuthenticationError, ValidationError
from participium.core.utils import utcnow
from participium.models.enums import Role
from participium.models.token import EmailVerificationToken
from participium.models.user import User
from participium.services.auth_service import AuthService


class TestRegisterUser:
    """Test suite per il metodo register_user."""

    def test_register_user_success_without_verification_url(
        self, auth_service, mock_user_repository, mock_session, mock_token_repository
    ):
        """Registrazione di un nuovo utente senza URL di verifica."""
        # Arrange
        payload = {
            "username": "newuser",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password": "SecurePass123!",
        }
        mock_user_repository.get_by_username.return_value = None
        mock_user_repository.get_by_email.return_value = None

        # Act
        user, verification_url = auth_service.register_user(payload)

        # Assert
        assert user is not None
        assert user.username == "newuser"
        assert user.email == "john@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.role == Role.CITIZEN
        assert user.is_active is True
        assert user.is_email_verified is False
        assert user.email_notifications_enabled is True
        assert verification_url is None
        mock_user_repository.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_token_repository.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_register_user_success_with_verification_url(
        self, auth_service, mock_user_repository, mock_session, mock_token_repository, mock_email_gateway
    ):
        """Registrazione con URL di verifica e invio email."""
        # Arrange
        payload = {
            "username": "newuser",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "password": "SecurePass123!",
        }
        mock_user_repository.get_by_username.return_value = None
        mock_user_repository.get_by_email.return_value = None
        verification_base_url = "http://localhost:3000/verify"

        # Act
        user, verification_url = auth_service.register_user(payload, verification_base_url)

        # Assert
        assert user is not None
        assert verification_url is not None
        assert verification_url.startswith("http://localhost:3000/verify/")
        mock_email_gateway.send.assert_called_once()
        call_kwargs = mock_email_gateway.send.call_args[1]
        assert call_kwargs["recipient"] == "jane@example.com"
        assert call_kwargs["subject"] == "Verify your Participium account"
        assert "Open this link to verify your account" in call_kwargs["body"]

    def test_register_user_verification_url_with_trailing_slash(
        self, auth_service, mock_user_repository, mock_session, mock_token_repository, mock_email_gateway
    ):
        """Registrazione gestisce correttamente URL con slash finale."""
        # Arrange
        payload = {
            "username": "user",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password": "Password123!",
        }
        mock_user_repository.get_by_username.return_value = None
        mock_user_repository.get_by_email.return_value = None
        verification_base_url = "http://localhost:3000/verify/"

        # Act
        user, verification_url = auth_service.register_user(payload, verification_base_url)

        # Assert
        # Deve rimuovere il trailing slash e aggiungere solo uno
        assert verification_url.startswith("http://localhost:3000/verify/")
        assert "verify//" not in verification_url

    def test_register_user_missing_all_required_fields(self, auth_service):
        """Errore se mancano tutti i campi obbligatori."""
        # Arrange
        payload = {}

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            auth_service.register_user(payload)

        assert "Missing required fields" in str(exc_info.value)
        assert "username" in str(exc_info.value)

    def test_register_user_missing_some_required_fields(self, auth_service):
        """Errore se mancano alcuni campi obbligatori."""
        # Arrange
        payload = {"username": "user", "first_name": "John"}

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            auth_service.register_user(payload)

        assert "Missing required fields" in str(exc_info.value)

    def test_register_user_username_already_exists(self, auth_service, mock_user_repository):
        """Errore se username è già in uso."""
        # Arrange
        existing_user = Mock(spec=User)
        mock_user_repository.get_by_username.return_value = existing_user
        payload = {
            "username": "existing",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password": "Password123!",
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            auth_service.register_user(payload)

        assert "Username already in use" in str(exc_info.value)

    def test_register_user_email_already_exists(self, auth_service, mock_user_repository):
        """Errore se email è già in uso."""
        # Arrange
        mock_user_repository.get_by_username.return_value = None
        existing_user = Mock(spec=User)
        mock_user_repository.get_by_email.return_value = existing_user
        payload = {
            "username": "newuser",
            "first_name": "John",
            "last_name": "Doe",
            "email": "taken@example.com",
            "password": "Password123!",
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            auth_service.register_user(payload)

        assert "Email already in use" in str(exc_info.value)

    def test_register_user_strips_whitespace(
        self, auth_service, mock_user_repository, mock_session, mock_token_repository
    ):
        """I dati vengono normalizzati (strip e lowercase email)."""
        # Arrange
        payload = {
            "username": "  newuser  ",
            "first_name": "  John  ",
            "last_name": "  Doe  ",
            "email": "  JOHN@EXAMPLE.COM  ",
            "password": "Password123!",
        }
        mock_user_repository.get_by_username.return_value = None
        mock_user_repository.get_by_email.return_value = None

        # Act
        user, _ = auth_service.register_user(payload)

        # Assert
        assert user.username == "newuser"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.email == "john@example.com"


class TestVerifyEmail:
    """Test suite per il metodo verify_email."""

    def test_verify_email_success(self, auth_service, mock_token_repository, mock_session):
        """Verifica dell'email con successo."""
        # Arrange
        user = Mock(spec=User)
        user.is_email_verified = False
        token = Mock(spec=EmailVerificationToken)
        token.is_used = False
        token.expires_at = utcnow() + timedelta(hours=24)
        token.user = user
        mock_token_repository.get_by_token.return_value = token

        # Act
        verified_user = auth_service.verify_email("valid_token_123")

        # Assert
        assert verified_user == user
        assert token.is_used is True
        assert user.is_email_verified is True
        mock_session.commit.assert_called_once()

    def test_verify_email_token_not_found(self, auth_service, mock_token_repository):
        """Errore se il token non esiste."""
        # Arrange
        mock_token_repository.get_by_token.return_value = None

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            auth_service.verify_email("nonexistent_token")

        assert "Verification token is invalid" in str(exc_info.value)

    def test_verify_email_token_already_used(self, auth_service, mock_token_repository):
        """Errore se il token è già stato usato."""
        # Arrange
        token = Mock(spec=EmailVerificationToken)
        token.is_used = True
        mock_token_repository.get_by_token.return_value = token

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            auth_service.verify_email("used_token")

        assert "Verification token is invalid" in str(exc_info.value)

    def test_verify_email_token_expired(self, auth_service, mock_token_repository):
        """Errore se il token è scaduto."""
        # Arrange
        token = Mock(spec=EmailVerificationToken)
        token.is_used = False
        token.expires_at = utcnow() - timedelta(hours=1)
        mock_token_repository.get_by_token.return_value = token

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            auth_service.verify_email("expired_token")

        assert "Verification token has expired" in str(exc_info.value)


class TestAuthenticate:
    """Test suite per il metodo authenticate."""

    def test_authenticate_success_with_username(
        self, auth_service, mock_user_repository
    ):
        """Autenticazione con successo usando username."""
        # Arrange
        user = Mock(spec=User)
        user.is_active = True
        user.is_email_verified = True
        user.password_hash = "hashed_password"
        mock_user_repository.get_by_username_or_email.return_value = user

        with patch("participium.services.auth_service.verify_password", return_value=True):
            # Act
            authenticated_user = auth_service.authenticate("testuser", "password123")

        # Assert
        assert authenticated_user == user
        mock_user_repository.get_by_username_or_email.assert_called_once_with("testuser")

    def test_authenticate_success_with_email(
        self, auth_service, mock_user_repository
    ):
        """Autenticazione con successo usando email."""
        # Arrange
        user = Mock(spec=User)
        user.is_active = True
        user.is_email_verified = True
        user.password_hash = "hashed_password"
        mock_user_repository.get_by_username_or_email.return_value = user

        with patch("participium.services.auth_service.verify_password", return_value=True):
            # Act
            authenticated_user = auth_service.authenticate("user@example.com", "password123")

        # Assert
        assert authenticated_user == user

    def test_authenticate_strips_whitespace_from_identifier(
        self, auth_service, mock_user_repository
    ):
        """L'identificativo viene pulito da spazi."""
        # Arrange
        user = Mock(spec=User)
        user.is_active = True
        user.is_email_verified = True
        user.password_hash = "hashed_password"
        mock_user_repository.get_by_username_or_email.return_value = user

        with patch("participium.services.auth_service.verify_password", return_value=True):
            # Act
            auth_service.authenticate("  testuser  ", "password123")

        # Assert
        mock_user_repository.get_by_username_or_email.assert_called_once_with("testuser")

    def test_authenticate_user_not_found(self, auth_service, mock_user_repository):
        """Errore se l'utente non è trovato."""
        # Arrange
        mock_user_repository.get_by_username_or_email.return_value = None

        # Act & Assert
        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.authenticate("nonexistent", "password123")

        assert "Invalid credentials" in str(exc_info.value)

    def test_authenticate_user_inactive(self, auth_service, mock_user_repository):
        """Errore se l'utente è inattivo."""
        # Arrange
        user = Mock(spec=User)
        user.is_active = False
        user.password_hash = "hashed_password"
        mock_user_repository.get_by_username_or_email.return_value = user

        with patch("participium.services.auth_service.verify_password", return_value=True):
            # Act & Assert
            with pytest.raises(AuthenticationError) as exc_info:
                auth_service.authenticate("testuser", "password123")

            assert "Invalid credentials" in str(exc_info.value)

    def test_authenticate_invalid_password(self, auth_service, mock_user_repository):
        """Errore se la password è errata."""
        # Arrange
        user = Mock(spec=User)
        user.is_active = True
        user.password_hash = "hashed_password"
        mock_user_repository.get_by_username_or_email.return_value = user

        with patch("participium.services.auth_service.verify_password", return_value=False):
            # Act & Assert
            with pytest.raises(AuthenticationError) as exc_info:
                auth_service.authenticate("testuser", "wrongpassword")

            assert "Invalid credentials" in str(exc_info.value)

    def test_authenticate_email_not_verified(self, auth_service, mock_user_repository):
        """Errore se l'email non è verificata."""
        # Arrange
        user = Mock(spec=User)
        user.is_active = True
        user.is_email_verified = False
        user.password_hash = "hashed_password"
        mock_user_repository.get_by_username_or_email.return_value = user

        with patch("participium.services.auth_service.verify_password", return_value=True):
            # Act & Assert
            with pytest.raises(AuthenticationError) as exc_info:
                auth_service.authenticate("testuser", "password123")

            assert "Email verification is required before login" in str(exc_info.value)