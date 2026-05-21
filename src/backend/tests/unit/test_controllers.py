from __future__ import annotations

from unittest.mock import Mock

import pytest

from participium.controllers.admin_controller import AdminController
from participium.controllers.auth_controller import AuthController
from participium.controllers.operator_controller import OperatorController
from participium.controllers.report_controller import ReportController
from participium.controllers.statistics_controller import StatisticsController
from participium.controllers.user_controller import UserController
from participium.models.enums import Role
from participium.models.user import User

pytestmark = pytest.mark.whitebox


def _user(role: Role, category_id: int | None = None) -> User:
    return User(id=1, username="test", role=role, is_active=True, category_id=category_id)


# ---------------------------------------------------------------------------
# OperatorController
# ---------------------------------------------------------------------------

class TestOperatorControllerDashboard:
    def _controller(self):
        report_service = Mock()
        report_service.list_pending_reports.return_value = []
        report_service.list_operator_reports.return_value = []
        notification_service = Mock()
        notification_service.count_unread_message_notifications_by_report.return_value = {}
        return OperatorController(report_service=report_service, notification_service=notification_service)

    def test_admin_gets_pending_reports_without_category_filter(self):
        ctrl = self._controller()
        ctrl.build_dashboard(_user(Role.ADMIN))
        ctrl.report_service.list_pending_reports.assert_called_once_with({})

    def test_citizen_gets_empty_pending_reports(self):
        ctrl = self._controller()
        result = ctrl.build_dashboard(_user(Role.CITIZEN))
        assert result.pending_reports == []
        ctrl.report_service.list_pending_reports.assert_not_called()


# ---------------------------------------------------------------------------
# UserController
# ---------------------------------------------------------------------------

class TestUserControllerAdminMethods:
    def _controller(self):
        user_service = Mock()
        user_service.list_users.return_value = []
        user_service.create_user.return_value = Mock()
        user_service.update_user.return_value = Mock()
        return UserController(user_service=user_service, notification_service=Mock())

    def test_list_users_delegates_to_service(self):
        ctrl = self._controller()
        result = ctrl.list_users()
        ctrl.user_service.list_users.assert_called_once()
        assert result == []

    def test_create_user_delegates_to_service(self):
        ctrl = self._controller()
        payload = {"username": "new", "email": "new@test.com"}
        ctrl.create_user(payload)
        ctrl.user_service.create_user.assert_called_once_with(payload)

    def test_update_user_delegates_to_service(self):
        ctrl = self._controller()
        ctrl.update_user(1, {"first_name": "Updated"})
        ctrl.user_service.update_user.assert_called_once_with(1, {"first_name": "Updated"})


# ---------------------------------------------------------------------------
# AdminController
# ---------------------------------------------------------------------------

class TestAdminControllerCategories:
    def _controller(self):
        return AdminController(
            category_service=Mock(),
            user_service=Mock(),
            statistics_service=Mock(),
        )

    def test_list_categories_delegates_to_service(self):
        ctrl = self._controller()
        ctrl.category_service.list_categories.return_value = []
        result = ctrl.list_categories(active_only=True)
        ctrl.category_service.list_categories.assert_called_once_with(active_only=True)
        assert result == []

    def test_create_category_delegates_to_service(self):
        ctrl = self._controller()
        ctrl.category_service.create_category.return_value = Mock()
        ctrl.create_category("Roads")
        ctrl.category_service.create_category.assert_called_once_with("Roads")

    def test_update_category_extracts_payload_fields(self):
        ctrl = self._controller()
        ctrl.category_service.update_category.return_value = Mock()
        ctrl.update_category(3, {"name": "New Name", "is_active": False})
        ctrl.category_service.update_category.assert_called_once_with(3, name="New Name", is_active=False)

    def test_admin_statistics_delegates_to_service(self):
        ctrl = self._controller()
        ctrl.statistics_service.admin_statistics.return_value = {}
        result = ctrl.admin_statistics()
        ctrl.statistics_service.admin_statistics.assert_called_once()
        assert result == {}


# ---------------------------------------------------------------------------
# AuthController
# ---------------------------------------------------------------------------

class TestAuthController:
    def _controller(self):
        return AuthController(auth_service=Mock())

    def test_register_delegates_to_service(self):
        ctrl = self._controller()
        ctrl.auth_service.register_user.return_value = (Mock(), "token")
        payload = {"email": "a@b.com", "password": "Pass1!"}
        ctrl.register(payload, verification_base_url="http://localhost")
        ctrl.auth_service.register_user.assert_called_once_with(payload, "http://localhost")

    def test_verify_email_delegates_to_service(self):
        ctrl = self._controller()
        ctrl.auth_service.verify_email.return_value = Mock()
        ctrl.verify_email("abc123")
        ctrl.auth_service.verify_email.assert_called_once_with("abc123")

    def test_login_delegates_to_service(self):
        ctrl = self._controller()
        ctrl.auth_service.authenticate.return_value = Mock()
        ctrl.login("user@example.com", "Pass1!")
        ctrl.auth_service.authenticate.assert_called_once_with("user@example.com", "Pass1!")


# ---------------------------------------------------------------------------
# ReportController
# ---------------------------------------------------------------------------

class TestReportController:
    def _controller(self):
        return ReportController(
            report_service=Mock(),
            messaging_service=Mock(),
            notification_service=Mock(),
        )

    def test_list_public_reports_delegates_to_service(self):
        ctrl = self._controller()
        ctrl.report_service.list_public_reports.return_value = []
        result = ctrl.list_public_reports()
        ctrl.report_service.list_public_reports.assert_called_once()
        assert result == []

    def test_list_user_reports_delegates_to_service(self):
        ctrl = self._controller()
        ctrl.report_service.list_user_reports.return_value = []
        user = Mock()
        result = ctrl.list_user_reports(user)
        ctrl.report_service.list_user_reports.assert_called_once_with(user)
        assert result == []

    def test_build_detail_context_marks_notifications_when_accessible(self):
        ctrl = self._controller()
        user = Mock(id=1)
        report = Mock(id=42)
        ctrl.report_service.get_accessible_report.return_value = report
        ctrl.messaging_service.can_access_thread.return_value = True

        ctx = ctrl.build_detail_context(42, user)

        assert ctx.can_access_messages is True
        ctrl.notification_service.mark_report_message_notifications_as_read.assert_called_once_with(1, 42)

    def test_build_detail_context_skips_notifications_when_no_access(self):
        ctrl = self._controller()
        user = Mock(id=1)
        report = Mock(id=42)
        ctrl.report_service.get_accessible_report.return_value = report
        ctrl.messaging_service.can_access_thread.return_value = False

        ctrl.build_detail_context(42, user)

        ctrl.notification_service.mark_report_message_notifications_as_read.assert_not_called()

    def test_build_detail_context_skips_notifications_when_anonymous(self):
        ctrl = self._controller()
        report = Mock(id=42)
        ctrl.report_service.get_accessible_report.return_value = report
        ctrl.messaging_service.can_access_thread.return_value = True

        ctrl.build_detail_context(42, user=None)

        ctrl.notification_service.mark_report_message_notifications_as_read.assert_not_called()

    def test_follow_report_delegates_to_service(self):
        ctrl = self._controller()
        user = Mock()
        ctrl.report_service.follow_report.return_value = Mock()
        ctrl.follow_report(7, user)
        ctrl.report_service.follow_report.assert_called_once_with(7, user)

    def test_send_message_delegates_to_messaging_service(self):
        ctrl = self._controller()
        report, sender = Mock(), Mock()
        ctrl.messaging_service.send_message.return_value = Mock()
        ctrl.send_message(report, sender, "hello")
        ctrl.messaging_service.send_message.assert_called_once_with(report, sender, "hello")


# ---------------------------------------------------------------------------
# StatisticsController
# ---------------------------------------------------------------------------

class TestStatisticsController:
    def _controller(self):
        return StatisticsController(statistics_service=Mock())

    def test_public_statistics_delegates_to_service(self):
        ctrl = self._controller()
        ctrl.statistics_service.public_statistics.return_value = {"total": 5}
        result = ctrl.public_statistics(granularity="week")
        ctrl.statistics_service.public_statistics.assert_called_once_with("week")
        assert result == {"total": 5}

    def test_public_statistics_default_granularity(self):
        ctrl = self._controller()
        ctrl.statistics_service.public_statistics.return_value = {}
        ctrl.public_statistics()
        ctrl.statistics_service.public_statistics.assert_called_once_with("day")
