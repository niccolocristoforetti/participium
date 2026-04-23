from __future__ import annotations

from participium.models.category import Category


class CategoryRepository:
    def get_by_id(self, category_id: int) -> Category | None:
        raise NotImplementedError
