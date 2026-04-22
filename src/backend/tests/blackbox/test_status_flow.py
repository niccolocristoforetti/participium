from __future__ import annotations

import pytest

from participium.core.exceptions import ValidationError
from participium.core.status_flow import ensure_transition_allowed
from participium.models.enums import ReportStatus  


@pytest.mark.skip(reason="Disabled.")  
@pytest.mark.parametrize(
    "current_status, next_status",
    [
        # TC-ID: SF1 - SF3  (Pending Approval -> Pending Approval, Assigned, Rejected)
        (ReportStatus.PENDING_APPROVAL, ReportStatus.ASSIGNED),
        (ReportStatus.PENDING_APPROVAL, ReportStatus.REJECTED),
        (ReportStatus.PENDING_APPROVAL, ReportStatus.PENDING_APPROVAL),
        # TC-ID: SF4 - SF7  (Assigned -> Assigned, In Progress, Suspended, Resolved)
        (ReportStatus.ASSIGNED, ReportStatus.IN_PROGRESS),
        (ReportStatus.ASSIGNED, ReportStatus.SUSPENDED),
        (ReportStatus.ASSIGNED, ReportStatus.RESOLVED),
        (ReportStatus.ASSIGNED, ReportStatus.ASSIGNED),
        # TC-ID: SF8 - SF10  (In Progress -> In Progress, Suspended, Resolved)
        (ReportStatus.IN_PROGRESS, ReportStatus.SUSPENDED),
        (ReportStatus.IN_PROGRESS, ReportStatus.RESOLVED),
        (ReportStatus.IN_PROGRESS, ReportStatus.IN_PROGRESS),
        # TC-ID: SF11 - SF13  (Suspended -> Suspended, In Progress, Resolved)
        (ReportStatus.SUSPENDED, ReportStatus.IN_PROGRESS),
        (ReportStatus.SUSPENDED, ReportStatus.RESOLVED),
        (ReportStatus.SUSPENDED, ReportStatus.SUSPENDED),
        # TC-ID: SF14  (Rejected -> Rejected)
        (ReportStatus.REJECTED, ReportStatus.REJECTED),
        # TC-ID: SF15  (Resolved -> Resolved)
        (ReportStatus.RESOLVED, ReportStatus.RESOLVED),
    ],
)
def test_ensure_transition_allowed_success(
    current_status: ReportStatus, next_status: ReportStatus) -> None:
    result = ensure_transition_allowed(current_status, next_status)
    assert result is True


@pytest.mark.skip(reason="Disabled.")  
@pytest.mark.parametrize(
    "current_status, next_status",
    [
        # TC-ID: SF16 - SF18  (Pending Approval -> transizioni negate)
        (ReportStatus.PENDING_APPROVAL, ReportStatus.RESOLVED),
        (ReportStatus.PENDING_APPROVAL, ReportStatus.SUSPENDED),
        (ReportStatus.PENDING_APPROVAL, ReportStatus.IN_PROGRESS),
        # TC-ID: SF19 - SF20  (Assigned -> transizioni negate)
        (ReportStatus.ASSIGNED, ReportStatus.PENDING_APPROVAL),
        (ReportStatus.ASSIGNED, ReportStatus.REJECTED),
        # TC-ID: SF21 - SF23  (In Progress -> transizioni negate)
        (ReportStatus.IN_PROGRESS, ReportStatus.ASSIGNED),
        (ReportStatus.IN_PROGRESS, ReportStatus.PENDING_APPROVAL),
        (ReportStatus.IN_PROGRESS, ReportStatus.REJECTED),
        # TC-ID: SF24 - SF26  (Suspended -> transizioni negate)
        (ReportStatus.SUSPENDED, ReportStatus.PENDING_APPROVAL),
        (ReportStatus.SUSPENDED, ReportStatus.ASSIGNED),
        (ReportStatus.SUSPENDED, ReportStatus.REJECTED),
        # TC-ID: SF27 - SF31  (Rejected -> tutte tranne Rejected)
        (ReportStatus.REJECTED, ReportStatus.ASSIGNED),
        (ReportStatus.REJECTED, ReportStatus.IN_PROGRESS),
        (ReportStatus.REJECTED, ReportStatus.SUSPENDED),
        (ReportStatus.REJECTED, ReportStatus.RESOLVED),
        (ReportStatus.REJECTED, ReportStatus.PENDING_APPROVAL),
        # TC-ID: SF32 - SF36  (Resolved -> tutte tranne Resolved)
        (ReportStatus.RESOLVED, ReportStatus.PENDING_APPROVAL),
        (ReportStatus.RESOLVED, ReportStatus.ASSIGNED),
        (ReportStatus.RESOLVED, ReportStatus.IN_PROGRESS),
        (ReportStatus.RESOLVED, ReportStatus.SUSPENDED),
        (ReportStatus.RESOLVED, ReportStatus.REJECTED),
    ],
)
def test_ensure_transition_allowed_invalid(
    current_status: ReportStatus, next_status: ReportStatus) -> None:
    with pytest.raises(ValidationError):
        ensure_transition_allowed(current_status, next_status)