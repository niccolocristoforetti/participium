from __future__ import annotations

from unittest.mock import Mock

import pytest

from participium.services.storage_service import LocalFileStorageService, StorageService


class TestStorageServiceBase:
    """Test suite per la classe base StorageService."""

    def test_save_returns_simulated_string(self):
        """Il metodo save della classe base restituisce una stringa simulata."""
        # Arrange
        service = StorageService()
        uploaded_file = Mock()

        # Act
        result = service.save(uploaded_file)

        # Assert
        assert result == "simulated-file"


class TestLocalFileStorageService:
    """Test suite per LocalFileStorageService."""

    def test_creates_media_directory_on_init(self, tmp_path):
        """Il costruttore crea la directory media_root se non esiste."""
        # Arrange
        media_root = tmp_path / "uploads"

        # Act
        LocalFileStorageService(media_root)

        # Assert
        assert media_root.is_dir()

    def test_save_stores_file_and_returns_relative_name(self, tmp_path):
        """save() salva il file e restituisce un nome con UUID prefix."""
        # Arrange
        media_root = tmp_path / "uploads"
        service = LocalFileStorageService(media_root)

        uploaded = Mock()
        uploaded.filename = "my photo.jpg"
        uploaded.save = Mock()

        # Act
        result = service.save(uploaded)

        # Assert
        assert result.endswith("_my_photo.jpg")
        uploaded.save.assert_called_once()

    def test_save_handles_none_filename(self, tmp_path):
        """Se filename è None, usa 'attachment.bin' come fallback."""
        # Arrange
        media_root = tmp_path / "uploads"
        service = LocalFileStorageService(media_root)

        uploaded = Mock()
        uploaded.filename = None
        uploaded.save = Mock()

        # Act
        result = service.save(uploaded)

        # Assert
        assert "attachment" in result
