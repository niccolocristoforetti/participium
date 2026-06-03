from __future__ import annotations

import pytest

from participium import create_app
from participium.database import close_connection
from tests.e2e.conftest import do_login, register_and_verify

pytestmark = pytest.mark.e2e


@pytest.fixture
def client_no_verification_links(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("AUTO_INIT_DB", "true")
    monkeypatch.setenv("BOOTSTRAP_REFERENCE_DATA", "false")
    monkeypatch.setenv("BOOTSTRAP_DEMO_DATA", "false")
    monkeypatch.setenv("EXPOSE_VERIFICATION_LINKS", "false")
    monkeypatch.setenv("MAIL_BACKEND", "console")
    monkeypatch.setenv("MEDIA_ROOT", str(tmp_path / "uploads"))
    application = create_app()
    application.config.update(TESTING=True)
    yield application.test_client()
    close_connection()


class TestHealth:
    def test_health_returns_ok(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "ok"}


class TestReferenceData:
    def test_reference_data_contains_roles_and_statuses(self, client):
        resp = client.get("/api/v1/meta/reference-data")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "roles" in data
        assert "report_statuses" in data
        assert "public_report_statuses" in data
        assert "citizen" in data["roles"]


class TestRegister:
    def test_register_creates_citizen_account(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "securepass",
                "first_name": "New",
                "last_name": "User",
            },
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["user"]["username"] == "newuser"
        assert data["user"]["email"] == "newuser@test.com"
        assert data["user"]["role"] == "citizen"

    def test_register_returns_verification_url(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "username": "verifyuser",
                "email": "verify@test.com",
                "password": "securepass",
                "first_name": "V",
                "last_name": "User",
            },
        )
        assert resp.status_code == 201
        assert "verification_url" in resp.get_json()

    def test_register_missing_username_returns_400(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": "x@test.com", "password": "pass", "first_name": "X", "last_name": "Y"},
        )
        assert resp.status_code == 400

    def test_register_missing_email_returns_400(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": "x", "password": "pass", "first_name": "X", "last_name": "Y"},
        )
        assert resp.status_code == 400

    def test_register_duplicate_email_returns_400(self, client):
        payload = {
            "username": "first",
            "email": "dup@test.com",
            "password": "pass",
            "first_name": "A",
            "last_name": "B",
        }
        client.post("/api/v1/auth/register", json=payload)
        payload["username"] = "second"
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 400

    def test_register_without_verification_link_exposed(self, client_no_verification_links):
        resp = client_no_verification_links.post(
            "/api/v1/auth/register",
            json={
                "username": "nolink",
                "email": "nolink@test.com",
                "password": "securepass",
                "first_name": "No",
                "last_name": "Link",
            },
        )
        assert resp.status_code == 201
        assert "verification_url" not in resp.get_json()

    def test_register_duplicate_username_returns_400(self, client):
        payload = {
            "username": "sameuser",
            "email": "first@test.com",
            "password": "pass",
            "first_name": "A",
            "last_name": "B",
        }
        client.post("/api/v1/auth/register", json=payload)
        payload["email"] = "second@test.com"
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 400


class TestVerifyEmail:
    def test_verify_valid_token_succeeds(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "username": "toverify",
                "email": "toverify@test.com",
                "password": "pass",
                "first_name": "V",
                "last_name": "U",
            },
        )
        token = resp.get_json()["verification_url"].split("/")[-1]
        resp = client.get(f"/api/v1/auth/verify/{token}")
        assert resp.status_code == 200
        assert resp.get_json()["user"]["is_email_verified"] is True

    def test_verify_invalid_token_returns_400(self, client):
        resp = client.get("/api/v1/auth/verify/notavalidtoken")
        assert resp.status_code == 400

    def test_verify_already_used_token_returns_400(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "username": "doubleverify",
                "email": "doubleverify@test.com",
                "password": "pass",
                "first_name": "D",
                "last_name": "V",
            },
        )
        token = resp.get_json()["verification_url"].split("/")[-1]
        client.get(f"/api/v1/auth/verify/{token}")
        resp = client.get(f"/api/v1/auth/verify/{token}")
        assert resp.status_code == 400


class TestLogin:
    def test_login_with_valid_email_returns_200(self, client):
        register_and_verify(client, username="loginuser", email="login@test.com", password="pass123")
        resp = do_login(client, "login@test.com", "pass123")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["user"]["email"] == "login@test.com"
        assert "message" in data

    def test_login_with_username_returns_200(self, client):
        register_and_verify(client, username="loginbyname", email="byname@test.com", password="pass123")
        resp = do_login(client, "loginbyname", "pass123")
        assert resp.status_code == 200

    def test_login_wrong_password_returns_401(self, client):
        register_and_verify(client, username="wrongpass", email="wrongpass@test.com", password="correct")
        resp = do_login(client, "wrongpass@test.com", "incorrect")
        assert resp.status_code == 401

    def test_login_unknown_user_returns_401(self, client):
        resp = do_login(client, "nobody@test.com", "pass")
        assert resp.status_code == 401

    def test_login_unverified_email_returns_401(self, client):
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "unverified",
                "email": "unverified@test.com",
                "password": "pass",
                "first_name": "U",
                "last_name": "V",
            },
        )
        resp = do_login(client, "unverified@test.com", "pass")
        assert resp.status_code == 401


class TestLogout:
    def test_logout_when_authenticated_returns_200(self, citizen_client):
        resp = citizen_client.post("/api/v1/auth/logout")
        assert resp.status_code == 200
        assert "Logged out" in resp.get_json()["message"]

    def test_logout_when_not_authenticated_returns_200(self, client):
        resp = client.post("/api/v1/auth/logout")
        assert resp.status_code == 200
