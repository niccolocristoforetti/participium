"""
Test di integrazione per ReportRepository.

Copertura al 100% dei metodi pubblici:
  - add(), add_photo(), add_status_entry(), add_follower()
  - get_by_id()                 — trovato (con relazioni caricate), non trovato
  - get_follower()              — trovato, non trovato
  - remove_follower()
  - list_followers()
  - list_reports()              — tutti i branch: public_only, category_id, status,
                                  date_from, date_to, sort asc/desc, tutti i filtri combinati
  - list_all()
  - list_user_reports()         — filtro reporter_id, ordinamento DESC, lista vuota
  - list_pending()              — branch: base, category_id, date_from, date_to, combinati
  - list_for_category()         — branch: con category_id e senza (None)
  - list_operator_reports()     — branch OPERATOR con category_id, OPERATOR senza category_id,
                                  non-OPERATOR (ADMIN)

Le fixture report_repository e db_session sono definite in conftest.py.
La fixture base_report è locale a questo file perché dipende da Report.


"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from participium.models.enums import ReportStatus, Role
from participium.models.message import Message
from participium.models.report import Report, ReportFollower, ReportPhoto, ReportStatusHistory
from sqlalchemy import select


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_report(title: str = "Test Report", category_id: int = 1, **kwargs) -> Report:
    """Factory che produce un Report con i campi obbligatori valorizzati."""
    return Report(
        title=title,
        description=kwargs.pop("description", "Descrizione"),
        latitude=kwargs.pop("latitude", 45.0),
        longitude=kwargs.pop("longitude", 9.0),
        category_id=category_id,
        **kwargs,
    )


# Fixtures locale
@pytest.fixture(scope="function")
def base_report(db_session):
    """Report base già persistito, usato come precondizione nei test sui follower."""
    report = _make_report(title="Base Report", status=ReportStatus.PENDING_APPROVAL)
    db_session.add(report)
    db_session.commit()
    return report


# add() — verifica ritorno e persistenza
@pytest.mark.integration
def test_add_assigns_primary_key(report_repository, db_session):
    """add() persiste il report: dopo il commit l'id è valorizzato."""
    report = _make_report(title="New Report")

    result = report_repository.add(report)
    db_session.commit()

    assert result.id is not None


@pytest.mark.integration
def test_add_returns_the_same_object(report_repository, db_session):
    """add() restituisce l'oggetto passato (identità, non copia)."""
    report = _make_report(title="Return Check")

    result = report_repository.add(report)
    db_session.commit()

    assert result is report


@pytest.mark.integration
def test_add_default_status_is_pending_approval(report_repository, db_session):
    """Lo status di default per un nuovo report è PENDING_APPROVAL."""
    report = _make_report(title="Default Status")

    report_repository.add(report)
    db_session.commit()
    db_session.expire(report)

    assert report.status == ReportStatus.PENDING_APPROVAL


# add_photo() / add_status_entry() / add_follower() — metodi autonomi
@pytest.mark.integration
def test_add_photo_persists_and_is_accessible_via_report(report_repository, base_report, db_session):
    """add_photo() persiste la foto associata al report."""
    photo = ReportPhoto(
        report_id=base_report.id,
        file_path="uploads/photo.jpg",
        original_filename="photo.jpg",
    )

    result = report_repository.add_photo(photo)
    db_session.commit()

    fetched = report_repository.get_by_id(base_report.id)
    assert result is photo
    assert len(fetched.photos) == 1
    assert fetched.photos[0].file_path == "uploads/photo.jpg"


@pytest.mark.integration
def test_add_status_entry_persists_history(report_repository, base_report, db_session):
    """add_status_entry() persiste la voce nello storico di stato del report."""
    entry = ReportStatusHistory(
        report_id=base_report.id,
        previous_status=ReportStatus.PENDING_APPROVAL,
        new_status=ReportStatus.ASSIGNED,
    )

    result = report_repository.add_status_entry(entry)
    db_session.commit()

    fetched = report_repository.get_by_id(base_report.id)
    assert result is entry
    assert len(fetched.status_history) == 1
    assert fetched.status_history[0].new_status == ReportStatus.ASSIGNED


@pytest.mark.integration
def test_add_follower_persists_follower(report_repository, base_report, db_session):
    """add_follower() persiste il follower associato al report."""
    follower = ReportFollower(report_id=base_report.id, user_id=42)

    result = report_repository.add_follower(follower)
    db_session.commit()

    fetched = report_repository.get_by_id(base_report.id)
    assert result is follower
    assert len(fetched.followers) == 1
    assert fetched.followers[0].user_id == 42


# get_by_id()
@pytest.mark.integration
def test_get_by_id_returns_report_with_all_relations(report_repository, db_session):
    """get_by_id() carica il report con foto, storico e follower via _detail_options."""
    report = _make_report(title="Full Load")
    report_repository.add(report)
    db_session.commit()

    report_repository.add_photo(ReportPhoto(
        report_id=report.id, file_path="p.jpg", original_filename="p.jpg",
    ))
    report_repository.add_status_entry(ReportStatusHistory(
        report_id=report.id, new_status=ReportStatus.ASSIGNED,
    ))
    report_repository.add_follower(ReportFollower(report_id=report.id, user_id=10))
    db_session.commit()

    fetched = report_repository.get_by_id(report.id)

    assert fetched is not None
    assert fetched.title == "Full Load"
    assert len(fetched.photos) == 1
    assert len(fetched.status_history) == 1
    assert len(fetched.followers) == 1


@pytest.mark.integration
def test_get_by_id_returns_none_for_missing_report(report_repository):
    """get_by_id() restituisce None per un id inesistente."""
    assert report_repository.get_by_id(999) is None


# get_follower() / remove_follower() / list_followers()
@pytest.mark.integration
def test_get_follower_returns_follower_when_exists(report_repository, base_report, db_session):
    """get_follower() trova il follower corretto per (report_id, user_id)."""
    report_repository.add_follower(ReportFollower(report_id=base_report.id, user_id=5))
    db_session.commit()

    result = report_repository.get_follower(base_report.id, 5)

    assert result is not None
    assert result.user_id == 5


@pytest.mark.integration
def test_get_follower_returns_none_when_not_found(report_repository, base_report):
    """get_follower() restituisce None quando l'utente non segue il report."""
    assert report_repository.get_follower(base_report.id, 99) is None


@pytest.mark.integration
def test_list_followers_returns_all_followers_for_report(report_repository, base_report, db_session):
    """list_followers() elenca tutti i follower di un report."""
    report_repository.add_follower(ReportFollower(report_id=base_report.id, user_id=5))
    report_repository.add_follower(ReportFollower(report_id=base_report.id, user_id=6))
    db_session.commit()

    results = report_repository.list_followers(base_report.id)

    assert len(results) == 2
    assert {f.user_id for f in results} == {5, 6}


@pytest.mark.integration
def test_list_followers_returns_empty_when_no_followers(report_repository, base_report):
    """list_followers() restituisce lista vuota per un report senza follower."""
    assert report_repository.list_followers(base_report.id) == []


@pytest.mark.integration
def test_remove_follower_deletes_follower_from_database(report_repository, base_report, db_session):
    """remove_follower() rimuove il follower: non è più recuperabile dopo il commit."""
    follower = ReportFollower(report_id=base_report.id, user_id=5)
    report_repository.add_follower(follower)
    db_session.commit()

    report_repository.remove_follower(follower)
    db_session.commit()

    assert report_repository.get_follower(base_report.id, 5) is None


# list_reports() — un test per ogni branch del filtro
@pytest.mark.integration
def test_list_reports_no_filter_returns_all_sorted_desc(report_repository, db_session):
    """list_reports() senza filtri restituisce tutti i report in ordine DESC per created_at."""
    now = datetime.now()
    r_old = _make_report(title="Old", created_at=now - timedelta(days=2))
    r_new = _make_report(title="New", created_at=now)
    db_session.add_all([r_old, r_new])
    db_session.commit()

    results = report_repository.list_reports()

    assert len(results) == 2
    assert results[0].title == "New"
    assert results[1].title == "Old"


@pytest.mark.integration
def test_list_reports_sort_asc(report_repository, db_session):
    """list_reports(sort='asc') restituisce i report dal più vecchio al più recente."""
    now = datetime.now()
    r_old = _make_report(title="Old", created_at=now - timedelta(days=2))
    r_new = _make_report(title="New", created_at=now)
    db_session.add_all([r_old, r_new])
    db_session.commit()

    results = report_repository.list_reports(sort="asc")

    assert results[0].title == "Old"
    assert results[1].title == "New"


@pytest.mark.integration
def test_list_reports_public_only_filters_by_public_statuses(
    report_repository, db_session, monkeypatch
):
    """list_reports(public_only=True/False) filtra correttamente in base a PUBLIC_VISIBLE_STATUSES.

    Patchando la costante nel modulo che la importa, il test è indipendente
    dai valori reali di produzione e verifica entrambi i branch dello stesso flag
    senza duplicare il setup.
    """
    monkeypatch.setattr(
        "participium.repositories.report_repository.PUBLIC_VISIBLE_STATUSES",
        [ReportStatus.IN_PROGRESS],
    )

    r_public  = _make_report(title="Public",  status=ReportStatus.IN_PROGRESS)
    r_private = _make_report(title="Private", status=ReportStatus.PENDING_APPROVAL)
    db_session.add_all([r_public, r_private])
    db_session.commit()

    # public_only=True: solo i report con status in PUBLIC_VISIBLE_STATUSES
    public_results = report_repository.list_reports(public_only=True)
    assert len(public_results) == 1
    assert public_results[0].status == ReportStatus.IN_PROGRESS

    # public_only=False: tutti i report indipendentemente dallo status
    all_results = report_repository.list_reports(public_only=False)
    assert len(all_results) == 2


@pytest.mark.integration
@pytest.mark.parametrize(
    "filter_params, expected_indexes",
    [
        # Filtro category_id
        ({"category_id": 2}, [1]),
        # Filtro status
        ({"status": ReportStatus.ASSIGNED}, [1]),
        # Filtro date_from
        ({"date_from_offset": -1}, [1, 2]),
        # Filtro date_to
        ({"date_to_offset": -1}, [0]),
        # Filtro range combinato date_from + date_to
        ({"date_from_offset": -6, "date_to_offset": 6}, [0, 1, 2]),
    ]
)
def test_list_reports_filters_parameterized(
    report_repository, db_session, filter_params, expected_indexes
):
    """Verifica ogni filtro di list_reports() in isolamento e la combinazione dei filtri di data."""
    now = datetime.now()
    reports = [
        _make_report(title="R1", category_id=1, status=ReportStatus.PENDING_APPROVAL,
                     created_at=now - timedelta(days=5)),
        _make_report(title="R2", category_id=2, status=ReportStatus.ASSIGNED,
                     created_at=now),
        _make_report(title="R3", category_id=1, status=ReportStatus.IN_PROGRESS,
                     created_at=now + timedelta(days=5)),
    ]
    db_session.add_all(reports)
    db_session.commit()

    kwargs = {}
    if "category_id" in filter_params:
        kwargs["category_id"] = filter_params["category_id"]
    if "status" in filter_params:
        kwargs["status"] = filter_params["status"]
    if "date_from_offset" in filter_params:
        kwargs["date_from"] = now + timedelta(days=filter_params["date_from_offset"])
    if "date_to_offset" in filter_params:
        kwargs["date_to"] = now + timedelta(days=filter_params["date_to_offset"])

    results = report_repository.list_reports(**kwargs)

    expected_titles = {reports[i].title for i in expected_indexes}
    result_titles   = {r.title for r in results}
    assert result_titles == expected_titles


@pytest.mark.integration
def test_list_reports_all_filters_combined(report_repository, db_session, monkeypatch):
    """list_reports() con tutti e cinque i filtri attivi contemporaneamente."""
    monkeypatch.setattr(
        "participium.repositories.report_repository.PUBLIC_VISIBLE_STATUSES",
        [ReportStatus.IN_PROGRESS],
    )
    now = datetime.now()
    r_match      = _make_report(title="Match",    category_id=1,
                                 status=ReportStatus.IN_PROGRESS, created_at=now)
    r_wrong_cat  = _make_report(title="WrongCat", category_id=2,
                                 status=ReportStatus.IN_PROGRESS, created_at=now)
    r_wrong_stat = _make_report(title="WrongStat", category_id=1,
                                 status=ReportStatus.ASSIGNED, created_at=now)
    r_too_old    = _make_report(title="TooOld",   category_id=1,
                                 status=ReportStatus.IN_PROGRESS,
                                 created_at=now - timedelta(days=10))
    r_too_new    = _make_report(title="TooNew",   category_id=1,
                                 status=ReportStatus.IN_PROGRESS,
                                 created_at=now + timedelta(days=10))
    db_session.add_all([r_match, r_wrong_cat, r_wrong_stat, r_too_old, r_too_new])
    db_session.commit()

    results = report_repository.list_reports(
        public_only=True,
        category_id=1,
        status=ReportStatus.IN_PROGRESS,
        date_from=now - timedelta(hours=1),
        date_to=now + timedelta(hours=1),
    )

    assert len(results) == 1
    assert results[0].title == "Match"


# list_all()
@pytest.mark.integration
def test_list_all_returns_all_reports(report_repository, base_report):
    """list_all() è un alias di list_reports(public_only=False)."""
    results = report_repository.list_all()

    assert len(results) == 1
    assert results[0].id == base_report.id


@pytest.mark.integration
def test_list_all_returns_empty_when_no_reports(report_repository):
    """list_all() restituisce lista vuota quando non ci sono report."""
    assert report_repository.list_all() == []


# list_user_reports()
@pytest.mark.integration
def test_list_user_reports_returns_only_that_users_reports(report_repository, db_session):
    """list_user_reports() filtra per reporter_id."""
    r_user10 = _make_report(title="U10", reporter_id=10)
    r_user99 = _make_report(title="U99", reporter_id=99)
    db_session.add_all([r_user10, r_user99])
    db_session.commit()

    results = report_repository.list_user_reports(10)

    assert len(results) == 1
    assert results[0].reporter_id == 10


@pytest.mark.integration
def test_list_user_reports_orders_by_created_at_desc(report_repository, db_session):
    """list_user_reports() ordina i report del reporter dal più recente al più vecchio."""
    now = datetime.now()
    r_old = _make_report(title="Old", reporter_id=7, created_at=now - timedelta(days=2))
    r_new = _make_report(title="New", reporter_id=7, created_at=now)
    db_session.add_all([r_old, r_new])
    db_session.commit()

    results = report_repository.list_user_reports(7)

    assert results[0].title == "New"
    assert results[1].title == "Old"


@pytest.mark.integration
def test_list_user_reports_returns_empty_for_unknown_user(report_repository):
    """list_user_reports() restituisce lista vuota per utente senza segnalazioni."""
    assert report_repository.list_user_reports(999) == []


# list_pending() — un test per ogni branch
@pytest.mark.integration
def test_list_pending_returns_only_pending_sorted_asc(report_repository, db_session):
    """list_pending() senza filtri restituisce solo i PENDING_APPROVAL, dal più vecchio."""
    now = datetime.now()
    p_old      = _make_report(title="P_Old", status=ReportStatus.PENDING_APPROVAL,
                               created_at=now - timedelta(days=1))
    p_new      = _make_report(title="P_New", status=ReportStatus.PENDING_APPROVAL,
                               created_at=now)
    r_assigned = _make_report(title="Assigned", status=ReportStatus.ASSIGNED)
    db_session.add_all([p_old, p_new, r_assigned])
    db_session.commit()

    results = report_repository.list_pending()

    assert len(results) == 2
    assert results[0].title == "P_Old"
    assert results[1].title == "P_New"


@pytest.mark.integration
def test_list_pending_filter_by_category_id(report_repository, db_session):
    """list_pending(category_id=X) restringe ai PENDING di quella categoria."""
    r_cat1 = _make_report(title="C1", category_id=1, status=ReportStatus.PENDING_APPROVAL)
    r_cat2 = _make_report(title="C2", category_id=2, status=ReportStatus.PENDING_APPROVAL)
    db_session.add_all([r_cat1, r_cat2])
    db_session.commit()

    results = report_repository.list_pending(category_id=1)

    assert len(results) == 1
    assert results[0].category_id == 1


@pytest.mark.integration
def test_list_pending_filter_by_date_from(report_repository, db_session):
    """list_pending(date_from=X) esclude i PENDING più vecchi di X."""
    now = datetime.now()
    p_old = _make_report(title="P_Old", status=ReportStatus.PENDING_APPROVAL,
                          created_at=now - timedelta(days=5))
    p_new = _make_report(title="P_New", status=ReportStatus.PENDING_APPROVAL,
                          created_at=now)
    db_session.add_all([p_old, p_new])
    db_session.commit()

    results = report_repository.list_pending(date_from=now - timedelta(days=1))

    assert len(results) == 1
    assert results[0].title == "P_New"


@pytest.mark.integration
def test_list_pending_filter_by_date_to(report_repository, db_session):
    """list_pending(date_to=X) esclude i PENDING più recenti di X."""
    now = datetime.now()
    p_old = _make_report(title="P_Old", status=ReportStatus.PENDING_APPROVAL,
                          created_at=now - timedelta(days=5))
    p_new = _make_report(title="P_New", status=ReportStatus.PENDING_APPROVAL,
                          created_at=now)
    db_session.add_all([p_old, p_new])
    db_session.commit()

    results = report_repository.list_pending(date_to=now - timedelta(days=2))

    assert len(results) == 1
    assert results[0].title == "P_Old"


@pytest.mark.integration
def test_list_pending_all_filters_combined(report_repository, db_session):
    """list_pending() con category_id, date_from e date_to tutti attivi contemporaneamente."""
    now = datetime.now()
    p_match     = _make_report(title="Match",    category_id=1,
                                status=ReportStatus.PENDING_APPROVAL, created_at=now)
    p_wrong_cat = _make_report(title="WrongCat", category_id=2,
                                status=ReportStatus.PENDING_APPROVAL, created_at=now)
    p_too_old   = _make_report(title="TooOld",   category_id=1,
                                status=ReportStatus.PENDING_APPROVAL,
                                created_at=now - timedelta(days=10))
    db_session.add_all([p_match, p_wrong_cat, p_too_old])
    db_session.commit()

    results = report_repository.list_pending(
        category_id=1,
        date_from=now - timedelta(hours=1),
        date_to=now + timedelta(hours=1),
    )

    assert len(results) == 1
    assert results[0].title == "Match"


# list_for_category() — branch con e senza category_id
@pytest.mark.integration
def test_list_for_category_with_id_excludes_pending_and_filters_category(
    report_repository, db_session
):
    """list_for_category(id) esclude i PENDING_APPROVAL e filtra per categoria."""
    r_cat1_assigned = _make_report(title="C1_A", category_id=1, status=ReportStatus.ASSIGNED)
    r_cat2_assigned = _make_report(title="C2_A", category_id=2, status=ReportStatus.ASSIGNED)
    r_cat1_pending  = _make_report(title="C1_P", category_id=1, status=ReportStatus.PENDING_APPROVAL)
    db_session.add_all([r_cat1_assigned, r_cat2_assigned, r_cat1_pending])
    db_session.commit()

    results = report_repository.list_for_category(1)

    assert len(results) == 1
    assert results[0].title == "C1_A"


@pytest.mark.integration
def test_list_for_category_with_none_returns_all_non_pending(report_repository, db_session):
    """list_for_category(None) esclude i PENDING_APPROVAL ma non filtra per categoria."""
    r_cat1 = _make_report(title="C1", category_id=1, status=ReportStatus.ASSIGNED)
    r_cat2 = _make_report(title="C2", category_id=2, status=ReportStatus.IN_PROGRESS)
    r_pend = _make_report(title="Pend", category_id=1, status=ReportStatus.PENDING_APPROVAL)
    db_session.add_all([r_cat1, r_cat2, r_pend])
    db_session.commit()

    results = report_repository.list_for_category(None)
    titles = {r.title for r in results}

    assert len(results) == 2
    assert "C1" in titles
    assert "C2" in titles
    assert "Pend" not in titles


# list_operator_reports() — tutti e tre i branch
@pytest.mark.integration
def test_list_operator_reports_operator_with_category_id(report_repository, db_session):
    """Con Role.OPERATOR e category_id valorizzato, filtra per quella categoria."""
    r_cat1 = _make_report(title="C1_A", category_id=1, status=ReportStatus.ASSIGNED)
    r_cat2 = _make_report(title="C2_A", category_id=2, status=ReportStatus.ASSIGNED)
    db_session.add_all([r_cat1, r_cat2])
    db_session.commit()

    results = report_repository.list_operator_reports(role=Role.OPERATOR, category_id=1)

    assert len(results) == 1
    assert results[0].title == "C1_A"


@pytest.mark.integration
def test_list_operator_reports_operator_without_category_id(report_repository, db_session):
    """Con Role.OPERATOR e category_id=None, restituisce tutti i non-PENDING (nessun filtro categoria)."""
    r_cat1 = _make_report(title="C1_A", category_id=1, status=ReportStatus.ASSIGNED)
    r_cat2 = _make_report(title="C2_A", category_id=2, status=ReportStatus.ASSIGNED)
    r_pend = _make_report(title="C1_P", category_id=1, status=ReportStatus.PENDING_APPROVAL)
    db_session.add_all([r_cat1, r_cat2, r_pend])
    db_session.commit()

    results = report_repository.list_operator_reports(role=Role.OPERATOR, category_id=None)
    titles = {r.title for r in results}

    assert len(results) == 2
    assert "C1_A" in titles
    assert "C2_A" in titles
    assert "C1_P" not in titles  # PENDING sempre esclusi da list_for_category


@pytest.mark.integration
def test_list_operator_reports_admin_ignores_category(report_repository, db_session):
    """Con Role.ADMIN (non-OPERATOR), il category_id viene ignorato e vede tutto il non-PENDING."""
    r_cat1 = _make_report(title="C1_A", category_id=1, status=ReportStatus.ASSIGNED)
    r_cat2 = _make_report(title="C2_A", category_id=2, status=ReportStatus.ASSIGNED)
    r_pend = _make_report(title="C1_P", category_id=1, status=ReportStatus.PENDING_APPROVAL)
    db_session.add_all([r_cat1, r_cat2, r_pend])
    db_session.commit()

    results = report_repository.list_operator_reports(role=Role.ADMIN, category_id=1)
    titles = {r.title for r in results}

    assert len(results) == 2
    assert "C1_A" in titles
    assert "C2_A" in titles
    assert "C1_P" not in titles


# Comportamento del Modello: Cascade Delete
@pytest.mark.integration
def test_delete_report_cascades_to_children(report_repository, base_report, db_session):
    """Eliminando un report vengono rimossi in cascata foto, storico, follower e messaggi.

    Le asserzioni usano i metodi del repository dove disponibili per non
    accoppiare il test allo schema interno del DB.
    """
    report_id = base_report.id

    report_repository.add_photo(ReportPhoto(
        report_id=report_id, file_path="p.jpg", original_filename="p.jpg",
    ))
    report_repository.add_status_entry(ReportStatusHistory(
        report_id=report_id, new_status=ReportStatus.ASSIGNED,
    ))
    report_repository.add_follower(ReportFollower(report_id=report_id, user_id=10))
    db_session.add(Message(report_id=report_id, body="test cascade msg"))
    db_session.commit()

    # ReportRepository non espone delete(): si usa la sessione direttamente.
    db_session.delete(base_report)
    db_session.commit()

    assert report_repository.list_followers(report_id) == []
    assert report_repository.get_by_id(report_id) is None
    # Foto, storico e messaggi non hanno metodi di query nel repository:
    # si verifica tramite sessione che sia avvenuta la cascade sul DB.
    assert db_session.scalars(
        select(ReportPhoto).where(ReportPhoto.report_id == report_id)
    ).all() == []
    assert db_session.scalars(
        select(ReportStatusHistory).where(ReportStatusHistory.report_id == report_id)
    ).all() == []
    assert db_session.scalars(
        select(Message).where(Message.report_id == report_id)
    ).all() == []