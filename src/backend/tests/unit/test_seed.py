from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import patch
from sqlalchemy.orm import Session

from participium.database.seed import seed_reference_data, _ensure_demo_photo, seed_demo_data
from participium.models.category import Category
from participium.models.user import User
from participium.models.report import Report, ReportPhoto, ReportStatusHistory
from participium.config.constants import DEFAULT_CATEGORIES
from participium.models.enums import Role, ReportStatus


@pytest.mark.unit
class TestSeedReferenceData:
    def test_seed_reference_data_adds_missing_categories(self, in_memory_session: Session):
        """Test che seed_reference_data aggiunga categorie mancanti."""
        # Prima chiamata: aggiunge tutte le categorie
        seed_reference_data(in_memory_session)
        categories = in_memory_session.query(Category).all()

        assert len(categories) == len(DEFAULT_CATEGORIES)
        category_names = {cat.name for cat in categories}
        assert category_names == set(DEFAULT_CATEGORIES)

        for cat in categories:
            assert cat.is_active is True

    def test_seed_reference_data_no_duplicates(self, in_memory_session: Session):
        """Test che seed_reference_data non aggiunga duplicati."""
        # Aggiungo una categoria
        existing_name = DEFAULT_CATEGORIES[0]
        in_memory_session.add(Category(name=existing_name, is_active=True))
        in_memory_session.commit()

        # Chiama seed e nel ciclo interno dovrebbe non aggiungere DEFAULT_CATEGORIES[0]
        seed_reference_data(in_memory_session)

        # Dovrebbe esserci solo una categoria con quel nome
        categories = in_memory_session.query(Category).filter_by(name=existing_name).all()
        assert len(categories) == 1


@pytest.mark.unit
class TestEnsureDemoPhoto:
    def test_ensure_demo_photo_with_media_root_creates_file(self, tmp_path):
        """Test che _ensure_demo_photo crei il file se non esiste."""
        media_root = tmp_path / "media"
        filename = "demo.svg"

        result = _ensure_demo_photo(str(media_root), filename)

        assert result == filename
        file_path = media_root / filename
        assert file_path.exists() # ad ora il file deve esistere 
        content = file_path.read_text() # deve contenere il testo "Participium demo photo"
        assert "Participium demo photo" in content

    def test_ensure_demo_photo_without_media_root_returns_filename(self):
        """Test che _ensure_demo_photo restituisca filename se media_root è None."""
        result = _ensure_demo_photo(None, "demo.svg")
        assert result == "demo.svg"

    def test_ensure_demo_photo_file_already_exists(self, tmp_path):
        """Test che _ensure_demo_photo non sovrascriva file esistente."""
        media_root = tmp_path / "media"
        media_root.mkdir()
        filename = "demo.svg"
        file_path = media_root / filename
        # Creo un file con contenuto "existing content"
        file_path.write_text("existing content")

        # Chiamo la funzione, che dovrebbe lasciare il file intatto
        result = _ensure_demo_photo(str(media_root), filename)

        assert result == filename
        assert file_path.read_text() == "existing content"  # Non cambiato


@pytest.mark.unit
class TestSeedDemoData:
    def test_seed_demo_data_creates_users(self, in_memory_session: Session):
        """Test che seed_demo_data crei gli utenti demo."""

        # chiamo seed_reference_data per avere le categorie
        seed_reference_data(in_memory_session)

        seed_demo_data(in_memory_session)

        # perche seed_demo_data crea 3 users
        users = in_memory_session.query(User).all()
        assert len(users) == 3

        emails = {user.email for user in users}
        assert emails == {"citizen@example.com", "operator@example.com", "admin@example.com"}

        # Verifica ruoli e categorie degli users creati
        citizen = in_memory_session.query(User).filter_by(email="citizen@example.com").first()
        assert citizen.role == Role.CITIZEN
        assert citizen.category_id is None

        operator = in_memory_session.query(User).filter_by(email="operator@example.com").first()
        assert operator.role == Role.OPERATOR
        assert operator.category_id is not None

        admin = in_memory_session.query(User).filter_by(email="admin@example.com").first()
        assert admin.role == Role.ADMIN
        assert admin.category_id is None

    def test_seed_demo_data_creates_reports(self, in_memory_session: Session):
        """Test che seed_demo_data crei i report demo."""
        seed_reference_data(in_memory_session)
        seed_demo_data(in_memory_session)

        # perchè seed_demo_data crea 2 report demo (uno pending e uno resolved)
        reports = in_memory_session.query(Report).all()
        assert len(reports) == 2

        titles = {report.title for report in reports}
        assert titles == {"Damaged bench near school", "Pothole on Via Roma"}

        # verifico che i dati inseriti siano coerenti con quanto scrittp in seed_demo_data
        pending = in_memory_session.query(Report).filter_by(title="Damaged bench near school").first()
        assert pending.status == ReportStatus.PENDING_APPROVAL
        assert pending.is_anonymous is False

        resolved = in_memory_session.query(Report).filter_by(title="Pothole on Via Roma").first()
        assert resolved.status == ReportStatus.RESOLVED
        assert resolved.is_anonymous is True

    def test_seed_demo_data_creates_photos_and_history(self, in_memory_session: Session):
        """Test che seed_demo_data crei foto e storico stati."""
        seed_reference_data(in_memory_session)
        seed_demo_data(in_memory_session)

        # perché seed_demo_data crea 2 report con 1 foto ciascuno
        photos = in_memory_session.query(ReportPhoto).all()
        assert len(photos) == 2
        
        # controllo sul nome della foto
        for photo in photos:
            assert photo.original_filename == "demo-report-photo.svg"

        # seed_demo_data crea 2 report, uno pending e uno resolved
        # quello pending non e mai stato modificato
        # mentre il resolved (pending->approved->resolved) ha subito 3 modifiche
        histories = in_memory_session.query(ReportStatusHistory).all()
        assert len(histories) == 4  # 1 per pending, 3 per resolved

    def test_seed_demo_data_no_duplicates(self, in_memory_session: Session):
        """Test che seed_demo_data non crei duplicati se già esistono report."""
        seed_reference_data(in_memory_session)
        # Aggiungi un report manuale
        citizen = User(
            email="citizen@example.com",
            username="citizen",
            first_name="Marco",
            last_name="Citizen",
            password_hash="hash",
            role=Role.CITIZEN,
            is_active=True,
            is_email_verified=True,
            email_notifications_enabled=True,
        )
        in_memory_session.add(citizen)
        in_memory_session.commit()

        report = Report(
            title="Existing Report",
            description="Test",
            latitude=0.0,
            longitude=0.0,
            is_anonymous=False,
            status=ReportStatus.PENDING_APPROVAL,
            reporter_id=citizen.id,
            category_id=in_memory_session.query(Category).first().id,
        )
        in_memory_session.add(report)
        in_memory_session.commit()

        # Chiama seed
        seed_demo_data(in_memory_session)

        # Dovrebbe esserci solo 1 report quello commitato
        # seed_demo_data non deve aggiungere il report demo perché ne esiste già uno
        reports = in_memory_session.query(Report).all()
        assert len(reports) == 1
        assert reports[0].title == "Existing Report"