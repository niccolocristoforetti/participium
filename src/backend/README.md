# Participium Backend

Backend setup, runtime configuration, database initialization, and test coverage commands.

The application automatically loads default environment variables from:

```text
src/backend/.env
```

## Windows

Open a terminal in `src/backend`, then run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python wsgi.py
```

The backend starts on:

```text
http://localhost:5050
```

The Swagger UI is available at:

```text
http://localhost:5050/apidocs/
```

`wsgi.py` runs Flask without the development reloader, so the application and the local SQLite database are initialized only once.

## Unix / macOS

Open a terminal in `src/backend`, then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python wsgi.py
```

The backend starts on:

```text
http://localhost:5050
```

## Useful Environment Variables

The default configuration is stored in `.env`:

```text
DATABASE_URL=sqlite+pysqlite:///instance/participium.db
SECRET_KEY=participium-dev-secret
HOST=0.0.0.0
PORT=5050
FLASK_ENV=development
FRONTEND_ORIGIN=http://localhost:5173
AUTO_INIT_DB=true
BOOTSTRAP_REFERENCE_DATA=true
BOOTSTRAP_DEMO_DATA=true
```

Values exported in the terminal override the values from `.env`.

Windows example:

```powershell
$env:PORT = "8000"
python wsgi.py
```

Unix / macOS example:

```bash
PORT=8000 python wsgi.py
```

## Database Initialization and Seed Data

The backend reads its database configuration from:

```text
DATABASE_URL
```

The default local configuration uses SQLite:

```text
DATABASE_URL=sqlite+pysqlite:///instance/participium.db
```


When the application starts, `create_app()` opens the database connection. If `AUTO_INIT_DB=true`, it also creates the database tables and optionally loads seed data.

### AUTO_INIT_DB

```text
AUTO_INIT_DB=true
```

When enabled, the backend creates all SQLAlchemy tables at startup if they do not already exist.

If disabled:

```text
AUTO_INIT_DB=false
```

the application opens the database connection but does not create tables and does not run any seed step.

### BOOTSTRAP_REFERENCE_DATA

```text
BOOTSTRAP_REFERENCE_DATA=true
```

When enabled, the backend loads reference data required by the application domain.

Currently this means the default report categories:

```text
Waterworks - Drinking Water
Architectural Barriers
Sewerage
Public Lighting
Waste
Road Signs and Traffic Lights
Roads and Urban Furniture
Public Green Areas and Playgrounds
Other
```

This step is idempotent: existing categories are not duplicated.

Reference data is not demo content. It is the baseline data the application needs in order to create and classify reports.

### BOOTSTRAP_DEMO_DATA

```text
BOOTSTRAP_DEMO_DATA=true
```

When enabled, the backend loads sample users and sample reports for local development and manual testing.

The seeded users are:

```text
citizen@example.com  / Citizen123!
operator@example.com / Operator123!
admin@example.com    / Admin123!
```

Demo data also creates example reports, report photos, and report status history entries.

This step depends on reference categories. In normal local development, keep both reference data and demo data enabled.

### Common Seed Modes

Local development with ready-to-use demo data:

```text
AUTO_INIT_DB=true
BOOTSTRAP_REFERENCE_DATA=true
BOOTSTRAP_DEMO_DATA=true
```

Clean application baseline without fake users or reports:

```text
AUTO_INIT_DB=true
BOOTSTRAP_REFERENCE_DATA=true
BOOTSTRAP_DEMO_DATA=false
```

No automatic schema or seed work:

```text
AUTO_INIT_DB=false
BOOTSTRAP_REFERENCE_DATA=false
BOOTSTRAP_DEMO_DATA=false
```

This last mode is useful only when the database schema and data are managed externally.

## Coverage

Run the full test suite with coverage from `src/backend`:

```powershell
python -m pytest --cov=participium --cov-config=.coveragerc --cov-report=term-missing --cov-report=html --cov-report=xml --cov-report=json
```

Generated reports are written under:

```text
reports/coverage/
```

### Separate Coverage Reports

Black-box test coverage:

```powershell
python -m pytest tests/blackbox --cov=participium --cov-config=.coveragerc --cov-report=term-missing --cov-report=html:reports/coverage/blackbox/html --cov-report=xml:reports/coverage/blackbox/coverage.xml --cov-report=json:reports/coverage/blackbox/coverage.json
```

White-box test coverage:

```powershell
python -m pytest tests/whitebox --cov=participium --cov-config=.coveragerc --cov-report=term-missing --cov-report=html:reports/coverage/whitebox/html --cov-report=xml:reports/coverage/whitebox/coverage.xml --cov-report=json:reports/coverage/whitebox/coverage.json
```

Other tests coverage:

```powershell
python -m pytest tests/unit tests/integration tests/e2e --cov=participium --cov-config=.coveragerc --cov-report=term-missing --cov-report=html:reports/coverage/other/html --cov-report=xml:reports/coverage/other/coverage.xml --cov-report=json:reports/coverage/other/coverage.json
```

The three reports are useful to inspect how much code is exercised by each testing activity. The coverage percentage is still computed at file level by `coverage.py`.

### Excluded From Coverage

The coverage configuration intentionally excludes code that is structural, declarative, generated-like, or not part of the behavior to test.

Excluded paths:

```text
participium/**/__init__.py
participium/api/*.py
participium/api/**/*.py
participium/config/*.py
participium/config/**/*.py
participium/database/*.py
participium/database/**/*.py
participium/gateways/*.py
participium/gateways/**/*.py
participium/models/*.py
```

In practical terms, students do not need to test:

- package glue files;
- Swagger/OpenAPI setup;
- environment and configuration loading;
- database connection/bootstrap helpers;
- email gateway stubs;
- SQLAlchemy model declarations;
- DTO/type declarations;
- enums and model-level constants.

The coverage target is the executable application behavior: controllers, routes, services, repositories, serializers, and core logic.
