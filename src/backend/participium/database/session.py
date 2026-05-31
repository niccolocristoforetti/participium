from __future__ import annotations
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from participium.models.base import Base

__all__ = [
    "Session",
    "close_connection",
    "configure_database",
    "create_all",
    "get_session",
    "open_connection",
    "remove_session",
]

SessionLocal = scoped_session(sessionmaker(autoflush=False, expire_on_commit=False))
_connection: Connection | None = None
_engine = None


def open_connection() -> Connection:
    global _connection, _engine
    close_connection()
    _engine = create_engine(_database_url_from_env(), future=True)
    _connection = _engine.connect()
    SessionLocal.configure(bind=_engine)
    return _connection


def close_connection() -> None:
    global _connection, _engine
    SessionLocal.remove()
    if _connection is not None:
        _connection.close()
        _connection = None
    if _engine is not None:
        _engine.dispose()
        _engine = None
    SessionLocal.configure(bind=None)


def configure_database() -> Connection:
    return open_connection()


def get_session():
    return SessionLocal()


def remove_session() -> None:
    SessionLocal.remove()


def create_all() -> None:
    if _engine is None:
        raise RuntimeError("Database connection is not open.")
    Base.metadata.create_all(bind=_engine)


def _database_url_from_env() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is required.")
    return database_url
