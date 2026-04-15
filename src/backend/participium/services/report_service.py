from __future__ import annotations

from datetime import datetime

from werkzeug.datastructures import FileStorage

from participium.models.enums import ReportStatus
from participium.models.report import Report
from participium.models.user import User


class ReportService:
    def create_report(
        self,
        reporter: User,
        category_id: int | str | None,
        title: str | None,
        description: str | None,
        latitude: float | str | None,
        longitude: float | str | None,
        photos: list[FileStorage],
        is_anonymous: bool = False,
    ) -> Report:
        """Create a new citizen report.

        Inputs:
            reporter: authenticated citizen creating the report.
            category_id: identifier of the chosen category.
            title: short report title.
            description: detailed report description.
            latitude: report latitude.
            longitude: report longitude.
            photos: uploaded photos; only entries with a filename count as valid.
            is_anonymous: whether the report hides the reporter publicly.

        Returns:
            The created `Report`, reloaded after persistence.

        Raises:
            ValidationError: if `category_id` is missing, malformed, unknown, or refers to an inactive category.
            ValidationError: if `title` or `description` is missing.
            ValidationError: if `latitude` or `longitude` is missing.
            ValidationError: if coordinates cannot be converted to valid numeric values.
            ValidationError: if there are no valid uploaded photos.
            ValidationError: if more than 3 valid photos are provided.

        Fixtures/data:
            Requires a persisted reporter user and at least one active category.
            Useful tests often need fake/uploaded files.
        """
        raise NotImplementedError

    def update_status(
        self,
        report_id: int,
        operator: User,
        next_status_value: str,
        note: str | None = None,
    ) -> Report:
        """Update the workflow status of an existing report.

        Inputs:
            report_id: identifier of the target report.
            operator: admin or operator attempting the transition.
            next_status_value: raw target status value.
            note: optional note; mandatory for rejections.

        Returns:
            The updated `Report`, reloaded after persistence.

        Raises:
            AuthorizationError: if `operator` is not allowed to update report statuses.
            AuthorizationError: if an operator tries to update a report outside their category.
            NotFoundError: if the report does not exist.
            ValidationError: if `next_status_value` is not a valid report status.
            ValidationError: if a rejection is requested without a note.
            ValidationError: if the transition is not allowed by the workflow rules.
        """
        raise NotImplementedError

    def list_public_reports(
        self,
        category_id: int | None = None,
        status: ReportStatus | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        sort: str = "desc",
    ) -> list[Report]:
        """List reports that are publicly visible, optionally filtered.

        Inputs:
            category_id: optional category filter.
            status: optional exact status filter.
            date_from: optional lower bound on creation timestamp.
            date_to: optional upper bound on creation timestamp.
            sort: creation timestamp order; meaningful values are `asc` and `desc`.

        Returns:
            A list of public `Report` objects matching the filters.

        Raises:
            No documented domain exception.
        """
        raise NotImplementedError
