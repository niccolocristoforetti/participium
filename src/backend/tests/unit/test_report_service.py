from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock

import pytest

from participium.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from participium.models.enums import ReportStatus, Role
from participium.models.report import Report
from participium.models.user import User
from participium.services.report_service import ReportService


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_user(*, user_id=1, role=Role.CITIZEN, category_id=None):
    """Helper per creare un Mock di User."""
    user = Mock(spec=User)
    user.id = user_id
    user.role = role
    user.category_id = category_id
    return user


def _make_report(*, report_id=1, status=ReportStatus.PENDING_APPROVAL,
                 reporter_id=10, category_id=1):
    """Helper per creare un Mock di Report."""
    report = Mock(spec=Report)
    report.id = report_id
    report.status = status
    report.reporter_id = reporter_id
    report.category_id = category_id
    report.reporter = _make_user(user_id=reporter_id) if reporter_id else None
    report.followers = []
    return report


# ---------------------------------------------------------------------------
# get_accessible_report
# ---------------------------------------------------------------------------

class TestGetAccessibleReport:
    """Test suite per il metodo get_accessible_report."""

    def test_public_report_accessible_without_user(
        self, report_service, mock_report_repository,
    ):
        """Un report pubblico è accessibile anche senza utente autenticato."""
        # Arrange
        report = _make_report(status=ReportStatus.ASSIGNED)
        mock_report_repository.get_by_id.return_value = report

        # Act
        result = report_service.get_accessible_report(1, user=None)

        # Assert
        assert result == report

    def test_non_public_without_user_raises(
        self, report_service, mock_report_repository,
    ):
        """Un report non pubblico senza utente genera errore di autorizzazione."""
        # Arrange
        report = _make_report(status=ReportStatus.PENDING_APPROVAL)
        mock_report_repository.get_by_id.return_value = report

        # Act & Assert
        with pytest.raises(AuthorizationError) as exc_info:
            report_service.get_accessible_report(1, user=None)

        assert "do not have access" in str(exc_info.value)

    def test_reporter_can_access_own_non_public_report(
        self, report_service, mock_report_repository,
    ):
        """Il reporter può accedere al proprio report non pubblico."""
        # Arrange
        report = _make_report(status=ReportStatus.PENDING_APPROVAL, reporter_id=10)
        mock_report_repository.get_by_id.return_value = report
        citizen = _make_user(user_id=10, role=Role.CITIZEN)

        # Act
        result = report_service.get_accessible_report(1, user=citizen)

        # Assert
        assert result == report

    def test_admin_can_access_any_report(
        self, report_service, mock_report_repository,
    ):
        """Un admin può accedere a qualsiasi report."""
        # Arrange
        report = _make_report(status=ReportStatus.PENDING_APPROVAL, reporter_id=10)
        mock_report_repository.get_by_id.return_value = report
        admin = _make_user(user_id=99, role=Role.ADMIN)

        # Act
        result = report_service.get_accessible_report(1, user=admin)

        # Assert
        assert result == report

    def test_operator_same_category_can_access(
        self, report_service, mock_report_repository,
    ):
        """Un operator della stessa categoria può accedere."""
        # Arrange
        report = _make_report(status=ReportStatus.PENDING_APPROVAL, category_id=5, reporter_id=10)
        mock_report_repository.get_by_id.return_value = report
        operator = _make_user(user_id=99, role=Role.OPERATOR, category_id=5)

        # Act
        result = report_service.get_accessible_report(1, user=operator)

        # Assert
        assert result == report

    def test_operator_different_category_raises(
        self, report_service, mock_report_repository,
    ):
        """Un operator di un'altra categoria non può accedere."""
        # Arrange
        report = _make_report(status=ReportStatus.PENDING_APPROVAL, category_id=5, reporter_id=10)
        mock_report_repository.get_by_id.return_value = report
        operator = _make_user(user_id=99, role=Role.OPERATOR, category_id=99)

        # Act & Assert
        with pytest.raises(AuthorizationError):
            report_service.get_accessible_report(1, user=operator)

    def test_other_citizen_cannot_access_non_public(
        self, report_service, mock_report_repository,
    ):
        """Un citizen diverso dal reporter non può accedere a un report non pubblico."""
        # Arrange
        report = _make_report(status=ReportStatus.PENDING_APPROVAL, reporter_id=10)
        mock_report_repository.get_by_id.return_value = report
        stranger = _make_user(user_id=99, role=Role.CITIZEN)

        # Act & Assert
        with pytest.raises(AuthorizationError):
            report_service.get_accessible_report(1, user=stranger)


# ---------------------------------------------------------------------------
# follow / unfollow
# ---------------------------------------------------------------------------

class TestFollowReport:
    """Test suite per follow_report e unfollow_report."""

    def test_follow_non_public_report_raises(
        self, report_service, mock_report_repository,
    ):
        """Errore se si prova a seguire un report non pubblico."""
        # Arrange
        report = _make_report(status=ReportStatus.PENDING_APPROVAL)
        mock_report_repository.get_by_id.return_value = report

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            report_service.follow_report(1, _make_user())

        assert "published" in str(exc_info.value)

    def test_follow_already_following_is_idempotent(
        self, report_service, mock_report_repository,
    ):
        """Seguire un report già seguito non crea un duplicato."""
        # Arrange
        report = _make_report(status=ReportStatus.ASSIGNED)
        mock_report_repository.get_by_id.return_value = report
        mock_report_repository.get_follower.return_value = Mock()  # already following

        # Act
        report_service.follow_report(1, _make_user())

        # Assert
        mock_report_repository.add_follower.assert_not_called()

    def test_unfollow_when_not_following(
        self, report_service, mock_report_repository, mock_session,
    ):
        """Unfollow quando non si sta seguendo non fa nulla."""
        # Arrange
        report = _make_report()
        mock_report_repository.get_by_id.return_value = report
        mock_report_repository.get_follower.return_value = None

        # Act
        report_service.unfollow_report(1, _make_user())

        # Assert
        mock_report_repository.remove_follower.assert_not_called()


# ---------------------------------------------------------------------------
# assign_report
# ---------------------------------------------------------------------------

class TestAssignReport:
    """Test suite per il metodo assign_report."""

    def test_citizen_cannot_assign(self, report_service):
        """Un citizen non può assegnare report."""
        # Arrange
        citizen = _make_user(role=Role.CITIZEN)

        # Act & Assert
        with pytest.raises(AuthorizationError) as exc_info:
            report_service.assign_report(1, citizen)

        assert "Only operators or admins" in str(exc_info.value)


# ---------------------------------------------------------------------------
# export_rows
# ---------------------------------------------------------------------------

class TestExportRows:
    """Test suite per il metodo export_rows."""

    def test_export_rows_returns_formatted_list(
        self, report_service, mock_report_repository,
    ):
        """export_rows restituisce una lista di dict con i campi corretti."""
        # Arrange
        report = Mock(spec=Report)
        report.id = 1
        report.title = "Pothole"
        report.status = ReportStatus.ASSIGNED
        report.latitude = 45.0
        report.longitude = 9.0
        report.created_at = datetime(2025, 6, 1, 12, 0)
        category = Mock()
        category.name = "Roads"
        report.category = category
        mock_report_repository.list_reports.return_value = [report]

        # Act
        rows = report_service.export_rows()

        # Assert
        assert len(rows) == 1
        assert rows[0]["id"] == 1
        assert rows[0]["title"] == "Pothole"
        assert rows[0]["category"] == "Roads"
        assert rows[0]["status"] == "Assigned"
        assert rows[0]["latitude"] == 45.0

    def test_export_rows_empty_list(self, report_service, mock_report_repository):
        """export_rows restituisce lista vuota se non ci sono report."""
        # Arrange
        mock_report_repository.list_reports.return_value = []

        # Act
        rows = report_service.export_rows()

        # Assert
        assert rows == []


# ---------------------------------------------------------------------------
# _recipients
# ---------------------------------------------------------------------------

class TestRecipients:
    """Test suite per il metodo statico _recipients."""

    def test_recipients_includes_reporter_and_followers(self):
        """Include il reporter e tutti i follower."""
        # Arrange
        reporter = _make_user(user_id=1)
        follower_obj = Mock()
        follower_obj.user = _make_user(user_id=2)

        report = Mock(spec=Report)
        report.reporter = reporter
        report.followers = [follower_obj]

        # Act
        recipients = ReportService._recipients(report)

        # Assert
        ids = {r.id for r in recipients}
        assert ids == {1, 2}

    def test_recipients_filters_none_reporter(self):
        """Se il reporter è None (cancellato), non lo include."""
        # Arrange
        follower_obj = Mock()
        follower_obj.user = _make_user(user_id=2)

        report = Mock(spec=Report)
        report.reporter = None
        report.followers = [follower_obj]

        # Act
        recipients = ReportService._recipients(report)

        # Assert
        assert len(recipients) == 1
        assert recipients[0].id == 2

    def test_recipients_empty_followers_and_reporter(self):
        """Se non c'è reporter e non ci sono follower, lista vuota."""
        # Arrange
        report = Mock(spec=Report)
        report.reporter = None
        report.followers = []

        # Act
        recipients = ReportService._recipients(report)

        # Assert
        assert recipients == []


# ---------------------------------------------------------------------------
# _ensure_operator_category_access
# ---------------------------------------------------------------------------

class TestEnsureOperatorCategoryAccess:
    """Test suite per il metodo statico _ensure_operator_category_access."""

    def test_admin_always_ok(self):
        """Un admin passa sempre il controllo."""
        # Arrange
        admin = _make_user(role=Role.ADMIN)
        report = _make_report(category_id=99)

        # Act & Assert — nessuna eccezione
        ReportService._ensure_operator_category_access(admin, report)

    def test_non_operator_raises(self):
        """Un citizen non può gestire report."""
        # Arrange
        citizen = _make_user(role=Role.CITIZEN)
        report = _make_report()

        # Act & Assert
        with pytest.raises(AuthorizationError) as exc_info:
            ReportService._ensure_operator_category_access(citizen, report)

        assert "Only operators" in str(exc_info.value)

    def test_operator_wrong_category_raises(self):
        """Un operator con categoria diversa non può accedere."""
        # Arrange
        operator = _make_user(role=Role.OPERATOR, category_id=1)
        report = _make_report(category_id=99)

        # Act & Assert
        with pytest.raises(AuthorizationError) as exc_info:
            ReportService._ensure_operator_category_access(operator, report)

        assert "does not belong" in str(exc_info.value)
