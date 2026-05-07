from __future__ import annotations

import io

import pytest

from participium.core.security import hash_password
from participium.database import get_session
from participium.models.enums import Role
from participium.models.user import User
from tests.e2e.conftest import do_login, photo, register_and_verify

pytestmark = pytest.mark.e2e


class TestMe:
    def test_unauthenticated_returns_401(self, client):
        resp = client.get("/api/v1/users/me")
        assert resp.status_code == 401

    def test_returns_authenticated_user_profile(self, citizen_client):
        resp = citizen_client.get("/api/v1/users/me")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["username"] == "citizen1"
        assert data["email"] == "citizen@test.com"
        assert data["role"] == "citizen"


class TestUpdateMe:
    def test_unauthenticated_returns_401(self, client):
        resp = client.put("/api/v1/users/me", json={"first_name": "X"})
        assert resp.status_code == 401

    def test_update_first_name(self, citizen_client):
        resp = citizen_client.put("/api/v1/users/me", json={"first_name": "UpdatedName"})
        assert resp.status_code == 200
        assert resp.get_json()["first_name"] == "UpdatedName"

    def test_update_username(self, citizen_client):
        resp = citizen_client.put("/api/v1/users/me", json={"username": "citizen1_renamed"})
        assert resp.status_code == 200
        assert resp.get_json()["username"] == "citizen1_renamed"

    def test_duplicate_username_returns_400(self, client):
        register_and_verify(client, username="user_a", email="usera@test.com", password="pass")
        register_and_verify(client, username="user_b", email="userb@test.com", password="pass")
        client.post("/api/v1/auth/login", json={"identifier": "usera@test.com", "password": "pass"})
        resp = client.put("/api/v1/users/me", json={"username": "user_b"})
        assert resp.status_code == 400

    def test_update_email_notifications_via_json(self, citizen_client):
        resp = citizen_client.put(
            "/api/v1/users/me", json={"email_notifications_enabled": False}
        )
        assert resp.status_code == 200
        assert resp.get_json()["email_notifications_enabled"] is False

    def test_upload_profile_picture(self, citizen_client):
        data = {"profile_picture": (io.BytesIO(b"fake image"), "avatar.jpg")}
        resp = citizen_client.put(
            "/api/v1/users/me", data=data, content_type="multipart/form-data"
        )
        assert resp.status_code == 200

    def test_update_username_via_form_data(self, citizen_client):
        resp = citizen_client.put(
            "/api/v1/users/me",
            data={"username": "citizen1_form"},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 200
        assert resp.get_json()["username"] == "citizen1_form"


class TestMyReports:
    def test_unauthenticated_returns_401(self, client):
        resp = client.get("/api/v1/users/me/reports")
        assert resp.status_code == 401

    def test_returns_empty_list_initially(self, citizen_client):
        resp = citizen_client.get("/api/v1/users/me/reports")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_returns_created_reports(self, citizen_client, seeded_category):
        citizen_client.post(
            "/api/v1/reports",
            data={
                "title": "My Report",
                "description": "desc",
                "category_id": str(seeded_category),
                "latitude": "45.0",
                "longitude": "9.0",
                "photos": photo(),
            },
            content_type="multipart/form-data",
        )
        resp = citizen_client.get("/api/v1/users/me/reports")
        assert resp.status_code == 200
        titles = [r["title"] for r in resp.get_json()]
        assert "My Report" in titles


class TestNotifications:
    def test_unauthenticated_returns_401(self, client):
        resp = client.get("/api/v1/users/me/notifications")
        assert resp.status_code == 401

    def test_returns_empty_list_initially(self, citizen_client):
        resp = citizen_client.get("/api/v1/users/me/notifications")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_mark_nonexistent_notification_returns_404(self, citizen_client):
        resp = citizen_client.post("/api/v1/users/me/notifications/9999/read")
        assert resp.status_code == 404

    def test_mark_notification_unauthenticated_returns_401(self, client):
        resp = client.post("/api/v1/users/me/notifications/1/read")
        assert resp.status_code == 401

    def test_mark_notification_as_read_success(self, app, seeded_category):
        citizen = app.test_client()
        register_and_verify(citizen, username="notif_citizen", email="notif@test.com", password="notifpass")
        do_login(citizen, "notif@test.com", "notifpass")

        operator = app.test_client()
        with app.app_context():
            op = User(
                username="notif_op",
                first_name="Op",
                last_name="User",
                email="notifop@test.com",
                password_hash=hash_password("oppass"),
                role=Role.OPERATOR,
                is_active=True,
                is_email_verified=True,
                category_id=seeded_category,
            )
            get_session().add(op)
            get_session().commit()
        do_login(operator, "notifop@test.com", "oppass")

        report_id = citizen.post(
            "/api/v1/reports",
            data={
                "title": "Notif Report",
                "description": "desc",
                "category_id": str(seeded_category),
                "latitude": "45.0",
                "longitude": "9.0",
                "photos": photo(),
            },
            content_type="multipart/form-data",
        ).get_json()["id"]

        operator.post(f"/api/v1/operator/reports/{report_id}/assign")

        notifications = citizen.get("/api/v1/users/me/notifications").get_json()
        assert len(notifications) >= 1
        notif_id = notifications[0]["id"]
        resp = citizen.post(f"/api/v1/users/me/notifications/{notif_id}/read")
        assert resp.status_code == 200
        assert resp.get_json()["is_read"] is True


class TestDeleteAccount:
    def test_unauthenticated_returns_401(self, client):
        resp = client.delete("/api/v1/users/me")
        assert resp.status_code == 401

    def test_deletes_account_and_logs_out(self, citizen_client):
        resp = citizen_client.delete("/api/v1/users/me")
        assert resp.status_code == 200
        assert "deleted" in resp.get_json()["message"].lower()

        resp = citizen_client.get("/api/v1/users/me")
        assert resp.status_code == 401
