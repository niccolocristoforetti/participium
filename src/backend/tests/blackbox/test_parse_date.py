from __future__ import annotations

from datetime import datetime

import pytest

from participium.core.utils import parse_date



# valori validi

@pytest.mark.parametrize(
    "value, expected",
    [
        # PD1 – None → None
        (None, None),
        # PD2 – stringa vuota → None
        ("", None),
        # PD3 – ISO completo con ora
        ("2024-01-15T10:30:00", datetime(2024, 1, 15, 10, 30, 0)),
        # PDB1 – solo data (senza ora)
        ("2023-10-25", datetime(2023, 10, 25, 0, 0, 0)),
        # PDB2 – data con solo ora
        ("2023-10-25T10", datetime(2023, 10, 25, 10, 0, 0)),
        # PDB3 – data con ora e minuti
        ("2023-10-25T10:01", datetime(2023, 10, 25, 10, 1, 0)),
    ],
)
def test_parse_date_success(value, expected) -> None:
    assert parse_date(value) == expected



# stringhe non valide → ValueError

@pytest.mark.parametrize(
    "value",
    [
        # PD4 – stringa non una data
        "not-a-date",
        # PDB4 – separatore di data errato (slash invece di trattino)
        "2023/10/25T10:00",
        # PDB5 – mese zero
        "2023-00-25T10:00:00",
        # PDB6 – mese tredici
        "2023-13-25T10:00:00",
        # PDB7 – giorno zero
        "2023-10-00T10:00:00",
        # PDB8 – giorno trentadue
        "2023-10-32T10:00:00",
        # PDB9 – solo anno e mese (formato incompleto)
        "2023-10",
        # PDB10 – ora ventiquattro
        "2024-01-15T24:00:00",
        # PDB11 – secondi negativi
        "2024-01-15T00:00:-1",
        # PDB12 – 29 febbraio in anno non bisestile
        "2023-02-29T10:00:00",
    ],
)
def test_parse_date_invalid(value) -> None:
    with pytest.raises(ValueError):
        parse_date(value)