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
        """Imposta is_read=True, fa commit e restituisce la notifica aggiornata."""
        # Arrange
        notification = Mock(spec=Notification)
        notification.is_read = False

        # Act
        result = notification_service.mark_as_read(notification)

        # Assert
        assert notification.is_read is True
        mock_session.commit.assert_called_once()
        assert result is notification


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


class TestNotifyStatusChange:
    """Test suite per notify_status_change."""

    def test_notifies_all_unique_non_none_recipients(
        self, notification_service, mock_notification_repository,
    ):
        """Invia notifiche a tutti i recipient distinti non-None."""
        # Arrange
        user_a = Mock(spec=User)
        user_a.id = 1
        user_a.email_notifications_enabled = False
        user_b = Mock(spec=User)
        user_b.id = 2
        user_b.email_notifications_enabled = False
        report = Mock(spec=Report)
        report.id = 10

        # Act
        notification_service.notify_status_change(
            recipients=[user_a, user_b], report=report, body="Status updated",
        )

        # Assert: add chiamato due volte (una per utente)
        assert mock_notification_repository.add.call_count == 2

    def test_skips_none_recipients(
        self, notification_service, mock_notification_repository,
    ):
        """Recipient None vengono ignorati."""
        # Arrange
        report = Mock(spec=Report)
        report.id = 5

        # Act
        notification_service.notify_status_change(
            recipients=[None, None], report=report, body="Update",
        )

        # Assert
        mock_notification_repository.add.assert_not_called()

    def test_deduplicates_recipients(
        self, notification_service, mock_notification_repository,
    ):
        """Lo stesso utente riceve una sola notifica anche se presente più volte."""
        # Arrange
        user = Mock(spec=User)
        user.id = 7
        user.email_notifications_enabled = False
        report = Mock(spec=Report)
        report.id = 3

        # Act
        notification_service.notify_status_change(
            recipients=[user, user], report=report, body="Dup",
        )

        # Assert
        assert mock_notification_repository.add.call_count == 1


class TestNotifyNewMessage:
    """Test suite per notify_new_message."""

    def test_creates_message_notification(
        self, notification_service, mock_notification_repository,
    ):
        """Crea una notifica di tipo MESSAGE per il recipient."""
        # Arrange
        recipient = Mock(spec=User)
        recipient.id = 4
        recipient.email_notifications_enabled = False
        report = Mock(spec=Report)
        report.id = 20

        # Act
        notification_service.notify_new_message(
            recipient=recipient, report=report,
            sender_name="Mario Rossi", body="Hello",
        )

        # Assert
        mock_notification_repository.add.assert_called_once()
        created = mock_notification_repository.add.call_args[0][0]
        assert "Mario Rossi" in created.body
        assert created.report_id == 20

    def test_skips_none_recipient(
        self, notification_service, mock_notification_repository,
    ):
        """Se recipient è None, non crea notifiche."""
        # Arrange
        report = Mock(spec=Report)
        report.id = 1

        # Act
        notification_service.notify_new_message(
            recipient=None, report=report,
            sender_name="X", body="Y",
        )

        # Assert
        mock_notification_repository.add.assert_not_called()


class TestListNotifications:
    """Test suite per list_notifications."""

    def test_delegates_to_repository(
        self, notification_service, mock_notification_repository,
    ):
        """list_notifications() delega al repository."""
        # Arrange
        notif = Mock(spec=Notification)
        mock_notification_repository.list_for_user.return_value = [notif]

        # Act
        result = notification_service.list_notifications(user_id=5)

        # Assert
        mock_notification_repository.list_for_user.assert_called_once_with(5)
        assert result == [notif]


class TestCountUnreadMessageNotifications:
    """Test suite per count_unread_message_notifications_by_report."""

    def test_returns_empty_dict_when_no_notifications(
        self, notification_service, mock_notification_repository,
    ):
        """Dizionario vuoto se non ci sono notifiche non lette."""
        # Arrange
        mock_notification_repository.list_unread_message_notifications.return_value = []

        # Act
        result = notification_service.count_unread_message_notifications_by_report(user_id=1)

        # Assert
        assert result == {}

    def test_groups_counts_by_report_id(
        self, notification_service, mock_notification_repository,
    ):
        """Raggruppa le notifiche non lette per report_id."""
        # Arrange
        n1 = Mock(spec=Notification)
        n1.report_id = 10
        n2 = Mock(spec=Notification)
        n2.report_id = 10
        n3 = Mock(spec=Notification)
        n3.report_id = 20
        mock_notification_repository.list_unread_message_notifications.return_value = [n1, n2, n3]

        # Act
        result = notification_service.count_unread_message_notifications_by_report(user_id=1)

        # Assert
        assert result == {10: 2, 20: 1}

    def test_skips_notifications_without_report_id(
        self, notification_service, mock_notification_repository,
    ):
        """Notifiche con report_id=None vengono ignorate."""
        # Arrange
        n = Mock(spec=Notification)
        n.report_id = None
        mock_notification_repository.list_unread_message_notifications.return_value = [n]

        # Act
        result = notification_service.count_unread_message_notifications_by_report(user_id=1)

        # Assert
        assert result == {}