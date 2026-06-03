import pytest

from participium.services.messaging_service import MessagingService
from participium.services.notification_service import NotificationService
from participium.services.report_service import ReportService
from participium.services.storage_service import StorageService


@pytest.fixture
def notification_service(db_session, notification_repository):
    return NotificationService(
        session=db_session,
        notification_repository=notification_repository,
    )


@pytest.fixture
def report_service(db_session, report_repository, category_repository, notification_service):
    return ReportService(
        session=db_session,
        report_repository=report_repository,
        category_repository=category_repository,
        storage_service=StorageService(),
        notification_service=notification_service,
    )


@pytest.fixture
def messaging_service(db_session, report_repository, message_repository, notification_service):
    return MessagingService(
        session=db_session,
        report_repository=report_repository,
        message_repository=message_repository,
        notification_service=notification_service,
    )
