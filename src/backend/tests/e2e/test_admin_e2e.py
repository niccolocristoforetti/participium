from __future__ import annotations

import pytest

from participium.database import get_session
from participium.models.category import Category
from tests.e2e.conftest import create_report

pytestmark = pytest.mark.e2e


class TestAdminUsers:
    def test_unauthenticated_returns_401(self, client):
        resp = client.get("/api/v1/admin/users")
        assert resp.status_code == 401

    def test_citizen_returns_403(self, citizen_client):
        resp = citizen_client.get("/api/v1/admin/users")
        assert resp.status_code == 403

    def test_operator_returns_403(self, operator_client):
        resp = operator_client.get("/api/v1/admin/users")
        assert resp.status_code == 403

    def test_admin_lists_users(self, admin_client):
        resp = admin_client.get("/api/v1/admin/users")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_admin_creates_operator_user(self, admin_client, seeded_category):
        resp = admin_client.post(
            "/api/v1/admin/users",
            json={
                "username": "newoperator",
                "email": "newop@test.com",
                "password": "securepass",
                "first_name": "New",
                "last_name": "Op",
                "role": "operator",
                "category_id": seeded_category,
            },
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["username"] == "newoperator"
        assert data["role"] == "operator"

    def test_create_user_missing_fields_returns_400(self, admin_client):
        resp = admin_client.post(
            "/api/v1/admin/users",
            json={"username": "incomplete"},
        )
        assert resp.status_code == 400

    def test_update_user_deactivate(self, admin_client, seeded_admin):
        users = admin_client.get("/api/v1/admin/users").get_json()
        admin_user = next(u for u in users if u["role"] == "admin")
        user_id = admin_user["id"]

        other_resp = admin_client.post(
            "/api/v1/admin/users",
            json={
                "username": "todeactivate",
                "email": "deact@test.com",
                "password": "pass",
                "first_name": "To",
                "last_name": "Deactivate",
                "role": "citizen",
            },
        )
        target_id = other_resp.get_json()["id"]
        resp = admin_client.put(
            f"/api/v1/admin/users/{target_id}",
            json={"is_active": False},
        )
        assert resp.status_code == 200
        assert resp.get_json()["is_active"] is False

    def test_update_nonexistent_user_returns_404(self, admin_client):
        resp = admin_client.put("/api/v1/admin/users/99999", json={"first_name": "X"})
        assert resp.status_code == 404


class TestAdminCategories:
    def test_unauthenticated_returns_401(self, client):
        resp = client.get("/api/v1/admin/categories")
        assert resp.status_code == 401

    def test_citizen_returns_403(self, citizen_client):
        resp = citizen_client.get("/api/v1/admin/categories")
        assert resp.status_code == 403

    def test_admin_lists_all_categories_including_inactive(self, admin_client, app):
        with app.app_context():
            session = get_session()
            session.add(Category(name="ActiveCat", is_active=True))
            session.add(Category(name="InactiveCat", is_active=False))
            session.commit()

        resp = admin_client.get("/api/v1/admin/categories")
        assert resp.status_code == 200
        names = [c["name"] for c in resp.get_json()]
        assert "ActiveCat" in names
        assert "InactiveCat" in names

    def test_admin_creates_category(self, admin_client):
        resp = admin_client.post(
            "/api/v1/admin/categories",
            json={"name": "New Category"},
        )
        assert resp.status_code == 201
        assert resp.get_json()["name"] == "New Category"

    def test_create_category_empty_name_returns_400(self, admin_client):
        resp = admin_client.post("/api/v1/admin/categories", json={"name": ""})
        assert resp.status_code == 400

    def test_create_duplicate_category_returns_400(self, admin_client):
        admin_client.post("/api/v1/admin/categories", json={"name": "DupCat"})
        resp = admin_client.post("/api/v1/admin/categories", json={"name": "DupCat"})
        assert resp.status_code == 400

    def test_admin_updates_category(self, admin_client, seeded_category):
        resp = admin_client.put(
            f"/api/v1/admin/categories/{seeded_category}",
            json={"name": "Updated Name", "is_active": True},
        )
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Updated Name"

    def test_update_nonexistent_category_returns_404(self, admin_client):
        resp = admin_client.put("/api/v1/admin/categories/99999", json={"name": "X"})
        assert resp.status_code == 404

    def test_deactivate_category(self, admin_client, seeded_category):
        resp = admin_client.put(
            f"/api/v1/admin/categories/{seeded_category}",
            json={"is_active": False},
        )
        assert resp.status_code == 200
        assert resp.get_json()["is_active"] is False


class TestAdminPendingReports:
    def test_admin_can_access_pending_reports(self, admin_client, citizen_client, seeded_category):
        create_report(citizen_client, seeded_category, title="Pending")
        resp = admin_client.get("/api/v1/operator/reports/pending")
        assert resp.status_code == 200
        assert len(resp.get_json()) >= 1


class TestAdminStats:
    def test_unauthenticated_returns_401(self, client):
        resp = client.get("/api/v1/admin/stats")
        assert resp.status_code == 401

    def test_citizen_returns_403(self, citizen_client):
        resp = citizen_client.get("/api/v1/admin/stats")
        assert resp.status_code == 403

    def test_admin_gets_stats(self, admin_client):
        resp = admin_client.get("/api/v1/admin/stats")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), dict)
