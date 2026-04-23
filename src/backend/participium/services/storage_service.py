from __future__ import annotations

from werkzeug.datastructures import FileStorage


class StorageService:
    def save(self, file: FileStorage) -> str:
        raise NotImplementedError
