from __future__ import annotations

from participium.models.report import Report, ReportPhoto, ReportStatusHistory


class ReportRepository:
    def get_by_id(self, report_id: int) -> Report | None:
        raise NotImplementedError

    def add(self, report: Report) -> None:
        raise NotImplementedError

    def add_photo(self, photo: ReportPhoto) -> None:
        raise NotImplementedError

    def add_status_entry(self, status_entry: ReportStatusHistory) -> None:
        raise NotImplementedError
