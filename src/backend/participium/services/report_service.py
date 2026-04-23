from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from werkzeug.datastructures import FileStorage

from participium.core.exceptions import ValidationError
from participium.database.session import Session
from participium.models.enums import ReportStatus
from participium.models.report import Report, ReportPhoto, ReportStatusHistory
from participium.models.user import User
from participium.repositories.category_repository import CategoryRepository
from participium.repositories.report_repository import ReportRepository
from participium.services.storage_service import StorageService

if TYPE_CHECKING:
    from participium.services.notification_service import NotificationService


class ReportService:
    def __init__(
        self,
        session: Session,
        report_repository: ReportRepository,
        category_repository: CategoryRepository,
        storage_service: StorageService,
        notification_service: NotificationService | None = None,
    ):
        self.session = session
        self.report_repository = report_repository
        self.category_repository = category_repository
        self.storage_service = storage_service
        self.notification_service = notification_service

    def get_report(self, report_id: int) -> Report:
        raise NotImplementedError

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
        """
        try:
            resolved_category_id = int(category_id) if category_id is not None else None
        except (TypeError, ValueError) as exc:
            raise ValidationError("A valid active category is required.") from exc

        category = self.category_repository.get_by_id(resolved_category_id) if resolved_category_id else None
        if not category or not category.is_active:
            raise ValidationError("A valid active category is required.")
        if not title or not description:
            raise ValidationError("Title and description are required.")
        if latitude is None or longitude is None:
            raise ValidationError("Latitude and longitude are required.")

        try:
            resolved_latitude = float(latitude)
            resolved_longitude = float(longitude)
        except (TypeError, ValueError) as exc:
            raise ValidationError("Latitude and longitude must be valid numbers.") from exc

        valid_photos = [photo for photo in photos if photo and photo.filename]
        if not valid_photos:
            raise ValidationError("At least one photo is required.")
        if len(valid_photos) > 3:
            raise ValidationError("A report can contain at most 3 photos.")

        report = Report(
            title=title.strip(),
            description=description.strip(),
            latitude=resolved_latitude,
            longitude=resolved_longitude,
            is_anonymous=bool(is_anonymous),
            status=ReportStatus.PENDING_APPROVAL,
            reporter_id=reporter.id,
            category_id=category.id,
        )
        self.report_repository.add(report)
        self.session.flush()

        for photo in valid_photos:
            stored_path = self.storage_service.save(photo)
            self.report_repository.add_photo(
                ReportPhoto(
                    report_id=report.id,
                    file_path=stored_path,
                    original_filename=photo.filename,
                    content_type=photo.content_type,
                )
            )

        self.report_repository.add_status_entry(
            ReportStatusHistory(
                report_id=report.id,
                previous_status=None,
                new_status=ReportStatus.PENDING_APPROVAL,
                note="Report submitted by citizen.",
                changed_by_id=reporter.id,
            )
        )
        self.session.commit()
        return self.get_report(report.id)

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
