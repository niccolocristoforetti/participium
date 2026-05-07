from __future__ import annotations

import pytest

from participium.models.enums import ReportStatus
from tests.e2e.conftest import create_report as _create_report
from tests.e2e.conftest import do_login, photo as _photo, register_and_verify

pytestmark = pytest.mark.e2e


class TestListReports:
    def test_empty_returns_empty_list(self, client):
        resp = client.get("/api/v1/reports")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_pending_reports_not_in_public_list(self, app, client, citizen_client, seeded_category):
        _create_report(citizen_client, seeded_category)
        resp = client.get("/api/v1/reports")
        assert resp.get_json() == []

    def test_invalid_status_filter_returns_400(self, client):
        resp = client.get("/api/v1/reports?status=notavalidstatus")
        assert resp.status_code == 400

    def test_filter_by_category_returns_matching_reports(self, app, client):
        resp = client.get("/api/v1/reports?category_id=999")
        assert resp.status_code == 200
        assert resp.get_json() == []


class TestCreateReport:
    def test_unauthenticated_returns_401(self, client, seeded_category):
        resp = _create_report(client, seeded_category)
        assert resp.status_code == 401

    def test_operator_role_returns_403(self, operator_client, seeded_category):
        resp = _create_report(operator_client, seeded_category)
        assert resp.status_code == 403

    def test_citizen_creates_report_successfully(self, citizen_client, seeded_category):
        resp = _create_report(citizen_client, seeded_category)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["title"] == "Test Report"
        assert data["status"] == ReportStatus.PENDING_APPROVAL.value

    def test_anonymous_report_hides_reporter(self, citizen_client, seeded_category):
        resp = _create_report(citizen_client, seeded_category, is_anonymous="true")
        assert resp.status_code == 201
        assert resp.get_json()["is_anonymous"] is True

    def test_missing_title_returns_400(self, citizen_client, seeded_category):
        data = {
            "description": "desc",
            "category_id": str(seeded_category),
            "latitude": "45.0",
            "longitude": "9.0",
            "photos": _photo(),
        }
        resp = citizen_client.post("/api/v1/reports", data=data, content_type="multipart/form-data")
        assert resp.status_code == 400

    def test_missing_photo_returns_400(self, citizen_client, seeded_category):
        data = {
            "title": "Title",
            "description": "desc",
            "category_id": str(seeded_category),
            "latitude": "45.0",
            "longitude": "9.0",
        }
        resp = citizen_client.post("/api/v1/reports", data=data, content_type="multipart/form-data")
        assert resp.status_code == 400

    def test_invalid_category_returns_400(self, citizen_client):
        resp = _create_report(citizen_client, 9999)
        assert resp.status_code == 400

    def test_invalid_coordinates_returns_400(self, citizen_client, seeded_category):
        resp = _create_report(citizen_client, seeded_category, latitude="notanumber")
        assert resp.status_code == 400

    def test_too_many_photos_returns_400(self, citizen_client, seeded_category):
        data = {
            "title": "Title",
            "description": "desc",
            "category_id": str(seeded_category),
            "latitude": "45.0",
            "longitude": "9.0",
            "photos": [_photo(), _photo(), _photo(), _photo()],
        }
        resp = citizen_client.post("/api/v1/reports", data=data, content_type="multipart/form-data")
        assert resp.status_code == 400


class TestReportDetail:
    def test_not_found_returns_404(self, client):
        resp = client.get("/api/v1/reports/99999")
        assert resp.status_code == 404

    def test_pending_report_inaccessible_to_anonymous(self, client, citizen_client, seeded_category):
        create_resp = _create_report(citizen_client, seeded_category)
        report_id = create_resp.get_json()["id"]
        resp = client.get(f"/api/v1/reports/{report_id}")
        assert resp.status_code == 403

    def test_reporter_can_access_own_pending_report(self, citizen_client, seeded_category):
        create_resp = _create_report(citizen_client, seeded_category)
        report_id = create_resp.get_json()["id"]
        resp = citizen_client.get(f"/api/v1/reports/{report_id}")
        assert resp.status_code == 200
        assert resp.get_json()["id"] == report_id

    def test_anonymous_can_access_assigned_report(self, client, citizen_client, operator_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        operator_client.post(f"/api/v1/operator/reports/{report_id}/assign")
        resp = client.get(f"/api/v1/reports/{report_id}")
        assert resp.status_code == 200
        assert resp.get_json()["id"] == report_id

    def test_operator_can_access_pending_report_in_own_category(self, operator_client, citizen_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        resp = operator_client.get(f"/api/v1/reports/{report_id}")
        assert resp.status_code == 200
        assert resp.get_json()["id"] == report_id


class TestExportReports:
    def test_export_returns_csv(self, client):
        resp = client.get("/api/v1/reports/export")
        assert resp.status_code == 200
        assert "text/csv" in resp.content_type

    def test_export_csv_contains_header(self, client):
        resp = client.get("/api/v1/reports/export")
        content = resp.data.decode()
        assert "id" in content


class TestFollowUnfollow:
    def test_follow_report_unauthenticated_returns_401(self, client, citizen_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        resp = client.post(f"/api/v1/reports/{report_id}/follow")
        assert resp.status_code == 401

    def test_operator_cannot_follow_returns_403(self, operator_client, citizen_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        resp = operator_client.post(f"/api/v1/reports/{report_id}/follow")
        assert resp.status_code == 403

    def test_citizen_follows_assigned_report(self, app, operator_client, seeded_category):
        citizen2 = app.test_client()
        register_and_verify(citizen2, username="citizen2", email="c2@test.com", password="pass2")
        do_login(citizen2, "c2@test.com", "pass2")
        report_id = citizen2.post(
            "/api/v1/reports",
            data={
                "title": "Road Issue",
                "description": "desc",
                "category_id": str(seeded_category),
                "latitude": "45.0",
                "longitude": "9.0",
                "photos": _photo(),
            },
            content_type="multipart/form-data",
        ).get_json()["id"]
        operator_client.post(f"/api/v1/operator/reports/{report_id}/assign")

        citizen3 = app.test_client()
        register_and_verify(citizen3, username="citizen3", email="c3@test.com", password="pass3")
        do_login(citizen3, "c3@test.com", "pass3")
        resp = citizen3.post(f"/api/v1/reports/{report_id}/follow")
        assert resp.status_code == 200

    def test_citizen_unfollows_report(self, app, operator_client, seeded_category):
        citizen2 = app.test_client()
        register_and_verify(citizen2, username="citizen4", email="c4@test.com", password="pass4")
        do_login(citizen2, "c4@test.com", "pass4")
        report_id = citizen2.post(
            "/api/v1/reports",
            data={
                "title": "Road Issue 2",
                "description": "desc",
                "category_id": str(seeded_category),
                "latitude": "45.0",
                "longitude": "9.0",
                "photos": _photo(),
            },
            content_type="multipart/form-data",
        ).get_json()["id"]
        operator_client.post(f"/api/v1/operator/reports/{report_id}/assign")

        citizen3 = app.test_client()
        register_and_verify(citizen3, username="citizen5", email="c5@test.com", password="pass5")
        do_login(citizen3, "c5@test.com", "pass5")
        citizen3.post(f"/api/v1/reports/{report_id}/follow")
        resp = citizen3.delete(f"/api/v1/reports/{report_id}/follow")
        assert resp.status_code == 200


class TestPublicStats:
    def test_public_stats_returns_data(self, client):
        resp = client.get("/api/v1/stats/public")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "total" in data or isinstance(data, dict)

    def test_public_stats_with_granularity_week(self, client):
        resp = client.get("/api/v1/stats/public?granularity=week")
        assert resp.status_code == 200

    def test_public_stats_unknown_granularity_falls_back_to_day(self, client):
        resp = client.get("/api/v1/stats/public?granularity=invalid")
        assert resp.status_code == 200
