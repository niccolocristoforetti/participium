from __future__ import annotations

from unittest.mock import Mock

import pytest

from participium.controllers.operator_controller import OperatorController
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
