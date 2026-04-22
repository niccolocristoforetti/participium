from __future__ import annotations

import pytest

from participium.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from participium.models.enums import ReportStatus, Role
from participium.models.report import Report
from participium.models.user import User
from participium.services.report_service import ReportService

'''
| US1 | 1(esistente) | operatore comunale | `"Assigned"` | `None` | Report con stato aggiornato | Report esistente ed in stato di `'Pending Approval'` e operatore esistente | EC1 x EC3 x EC6 x EC9 |
| US2 | 1(esiste) | operatore comunale | `"Rejected"` | `"Motivo del rifiuto"` | Report rifiutato, aggiornamento stato e rimozione dalla mappa | Report esistente in stato `"Pending Approval"` e operatore esistente | EC1 x EC3 x EC6 x EC8 |
| US3 | 99(non esiste) | operatore comunale | `"Assigned"` | `None` | `NotFoundError` | Report non esistente ma operatore esistente | EC2 x EC3 x EC6 x EC9 |
| US4 | 1(esiste) | cittadino | `"Assigned"` | `None` | `AuthorizationError` | Report esistente in stato `"Pending Approval"` e cittadino esistente| EC1 x EC4 x EC6 x EC9 |
| US5 |	1(esiste) |	operatore comunale | `"statoInvalido"` |	`None` | 	`ValidationError` |	Report esistente e operatore esistente | EC1 x EC3 x EC7 x EC9 |
| US6 |	1(esiste) |	operatore no valido |	`"Accepted"` | `None` | `AuthorizationError` | Reoport esistente in `"Pending Approval"` e operatore non esistente | EC1 x EC5 x EC6 x EC9 |


Boundary : validità del next_status_value**
Test sulla validità della str next_status_value. La validità delle transizioni segue il TC-3 (ensure_transition_allowed)

| TC-ID | report_id | operator | next_status_value | note | Expected | Fixture | EC covered |
| :---- | :-------- | :------- | :---------------- | :--- | :------- | :------ | ------- | 
| US7 | 1(esiste) | 1(esiste) |`"ASSIGNED"`  | `None` | ValidationError | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC3 x EC7 x EC9|
| US8 | 1(esiste) | 1(esiste) |`" Assigned"`  | `None` | ValidationError | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC3 x EC7 x EC9|
| US9 | 1(esiste) | 1(esiste) |`"assigned "`  | `None` | ValidationError | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC3 x EC7 x EC9|
| US10 | 1(esiste) | 1(esiste) |`""`  | `None` | ValidationError | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC3 x EC7 x EC9|
| US11 | 1(esiste) | 1(esiste) |`"Assigned"`  | `Qualsiasi` | Report cambia stato | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC3 x EC7 x EC9|


*Boundary : note**   
Test sui possibili valori del note.

| TC-ID | report_id | operator | next_status_value | note | Expected | Fixture | EC covered |
| :---- | :-------- | :------- | :---------------- | :--- | :------- | :------ | ------- | 
| US12 | 1(esiste) | operatore comunale |`"Rejected"`  | `None` | ValidationError | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC3 x EC6 x EC9|
| US13 | 1(esiste) | operatore comunale |`"Rejected"`  | `""` | ValidationError | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC3 x EC6 x EC9|
| US14 | 1(esiste) | operatore comunale |`"Assigned"`  | `""` | Report cambia stato | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC3 x EC6 x EC9|
| US15 | 1(esiste) | operatore comunale |`"Rejected"`  | `"motivo"` | Report rifiutato | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC3 x EC6 x EC9|

'''
# Test data fixtures
VALID_REPORTER = User(id=1, username="mario.rossi", role=Role.CITIZEN, is_active=True)

VALID_OPERATOR = User(
    id=2,
    username="operatore1",
    role=Role.OPERATOR,
    category_id=1,
    is_active=True,
)

OTHER_CATEGORY_OPERATOR = User(
    id=3,
    username="operatore2",
    role=Role.OPERATOR,
    category_id=2,
    is_active=True,
)

UNVALID_OPERATOR = User(
    id=6,
    username="operatore3",
    role=Role.OPERATOR,
    category_id=3,
    is_active=False,
)

INVALID_USER = User(id=5, username="citadino1", role=Role.CITIZEN, is_active=True)


@pytest.fixture
def seed_update_status_data() -> None:
    # Popola il sistema con i prerequisiti di `update_status`.
    # - report con id=100 appartenente a category_id=1 e status Pending Approval
    # - operatore con category_id=1
    # - operatore con category_id=2
    # - amministratore
    pass


@pytest.mark.parametrize(
    "operator,next_status_value,note,expected_status,expected_rejection_reason,",
    [
        # US1
        (VALID_OPERATOR,ReportStatus.ASSIGNED.value,None,ReportStatus.ASSIGNED,None,),
        # US2
        (VALID_OPERATOR,ReportStatus.REJECTED.value,"Motivo del rifiuto",ReportStatus.REJECTED,"Motivo del rifiuto",),
        # US11
        (VALID_OPERATOR,ReportStatus.ASSIGNED.value,None,ReportStatus.ASSIGNED,None,),
        # US14
        (VALID_OPERATOR,ReportStatus.ASSIGNED.value,"",ReportStatus.ASSIGNED,None,),
        # US15
        (VALID_OPERATOR, ReportStatus.REJECTED.value, "motivo", ReportStatus.REJECTED, "motivo", ),
    ],
)
def test_update_status_success(
    seed_update_status_data: None,
    operator: User,
    next_status_value: str,
    note: str | None,
    expected_status: ReportStatus,
    expected_rejection_reason: str | None,
) -> None:
    report_service = ReportService()

    updated_report = report_service.update_status(
        report_id=100,
        operator=operator,
        next_status_value=next_status_value,
        note=note,
    )

    assert isinstance(updated_report, Report)
    assert updated_report.status == expected_status

    if expected_rejection_reason is not None:
        assert updated_report.rejection_reason == expected_rejection_reason


@pytest.mark.parametrize(
    "operator,report_id,next_status_value,note,expected_exception,",
    [
        #US3
        (VALID_OPERATOR, 99, ReportStatus.ASSIGNED.value, None, NotFoundError,),
        #US4
        (INVALID_USER, 100, ReportStatus.ASSIGNED.value, None, AuthorizationError,),
        #US5
        (VALID_OPERATOR, 100, "statoInvalido", None, ValidationError,),
        #US6
        (UNVALID_OPERATOR, 100, "Accepted", None, AuthorizationError,),
        #US7
        (VALID_OPERATOR, 100, "ASSIGNED", None, ValidationError,),
        #US8
        (VALID_OPERATOR, 100, " Assigned", None, ValidationError,),
        #US9
        (VALID_OPERATOR, 100, "assigned ", None, ValidationError,),
        #US10
        (VALID_OPERATOR, 100, "", None, ValidationError,),
        #US12
        (VALID_OPERATOR, 100, ReportStatus.REJECTED.value, None, ValidationError,),
        #US13
        (VALID_OPERATOR, 100, ReportStatus.REJECTED.value, "", ValidationError,),
    ],
)
def test_update_status_errors(
    seed_update_status_data: None,
    operator: User,
    report_id: int,
    next_status_value: str,
    note: str | None,
    expected_exception: type[BaseException],
) -> None:
    report_service = ReportService()

    with pytest.raises(expected_exception):
        report_service.update_status(
            report_id=report_id,
            operator=operator,
            next_status_value=next_status_value,
            note=note,
        )
