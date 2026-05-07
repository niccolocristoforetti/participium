from __future__ import annotations

import pytest

from participium.database import get_session
from participium.models.category import Category

pytestmark = pytest.mark.e2e


class TestListCategories:
    def test_empty_returns_empty_list(self, client):
        resp = client.get("/api/v1/categories")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_returns_active_categories(self, app, client):
        with app.app_context():
            session = get_session()
            session.add(Category(name="Roads", is_active=True))
            session.add(Category(name="Parks", is_active=True))
            session.commit()

        resp = client.get("/api/v1/categories")
        assert resp.status_code == 200
        names = [c["name"] for c in resp.get_json()]
        assert "Roads" in names
        assert "Parks" in names

    def test_inactive_categories_are_excluded(self, app, client):
        with app.app_context():
            session = get_session()
            session.add(Category(name="Active Cat", is_active=True))
            session.add(Category(name="Inactive Cat", is_active=False))
            session.commit()

        resp = client.get("/api/v1/categories")
        names = [c["name"] for c in resp.get_json()]
        assert "Active Cat" in names
        assert "Inactive Cat" not in names

    def test_category_response_shape(self, app, client):
        with app.app_context():
            session = get_session()
            session.add(Category(name="Lighting", is_active=True))
            session.commit()

        data = client.get("/api/v1/categories").get_json()
        assert len(data) == 1
        cat = data[0]
        assert "id" in cat
        assert "name" in cat
        assert cat["name"] == "Lighting"
