from __future__ import annotations

from participium.models.enums import ReportStatus


def ensure_transition_allowed(current_status: ReportStatus, next_status: ReportStatus) -> bool:
    """Check whether a report status transition is allowed.

    Inputs:
        current_status: current status of the report.
        next_status: requested next status.

    Returns:
        `True` when the transition is allowed, including self-transitions.

    Raises:
        ValidationError: if the transition is not allowed by the workflow rules.

    Allowed transitions:
        Pending Approval -> Pending Approval, Assigned, Rejected
        Assigned -> Assigned, In Progress, Suspended, Resolved
        In Progress -> In Progress, Suspended, Resolved
        Suspended -> Suspended, In Progress, Resolved
        Rejected -> Rejected
        Resolved -> Resolved
    """
    raise NotImplementedError
