from __future__ import annotations

import pytest

from participium.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from participium.models.enums import ReportStatus, Role
from participium.models.report import Report
from participium.models.user import User
from participium.services.report_service import ReportService

'''
| TC-ID | report_id | operator | next_status_value | note | Expected | Fixture | EC covered |
| :---- | :-------- | :------- | :---------------- | :--- | :------- | :------ | :--------- |
| US1 | 1 (esiste) | admin | `"Assigned"` | `None` | `Report` aggiornato | report in `Pending Approval`, admin autorizzato, transizione valida | EC1 × EC3 × EC8 × EC10 × EC13 |
| US2 | 1 (esiste) | operator (stessa cat.) | `"Assigned"` | `None` | `Report` aggiornato | report in `Pending Approval`, operator stessa categoria, transizione valida | EC1 × EC4 × EC8 × EC10 × EC13 |
| US3 | 1 (esiste) | admin | `"Rejected"` | `"Motivo rifiuto"` | `Report` rifiutato | report in `Pending Approval`, admin, Rejected con note | EC1 × EC3 × EC8 × EC11 × EC13 |
| US4 | 1 (esiste) | operator (stessa cat.) | `"Rejected"` | `"Motivo"` | `Report` rifiutato | report in `Pending Approval`, operator stessa cat., Rejected con note | EC1 × EC4 × EC8 × EC11 × EC13 |
| US5 | 99 (non esiste) | admin | `"Assigned"` | `None` | `NotFoundError` | report non esiste | EC2 × EC3 × EC8 × EC10 × EC13 |
| US6 | 1 (esiste) | operator (cat. diversa) | `"Assigned"` | `None` | `AuthorizationError` | report esiste, operator categoria diversa | EC1 × EC5 × EC8 × EC10 × EC13 |
| US7 | 1 (esiste) | citizen | `"Assigned"` | `None` | `AuthorizationError` | report esiste, operator citizen non autorizzato | EC1 × EC6 × EC8 × EC10 × EC13 |
| US8 | 1 (esiste) | operatore non valido | `"Assigned"` | `None` | `AuthorizationError` | report esiste, operator inesistente | EC1 × EC7 × EC8 × EC10 × EC13 |
| US9 | 1 (esiste) | admin | `"STATO_INVALIDO"` | `None` | `ValidationError` | report esiste, admin, status non in ReportStatus | EC1 × EC3 × EC9 × EC10 × EC13 |
| US10 | 1 (esiste) | admin | `"Rejected"` | `None` | `ValidationError` | report esiste, admin, Rejected senza note | EC1 × EC3 × EC8 × EC12 × EC13 |
| US11 | 1 (esiste) | admin | `"Rejected"` | `""` | `ValidationError` | report esiste, admin, Rejected con note vuota | EC1 × EC3 × EC8 × EC12 × EC13 |
| US12 | 1 (esiste, `Assigned`) | admin | `"Pending Approval"` | `None` | `ValidationError` | report in Assigned, transizione a Pending Approval non consentita | EC1 × EC3 × EC8 × EC10 × EC14 |
| US13 | 1 (esiste) | admin | `" Assigned "` | `None` | `ValidationError` | status invalido (spazi attorno) | EC1 × EC3 × EC9 × EC10 × EC13 |
| US14 | 1 (esiste) | admin | `""` | `None` | `ValidationError` | status vuoto | EC1 × EC3 × EC9 × EC10 × EC13 |


**Boundary : validità del next_status_value**
Test sulla validità della str next_status_value. La validità delle transizioni segue il TC-3 (ensure_transition_allowed)

| TC-ID | report_id | operator | next_status_value | note | Expected | Fixture | EC covered |
| :---- | :-------- | :------- | :---------------- | :--- | :------- | :------ | ------- | 
| US15 | 1(esiste) | operator (stessa cat.) |`"ASSIGNED"`  | `None` | ValidationError | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC4 x EC9 x EC10 x EC13|
| US16 | 1(esiste) | operator (stessa cat.) |`" Assigned"`  | `None` | ValidationError | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC4 x EC9 x EC10 x EC13|
| US17 | 1(esiste) | operator (stessa cat.) |`"assigned "`  | `None` | ValidationError | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC4 x EC9 x EC10 x EC13|
| US18 | 1(esiste) | operator (stessa cat.) |`""`  | `None` | ValidationError | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC4 x EC9 x EC10 x EC13|
| US11 | 1(esiste) | operator (stessa cat.) |`"Assigned"`  | `Qualsiasi` | Report cambia stato | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC4 x EC9 x EC10 x EC13|

**Boundary : note**   
Test sui possibili valori del note.

| TC-ID | report_id | operator | next_status_value | note | Expected | Fixture | EC covered |
| :---- | :-------- | :------- | :---------------- | :--- | :------- | :------ | ------- | 
| US19 | 1(esiste) | operatore comunale |`"Rejected"`  | `None` | ValidationError | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC3 x EC6 x EC9|
| US20 | 1(esiste) | operatore comunale |`"Rejected"`  | `""` | ValidationError | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC3 x EC6 x EC9|
| US21 | 1(esiste) | operatore comunale |`"Assigned"`  | `""` | Report cambia stato | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC3 x EC6 x EC9|
| US22 | 1(esiste) | operatore comunale |`"Rejected"`  | `"motivo"` | Report rifiutato | Reoport esistente in `"Pending Approval"` e operatore esistente | EC1 x EC3 x EC6 x EC9|
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
def seed_update_status_data(db_session) -> dict[str, User]:
    from participium.models.report import Report
    report = Report(
        id=1,
        title="Test Report",
        description="Descrizione",
        latitude=45.0,
        longitude=9.0,
        category_id=1,
        status=ReportStatus.PENDING_APPROVAL,
    )
    db_session.add(report)
    db_session.commit()

    admin = User(id=10, username="admin", role=Role.ADMIN, is_active=True)
    operator_same_cat = User(id=2, username="operatore1", role=Role.OPERATOR, category_id=1, is_active=True)
    operator_diff_cat = User(id=3, username="operatore2", role=Role.OPERATOR, category_id=2, is_active=True)
    citizen = User(id=4, username="citadino", role=Role.CITIZEN, is_active=True)
    invalid_operator = User(id=5, username="invalid", role=Role.OPERATOR, is_active=False)
    return {
        "admin": admin,
        "operator_same_cat": operator_same_cat,
        "operator_diff_cat": operator_diff_cat,
        "citizen": citizen,
        "invalid_operator": invalid_operator,
    }





@pytest.mark.parametrize(
    "report_id,operator,next_status_value,note",
    [
        # US1: admin, Assigned valido
        (1, "admin", "Assigned", None),
        # US2: operator stessa cat., Assigned valido
        (1, "operator_same_cat", "Assigned", None),
        # US3: admin, Rejected con note
        (1, "admin", "Rejected", "Motivo rifiuto"),
        # US4: operator stessa cat., Rejected con note
        (1, "operator_same_cat", "Rejected", "Motivo"),
        # US21: Assigned con note vuota (non Rejected)
        (1, "operator_same_cat", "Assigned", ""),
        # US22: Rejected con note
        (1, "operator_same_cat", "Rejected", "motivo"),
    ],
)
def test_update_status_success(
    seed_update_status_data: dict[str, User],
    report_service: ReportService,
    report_id: int,
    operator: str,
    next_status_value: str,
    note: str | None,
) -> None:
    operator_user = seed_update_status_data[operator]

    result = report_service.update_status(
        report_id=report_id,
        operator=operator_user,
        next_status_value=next_status_value,
        note=note,
    )

    assert isinstance(result, Report)





@pytest.mark.parametrize(
    "report_id,operator,next_status_value,note,expected_exception",
    [
        # US5: report non esiste
        (99, "admin", "Assigned", None, NotFoundError),
        # US6: operator cat. diversa
        (1, "operator_diff_cat", "Assigned", None, AuthorizationError),
        # US7: citizen
        (1, "citizen", "Assigned", None, AuthorizationError),
        # US8: operator non valido
        (1, "invalid_operator", "Assigned", None, AuthorizationError),
        # US9: status invalido
        (1, "admin", "STATO_INVALIDO", None, ValidationError),
        # US10: Rejected senza note
        (1, "admin", "Rejected", None, ValidationError),
        # US11: Rejected con note vuota
        (1, "admin", "Rejected", "", ValidationError),
        # US12: transizione non consentita (Pending Approval -> In Progress non è permessa)
        (1, "admin", "In Progress", None, ValidationError),
        # US13: status invalido (spazi)
        (1, "admin", " Assigned ", None, ValidationError),
        # US14: status vuoto
        (1, "admin", "", None, ValidationError),
        # US15: boundary status invalido (ASSIGNED maiuscolo)
        (1, "operator_same_cat", "ASSIGNED", None, ValidationError),
        # US16: boundary status invalido (spazio iniziale)
        (1, "operator_same_cat", " Assigned", None, ValidationError),
        # US17: boundary status invalido (spazio finale)
        (1, "operator_same_cat", "assigned ", None, ValidationError),
        # US18: boundary status vuoto
        (1, "operator_same_cat", "", None, ValidationError),
        # US19: Rejected senza note
        (1, "operator_same_cat", "Rejected", None, ValidationError),
        # US20: Rejected con note vuota
        (1, "operator_same_cat", "Rejected", "", ValidationError),
    ],
)
def test_update_status_exceptions(
    seed_update_status_data: dict[str, User],
    report_service: ReportService,
    report_id: int,
    operator: str,
    next_status_value: str,
    note: str | None,
    expected_exception: type[Exception],
) -> None:
    operator_user = seed_update_status_data[operator]

    with pytest.raises(expected_exception):
        report_service.update_status(
            report_id=report_id,
            operator=operator_user,
            next_status_value=next_status_value,
            note=note,
        )
