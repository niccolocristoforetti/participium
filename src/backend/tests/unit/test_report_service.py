from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock

import pytest

from participium.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from participium.models.enums import ReportStatus, Role
from participium.models.report import Report
from participium.models.user import User
from participium.services.report_service import ReportService


# Helper

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


# get_accessible_report

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


# follow / unfollow

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


# assign_report

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

    def test_assign_non_pending_report_raises(
        self, report_service, mock_report_repository,
    ):
        """Errore se il report non è in stato PENDING_APPROVAL."""
        # Arrange
        report = _make_report(status=ReportStatus.ASSIGNED, category_id=1)
        mock_report_repository.get_by_id.return_value = report
        operator = _make_user(role=Role.OPERATOR, category_id=1)

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            report_service.assign_report(1, operator)

        assert "pending" in str(exc_info.value)

    def test_assign_report_success(
        self, report_service, mock_report_repository, mock_session,
    ):
        """Assegnazione con successo: status aggiornato, storico aggiunto, commit."""
        # Arrange
        report = _make_report(status=ReportStatus.PENDING_APPROVAL, category_id=1)
        report.category = Mock()
        report.category.name = "Roads"
        assigned_report = Mock(spec=Report)
        mock_report_repository.get_by_id.side_effect = [report, assigned_report]
        operator = _make_user(role=Role.OPERATOR, category_id=1)

        # Act
        result = report_service.assign_report(1, operator)

        # Assert
        assert report.status == ReportStatus.ASSIGNED
        mock_report_repository.add_status_entry.assert_called_once()
        report_service.notification_service.notify_status_change.assert_called_once()
        mock_session.commit.assert_called_once()
        assert result is assigned_report


# export_rows

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

    def test_export_rows_forwards_filters_to_repository(
        self, report_service, mock_report_repository,
    ):
        """export_rows passa correttamente i filtri a list_public_reports → list_reports."""
        # Arrange
        mock_report_repository.list_reports.return_value = []
        from datetime import datetime
        date_from = datetime(2025, 1, 1)
        date_to = datetime(2025, 12, 31)

        # Act
        report_service.export_rows(
            category_id=3,
            status=ReportStatus.ASSIGNED,
            date_from=date_from,
            date_to=date_to,
            sort="asc",
        )

        # Assert
        mock_report_repository.list_reports.assert_called_once_with(
            public_only=True,
            category_id=3,
            status=ReportStatus.ASSIGNED,
            date_from=date_from,
            date_to=date_to,
            sort="asc",
        )


# _recipients

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


# _ensure_operator_category_access

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


# create_report

class TestCreateReport:
    """Test suite per il metodo create_report."""

    def _make_reporter(self):
        reporter = Mock(spec=User)
        reporter.id = 1
        reporter.role = Role.CITIZEN
        return reporter

    def _make_photo(self, filename="photo.jpg"):
        photo = Mock()
        photo.filename = filename
        photo.content_type = "image/jpeg"
        return photo

    def test_invalid_category_id_raises(self, report_service):
        """category_id non convertibile a int solleva ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            report_service.create_report(
                reporter=self._make_reporter(), category_id="abc",
                title="T", description="D", latitude=45.0, longitude=9.0,
                photos=[self._make_photo()],
            )
        assert "valid active category" in str(exc_info.value)

    def test_missing_category_raises(self, report_service, mock_category_repository):
        """category_id None solleva ValidationError."""
        mock_category_repository.get_by_id.return_value = None
        with pytest.raises(ValidationError) as exc_info:
            report_service.create_report(
                reporter=self._make_reporter(), category_id=None,
                title="T", description="D", latitude=45.0, longitude=9.0,
                photos=[self._make_photo()],
            )
        assert "valid active category" in str(exc_info.value)

    def test_inactive_category_raises(self, report_service, mock_category_repository):
        """Categoria inattiva solleva ValidationError."""
        category = Mock()
        category.is_active = False
        mock_category_repository.get_by_id.return_value = category
        with pytest.raises(ValidationError) as exc_info:
            report_service.create_report(
                reporter=self._make_reporter(), category_id=1,
                title="T", description="D", latitude=45.0, longitude=9.0,
                photos=[self._make_photo()],
            )
        assert "valid active category" in str(exc_info.value)

    def test_missing_title_raises(self, report_service, mock_category_repository):
        """Titolo mancante solleva ValidationError."""
        category = Mock()
        category.is_active = True
        mock_category_repository.get_by_id.return_value = category
        with pytest.raises(ValidationError) as exc_info:
            report_service.create_report(
                reporter=self._make_reporter(), category_id=1,
                title=None, description="D", latitude=45.0, longitude=9.0,
                photos=[self._make_photo()],
            )
        assert "Title and description" in str(exc_info.value)

    def test_invalid_coordinates_raises(self, report_service, mock_category_repository):
        """Coordinate non numeriche sollevano ValidationError."""
        category = Mock()
        category.is_active = True
        mock_category_repository.get_by_id.return_value = category
        with pytest.raises(ValidationError) as exc_info:
            report_service.create_report(
                reporter=self._make_reporter(), category_id=1,
                title="T", description="D", latitude="notanumber", longitude=9.0,
                photos=[self._make_photo()],
            )
        assert "valid numbers" in str(exc_info.value)

    def test_no_valid_photos_raises(self, report_service, mock_category_repository):
        """Lista foto vuota solleva ValidationError."""
        category = Mock()
        category.is_active = True
        mock_category_repository.get_by_id.return_value = category
        with pytest.raises(ValidationError) as exc_info:
            report_service.create_report(
                reporter=self._make_reporter(), category_id=1,
                title="T", description="D", latitude=45.0, longitude=9.0,
                photos=[],
            )
        assert "photo" in str(exc_info.value)

    def test_too_many_photos_raises(self, report_service, mock_category_repository):
        """Più di 3 foto sollevano ValidationError."""
        category = Mock()
        category.is_active = True
        mock_category_repository.get_by_id.return_value = category
        photos = [self._make_photo(f"p{i}.jpg") for i in range(4)]
        with pytest.raises(ValidationError) as exc_info:
            report_service.create_report(
                reporter=self._make_reporter(), category_id=1,
                title="T", description="D", latitude=45.0, longitude=9.0,
                photos=photos,
            )
        assert "at most 3" in str(exc_info.value)

    def test_create_report_success(
        self, report_service, mock_category_repository,
        mock_report_repository, mock_storage_service, mock_session,
    ):
        """Creazione con successo: flush, commit, get_report finale."""
        category = Mock()
        category.id = 1
        category.is_active = True
        mock_category_repository.get_by_id.return_value = category

        created_report = Mock(spec=Report)
        created_report.id = 99
        mock_report_repository.add.return_value = None
        mock_report_repository.get_by_id.return_value = created_report
        mock_storage_service.save.return_value = "stored.jpg"

        reporter = self._make_reporter()
        result = report_service.create_report(
            reporter=reporter, category_id=1,
            title="Pothole", description="Big hole",
            latitude=45.0, longitude=9.0,
            photos=[self._make_photo()],
        )

        mock_session.flush.assert_called_once()
        mock_session.commit.assert_called_once()
        assert result is created_report


# update_status

class TestUpdateStatus:
    """Test suite per il metodo update_status."""

    def _operator(self, category_id=1):
        op = Mock(spec=User)
        op.id = 10
        op.role = Role.OPERATOR
        op.category_id = category_id
        return op

    def test_citizen_cannot_update_status(self, report_service):
        """Un citizen non può aggiornare lo status."""
        citizen = Mock(spec=User)
        citizen.role = Role.CITIZEN
        with pytest.raises(AuthorizationError) as exc_info:
            report_service.update_status(1, citizen, "Assigned")
        assert "operators and admins" in str(exc_info.value)

    def test_invalid_status_value_raises(
        self, report_service, mock_report_repository,
    ):
        """Status non valido solleva ValidationError."""
        report = _make_report(status=ReportStatus.ASSIGNED, category_id=1)
        mock_report_repository.get_by_id.return_value = report
        with pytest.raises(ValidationError) as exc_info:
            report_service.update_status(1, self._operator(), "NotAStatus")
        assert "Invalid report status" in str(exc_info.value)

    def test_rejection_without_note_raises(
        self, report_service, mock_report_repository,
    ):
        """Rejection senza nota solleva ValidationError."""
        report = _make_report(status=ReportStatus.PENDING_APPROVAL, category_id=1)
        mock_report_repository.get_by_id.return_value = report
        with pytest.raises(ValidationError) as exc_info:
            report_service.update_status(1, self._operator(), "Rejected", note=None)
        assert "Rejection reason" in str(exc_info.value)

    def test_invalid_transition_raises(
        self, report_service, mock_report_repository,
    ):
        """Transizione non consentita solleva ValidationError."""
        report = _make_report(status=ReportStatus.RESOLVED, category_id=1)
        mock_report_repository.get_by_id.return_value = report
        with pytest.raises(ValidationError):
            report_service.update_status(1, self._operator(), "Pending Approval")

    def test_update_status_success(
        self, report_service, mock_report_repository, mock_session,
    ):
        """Aggiornamento di status con successo: storico aggiunto, notifiche inviate, commit."""
        report = _make_report(status=ReportStatus.ASSIGNED, category_id=1)
        report.category = Mock()
        report.category.name = "Roads"
        updated_report = Mock(spec=Report)
        mock_report_repository.get_by_id.side_effect = [report, updated_report]

        report_service.update_status(1, self._operator(), "In Progress", note="On it")

        mock_report_repository.add_status_entry.assert_called_once()
        report_service.notification_service.notify_status_change.assert_called_once()
        mock_session.commit.assert_called_once()