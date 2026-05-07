import pytest

from participium.services.notification_service import NotificationService
from participium.services.report_service import ReportService
from participium.services.storage_service import StorageService


@pytest.fixture
def report_service(db_session, report_repository, category_repository, notification_repository):
    return ReportService(
        session=db_session,
        report_repository=report_repository,
        category_repository=category_repository,
        storage_service=StorageService(),
        notification_service=NotificationService(
            session=db_session,
            notification_repository=notification_repository,
        ),
    )
