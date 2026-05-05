from __future__ import annotations

import pytest

from tests.e2e.conftest import create_report as _create_report

pytestmark = pytest.mark.e2e


class TestPendingReports:
    def test_unauthenticated_returns_401(self, client):
        resp = client.get("/api/v1/operator/reports/pending")
        assert resp.status_code == 401

    def test_citizen_returns_403(self, citizen_client):
        resp = citizen_client.get("/api/v1/operator/reports/pending")
        assert resp.status_code == 403

    def test_operator_returns_empty_list(self, operator_client):
        resp = operator_client.get("/api/v1/operator/reports/pending")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_operator_sees_pending_reports(self, operator_client, citizen_client, seeded_category):
        _create_report(citizen_client, seeded_category)
        resp = operator_client.get("/api/v1/operator/reports/pending")
        assert resp.status_code == 200
        assert len(resp.get_json()) == 1


class TestAssignedReports:
    def test_unauthenticated_returns_401(self, client):
        resp = client.get("/api/v1/operator/reports/assigned")
        assert resp.status_code == 401

    def test_citizen_returns_403(self, citizen_client):
        resp = citizen_client.get("/api/v1/operator/reports/assigned")
        assert resp.status_code == 403

    def test_operator_returns_list(self, operator_client):
        resp = operator_client.get("/api/v1/operator/reports/assigned")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)


class TestAssignReport:
    def test_unauthenticated_returns_401(self, client):
        resp = client.post("/api/v1/operator/reports/1/assign")
        assert resp.status_code == 401

    def test_citizen_returns_403(self, citizen_client):
        resp = citizen_client.post("/api/v1/operator/reports/1/assign")
        assert resp.status_code == 403

    def test_assign_nonexistent_report_returns_404(self, operator_client):
        resp = operator_client.post("/api/v1/operator/reports/99999/assign")
        assert resp.status_code == 404

    def test_assign_pending_report_succeeds(self, operator_client, citizen_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        resp = operator_client.post(f"/api/v1/operator/reports/{report_id}/assign")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "Assigned"

    def test_assign_already_assigned_report_returns_400(self, operator_client, citizen_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        operator_client.post(f"/api/v1/operator/reports/{report_id}/assign")
        resp = operator_client.post(f"/api/v1/operator/reports/{report_id}/assign")
        assert resp.status_code == 400


class TestUpdateReportStatus:
    def test_unauthenticated_returns_401(self, client):
        resp = client.post("/api/v1/operator/reports/1/status", json={"status": "In Progress"})
        assert resp.status_code == 401

    def test_citizen_returns_403(self, citizen_client):
        resp = citizen_client.post("/api/v1/operator/reports/1/status", json={"status": "Resolved"})
        assert resp.status_code == 403

    def test_invalid_status_returns_400(self, operator_client, citizen_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        operator_client.post(f"/api/v1/operator/reports/{report_id}/assign")
        resp = operator_client.post(
            f"/api/v1/operator/reports/{report_id}/status",
            json={"status": "NotAStatus"},
        )
        assert resp.status_code == 400

    def test_update_status_to_in_progress(self, operator_client, citizen_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        operator_client.post(f"/api/v1/operator/reports/{report_id}/assign")
        resp = operator_client.post(
            f"/api/v1/operator/reports/{report_id}/status",
            json={"status": "In Progress", "note": "Working on it"},
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "In Progress"

    def test_update_status_to_resolved(self, operator_client, citizen_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        operator_client.post(f"/api/v1/operator/reports/{report_id}/assign")
        operator_client.post(
            f"/api/v1/operator/reports/{report_id}/status",
            json={"status": "In Progress"},
        )
        resp = operator_client.post(
            f"/api/v1/operator/reports/{report_id}/status",
            json={"status": "Resolved"},
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "Resolved"


class TestMessaging:
    def test_list_messages_unauthenticated_returns_401(self, client, citizen_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        resp = client.get(f"/api/v1/reports/{report_id}/messages")
        assert resp.status_code == 401

    def test_list_messages_for_own_report(self, citizen_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        resp = citizen_client.get(f"/api/v1/reports/{report_id}/messages")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_send_message_unauthenticated_returns_401(self, client, citizen_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        resp = client.post(f"/api/v1/reports/{report_id}/messages", json={"body": "Hello"})
        assert resp.status_code == 401

    def test_operator_sends_message_to_assigned_report(self, operator_client, citizen_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        operator_client.post(f"/api/v1/operator/reports/{report_id}/assign")
        resp = operator_client.post(
            f"/api/v1/reports/{report_id}/messages", json={"body": "We are on it"}
        )
        assert resp.status_code == 201
        assert resp.get_json()["body"] == "We are on it"

    def test_citizen_replies_after_operator_message(self, operator_client, citizen_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        operator_client.post(f"/api/v1/operator/reports/{report_id}/assign")
        operator_client.post(
            f"/api/v1/reports/{report_id}/messages", json={"body": "We are on it"}
        )
        resp = citizen_client.post(
            f"/api/v1/reports/{report_id}/messages", json={"body": "Thank you"}
        )
        assert resp.status_code == 201
        assert resp.get_json()["body"] == "Thank you"

    def test_citizen_cannot_message_without_prior_operator_contact(self, citizen_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        resp = citizen_client.post(
            f"/api/v1/reports/{report_id}/messages", json={"body": "Hello?"}
        )
        assert resp.status_code == 400

    def test_send_empty_message_returns_400(self, citizen_client, seeded_category):
        report_id = _create_report(citizen_client, seeded_category).get_json()["id"]
        resp = citizen_client.post(
            f"/api/v1/reports/{report_id}/messages", json={"body": ""}
        )
        assert resp.status_code == 400
