from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from participium.models.base import Base


@pytest.fixture
def in_memory_session():
    """Fixture per creare una sessione SQLAlchemy in-memory per test unitari."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
    