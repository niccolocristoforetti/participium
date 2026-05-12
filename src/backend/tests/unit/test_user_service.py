from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from participium.core.exceptions import NotFoundError, ValidationError
from participium.models.enums import Role
from participium.models.user import User
from participium.services.user_service import UserService


class TestUpdateProfile:
    """Test suite per il metodo update_profile."""

    def test_update_profile_username_already_in_use(
        self, user_service, mock_user_repository,
    ):
        """Errore se il nuovo username è già in uso da un altro account."""
        # Arrange
        user = Mock(spec=User)
        user.username = "current"
        mock_user_repository.get_by_username.return_value = Mock(spec=User)

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            user_service.update_profile(user, username="taken")

        assert "Username already in use" in str(exc_info.value)

    def test_update_profile_updates_first_and_last_name(
        self, user_service, mock_user_repository, mock_session,
    ):
        """Aggiorna first_name e last_name con strip degli spazi."""
        # Arrange
        user = Mock(spec=User)
        user.username = "current"

        # Act
        user_service.update_profile(user, first_name="  Mario  ", last_name="  Rossi  ")

        # Assert
        assert user.first_name == "Mario"
        assert user.last_name == "Rossi"
        mock_session.commit.assert_called_once()

    def test_update_profile_updates_email_notifications(
        self, user_service, mock_session,
    ):
        """Aggiorna la preferenza email_notifications_enabled."""
        # Arrange
        user = Mock(spec=User)
        user.username = "user"
        user.email_notifications_enabled = True

        # Act
        user_service.update_profile(user, email_notifications_enabled=False)

        # Assert
        assert user.email_notifications_enabled is False

    def test_update_profile_saves_profile_picture(
        self, user_service, mock_storage_service, mock_session,
    ):
        """Salva la foto profilo tramite storage_service."""
        # Arrange
        user = Mock(spec=User)
        user.username = "user"
        photo = Mock()
        photo.filename = "avatar.jpg"
        mock_storage_service.save.return_value = "stored_avatar.jpg"

        # Act
        user_service.update_profile(user, profile_picture=photo)

        # Assert
        assert user.profile_picture_path == "stored_avatar.jpg"
        mock_storage_service.save.assert_called_once_with(photo)

    def test_update_profile_ignores_photo_without_filename(
        self, user_service, mock_storage_service, mock_session,
    ):
        """Se profile_picture non ha filename, non viene salvata."""
        # Arrange
        user = Mock(spec=User)
        user.username = "user"
        photo = Mock()
        photo.filename = ""

        # Act
        user_service.update_profile(user, profile_picture=photo)

        # Assert
        mock_storage_service.save.assert_not_called()


class TestDeleteAccount:
    """Test suite per il metodo delete_account."""

    def test_delete_account_anonymizes_reports_and_cleans_relations(
        self, user_service, mock_session, mock_notification_repository,
        mock_token_repository, mock_user_repository,
    ):
        """Eliminazione account anonimizza report, rimuove follower, pulisce messaggi e history."""
        # Arrange
        user = Mock(spec=User)
        user.id = 5

        report = Mock()
        report.reporter_id = 5

        follower = Mock()

        msg_both = Mock()
        msg_both.sender_id = 5
        msg_both.recipient_id = 5

        history = Mock()
        history.changed_by_id = 5

        mock_session.scalars.side_effect = [
            iter([report]),      # reports
            iter([follower]),    # followers
            iter([msg_both]),    # messages
            iter([history]),     # histories
        ]
        mock_notification_repository.list_for_user.return_value = [Mock()]
        mock_token_repository.list_for_user.return_value = [Mock()]

        # Act
        user_service.delete_account(user)

        # Assert
        assert report.reporter_id is None
        assert report.is_anonymous is True
        assert msg_both.sender_id is None
        assert msg_both.recipient_id is None
        assert history.changed_by_id is None
        mock_user_repository.delete.assert_called_once_with(user)
        mock_session.commit.assert_called_once()

    def test_delete_account_message_only_sender(
        self, user_service, mock_session, mock_notification_repository,
        mock_token_repository, mock_user_repository,
    ):
        """Copre il branch dove l'utente è solo sender del messaggio."""
        # Arrange
        user = Mock(spec=User)
        user.id = 5

        msg = Mock()
        msg.sender_id = 5
        msg.recipient_id = 99

        mock_session.scalars.side_effect = [
            iter([]),       # reports
            iter([]),       # followers
            iter([msg]),    # messages
            iter([]),       # histories
        ]
        mock_notification_repository.list_for_user.return_value = []
        mock_token_repository.list_for_user.return_value = []

        # Act
        user_service.delete_account(user)

        # Assert
        assert msg.sender_id is None
        assert msg.recipient_id == 99  # invariato

    def test_delete_account_message_only_recipient(
        self, user_service, mock_session, mock_notification_repository,
        mock_token_repository, mock_user_repository,
    ):
        """Copre il branch dove l'utente è solo recipient del messaggio."""
        # Arrange
        user = Mock(spec=User)
        user.id = 5

        msg = Mock()
        msg.sender_id = 99
        msg.recipient_id = 5

        mock_session.scalars.side_effect = [
            iter([]),       # reports
            iter([]),       # followers
            iter([msg]),    # messages
            iter([]),       # histories
        ]
        mock_notification_repository.list_for_user.return_value = []
        mock_token_repository.list_for_user.return_value = []

        # Act
        user_service.delete_account(user)

        # Assert
        assert msg.sender_id == 99  # invariato
        assert msg.recipient_id is None


class TestCreateUser:
    """Test suite per il metodo create_user."""

    def test_create_user_missing_required_fields(self, user_service):
        """Errore se mancano campi obbligatori."""
        # Arrange
        payload = {"username": "partial"}

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            user_service.create_user(payload)

        assert "Missing required fields" in str(exc_info.value)

    def test_create_user_duplicate_username(self, user_service, mock_user_repository):
        """Errore se lo username è già in uso."""
        # Arrange
        mock_user_repository.get_by_username.return_value = Mock(spec=User)
        payload = {
            "username": "taken", "first_name": "A", "last_name": "B",
            "email": "a@b.com", "password": "pw", "role": "citizen",
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            user_service.create_user(payload)

        assert "Username already in use" in str(exc_info.value)

    def test_create_user_duplicate_email(self, user_service, mock_user_repository):
        """Errore se l'email è già in uso."""
        # Arrange
        mock_user_repository.get_by_username.return_value = None
        mock_user_repository.get_by_email.return_value = Mock(spec=User)
        payload = {
            "username": "new", "first_name": "A", "last_name": "B",
            "email": "taken@b.com", "password": "pw", "role": "citizen",
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            user_service.create_user(payload)

        assert "Email already in use" in str(exc_info.value)

    def test_create_user_invalid_role(self, user_service, mock_user_repository):
        """Errore se il ruolo fornito non è valido."""
        # Arrange
        mock_user_repository.get_by_username.return_value = None
        mock_user_repository.get_by_email.return_value = None
        payload = {
            "username": "x", "first_name": "A", "last_name": "B",
            "email": "x@b.com", "password": "pw", "role": "superadmin",
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            user_service.create_user(payload)

        assert "Invalid user role" in str(exc_info.value)

    @patch("participium.services.user_service.hash_password", return_value="hashed")
    def test_create_user_success_citizen(
        self, _hash, user_service, mock_user_repository, mock_session,
    ):
        """Creazione con successo di un utente citizen."""
        # Arrange
        mock_user_repository.get_by_username.return_value = None
        mock_user_repository.get_by_email.return_value = None
        payload = {
            "username": "new", "first_name": "A", "last_name": "B",
            "email": "new@b.com", "password": "pw", "role": "citizen",
        }

        # Act
        result = user_service.create_user(payload)

        # Assert
        mock_user_repository.add.assert_called_once()
        mock_session.commit.assert_called_once()
        assert result.role == Role.CITIZEN


class TestResolveOperatorCategory:
    """Test suite per il metodo _resolve_operator_category."""

    def test_non_operator_returns_none(self, user_service):
        """Per un ruolo non-operator restituisce None."""
        # Act
        result = user_service._resolve_operator_category(Role.CITIZEN, 1)

        # Assert
        assert result is None

    def test_operator_without_category_raises(self, user_service):
        """Errore se operator non ha category_id."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            user_service._resolve_operator_category(Role.OPERATOR, None)

        assert "Operator category is required" in str(exc_info.value)

    def test_operator_with_empty_string_category_raises(self, user_service):
        """Errore se operator ha category_id vuoto."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            user_service._resolve_operator_category(Role.OPERATOR, "")

        assert "Operator category is required" in str(exc_info.value)

    def test_operator_with_invalid_category_id_raises(self, user_service):
        """Errore se category_id non è convertibile a int."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            user_service._resolve_operator_category(Role.OPERATOR, "abc")

        assert "valid active category" in str(exc_info.value)

    def test_operator_with_unknown_category_raises(self, user_service, mock_category_repository):
        """Errore se la categoria non esiste nel repository."""
        # Arrange
        mock_category_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            user_service._resolve_operator_category(Role.OPERATOR, 999)

        assert "valid active category" in str(exc_info.value)

    def test_operator_with_inactive_category_raises(self, user_service, mock_category_repository):
        """Errore se la categoria esiste ma è inattiva."""
        # Arrange
        category = Mock()
        category.is_active = False
        mock_category_repository.get_by_id.return_value = category

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            user_service._resolve_operator_category(Role.OPERATOR, 1)

        assert "valid active category" in str(exc_info.value)

    def test_operator_with_valid_active_category_returns_it(self, user_service, mock_category_repository):
        """Con una categoria valida e attiva, restituisce la categoria."""
        # Arrange
        category = Mock()
        category.id = 1
        category.is_active = True
        mock_category_repository.get_by_id.return_value = category

        # Act
        result = user_service._resolve_operator_category(Role.OPERATOR, 1)

        # Assert
        assert result.id == 1
