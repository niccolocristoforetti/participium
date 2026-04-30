"""
Test di integrazione per ReportRepository.

Copertura al 100% dei metodi pubblici:
  - add(), add_photo(), add_status_entry(), add_follower()
  - get_by_id()
  - get_follower(), remove_follower(), list_followers()
  - list_reports()        — tutti i branch: public_only, category_id, status,
                            date_from, date_to, sort asc/desc
  - list_all()
  - list_user_reports()
  - list_pending()        — branch: base, category_id, date_from, date_to
  - list_for_category()   — branch: con category_id e senza (None)
  - list_operator_reports() — branch OPERATOR e non-OPERATOR

La fixture report_repository e la fixture db_session sono definite in
conftest.py. La fixture base_report è specifica di questo file perché
dipende da un Report e non è condivisa con altri test file.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from participium.models.enums import ReportStatus, Role
from participium.models.report import Report, ReportFollower, ReportPhoto, ReportStatusHistory


# ---------------------------------------------------------------------------
# FIXTURE LOCALE — solo base_report, che è specifica di questo file
# ---------------------------------------------------------------------------

@pytest.fixture
def base_report(db_session):
    """Report base già persistito, utile come precondizione nei test sui follower."""
    report = Report(
        title="Base Report",
        description="Desc",
        latitude=45.0,
        longitude=9.0,
        category_id=1,
        status=ReportStatus.PENDING_APPROVAL,
    )
    db_session.add(report)
    db_session.commit()
    return report


# ---------------------------------------------------------------------------
# ADD / GET_BY_ID — verifica che tutte le relazioni caricate via _detail_options
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_add_report_and_get_by_id_returns_report_with_all_relations(report_repository, db_session):
    """add() persiste il report; get_by_id() lo recupera con foto, storico e follower."""
    # Arrange
    report = Report(title="T1", description="D1", latitude=0.0, longitude=0.0, category_id=2)
    added_report = report_repository.add(report)
    db_session.commit()

    assert added_report.id is not None

    photo    = ReportPhoto(report_id=added_report.id, file_path="path.jpg", original_filename="a.jpg")
    history  = ReportStatusHistory(report_id=added_report.id, new_status=ReportStatus.ASSIGNED)
    follower = ReportFollower(report_id=added_report.id, user_id=10)

    report_repository.add_photo(photo)
    report_repository.add_status_entry(history)
    report_repository.add_follower(follower)
    db_session.commit()

    # Act
    fetched = report_repository.get_by_id(added_report.id)

    # Assert
    assert fetched is not None
    assert fetched.title == "T1"
    assert len(fetched.photos) == 1
    assert len(fetched.status_history) == 1
    assert len(fetched.followers) == 1


@pytest.mark.integration
def test_get_by_id_returns_none_for_missing_report(report_repository):
    """get_by_id() restituisce None per un id inesistente."""
    assert report_repository.get_by_id(999) is None


# ---------------------------------------------------------------------------
# FOLLOWER MANAGEMENT
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_follower_add_get_list_and_remove(report_repository, base_report, db_session):
    """Ciclo completo: aggiunta, recupero, lista e rimozione di un follower."""
    # Arrange
    follower = ReportFollower(report_id=base_report.id, user_id=5)
    report_repository.add_follower(follower)
    db_session.commit()

    # get_follower — trovato
    found = report_repository.get_follower(base_report.id, 5)
    assert found is not None

    # get_follower — non trovato
    assert report_repository.get_follower(base_report.id, 99) is None

    # list_followers
    followers_list = report_repository.list_followers(base_report.id)
    assert len(followers_list) == 1

    # remove_follower
    report_repository.remove_follower(found)
    db_session.commit()
    assert report_repository.get_follower(base_report.id, 5) is None
    assert report_repository.list_followers(base_report.id) == []


# ---------------------------------------------------------------------------
# LIST_REPORTS — tutti i branch dei filtri testati in test separati
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_list_reports_no_filter_returns_all_sorted_desc(report_repository, db_session):
    """list_reports() senza filtri restituisce tutti i report in ordine DESC per created_at."""
    now = datetime.now()
    r_old = Report(title="Old", description="D", latitude=0, longitude=0, category_id=1,
                   created_at=now - timedelta(days=2))
    r_new = Report(title="New", description="D", latitude=0, longitude=0, category_id=1,
                   created_at=now)
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
    r_old = Report(title="Old", description="D", latitude=0, longitude=0, category_id=1,
                   created_at=now - timedelta(days=2))
    r_new = Report(title="New", description="D", latitude=0, longitude=0, category_id=1,
                   created_at=now)
    db_session.add_all([r_old, r_new])
    db_session.commit()

    results = report_repository.list_reports(sort="asc")

    assert len(results) == 2
    assert results[0].title == "Old"
    assert results[1].title == "New"


@pytest.mark.integration
def test_list_reports_public_only_filters_by_public_statuses(report_repository, db_session, monkeypatch):
    """list_reports(public_only=True) include solo i report con status in PUBLIC_VISIBLE_STATUSES.

    Patchiamo la costante nel modulo che la importa (non dove è definita) per
    isolare la logica del branch senza dipendere dai valori reali della costante.
    """
    monkeypatch.setattr(
        "participium.repositories.report_repository.PUBLIC_VISIBLE_STATUSES",
        [ReportStatus.IN_PROGRESS],
    )

    r_public  = Report(title="Public",  description="D", latitude=0, longitude=0,
                       category_id=1, status=ReportStatus.IN_PROGRESS)
    r_private = Report(title="Private", description="D", latitude=0, longitude=0,
                       category_id=1, status=ReportStatus.PENDING_APPROVAL)
    db_session.add_all([r_public, r_private])
    db_session.commit()

    results = report_repository.list_reports(public_only=True)

    assert len(results) == 1
    assert results[0].status == ReportStatus.IN_PROGRESS


@pytest.mark.integration
def test_list_reports_filter_by_category_id(report_repository, db_session):
    """list_reports(category_id=X) restituisce solo i report di quella categoria."""
    r_cat1 = Report(title="Cat1", description="D", latitude=0, longitude=0, category_id=1)
    r_cat2 = Report(title="Cat2", description="D", latitude=0, longitude=0, category_id=2)
    db_session.add_all([r_cat1, r_cat2])
    db_session.commit()

    results = report_repository.list_reports(category_id=2)

    assert len(results) == 1
    assert results[0].category_id == 2


@pytest.mark.integration
def test_list_reports_filter_by_status(report_repository, db_session):
    """list_reports(status=X) restituisce solo i report con quello status."""
    r_pending  = Report(title="P", description="D", latitude=0, longitude=0,
                        category_id=1, status=ReportStatus.PENDING_APPROVAL)
    r_assigned = Report(title="A", description="D", latitude=0, longitude=0,
                        category_id=1, status=ReportStatus.ASSIGNED)
    db_session.add_all([r_pending, r_assigned])
    db_session.commit()

    results = report_repository.list_reports(status=ReportStatus.ASSIGNED)

    assert len(results) == 1
    assert results[0].status == ReportStatus.ASSIGNED


@pytest.mark.integration
def test_list_reports_filter_by_date_from(report_repository, db_session):
    """list_reports(date_from=X) esclude i report creati prima di X."""
    now = datetime.now()
    r_before = Report(title="Before", description="D", latitude=0, longitude=0,
                      category_id=1, created_at=now - timedelta(days=5))
    r_after  = Report(title="After",  description="D", latitude=0, longitude=0,
                      category_id=1, created_at=now)
    db_session.add_all([r_before, r_after])
    db_session.commit()

    results = report_repository.list_reports(date_from=now - timedelta(days=1))

    assert len(results) == 1
    assert results[0].title == "After"


@pytest.mark.integration
def test_list_reports_filter_by_date_to(report_repository, db_session):
    """list_reports(date_to=X) esclude i report creati dopo X."""
    now = datetime.now()
    r_old    = Report(title="Old",    description="D", latitude=0, longitude=0,
                      category_id=1, created_at=now - timedelta(days=5))
    r_recent = Report(title="Recent", description="D", latitude=0, longitude=0,
                      category_id=1, created_at=now)
    db_session.add_all([r_old, r_recent])
    db_session.commit()

    results = report_repository.list_reports(date_to=now - timedelta(days=2))

    assert len(results) == 1
    assert results[0].title == "Old"


@pytest.mark.integration
def test_list_reports_filter_by_date_range(report_repository, db_session):
    """list_reports(date_from, date_to) applica entrambi i limiti contemporaneamente."""
    now = datetime.now()
    r_in_range  = Report(title="InRange",  description="D", latitude=0, longitude=0,
                         category_id=1, created_at=now)
    r_too_old   = Report(title="TooOld",   description="D", latitude=0, longitude=0,
                         category_id=1, created_at=now - timedelta(days=10))
    r_too_new   = Report(title="TooNew",   description="D", latitude=0, longitude=0,
                         category_id=1, created_at=now + timedelta(days=10))
    db_session.add_all([r_in_range, r_too_old, r_too_new])
    db_session.commit()

    results = report_repository.list_reports(
        date_from=now - timedelta(days=1),
        date_to=now + timedelta(days=1),
    )

    assert len(results) == 1
    assert results[0].title == "InRange"


# ---------------------------------------------------------------------------
# LIST_ALL
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_list_all_returns_all_reports(report_repository, base_report):
    """list_all() è un alias di list_reports(public_only=False)."""
    results = report_repository.list_all()
    assert len(results) == 1
    assert results[0].id == base_report.id


# ---------------------------------------------------------------------------
# LIST_USER_REPORTS
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_list_user_reports_returns_only_that_users_reports(report_repository, db_session):
    """list_user_reports() filtra per reporter_id."""
    r_user10 = Report(title="U10", description="D", latitude=0, longitude=0,
                      category_id=1, reporter_id=10)
    r_user99 = Report(title="U99", description="D", latitude=0, longitude=0,
                      category_id=1, reporter_id=99)
    db_session.add_all([r_user10, r_user99])
    db_session.commit()

    results = report_repository.list_user_reports(10)

    assert len(results) == 1
    assert results[0].reporter_id == 10


@pytest.mark.integration
def test_list_user_reports_returns_empty_for_unknown_user(report_repository):
    """list_user_reports() restituisce lista vuota per utente senza segnalazioni."""
    assert report_repository.list_user_reports(999) == []


# ---------------------------------------------------------------------------
# LIST_PENDING — branch: base, solo category_id, solo date_from, solo date_to,
#               tutti e tre i filtri combinati
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_list_pending_returns_only_pending_sorted_asc(report_repository, db_session):
    """list_pending() senza filtri restituisce solo i PENDING_APPROVAL, dal più vecchio."""
    now = datetime.now()
    p_old      = Report(title="P_Old", description="D", latitude=0, longitude=0,
                        category_id=1, status=ReportStatus.PENDING_APPROVAL,
                        created_at=now - timedelta(days=1))
    p_new      = Report(title="P_New", description="D", latitude=0, longitude=0,
                        category_id=1, status=ReportStatus.PENDING_APPROVAL,
                        created_at=now)
    r_assigned = Report(title="Assigned", description="D", latitude=0, longitude=0,
                        category_id=1, status=ReportStatus.ASSIGNED)
    db_session.add_all([p_old, p_new, r_assigned])
    db_session.commit()

    results = report_repository.list_pending()

    assert len(results) == 2
    assert results[0].title == "P_Old"   # più vecchio viene per primo (ASC)
    assert results[1].title == "P_New"


@pytest.mark.integration
def test_list_pending_filter_by_category_id(report_repository, db_session):
    """list_pending(category_id=X) restringe ai PENDING di quella categoria."""
    r_cat1 = Report(title="C1", description="D", latitude=0, longitude=0,
                    category_id=1, status=ReportStatus.PENDING_APPROVAL)
    r_cat2 = Report(title="C2", description="D", latitude=0, longitude=0,
                    category_id=2, status=ReportStatus.PENDING_APPROVAL)
    db_session.add_all([r_cat1, r_cat2])
    db_session.commit()

    results = report_repository.list_pending(category_id=1)

    assert len(results) == 1
    assert results[0].category_id == 1


@pytest.mark.integration
def test_list_pending_filter_by_date_from(report_repository, db_session):
    """list_pending(date_from=X) esclude i PENDING più vecchi di X."""
    now = datetime.now()
    p_old  = Report(title="P_Old",  description="D", latitude=0, longitude=0,
                    category_id=1, status=ReportStatus.PENDING_APPROVAL,
                    created_at=now - timedelta(days=5))
    p_new  = Report(title="P_New",  description="D", latitude=0, longitude=0,
                    category_id=1, status=ReportStatus.PENDING_APPROVAL,
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
    p_old  = Report(title="P_Old",  description="D", latitude=0, longitude=0,
                    category_id=1, status=ReportStatus.PENDING_APPROVAL,
                    created_at=now - timedelta(days=5))
    p_new  = Report(title="P_New",  description="D", latitude=0, longitude=0,
                    category_id=1, status=ReportStatus.PENDING_APPROVAL,
                    created_at=now)
    db_session.add_all([p_old, p_new])
    db_session.commit()

    results = report_repository.list_pending(date_to=now - timedelta(days=2))

    assert len(results) == 1
    assert results[0].title == "P_Old"


@pytest.mark.integration
def test_list_pending_all_filters_combined(report_repository, db_session):
    """list_pending() con category_id, date_from e date_to tutti attivi insieme."""
    now = datetime.now()
    p_match  = Report(title="Match",    description="D", latitude=0, longitude=0,
                      category_id=1, status=ReportStatus.PENDING_APPROVAL, created_at=now)
    p_wrong_cat = Report(title="WrongCat", description="D", latitude=0, longitude=0,
                         category_id=2, status=ReportStatus.PENDING_APPROVAL, created_at=now)
    p_too_old   = Report(title="TooOld",   description="D", latitude=0, longitude=0,
                         category_id=1, status=ReportStatus.PENDING_APPROVAL,
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


# ---------------------------------------------------------------------------
# LIST_FOR_CATEGORY — branch con e senza category_id (None)
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_list_for_category_with_category_id_excludes_pending(report_repository, db_session):
    """list_for_category(id) esclude i PENDING_APPROVAL e filtra per categoria."""
    r_cat1_assigned = Report(title="C1_A", description="D", latitude=0, longitude=0,
                             category_id=1, status=ReportStatus.ASSIGNED)
    r_cat2_assigned = Report(title="C2_A", description="D", latitude=0, longitude=0,
                             category_id=2, status=ReportStatus.ASSIGNED)
    r_cat1_pending  = Report(title="C1_P", description="D", latitude=0, longitude=0,
                             category_id=1, status=ReportStatus.PENDING_APPROVAL)
    db_session.add_all([r_cat1_assigned, r_cat2_assigned, r_cat1_pending])
    db_session.commit()

    results = report_repository.list_for_category(1)

    assert len(results) == 1
    assert results[0].title == "C1_A"


@pytest.mark.integration
def test_list_for_category_with_none_returns_all_non_pending(report_repository, db_session):
    """list_for_category(None) esclude i PENDING_APPROVAL ma non filtra per categoria."""
    r_cat1 = Report(title="C1", description="D", latitude=0, longitude=0,
                    category_id=1, status=ReportStatus.ASSIGNED)
    r_cat2 = Report(title="C2", description="D", latitude=0, longitude=0,
                    category_id=2, status=ReportStatus.IN_PROGRESS)
    r_pend  = Report(title="Pend", description="D", latitude=0, longitude=0,
                     category_id=1, status=ReportStatus.PENDING_APPROVAL)
    db_session.add_all([r_cat1, r_cat2, r_pend])
    db_session.commit()

    results = report_repository.list_for_category(None)

    titles = [r.title for r in results]
    assert len(results) == 2
    assert "C1" in titles
    assert "C2" in titles
    assert "Pend" not in titles


# ---------------------------------------------------------------------------
# LIST_OPERATOR_REPORTS — branch OPERATOR e non-OPERATOR
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_list_operator_reports_operator_role_filters_by_category(report_repository, db_session):
    """Con Role.OPERATOR, list_operator_reports() usa il category_id passato."""
    r_cat1 = Report(title="C1_A", description="D", latitude=0, longitude=0,
                    category_id=1, status=ReportStatus.ASSIGNED)
    r_cat2 = Report(title="C2_A", description="D", latitude=0, longitude=0,
                    category_id=2, status=ReportStatus.ASSIGNED)
    db_session.add_all([r_cat1, r_cat2])
    db_session.commit()

    results = report_repository.list_operator_reports(role=Role.OPERATOR, category_id=1)

    assert len(results) == 1
    assert results[0].title == "C1_A"


@pytest.mark.integration
def test_list_operator_reports_non_operator_role_ignores_category(report_repository, db_session):
    """Con Role.ADMIN (o qualsiasi non-OPERATOR), il category_id viene ignorato."""
    r_cat1  = Report(title="C1_A", description="D", latitude=0, longitude=0,
                     category_id=1, status=ReportStatus.ASSIGNED)
    r_cat2  = Report(title="C2_A", description="D", latitude=0, longitude=0,
                     category_id=2, status=ReportStatus.ASSIGNED)
    r_pend  = Report(title="C1_P", description="D", latitude=0, longitude=0,
                     category_id=1, status=ReportStatus.PENDING_APPROVAL)
    db_session.add_all([r_cat1, r_cat2, r_pend])
    db_session.commit()

    results = report_repository.list_operator_reports(role=Role.ADMIN, category_id=1)

    titles = [r.title for r in results]
    assert len(results) == 2
    assert "C1_A" in titles
    assert "C2_A" in titles
    # I PENDING sono sempre esclusi da list_for_category
    assert "C1_P" not in titles