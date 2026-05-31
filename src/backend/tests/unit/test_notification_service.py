from __future__ import annotations

from unittest.mock import Mock

import pytest

from participium.core.exceptions import AuthorizationError, NotFoundError
from participium.models.enums import NotificationType
from participium.models.notification import Notification
from participium.models.report import Report
from participium.models.user import User


class TestCreateNotification:
    """Test suite per il metodo create_notification."""

    def test_create_notification_returns_none_when_user_is_none(self, notification_service):
        """Se user è None, restituisce None senza creare notifiche."""
        # Act
        result = notification_service.create_notification(
            user=None,
            notification_type=NotificationType.STATUS_CHANGE,
            title="Title",
            body="Body",
        )

        # Assert
        assert result is None

    def test_create_notification_sends_email_when_enabled(
        self, notification_service, mock_notification_repository, mock_email_gateway,
    ):
        """Se email_notifications_enabled è True, invia l'email dopo la creazione."""
        # Arrange
        user = Mock(spec=User)
        user.id = 1
        user.email = "user@test.com"
        user.email_notifications_enabled = True
        report = Mock(spec=Report)
        report.id = 10

        # Act
        result = notification_service.create_notification(
            user=user,
            notification_type=NotificationType.STATUS_CHANGE,
            title="Title",
            body="Body",
            report=report,
        )

        # Assert
        assert result is not None
        mock_notification_repository.add.assert_called_once()
        mock_email_gateway.send.assert_called_once_with(recipient="user@test.com", subject="Title", body="Body")

    def test_create_notification_skips_email_when_disabled(
        self, notification_service, mock_email_gateway,
    ):
        """Se email_notifications_enabled è False, non invia l'email."""
        # Arrange
        user = Mock(spec=User)
        user.id = 1
        user.email_notifications_enabled = False

        # Act
        notification_service.create_notification(
            user=user,
            notification_type=NotificationType.MESSAGE,
            title="T",
            body="B",
        )

        # Assert
        mock_email_gateway.send.assert_not_called()

    def test_create_notification_logs_email_failure_without_raising(
        self, notification_service, mock_email_gateway, mock_notification_repository,
    ):
        """Se l'invio email fallisce, la notifica viene creata ugualmente."""
        # Arrange
        user = Mock(spec=User)
        user.id = 1
        user.email = "user@test.com"
        user.email_notifications_enabled = True
        mock_email_gateway.send.side_effect = RuntimeError("SMTP down")

        # Act
        result = notification_service.create_notification(
            user=user,
            notification_type=NotificationType.STATUS_CHANGE,
            title="T",
            body="B",
        )

        # Assert
        assert result is not None
        mock_notification_repository.add.assert_called_once()


class TestGetUserNotification:
    """Test suite per il metodo get_user_notification."""

    def test_get_user_notification_not_found(self, notification_service, mock_notification_repository):
        """Errore se la notifica non esiste."""
        # Arrange
        mock_notification_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            notification_service.get_user_notification(user_id=1, notification_id=999)

        assert "Notification not found" in str(exc_info.value)

    def test_get_user_notification_wrong_user(self, notification_service, mock_notification_repository):
        """Errore se la notifica appartiene a un altro utente."""
        # Arrange
        notification = Mock(spec=Notification)
        notification.user_id = 5
        mock_notification_repository.get_by_id.return_value = notification

        # Act & Assert
        with pytest.raises(AuthorizationError) as exc_info:
            notification_service.get_user_notification(user_id=99, notification_id=10)

        assert "cannot access" in str(exc_info.value)

    def test_get_user_notification_success(self, notification_service, mock_notification_repository):
        """Restituisce la notifica se appartiene all'utente corretto."""
        # Arrange
        notification = Mock(spec=Notification)
        notification.user_id = 5
        mock_notification_repository.get_by_id.return_value = notification

        # Act
        result = notification_service.get_user_notification(user_id=5, notification_id=10)

        # Assert
        assert result == notification


class TestMarkAsRead:
    """Test suite per il metodo mark_as_read."""

    def test_mark_as_read_sets_flag_and_commits(self, notification_service, mock_session):
        """Imposta is_read=True e fa commit."""
        # Arrange
        notification = Mock(spec=Notification)
        notification.is_read = False

        # Act
        result = notification_service.mark_as_read(notification)

        # Assert
        assert notification.is_read is True
        mock_session.commit.assert_called_once()


class TestMarkReportMessageNotifications:
    """Test suite per mark_report_message_notifications_as_read."""

    def test_returns_zero_when_no_unread(
        self, notification_service, mock_notification_repository, mock_session,
    ):
        """Restituisce 0 e non fa commit se non ci sono notifiche da marcare."""
        # Arrange
        mock_notification_repository.list_unread_message_notifications.return_value = []

        # Act
        count = notification_service.mark_report_message_notifications_as_read(
            user_id=1, report_id=1,
        )

        # Assert
        assert count == 0
        mock_session.commit.assert_not_called()

    def test_marks_all_unread_and_commits(
        self, notification_service, mock_notification_repository, mock_session,
    ):
        """Marca tutte le notifiche non lette e fa commit."""
        # Arrange
        n1 = Mock(spec=Notification, is_read=False)
        n2 = Mock(spec=Notification, is_read=False)
        mock_notification_repository.list_unread_message_notifications.return_value = [n1, n2]

        # Act
        count = notification_service.mark_report_message_notifications_as_read(
            user_id=1, report_id=1,
        )

        # Assert
        assert count == 2
        assert n1.is_read is True
        assert n2.is_read is True
        mock_session.commit.assert_called_once()
