from __future__ import annotations

import io

import pytest

from participium import create_app
from participium.core.security import hash_password
from participium.database import close_connection, get_session
from participium.models.category import Category
from participium.models.enums import Role
from participium.models.user import User


@pytest.fixture
def app(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("AUTO_INIT_DB", "true")
    monkeypatch.setenv("BOOTSTRAP_REFERENCE_DATA", "false")
    monkeypatch.setenv("BOOTSTRAP_DEMO_DATA", "false")
    monkeypatch.setenv("EXPOSE_VERIFICATION_LINKS", "true")
    monkeypatch.setenv("MAIL_BACKEND", "console")
    monkeypatch.setenv("MEDIA_ROOT", str(tmp_path / "uploads"))

    application = create_app()
    application.config.update(TESTING=True)
    yield application
    close_connection()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seeded_category(app):
    with app.app_context():
        cat = Category(name="Infrastructure", is_active=True)
        session = get_session()
        session.add(cat)
        session.commit()
        return cat.id


@pytest.fixture
def seeded_operator(app, seeded_category):
    with app.app_context():
        user = User(
            username="operator1",
            first_name="Op",
            last_name="User",
            email="operator@test.com",
            password_hash=hash_password("operatorpass"),
            role=Role.OPERATOR,
            is_active=True,
            is_email_verified=True,
            category_id=seeded_category,
        )
        get_session().add(user)
        get_session().commit()
    return {"email": "operator@test.com", "password": "operatorpass"}


@pytest.fixture
def seeded_admin(app):
    with app.app_context():
        user = User(
            username="admin1",
            first_name="Admin",
            last_name="User",
            email="admin@test.com",
            password_hash=hash_password("adminpass"),
            role=Role.ADMIN,
            is_active=True,
            is_email_verified=True,
        )
        get_session().add(user)
        get_session().commit()
    return {"email": "admin@test.com", "password": "adminpass"}


def register_and_verify(client, *, username, email, password, first_name="Test", last_name="User"):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        },
    )
    data = resp.get_json()
    if "verification_url" in data:
        token = data["verification_url"].split("/")[-1]
        client.get(f"/api/v1/auth/verify/{token}")
    return resp


def do_login(client, identifier, password):
    return client.post("/api/v1/auth/login", json={"identifier": identifier, "password": password})


def photo():
    return (io.BytesIO(b"fake image data"), "photo.jpg")


def create_report(client, category_id, **overrides):
    data = {
        "title": overrides.get("title", "Test Report"),
        "description": overrides.get("description", "A test description"),
        "category_id": str(category_id),
        "latitude": overrides.get("latitude", "45.0"),
        "longitude": overrides.get("longitude", "9.0"),
        "photos": photo(),
    }
    if "is_anonymous" in overrides:
        data["is_anonymous"] = overrides["is_anonymous"]
    return client.post("/api/v1/reports", data=data, content_type="multipart/form-data")


@pytest.fixture
def citizen_client(app):
    c = app.test_client()
    register_and_verify(c, username="citizen1", email="citizen@test.com", password="citizenpass")
    do_login(c, "citizen@test.com", "citizenpass")
    return c


@pytest.fixture
def operator_client(app, seeded_operator):
    c = app.test_client()
    do_login(c, seeded_operator["email"], seeded_operator["password"])
    return c


@pytest.fixture
def admin_client(app, seeded_admin):
    c = app.test_client()
    do_login(c, seeded_admin["email"], seeded_admin["password"])
    return c
