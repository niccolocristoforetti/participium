from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock

import pytest

from participium.models.enums import ReportStatus
from participium.services.statistics_service import StatisticsService


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

_UNSET = object()


def _make_report(*, category_name="Infrastructure", status=ReportStatus.ASSIGNED,
                 reporter_username="alice", reporter_id=1, reporter=_UNSET,
                 created_at=None):
    """Helper per creare un Mock di Report con relazioni annesse."""
    report = Mock()
    report.status = status
    report.created_at = created_at or datetime(2025, 3, 15, 10, 0)

    category = Mock()
    category.name = category_name
    report.category = category

    if reporter is not _UNSET:
        report.reporter = reporter
    else:
        mock_reporter = Mock()
        mock_reporter.username = reporter_username
        mock_reporter.id = reporter_id
        report.reporter = mock_reporter

    return report


class TestPublicStatistics:
    """Test suite per il metodo public_statistics."""

    def test_public_statistics_empty_reports(self, statistics_service, mock_report_repository):
        """Statistiche pubbliche con zero report restituiscono contatori vuoti."""
        # Arrange
        mock_report_repository.list_reports.return_value = []

        # Act
        result = statistics_service.public_statistics()

        # Assert
        assert result["total_reports"] == 0
        assert result["reports_by_category"] == {}
        assert result["trends"] == {}

    def test_public_statistics_counts_by_category(self, statistics_service, mock_report_repository):
        """Le statistiche raggruppano correttamente i report per categoria."""
        # Arrange
        reports = [
            _make_report(category_name="Infrastructure", created_at=datetime(2025, 3, 1)),
            _make_report(category_name="Infrastructure", created_at=datetime(2025, 3, 2)),
            _make_report(category_name="Environment", created_at=datetime(2025, 3, 3)),
        ]
        mock_report_repository.list_reports.return_value = reports

        # Act
        result = statistics_service.public_statistics()

        # Assert
        assert result["total_reports"] == 3
        assert result["reports_by_category"] == {"Infrastructure": 2, "Environment": 1}

    def test_public_statistics_trends_day_granularity(self, statistics_service, mock_report_repository):
        """Trend con granularità day aggrega per data YYYY-MM-DD."""
        # Arrange
        reports = [
            _make_report(created_at=datetime(2025, 3, 10, 8, 0)),
            _make_report(created_at=datetime(2025, 3, 10, 14, 0)),
            _make_report(created_at=datetime(2025, 3, 11, 9, 0)),
        ]
        mock_report_repository.list_reports.return_value = reports

        # Act
        result = statistics_service.public_statistics(granularity="day")

        # Assert
        assert result["trends"] == {"2025-03-10": 2, "2025-03-11": 1}

    def test_public_statistics_trends_week_granularity(self, statistics_service, mock_report_repository):
        """Trend con granularità week aggrega per settimana ISO YYYY-Www."""
        # Arrange
        reports = [
            _make_report(created_at=datetime(2025, 1, 6)),   # settimana 02
            _make_report(created_at=datetime(2025, 1, 13)),  # settimana 03
        ]
        mock_report_repository.list_reports.return_value = reports

        # Act
        result = statistics_service.public_statistics(granularity="week")

        # Assert
        keys = list(result["trends"].keys())
        assert all(k.startswith("2025-W") for k in keys)
        assert sum(result["trends"].values()) == 2

    def test_public_statistics_trends_month_granularity(self, statistics_service, mock_report_repository):
        """Trend con granularità month aggrega per mese YYYY-MM."""
        # Arrange
        reports = [
            _make_report(created_at=datetime(2025, 1, 15)),
            _make_report(created_at=datetime(2025, 2, 20)),
            _make_report(created_at=datetime(2025, 2, 25)),
        ]
        mock_report_repository.list_reports.return_value = reports

        # Act
        result = statistics_service.public_statistics(granularity="month")

        # Assert
        assert result["trends"] == {"2025-01": 1, "2025-02": 2}


class TestAdminStatistics:
    """Test suite per il metodo admin_statistics."""

    def test_admin_statistics_empty_reports(self, statistics_service, mock_report_repository):
        """Statistiche admin con zero report restituiscono dizionari vuoti."""
        # Arrange
        mock_report_repository.list_all.return_value = []

        # Act
        result = statistics_service.admin_statistics()

        # Assert
        assert result["reports_by_status"] == {}
        assert result["reports_by_type"] == {}
        assert result["top_1_percent_by_type"] == {}
        assert result["top_5_percent_by_type"] == {}

    def test_admin_statistics_full_breakdown(self, statistics_service, mock_report_repository):
        """Statistiche admin con più report e reporter diversi."""
        # Arrange
        reports = [
            _make_report(category_name="Roads", status=ReportStatus.ASSIGNED,
                         reporter_username="alice", reporter_id=10),
            _make_report(category_name="Roads", status=ReportStatus.RESOLVED,
                         reporter_username="alice", reporter_id=10),
            _make_report(category_name="Environment", status=ReportStatus.ASSIGNED,
                         reporter_username="bob", reporter_id=20),
        ]
        mock_report_repository.list_all.return_value = reports

        # Act
        result = statistics_service.admin_statistics()

        # Assert
        assert result["reports_by_status"] == {"Assigned": 2, "Resolved": 1}
        assert result["reports_by_type"] == {"Roads": 2, "Environment": 1}
        assert "Roads | Assigned" in result["reports_by_type_and_status"]
        assert "alice (10)" in result["reports_by_reporter"]
        assert "bob (20)" in result["reports_by_reporter"]
        assert isinstance(result["top_1_percent_by_type"], dict)
        assert isinstance(result["top_5_percent_by_type"], dict)

    def test_admin_statistics_deleted_reporter(self, statistics_service, mock_report_repository):
        """Un reporter cancellato viene etichettato come 'Deleted Citizen'."""
        # Arrange
        reports = [_make_report(reporter=None)]
        mock_report_repository.list_all.return_value = reports

        # Act
        result = statistics_service.admin_statistics()

        # Assert
        assert "Deleted Citizen" in result["reports_by_reporter"]

    def test_admin_statistics_top_percent_single_reporter(self, statistics_service, mock_report_repository):
        """Con un solo reporter, top 1% e top 5% includono tutti i suoi report."""
        # Arrange
        reports = [
            _make_report(category_name="Roads", reporter_username="alice", reporter_id=10)
            for _ in range(5)
        ]
        mock_report_repository.list_all.return_value = reports

        # Act
        result = statistics_service.admin_statistics()

        # Assert
        assert result["top_1_percent_by_type"] == {"Roads": 5}
        assert result["top_5_percent_by_type"] == {"Roads": 5}
