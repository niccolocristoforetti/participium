from __future__ import annotations

import pytest

from participium.models.category import Category

pytestmark = pytest.mark.integration


class TestAdd:
    def test_add_persists_category(self, category_repository, db_session):
        cat = category_repository.add(Category(name="Strade", is_active=True))
        db_session.commit()
        assert db_session.get(Category, cat.id) is not None


class TestGetById:
    def test_existing_id_returns_category(self, category_repository, db_session):
        cat = category_repository.add(Category(name="Verde", is_active=True))
        db_session.commit()
        result = category_repository.get_by_id(cat.id)
        assert result is not None
        assert result.name == "Verde"

    def test_nonexistent_id_returns_none(self, category_repository):
        assert category_repository.get_by_id(9999) is None


class TestGetByName:
    def test_existing_name_returns_category(self, category_repository, db_session):
        category_repository.add(Category(name="Illuminazione", is_active=True))
        db_session.commit()
        result = category_repository.get_by_name("Illuminazione")
        assert result is not None
        assert result.name == "Illuminazione"

    def test_nonexistent_name_returns_none(self, category_repository):
        assert category_repository.get_by_name("Inesistente") is None


class TestListAll:
    def test_returns_all_categories(self, category_repository, db_session):
        category_repository.add(Category(name="Acqua", is_active=True))
        category_repository.add(Category(name="Rifiuti", is_active=False))
        db_session.commit()
        result = category_repository.list_all()
        assert len(result) == 2

    def test_active_only_excludes_inactive(self, category_repository, db_session):
        category_repository.add(Category(name="Attiva", is_active=True))
        category_repository.add(Category(name="Inattiva", is_active=False))
        db_session.commit()
        result = category_repository.list_all(active_only=True)
        assert all(c.is_active for c in result)
        assert len(result) == 1

    def test_results_are_sorted_by_name(self, category_repository, db_session):
        category_repository.add(Category(name="Zanzare", is_active=True))
        category_repository.add(Category(name="Alberi", is_active=True))
        db_session.commit()
        result = category_repository.list_all()
        names = [c.name for c in result]
        assert names == sorted(names)
