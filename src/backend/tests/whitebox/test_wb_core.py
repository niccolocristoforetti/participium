from __future__ import annotations

from unittest.mock import Mock

import pytest

import flask

from participium.core.auth import login_required, roles_required
from participium.core.exceptions import (
    AuthenticationError,
    DomainError,
    ValidationError,
)
from participium.core.serialization import _serialize_party, _serialize_reporter
from participium.core.status_flow import ensure_transition_allowed
from participium.core.utils import parse_date
from participium.models.enums import ReportStatus, Role
from participium.models.report import Report
from participium.models.user import User

pytestmark = pytest.mark.whitebox


# ---------------------------------------------------------------------------
# exceptions.py
# ---------------------------------------------------------------------------

class TestDomainError:
    def test_custom_status_code_is_stored(self):
        err = DomainError("msg", status_code=422)
        assert err.status_code == 422

    def test_default_status_code_unchanged_when_none(self):
        err = DomainError("msg")
        assert err.status_code == 400


# ---------------------------------------------------------------------------
# status_flow.py
# ---------------------------------------------------------------------------

class TestEnsureTransitionAllowed:
    def test_valid_transition_returns_true(self):
        result = ensure_transition_allowed(ReportStatus.PENDING_APPROVAL, ReportStatus.ASSIGNED)
        assert result is True

    def test_invalid_transition_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ensure_transition_allowed(ReportStatus.ASSIGNED, ReportStatus.PENDING_APPROVAL)

    def test_self_transition_always_allowed(self):
        assert ensure_transition_allowed(ReportStatus.RESOLVED, ReportStatus.RESOLVED) is True


# ---------------------------------------------------------------------------
# utils.py
# ---------------------------------------------------------------------------

class TestParseDate:
    def test_none_returns_none(self):
        assert parse_date(None) is None

    def test_empty_string_returns_none(self):
        assert parse_date("") is None

    def test_valid_iso_string_returns_datetime(self):
        result = parse_date("2024-01-15T10:30:00")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1

    def test_invalid_string_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_date("not-a-date")


# ---------------------------------------------------------------------------
# serialization.py — _serialize_party
# ---------------------------------------------------------------------------

class TestSerializeParty:
    def test_none_user_returns_deleted_user(self):
        result = _serialize_party(None)
        assert result["id"] is None
        assert result["display_name"] == "Deleted User"
        assert result["role"] is None


# ---------------------------------------------------------------------------
# serialization.py — _serialize_reporter
# ---------------------------------------------------------------------------

def _make_report(*, is_anonymous=False, reporter=None, reporter_id=None, category_id=1):
    report = Mock(spec=Report)
    report.is_anonymous = is_anonymous
    report.reporter = reporter
    report.reporter_id = reporter_id
    report.category_id = category_id
    report.followers = []
    report.status = ReportStatus.ASSIGNED
    report.photos = []
    return report


def _make_user(role=Role.CITIZEN, user_id=1, category_id=None):
    user = Mock(spec=User)
    user.id = user_id
    user.role = role
    user.category_id = category_id
    user.first_name = "Test"
    user.last_name = "User"
    user.username = "testuser"
    user.category = None
    return user


class TestSerializeReporter:
    def test_deleted_reporter_returns_deleted_citizen(self):
        report = _make_report(reporter=None)
        result = _serialize_reporter(report, viewer=None)
        assert result["display_name"] == "Deleted Citizen"
        assert result["id"] is None

    def test_non_anonymous_report_shows_reporter(self):
        reporter = _make_user(role=Role.CITIZEN, user_id=5)
        report = _make_report(is_anonymous=False, reporter=reporter, reporter_id=5)
        result = _serialize_reporter(report, viewer=None)
        assert result["id"] == 5

    def test_anonymous_report_viewer_none_hides_reporter(self):
        reporter = _make_user(user_id=5)
        report = _make_report(is_anonymous=True, reporter=reporter, reporter_id=5)
        result = _serialize_reporter(report, viewer=None)
        assert result["display_name"] == "Anonymous Citizen"
        assert result["id"] is None

    def test_anonymous_report_admin_viewer_sees_reporter(self):
        reporter = _make_user(user_id=5)
        admin = _make_user(role=Role.ADMIN, user_id=99)
        report = _make_report(is_anonymous=True, reporter=reporter, reporter_id=5, category_id=1)
        result = _serialize_reporter(report, viewer=admin)
        assert result["id"] == 5

    def test_anonymous_report_operator_same_cat_sees_reporter(self):
        reporter = _make_user(user_id=5)
        operator = _make_user(role=Role.OPERATOR, user_id=10, category_id=1)
        report = _make_report(is_anonymous=True, reporter=reporter, reporter_id=5, category_id=1)
        result = _serialize_reporter(report, viewer=operator)
        assert result["id"] == 5

    def test_anonymous_report_other_citizen_hides_reporter(self):
        reporter = _make_user(user_id=5)
        other = _make_user(role=Role.CITIZEN, user_id=99)
        report = _make_report(is_anonymous=True, reporter=reporter, reporter_id=5)
        result = _serialize_reporter(report, viewer=other)
        assert result["display_name"] == "Anonymous Citizen"
        assert result["id"] is None


# ---------------------------------------------------------------------------
# auth.py — login_required e roles_required
# ---------------------------------------------------------------------------

class TestAuthDecorators:
    def test_login_required_redirects_on_non_api_path(self):
        mini_app = flask.Flask(__name__)
        web_bp = flask.Blueprint("web", __name__)

        @web_bp.route("/login")
        def login():
            return "login page"

        mini_app.register_blueprint(web_bp)

        @mini_app.route("/dashboard")
        @login_required
        def dashboard():
            return "ok"

        with mini_app.test_client() as c:
            resp = c.get("/dashboard")
            assert resp.status_code == 302

    def test_roles_required_raises_authentication_error_when_no_user(self):
        mini_app = flask.Flask(__name__)

        @mini_app.errorhandler(AuthenticationError)
        def handle_auth(e):
            return flask.jsonify({"error": str(e)}), 401

        @mini_app.route("/admin")
        @roles_required(Role.ADMIN)
        def admin_view():
            return "ok"

        with mini_app.test_client() as c:
            resp = c.get("/admin")
            assert resp.status_code == 401
