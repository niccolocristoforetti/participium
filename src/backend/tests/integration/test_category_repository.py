"""
Test di integrazione per CategoryRepository.

Copertura al 100% dei metodi pubblici:
  - add()
  - get_by_id()    — trovato, non trovato
  - get_by_name()  — trovato, non trovato
  - list_all()     — tutte le categorie, active_only=True, ordinamento ASC per name,
                     lista vuota

Ogni test dipende esclusivamente dalle fixture ``category_repository``
e ``db_session`` definite in conftest.py.
Il vincolo UNIQUE su Category.name è verificato esplicitamente.
"""

from __future__ import annotations

import pytest
import sqlalchemy.exc

from participium.models.category import Category


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_category(name: str, is_active: bool = True, **kwargs) -> Category:
    """Factory che produce una Category con i campi obbligatori valorizzati."""
    return Category(name=name, is_active=is_active, **kwargs)


# ---------------------------------------------------------------------------
# add()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_add_assigns_primary_key(category_repository, db_session):
    """add() persiste la categoria: dopo il commit l'id è valorizzato."""
    cat = category_repository.add(_make_category("Architectural Barriers"))

    db_session.commit()

    assert cat.id is not None


@pytest.mark.integration
def test_add_returns_the_same_object(category_repository, db_session):
    """add() restituisce l'oggetto passato (identità, non copia)."""
    cat = _make_category("Waste")

    result = category_repository.add(cat)
    db_session.commit()

    assert result is cat


@pytest.mark.integration
def test_add_persists_all_fields(category_repository, db_session):
    """add() salva correttamente name e is_active dopo expire()."""
    cat = category_repository.add(_make_category("Public Lighting", is_active=False))
    db_session.commit()
    db_session.expire(cat)

    assert cat.name == "Public Lighting"
    assert cat.is_active is False


@pytest.mark.integration
def test_add_default_is_active_is_true(category_repository, db_session):
    """Il valore di default di is_active è True quando non viene passato esplicitamente."""
    cat = Category(name="DefaultAttiva")
    category_repository.add(cat)
    db_session.commit()
    db_session.expire(cat)

    assert cat.is_active is True


@pytest.mark.integration
def test_add_duplicate_name_raises_integrity_error(category_repository, db_session):
    """Il vincolo UNIQUE su Category.name viene rispettato: due categorie con lo stesso
    nome sollevano IntegrityError al momento del commit."""
    category_repository.add(_make_category("Duplicata"))
    db_session.commit()

    category_repository.add(_make_category("Duplicata"))
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db_session.commit()


# ---------------------------------------------------------------------------
# get_by_id()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_get_by_id_returns_correct_category(category_repository, db_session):
    """get_by_id() recupera la categoria con l'id corretto."""
    cat = category_repository.add(_make_category("Waste"))
    db_session.commit()

    result = category_repository.get_by_id(cat.id)

    assert result is not None
    assert result.name == "Waste"
    assert result.id == cat.id


@pytest.mark.integration
def test_get_by_id_returns_none_for_missing_id(category_repository):
    """get_by_id() restituisce None per un id inesistente."""
    assert category_repository.get_by_id(9999) is None


# ---------------------------------------------------------------------------
# get_by_name()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_get_by_name_returns_correct_category(category_repository, db_session):
    """get_by_name() recupera la categoria con quel nome."""
    category_repository.add(_make_category("Waste"))
    db_session.commit()

    result = category_repository.get_by_name("Waste")

    assert result is not None
    assert result.name == "Waste"


@pytest.mark.integration
def test_get_by_name_returns_none_for_missing_name(category_repository):
    """get_by_name() restituisce None per un nome inesistente."""
    assert category_repository.get_by_name("Inesistente") is None


@pytest.mark.integration
def test_get_by_name_is_case_sensitive(category_repository, db_session):
    """get_by_name() distingue maiuscole e minuscole: 'rifiuti' ≠ 'Rifiuti'."""
    category_repository.add(_make_category("Waste"))
    db_session.commit()

    assert category_repository.get_by_name("waste") is None


# ---------------------------------------------------------------------------
# list_all()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_list_all_returns_empty_list_when_no_categories(category_repository):
    """list_all() restituisce una lista vuota quando non ci sono categorie."""
    assert category_repository.list_all() == []


@pytest.mark.integration
def test_list_all_returns_all_categories(category_repository, db_session):
    """list_all() restituisce sia le categorie attive sia quelle inattive."""
    category_repository.add(_make_category("Attiva",   is_active=True))
    category_repository.add(_make_category("Inattiva", is_active=False))
    db_session.commit()

    results = category_repository.list_all()

    assert len(results) == 2
    statuses = {c.is_active for c in results}
    assert statuses == {True, False}


@pytest.mark.integration
def test_list_all_active_only_excludes_inactive(category_repository, db_session):
    """list_all(active_only=True) restituisce solo le categorie con is_active=True."""
    category_repository.add(_make_category("Attiva1",  is_active=True))
    category_repository.add(_make_category("Attiva2",  is_active=True))
    category_repository.add(_make_category("Inattiva", is_active=False))
    db_session.commit()

    results = category_repository.list_all(active_only=True)

    assert len(results) == 2
    assert all(c.is_active for c in results)


@pytest.mark.integration
def test_list_all_active_only_returns_empty_when_all_inactive(category_repository, db_session):
    """list_all(active_only=True) restituisce lista vuota se tutte le categorie sono inattive."""
    category_repository.add(_make_category("Inattiva1", is_active=False))
    category_repository.add(_make_category("Inattiva2", is_active=False))
    db_session.commit()

    assert category_repository.list_all(active_only=True) == []


@pytest.mark.integration
def test_list_all_orders_by_name_asc(category_repository, db_session):
    """list_all() ordina le categorie alfabeticamente per name (ASC).

    Le categorie vengono inserite in ordine inverso rispetto all'atteso per
    verificare che sia l'ORDER BY della query a determinare il risultato.
    """
    category_repository.add(_make_category("Waste"))
    category_repository.add(_make_category("Public Lighting"))
    category_repository.add(_make_category("Architectural Barriers"))
    db_session.commit()

    results = category_repository.list_all()
    names = [c.name for c in results]

    assert names == sorted(names)
    assert names[0] == "Architectural Barriers"
    assert names[-1] == "Waste"


@pytest.mark.integration
def test_list_all_active_only_also_ordered_by_name(category_repository, db_session):
    """list_all(active_only=True) mantiene l'ordinamento alfabetico per name."""
    category_repository.add(_make_category("Waste",    is_active=True))
    category_repository.add(_make_category("Public Lighting",     is_active=True))
    category_repository.add(_make_category("Architectural Barriers",   is_active=False))
    db_session.commit()

    results = category_repository.list_all(active_only=True)
    names = [c.name for c in results]

    assert names == sorted(names)