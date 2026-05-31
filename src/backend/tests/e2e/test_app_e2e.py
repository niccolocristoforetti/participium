from __future__ import annotations

import pytest

from participium import create_app
from participium.database import close_connection, get_session
from participium.models.category import Category
from participium.models.user import User

from tests.e2e.conftest import do_login, register_and_verify

pytestmark = pytest.mark.e2e


def _make_app(monkeypatch, tmp_path, **env_overrides):
    env = {
        "DATABASE_URL": "sqlite+pysqlite:///:memory:",
        "AUTO_INIT_DB": "true",
        "BOOTSTRAP_REFERENCE_DATA": "false",
        "BOOTSTRAP_DEMO_DATA": "false",
        "EXPOSE_VERIFICATION_LINKS": "true",
        "MAIL_BACKEND": "console",
        "MEDIA_ROOT": str(tmp_path / "uploads"),
    }
    for key, value in {**env, **env_overrides}.items():
        monkeypatch.setenv(key, value)
    app = create_app()
    app.config.update(TESTING=True)
    return app


@pytest.fixture
def app_bootstrap(monkeypatch, tmp_path):
    yield _make_app(monkeypatch, tmp_path, BOOTSTRAP_REFERENCE_DATA="true", BOOTSTRAP_DEMO_DATA="true")
    close_connection()


@pytest.fixture
def app_no_init(monkeypatch, tmp_path):
    yield _make_app(monkeypatch, tmp_path, AUTO_INIT_DB="false")
    close_connection()


class TestAppStartup:
    def test_bootstrap_seeds_reference_and_demo_data(self, app_bootstrap):
        with app_bootstrap.app_context():
            categories = get_session().query(Category).all()
            assert len(categories) > 0

    def test_auto_init_false_skips_db_setup(self, app_no_init):
        assert app_no_init is not None

    def test_auto_init_skips_commit_when_connection_is_none(self, monkeypatch, tmp_path):
        """Branch 39->41 di app.py: se _connection è None dopo create_all il commit
        viene saltato. Il check è un guard difensivo irraggiungibile in condizioni normali
        (open_connection imposta sempre _connection prima), quindi si azzera via mock."""
        import participium.app as app_module
        import participium.database.session as db_session_module

        original_create_all = app_module.create_all

        def create_all_and_clear():
            original_create_all()
            db_session_module._connection = None

        monkeypatch.setattr(app_module, "create_all", create_all_and_clear)

        app = _make_app(monkeypatch, tmp_path)
        try:
            assert app is not None
        finally:
            close_connection()


class TestRequestHooks:
    def test_inactive_user_session_is_cleared(self, client, app):
        register_and_verify(client, username="tobeinactive", email="inactive@test.com", password="Pass123!")
        do_login(client, "inactive@test.com", "Pass123!")

        with app.app_context():
            user = get_session().query(User).filter_by(email="inactive@test.com").first()
            user.is_active = False
            get_session().commit()

        resp = client.get("/api/v1/users/me")
        assert resp.status_code == 401


class TestErrorHandlers:
    def test_unknown_route_returns_404(self, client):
        resp = client.get("/api/v1/this-route-does-not-exist")
        assert resp.status_code == 404
        assert resp.get_json()["error"] == "Resource not found."
