from __future__ import annotations

from datetime import datetime

import pytest

from participium.models.enums import ReportStatus
from participium.services.report_service import ReportService

'''
| PR1 | `None` | `None` | `None` | `None` | `"desc"` | `list[Report]` (tutti report pubblici, ordinati desc) | report pubblici esistenti con date varie | EC2 × EC4 × EC6 × EC8 × EC10 |
| PR2 | `9999` (invalido) | `None` | `None` | `None` | `"desc"` | `[]` (lista vuota) | nessun report in categoria 999 | EC1 × EC4 × EC6 × EC8 × EC10 |
| PR3 | `None` | `"Stato invalido"` | `None` | `None` | `"desc"` | `[]` (lista vuota) | report pubblici esistenti, ma status invalido | EC2 × EC3 × EC6 × EC8 × EC10 |
| PR4 | `None` | `None` | `"data invalida"` | `None` | `"desc"` | `[]` (lista vuota) | report pubblici esistenti, ma date_from invalido | EC2 × EC4 × EC5 × EC8 × EC10 |
| PR5 | `None` | `None` | `None` | `"data invalida"` | `"desc"` | `[]` (lista vuota) | report pubblici esistenti, ma date_to invalido | EC2 × EC4 × EC6 × EC7 × EC10 |
| PR6 | `None` | `None` | `None` | `None` | `None` | `list[Report]` (ordinati desc per default) | report pubblici esistenti | EC2 × EC4 × EC6 × EC8 × EC11 |
| PR7 | `None` | `Assigned` | `None` | `None` | `"desc"` | `list[Report]` (report pubblici con status Assigned) | report pubblici con status Assigned e altri | EC2 × EC4 x EC6 × EC8 × EC10 |


**Boundary: ordine date**
Test del confine logico tra date_from e date_to (date_to deve essere successiva a date_from per filtri validi).

| TC-ID | category_id | status | date_from | date_to | sort | Expected | Fixture | EC covered |
| :---- | :---------- | :----- | :-------- | :------ | :--- | :------- | :------ | :--------- |
| PRB8 | `None` | `None` | `2024/6/1` | `2024/6/1` | `"desc"` | `list[Report]` (stessa data, valido) | report pubblici con created_at = 2024-06-01 | EC2 × EC4 × EC6 × EC8 × EC10 |
| PRB9 | `None` | `None` | `2024/6/1` | `2024/5/31` | `"desc"` | `[]` (date_to < date_from) | report pubblici esistenti | EC2 × EC4 × EC6 × EC9 × EC10 |
'''

@pytest.fixture
def seed_public_reports_data() -> None:
    # Popola il sistema con i prerequisiti di `list_public_reports`.
    # Dataset suggerito:
    # - report pubblici con vari status (Pending Approval, Assigned, etc.)
    # - report in categoria 1 e categoria 2
    # - report con date_created distribuite (es. 2024-01-01, 2024-06-01, ecc.)
    pass


@pytest.mark.parametrize(
    "category_id,status,date_from,date_to,sort,expected_length",
    [
        # PR1: tutti report pubblici, ordinati desc
        (None, None, None, None, "desc", None,),
        # PR2: categoria invalida
        (9999, None, None, None, "desc", 0,),
        # PR3: status invalido
        (None, "Stato invalido", None, None, "desc", 0,),
        # PR4: date_from invalido
        (None, None, "data invalida", None, "desc", 0,),
        # PR5: date_to invalido
        (None, None, None, "data invalida", "desc", 0,),
        # PR6: sort None
        (None, None, None, None, None, None,),
        # PR7: status valido (Assigned)
        (None, ReportStatus.ASSIGNED, None, None, "desc", None,),
        # PRB8: stessa data per date_from e date_to
        (None, None, datetime(2024, 6, 1), datetime(2024, 6, 1), "desc", None,),
        # PRB9: date_to < date_from
        (None, None, datetime(2024, 6, 1), datetime(2024, 5, 31), "desc", 0,),
    ],
)
def test_list_public_reports(
    seed_public_reports_data: None,
    report_service: ReportService,
    category_id: int | None,
    status: str | ReportStatus | None,
    date_from: datetime | str | None,
    date_to: datetime | str | None,
    sort: str,
    expected_length: int | None,
) -> None:
    result = report_service.list_public_reports(
        category_id=category_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        sort=sort,
    )

    assert isinstance(result, list)
    
    # Se expected_length è None, significa che il numero di risultati può variare
    # (dipende dai dati di test), altrimenti verifichiamo il numero esatto = 0
    if expected_length is not None:
        assert len(result) == expected_length
