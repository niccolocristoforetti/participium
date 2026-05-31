from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from participium import create_app
from participium.database import close_connection, get_session
from participium.models.category import Category


@pytest.mark.e2e
@pytest.mark.skip(reason="This test is a crude example.")
def test_get_categories_after_inserting_category_with_flask_test_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")

    # test end-to-end di Flask: creiamo l'oggetto reale dell'applicazione
    # e poi lo richiamiamo tramite il test client di Flask.
    # Dato che create_app() viene eseguita, questi flag di avvio vengono effettivamente letti
    monkeypatch.setenv("AUTO_INIT_DB", "true")
    monkeypatch.setenv("BOOTSTRAP_REFERENCE_DATA", "false")
    monkeypatch.setenv("BOOTSTRAP_DEMO_DATA", "false")

    # create_app() apre la connessione al database e, dato AUTO_INIT_DB=true, crea lo schema
    application = create_app()
    application.config.update(TESTING=True)
    client: FlaskClient = application.test_client()


    with application.app_context():
        session = get_session()
        session.add(Category(name="Example E2E Category", is_active=True))
        session.commit()

    # Questa richiesta non è inviata sulla rete. Flask's test client simula una richiesta HTTP request
    response = client.get("/api/v1/categories")

    assert response.status_code == 200
    category_names = [category["name"] for category in response.get_json()]
    assert "Example E2E Category" in category_names

    # la connessione al database di test è aperta da create_app() va essere chiusa.
    close_connection()
