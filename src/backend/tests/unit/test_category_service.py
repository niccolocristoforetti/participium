from __future__ import annotations

from unittest.mock import Mock

import pytest

from participium.core.exceptions import NotFoundError, ValidationError
from participium.models.category import Category
from participium.services.category_service import CategoryService


def _make_category(id=None, name=None, is_active=None):
    """Helper per creare Mock di Category con attributi corretti."""
    category = Mock(spec=Category)
    if id is not None:
        category.id = id
    if name is not None:
        category.name = name
    if is_active is not None:
        category.is_active = is_active
    return category


class TestListCategories:
    """Test suite per il metodo list_categories."""

    def test_list_categories_all(self, category_service, mock_category_repository):
        """Lista tutte le categorie."""
        # Arrange
        categories = [
            _make_category(id=1, name="Category 1"),
            _make_category(id=2, name="Category 2"),
        ]
        mock_category_repository.list_all.return_value = categories

        # Act
        result = category_service.list_categories(active_only=False)

        # Assert
        assert result == categories
        mock_category_repository.list_all.assert_called_once_with(active_only=False)

    def test_list_categories_active_only(self, category_service, mock_category_repository):
        """Lista solo le categorie attive."""
        # Arrange
        active_categories = [_make_category(id=1, name="Active 1")]
        mock_category_repository.list_all.return_value = active_categories

        # Act
        result = category_service.list_categories(active_only=True)

        # Assert
        assert result == active_categories
        mock_category_repository.list_all.assert_called_once_with(active_only=True)

    def test_list_categories_default_is_false(self, category_service, mock_category_repository):
        """Il parametro active_only di default è False."""
        # Arrange
        mock_category_repository.list_all.return_value = []

        # Act
        category_service.list_categories()

        # Assert
        mock_category_repository.list_all.assert_called_once_with(active_only=False)


class TestGetCategory:
    """Test suite per il metodo get_category."""

    def test_get_category_found(self, category_service, mock_category_repository):
        """Recupero di una categoria esistente."""
        # Arrange
        category = _make_category(id=1, name="Test Category")
        mock_category_repository.get_by_id.return_value = category

        # Act
        result = category_service.get_category(1)

        # Assert
        assert result == category
        mock_category_repository.get_by_id.assert_called_once_with(1)

    def test_get_category_not_found(self, category_service, mock_category_repository):
        """Errore se la categoria non esiste."""
        # Arrange
        mock_category_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            category_service.get_category(999)

        assert "Category not found" in str(exc_info.value)
        mock_category_repository.get_by_id.assert_called_once_with(999)


class TestCreateCategory:
    """Test suite per il metodo create_category."""

    def test_create_category_success(self, category_service, mock_category_repository, mock_session):
        """Creazione di una nuova categoria con successo."""
        # Arrange
        new_category = _make_category(name="New Category", is_active=True)
        mock_category_repository.get_by_name.return_value = None
        mock_category_repository.add.return_value = new_category

        # Act
        result = category_service.create_category("New Category")

        # Assert
        assert result == new_category
        mock_category_repository.get_by_name.assert_called_once_with("New Category")
        mock_category_repository.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_create_category_strips_whitespace(
        self, category_service, mock_category_repository, mock_session
    ):
        """Il nome viene pulito da spazi."""
        # Arrange
        new_category = _make_category(name="Clean Name", is_active=True)
        mock_category_repository.get_by_name.return_value = None
        mock_category_repository.add.return_value = new_category

        # Act
        category_service.create_category("  Clean Name  ")

        # Assert
        mock_category_repository.get_by_name.assert_called_once_with("Clean Name")
        # Verifichiamo che add sia stato chiamato con un Category che ha il nome pulito
        add_call_args = mock_category_repository.add.call_args[0][0]
        assert add_call_args.name == "Clean Name"

    def test_create_category_empty_name(self, category_service):
        """Errore se il nome è vuoto."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            category_service.create_category("")

        assert "Category name is required" in str(exc_info.value)

    def test_create_category_only_whitespace(self, category_service):
        """Errore se il nome contiene solo spazi."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            category_service.create_category("   ")

        assert "Category name is required" in str(exc_info.value)

    def test_create_category_duplicate_name(self, category_service, mock_category_repository):
        """Errore se il nome della categoria esiste già."""
        # Arrange
        existing_category = _make_category(id=1, name="Existing")
        mock_category_repository.get_by_name.return_value = existing_category

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            category_service.create_category("Existing")

        assert "Category name already exists" in str(exc_info.value)


class TestUpdateCategory:
    """Test suite per il metodo update_category."""

    def test_update_category_name_only(
        self, category_service, mock_category_repository, mock_session
    ):
        """Update del solo nome della categoria."""
        # Arrange
        category = _make_category(id=1, name="Old Name", is_active=True)
        mock_category_repository.get_by_id.return_value = category
        mock_category_repository.get_by_name.return_value = None

        # Act
        result = category_service.update_category(1, name="New Name")

        # Assert
        assert result == category
        assert category.name == "New Name"
        mock_session.commit.assert_called_once()

    def test_update_category_active_status_only(
        self, category_service, mock_category_repository, mock_session
    ):
        """Update del solo status attivo/inattivo."""
        # Arrange
        category = _make_category(id=1, name="Category", is_active=True)
        mock_category_repository.get_by_id.return_value = category

        # Act
        result = category_service.update_category(1, is_active=False)

        # Assert
        assert result == category
        assert category.is_active is False
        mock_session.commit.assert_called_once()

    def test_update_category_both_name_and_status(
        self, category_service, mock_category_repository, mock_session
    ):
        """Update di nome e status insieme."""
        # Arrange
        category = _make_category(id=1, name="Old Name", is_active=True)
        mock_category_repository.get_by_id.return_value = category
        mock_category_repository.get_by_name.return_value = None

        # Act
        result = category_service.update_category(1, name="New Name", is_active=False)

        # Assert
        assert category.name == "New Name"
        assert category.is_active is False
        mock_session.commit.assert_called_once()

    def test_update_category_name_strips_whitespace(
        self, category_service, mock_category_repository, mock_session
    ):
        """Il nome viene pulito da spazi durante l'update."""
        # Arrange
        category = _make_category(id=1, name="Old", is_active=True)
        mock_category_repository.get_by_id.return_value = category
        mock_category_repository.get_by_name.return_value = None

        # Act
        category_service.update_category(1, name="  New Name  ")

        # Assert
        assert category.name == "New Name"

    def test_update_category_duplicate_name_different_id(
        self, category_service, mock_category_repository
    ):
        """Errore se il nuovo nome è già usato da un'altra categoria."""
        # Arrange
        category = _make_category(id=1, name="Category 1", is_active=True)
        existing = _make_category(id=2, name="Category 2")
        mock_category_repository.get_by_id.return_value = category
        mock_category_repository.get_by_name.return_value = existing

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            category_service.update_category(1, name="Category 2")

        assert "Category name already exists" in str(exc_info.value)

    def test_update_category_duplicate_name_same_id_allowed(
        self, category_service, mock_category_repository, mock_session
    ):
        """Update con lo stesso nome è consentito (per la stessa categoria)."""
        # Arrange
        category = _make_category(id=1, name="Category 1", is_active=True)
        mock_category_repository.get_by_id.return_value = category
        # Ritorna la stessa categoria (stesso ID)
        mock_category_repository.get_by_name.return_value = category

        # Act
        result = category_service.update_category(1, name="Category 1")

        # Assert
        assert result == category
        mock_session.commit.assert_called_once()

    def test_update_category_not_found(self, category_service, mock_category_repository):
        """Errore se la categoria non esiste."""
        # Arrange
        mock_category_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            category_service.update_category(999, name="New Name")

        assert "Category not found" in str(exc_info.value)

    def test_update_category_with_is_active_false_value(
        self, category_service, mock_category_repository, mock_session
    ):
        """Update con is_active=False viene applicato correttamente."""
        # Arrange
        category = _make_category(id=1, name="Category", is_active=True)
        mock_category_repository.get_by_id.return_value = category

        # Act
        category_service.update_category(1, is_active=False)

        # Assert
        assert category.is_active is False

    def test_update_category_with_is_active_true_value(
        self, category_service, mock_category_repository, mock_session
    ):
        """Update con is_active=True viene applicato correttamente."""
        # Arrange
        category = _make_category(id=1, name="Category", is_active=False)
        mock_category_repository.get_by_id.return_value = category

        # Act
        category_service.update_category(1, is_active=True)

        # Assert
        assert category.is_active is True

    def test_update_category_with_none_values_unchanged(
        self, category_service, mock_category_repository, mock_session
    ):
        """Se name e is_active sono None, la categoria non cambia."""
        # Arrange
        category = _make_category(id=1, name="Original", is_active=True)
        mock_category_repository.get_by_id.return_value = category

        # Act
        category_service.update_category(1)

        # Assert
        assert category.name == "Original"
        assert category.is_active is True
        mock_session.commit.assert_called_once()
