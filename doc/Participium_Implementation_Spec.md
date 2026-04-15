# Participium - Implementation Specification

## 1. Purpose of this document

This document defines the implementation rules for **Participium**, a citizen-participation web system for the Municipality of Turin. It is intended as a practical implementation baseline for the project.

The system scope must remain aligned with the official documentation: geo-located citizen reports, public map and table consultation, report lifecycle management, notifications, messaging, public/private statistics, and administrative configuration. The central domain object is the **Report**, enriched with category, location, status, and up to **3 photos**. Public transparency, municipal workflow support, and citizen communication are core system goals.

This specification adds architectural, technological, deployment, and testing constraints that must drive the implementation.

---

## 2. Scope to implement

The implementation must cover the following functional areas already defined in the official material:

- citizen registration, email verification, login, logout, and profile preferences;
- report submission with OpenStreetMap-based geo-location;
- title, description, category, anonymity flag, and **1 to 3 photos** per report;
- report lifecycle with the statuses:
  - Pending Approval
  - Assigned
  - In Progress
  - Suspended
  - Rejected
  - Resolved
- public consultation through:
  - map view,
  - filterable/sortable table view,
  - report details page,
  - CSV export,
  - public statistics;
- authenticated citizens can follow reports;
- municipal operators can manage reports and exchange messages with citizens;
- administrators can manage categories/configuration and access private statistics.

The implementation should remain close to the official requirements baseline and avoid unrequested scope expansion. Examples of rejected scope extensions:

- native mobile apps,
- non-baseline notification channels as core features,
- unnecessary advanced infrastructure,
- framework-heavy solutions that make the code harder to understand or test.

---

## 3. Global implementation principles

### 3.1 Implementation priority

The main architectural goal is **testable code**:

- simple structure,
- low coupling,
- high cohesion,
- readable responsibilities,
- easy mocking,
- easy layer isolation,
- clear distinction between unit and integration tests.

### 3.2 Simplicity over sophistication

Use mainstream and readable patterns. Avoid needless abstractions, metaprogramming, excessive decorators, hidden magic, overly generic base classes, or patterns that reduce readability and maintainability.

### 3.3 Replaceability of infrastructure

Infrastructure concerns must be isolated:

- DBMS must be replaceable through **environment variables + Docker Compose**;
- email provider must be replaceable through configuration;
- photo storage path must be configurable;
- frontend API base URL must be configurable.

### 3.4 Frameworks must not absorb domain logic

Framework code must stay at the edges:

- Flask handles HTTP and app wiring;
- repositories handle persistence;
- services implement business rules;
- controllers orchestrate use cases and aggregate service calls;
- routes only adapt HTTP input/output.

### 3.5 Public/private data separation

The implementation must strictly separate:

- public report data,
- authenticated citizen data,
- operator data,
- administrator-only analytics,
- private identity data for anonymous public reports.  
  This is mandatory because anonymity must not leak through map, table, details, statistics, or CSV exports.

---

## 4. Mandatory technology choices

## 4.1 Backend

The backend must be implemented with:

- **Python**
- **Flask**
- **REST API**
- **Swagger / OpenAPI documentation** for the exposed APIs
- **SQLAlchemy** as ORM and DB abstraction layer
- **pytest** for tests

Recommended supporting libraries:

- Flask blueprint support
- `flask-smorest` or equivalent OpenAPI-first Flask integration
- `marshmallow` or equivalent schema validation/serialization library
- `pytest-cov`
- `pytest-mock`

Rationale:

- Flask is lightweight and pedagogically appropriate.
- SQLAlchemy makes the transition from SQLite to MySQL realistic with minimal code changes.
- OpenAPI makes API contracts explicit and testable.

## 4.2 Frontend

The frontend must be implemented with:

- **React**
- JavaScript or TypeScript (TypeScript preferred if the repository is already prepared for it)
- a dedicated API client layer
- Selenium-ready GUI structure

Recommended supporting libraries:

- React Router
- Axios or Fetch wrapper
- React Hook Form or controlled forms
- Leaflet + OpenStreetMap tiles for maps
- a lightweight chart library for statistics
- testing support suitable for component/unit tests in addition to Selenium end-to-end tests

## 4.3 Database

The default DBMS is:

- **SQLite** for the baseline local setup

The alternative DBMS to enable later only via configuration is:

- **MySQL**, delivered through an off-the-shelf Docker image

The code must not contain SQLite-only assumptions.

## 4.4 Containers

The project must be prepared so that teams can later add or adapt:

- backend Dockerfile,
- frontend Dockerfile,
- Docker Compose stack with:
  - frontend,
  - backend,
  - optional MySQL service.

The transition from SQLite to MySQL must require only:

- Docker Compose changes,
- environment variable changes,
- no business logic changes,
- no controller changes,
- no route changes,
- ideally no repository API changes.

---

## 5. System architecture

## 5.1 High-level style

Use a **multilayer architecture**.

Mandatory backend layers:

1. **Routes**
2. **Controllers**
3. **Services**
4. **Repositories**
5. **Persistence models / ORM entities**

Supporting modules:

- schemas / DTO mapping
- config
- auth
- extensions
- utils
- tests

## 5.2 Responsibilities of each backend layer

### Routes

Routes:

- own the HTTP endpoint definitions;
- parse HTTP-level inputs;
- invoke controllers;
- convert controller results into HTTP responses;
- must not implement business logic;
- must not directly query the database;
- must not coordinate multiple repositories.

Routes may handle:

- URL params,
- query params,
- body parsing,
- file upload extraction,
- authentication decorators,
- HTTP status code mapping.

Routes must not:

- contain workflow rules,
- perform report status validation logic,
- compute statistics,
- decide notification recipients,
- implement filtering semantics beyond simple request parsing.

### Controllers

Controllers:

- operate on already parsed data;
- orchestrate one or more services;
- coordinate a use case;
- prepare the response data structure returned to routes;
- must not contain HTTP framework details;
- must not return Flask `Response` objects.

Controllers are the ideal place for:

- use-case orchestration,
- composition of service results,
- selection of output DTOs,
- transaction boundary coordination if not centralized elsewhere.

### Services

Services:

- contain the business logic;
- enforce domain rules;
- validate workflow transitions;
- coordinate repositories;
- trigger notifications and messaging rules;
- compute statistics;
- must be testable in isolation with mocked repositories.

Examples:

- registration and verification flow
- report submission rules
- report follow/unfollow
- status transition validation
- rejection motivation requirement
- public/private statistics generation
- notification generation
- CSV export data selection

### Repositories

Repositories:

- are the only layer that accesses ORM queries directly;
- encapsulate persistence details;
- provide focused CRUD and query methods;
- return domain-oriented objects or entities, not Flask objects.

Repositories must not:

- implement workflow policy,
- send notifications,
- perform authorization decisions,
- mix unrelated aggregates.

### ORM models

ORM models:

- represent the persistence schema;
- stay simple;
- should not contain business logic beyond very light structural helpers if strictly needed.

Business rules must not live in ORM entity methods if that makes isolated testing harder.

---

## 6. Backend project structure

A recommended backend structure is:

```text
backend/
  app/
    __init__.py
    config/
      settings.py
    extensions/
      db.py
      api.py
      jwt.py
    models/
      user.py
      report.py
      photo.py
      category.py
      report_update.py
      follow.py
      notification.py
      message.py
    repositories/
      user_repository.py
      report_repository.py
      category_repository.py
      notification_repository.py
      message_repository.py
      statistics_repository.py
    services/
      auth_service.py
      user_service.py
      report_service.py
      follow_service.py
      notification_service.py
      message_service.py
      statistics_service.py
      export_service.py
    controllers/
      auth_controller.py
      user_controller.py
      report_controller.py
      admin_controller.py
      statistics_controller.py
    schemas/
      auth_schema.py
      report_schema.py
      user_schema.py
      statistics_schema.py
    routes/
      public_routes.py
      auth_routes.py
      citizen_routes.py
      operator_routes.py
      admin_routes.py
    auth/
      decorators.py
      permissions.py
    utils/
      exceptions.py
      pagination.py
      file_storage.py
      mailer.py
  tests/
    unit/
    integration/
    fixtures/
  run.py
  requirements.txt
```

The exact file names may change, but the **layering and separation of concerns are mandatory**.

---

## 7. Frontend architecture

## 7.1 High-level structure

The frontend must be:

- simple,
- responsive,
- visually clean,
- consistent with the examples in the project documents,
- easy to test,
- organized by features.

A recommended structure is:

```text
frontend/
  src/
    app/
      router.jsx
      providers.jsx
    api/
      client.js
      authApi.js
      reportsApi.js
      usersApi.js
      statisticsApi.js
      adminApi.js
    components/
      common/
      layout/
      forms/
      maps/
      charts/
      tables/
      messages/
      notifications/
    features/
      auth/
      reports/
      profile/
      statistics/
      admin/
    pages/
      PublicMapPage.jsx
      PublicTablePage.jsx
      ReportDetailPage.jsx
      LoginPage.jsx
      RegisterPage.jsx
      ProfilePage.jsx
      SubmitReportPage.jsx
      OperatorDashboardPage.jsx
      AdminStatisticsPage.jsx
      AdminConfigurationPage.jsx
    hooks/
    utils/
    styles/
    tests/
      unit/
      integration/
      e2e/
```

## 7.2 Frontend rules

The frontend must include:

- a dedicated API layer, never raw fetches scattered in components;
- presentational components separated from page orchestration where reasonable;
- reusable form components for common fields and validation feedback;
- route guards for protected areas;
- explicit loading, empty, and error states;
- stable DOM identifiers or selectors for Selenium tests.

The frontend must not:

- embed business rules that belong to backend services;
- duplicate server-side authorization logic;
- hide API contracts inside arbitrary component code.

## 7.3 Styling

The UI should be:

- clean,
- modern enough to be pleasant,
- not overly styled,
- accessible,
- responsive on desktop and mobile.

A lightweight CSS solution or a well-known component library may be used, provided it does not hide too much logic or complicate tests.

---

## 8. Domain and data modeling rules

## 8.1 Main domain entities

The implementation should cover at least these conceptual entities:

- User
- Citizen profile data / preferences
- Report
- Photo
- Category
- ReportStatus
- ReportUpdate / StatusHistory
- Follow
- Notification
- Message / MessageThread
- Verification token / session or auth token support
- Administrative configuration objects where needed

The central object is **Report**. Reports are geo-located, categorized, trackable, and enriched with up to three photos.

## 8.2 Photo rule

A report must contain **1 to 3 photos**. This must be enforced:

- at request validation level,
- at service/business logic level,
- ideally also defensively in persistence constraints or service guards.  
  The official baseline explicitly states one to three photos, with a maximum of 3.

## 8.3 Report statuses

Use a finite status model with exactly these values:

- Pending Approval
- Assigned
- In Progress
- Suspended
- Rejected
- Resolved

These are part of the official baseline and must not be renamed casually.

## 8.4 Rejection rule

If an operator rejects a report, a rejection motivation is mandatory.

## 8.5 Anonymity rule

If a report is marked anonymous:

- the reporter identity is hidden in all public outputs,
- but the municipality can still access the identity for operational purposes,
- public CSV/statistics/details must not leak identity.

## 8.6 Statistics rule

Statistics are **derived data**, not primary domain entities.  
Implement them through services and query/result DTOs, not as a core persistent aggregate unless there is a specific generated-report requirement later.

---

## 9. API design rules

## 9.1 General

The backend must expose REST APIs grouped logically, for example:

- `/api/public/...`
- `/api/auth/...`
- `/api/citizen/...`
- `/api/operator/...`
- `/api/admin/...`

Exact paths may vary, but role separation must stay clear.

## 9.2 Swagger / OpenAPI

All exposed APIs must be documented via Swagger / OpenAPI:

- endpoints,
- request bodies,
- params,
- response schemas,
- auth requirements,
- file uploads,
- error responses.

Swagger UI must be enabled in development.

## 9.3 DTO discipline

Never expose raw ORM entities directly.
Use schemas / DTO serializers for:

- public report summaries,
- detailed report views,
- profile data,
- notifications,
- messages,
- statistics,
- admin responses.

## 9.4 Error handling

Adopt centralized error handling:

- validation errors,
- authorization errors,
- not found,
- business rule violations,
- infrastructure errors.

Routes should map these to HTTP responses through a predictable mechanism.

## 9.5 Pagination and filtering

Public list endpoints should support:

- category filter,
- status filter,
- time period filter,
- sorting,
- pagination if needed.

The CSV export endpoint should reuse the same filtering semantics as the public table view. This alignment is required by the requirements baseline.

---

## 10. Persistence and DB portability rules

## 10.1 Mandatory DB abstraction rule

The application must be written so that switching from SQLite to MySQL requires only configuration changes.

Use:

- SQLAlchemy connection URL from environment variables,
- ORM models independent from DB vendor specifics,
- no raw SQL tied to SQLite syntax,
- no SQLite-only datatypes or pragma-dependent behavior in business logic.

## 10.2 Configuration approach

The backend must support at least:

- a full `DATABASE_URL`, or
- structured variables such as:
  - `DB_DRIVER`
  - `DB_HOST`
  - `DB_PORT`
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`

Recommended rule:

- accept `DATABASE_URL` if present,
- otherwise compose it from structured environment variables.

Examples:

- SQLite local: file-based URL
- MySQL in Docker Compose: service host + credentials

## 10.3 Compose-driven switch

Switching DBMS must be possible by changing:

- Compose service definitions,
- environment variables,
- mounted volumes if necessary.

No application source code changes should be required.

## 10.4 Repository isolation

Repositories must hide ORM query details so that DB changes do not propagate upward.

## 10.5 Migrations

Database migrations are recommended if time allows, but not mandatory for the initial baseline.  
If included, they must stay simple and readable.

---

## 11. File and photo storage rules

Report photos and optional profile pictures must not be stored as raw binary blobs in the main DB unless there is a specific technical reason to do so.

Preferred baseline:

- files stored on local filesystem,
- metadata stored in DB,
- base storage path configurable via environment variables,
- upload size and type limits configurable,
- paths abstracted behind a storage utility/service.

This makes local development and Docker mounting easier.

---

## 12. Authentication and authorization rules

## 12.1 Roles

At minimum support:

- visitor,
- citizen,
- operator,
- administrator.

## 12.2 Auth design

Use a simple and explicit auth model. JWT is acceptable if implemented cleanly. Session-based auth is also acceptable if it keeps the architecture simple.

Whichever option is chosen, the implementation must clearly support:

- registration,
- email verification,
- login,
- logout,
- role-based access control.

## 12.3 Authorization placement

Authorization checks may appear in:

- route decorators for coarse endpoint access,
- services/controllers for finer business constraints.

Do not bury authorization rules inside repositories.

---

## 13. Notification and messaging rules

When a report status changes, the system must create in-platform notifications for:

- the original reporter,
- all followers.

If email notifications are enabled for a user:

- an email copy may be sent,
- but email failure must never prevent the in-platform notification.

Messaging between operators and citizens is a first-class feature and must be modeled explicitly, not as an afterthought.

Implementation rule:

- notification creation and optional email sending must be separated,
- email sending should be wrapped behind a mailer abstraction,
- service tests must be able to mock email delivery easily.

---

## 14. Statistics implementation rules

## 14.1 Public statistics

Public statistics must include:

- reports by category,
- trends over time aggregated by day, week, or month.

## 14.2 Private statistics

Private statistics must include the official requested breakdowns:

- by status,
- by type/category,
- by type/category and status,
- by reporter,
- by reporter and type/category,
- by reporter, type/category, and status,
- top 1% reporters by type/category,
- top 5% reporters by type/category.

## 14.3 Implementation style

Implement statistics through:

- dedicated service methods,
- possibly dedicated read-only repositories or query helpers,
- explicit response DTOs.

Do not represent statistics as random arrays without semantics.
Use named structures such as:

- label + count,
- period + count,
- reporter + category + status + count.

---

## 15. Testing strategy

## 15.1 General testing goal

The codebase must be intentionally structured so teams can write meaningful:

- unit tests,
- integration tests,
- GUI tests.

The provided implementation should make it realistic to achieve the target coverage with understandable tests.

## 15.2 Backend testing rules

Use:

- `pytest`
- `pytest-cov`
- mocking where appropriate

Mandatory test categories:

### Unit tests

Focus on:

- services,
- controllers,
- selected utility modules,
- pure validation logic,
- permission logic.

Unit tests must isolate dependencies with mocks or fakes.

### Integration tests

Focus on:

- repository behavior,
- API endpoints with Flask test client,
- auth flow,
- DB interactions,
- serialization contracts,
- transactionally relevant workflows.

Recommended approach:

- temporary SQLite DB for integration tests,
- test app factory,
- fixtures for seeded data.

### What to mock

Mock external or non-essential infrastructure in unit tests:

- repositories when testing services,
- mailer,
- file storage,
- third-party map or email integrations,
- cross-service dependencies if the unit boundary requires it.

### What not to mock in integration tests

Do not mock:

- the whole persistence layer,
- request/response serialization,
- Flask routing,
  when the purpose is integration verification.

## 15.3 Frontend testing rules

Frontend testing for this baseline should focus on GUI verification with Selenium. Backend tests already cover the core validation and service logic. Frontend TypeScript unit testing is therefore outside the current scope.

### GUI / end-to-end tests

Use **Selenium** for browser-level tests on key flows:

- public report browsing,
- login,
- report submission,
- follow report,
- operator status update,
- profile preference change,
- admin statistics access.

To support Selenium:

- use stable selectors,
- avoid brittle DOM structures,
- keep pages deterministic,
- expose loading completion cues.

## 15.4 Coverage rules

Coverage must be measurable separately and clearly.

Recommended backend coverage setup:

- include controllers, services, repositories, auth helpers, and utility logic;
- exclude folders with little or no business logic if pedagogically justified, for example:
  - ORM models,
  - generated files,
  - configuration boilerplate,
  - migrations.

Recommended frontend coverage setup:

- include pages, components, hooks, API wrappers, and utility logic;
- exclude generated assets, trivial entrypoints, or style-only files if needed.

The exclusions must be explicit in configuration and documented so contributors understand what is counted and why.

## 15.5 Coverage tools

Recommended:

- backend: `pytest-cov`
- frontend: the standard coverage tool of the chosen frontend test runner
- GUI tests: keep GUI coverage/reporting separate from unit/component coverage

---

## 16. Project layout for testing

The repository should be organized so that tests can target layers independently.

Recommended root structure:

```text
project/
  backend/
  frontend/
  docs/
  docker/
    backend/
    frontend/
    mysql/
  compose/
    docker-compose.dev.yml
    docker-compose.mysql.yml
  .github/
```

Alternative equivalent organizations are acceptable if the same clarity is preserved.

Key rule:

- keep Docker-related files in dedicated folders,
- keep backend and frontend independent enough to be run/tested separately,
- keep shared documentation centralized.

---

## 17. Configuration and environment variables

## 17.1 Backend environment variables

At minimum define variables for:

- app environment
- secret key / auth secret
- database configuration
- email configuration
- file storage path
- CORS / frontend origin
- optional pagination defaults

Example set:

```env
FLASK_ENV=development
SECRET_KEY=change-me
DATABASE_URL=sqlite:///data/participium.db
DB_DRIVER=sqlite
DB_HOST=
DB_PORT=
DB_NAME=participium
DB_USER=
DB_PASSWORD=
UPLOAD_DIR=/app/uploads
MAIL_ENABLED=false
MAIL_HOST=
MAIL_PORT=
MAIL_USERNAME=
MAIL_PASSWORD=
FRONTEND_ORIGIN=http://localhost:3000
```

## 17.2 Frontend environment variables

At minimum define variables for:

- API base URL
- app title if desired
- feature flags if needed for education/demo purposes

Example:

```env
VITE_API_BASE_URL=http://localhost:5000/api
VITE_APP_NAME=Participium
```

## 17.3 Configuration rule

Every deploy-relevant value must come from configuration, not hardcoded literals in app code.

---

## 18. Docker and Compose requirements

## 18.1 Initial baseline

The initial baseline may run:

- frontend locally,
- backend locally,
- SQLite file locally,
  without full containerization.

But the structure must already anticipate containerization.

## 18.2 Target deployment baseline

The project must later support the following activities:

- write backend Dockerfile,
- write frontend Dockerfile,
- create/adapt Docker Compose,
- add an off-the-shelf MySQL image,
- switch from SQLite to MySQL only through environment variables and Compose edits.

Therefore, the code must already be compatible with this target.

## 18.3 Compose design rule

Compose must treat services as configurable units:

- frontend reads API base URL from env/build config,
- backend reads DB/mail/storage settings from env,
- MySQL service exposes credentials through env,
- volumes are used for persistent data where appropriate.

## 18.4 No hardcoded localhost assumptions

Neither frontend nor backend should assume:

- localhost-only deployment,
- fixed container names in code,
- direct filesystem paths that cannot be overridden.

---

## 19. Non-functional implementation rules

These rules operationalize the official NFRs.

### Responsiveness

The frontend must work on desktop and mobile without horizontal overflow in key flows.

### Security

Protected actions must be inaccessible without authentication or the correct role.

### Privacy

Anonymous public reports must never reveal the reporter identity.

### Reliability

In-platform notifications remain valid even if email delivery fails.

### Auditability

Status changes and messages must remain timestamped and traceable.

### Export safety

CSV export must contain only data already visible in the public table view.

---

## 20. Coding rules

The implementation should follow these mandatory rules:

1. Keep functions short and focused.
2. Prefer explicit names over clever abstractions.
3. Do not place business logic in Flask routes.
4. Do not place business logic in ORM models.
5. Repositories must hide ORM query details.
6. Services must be directly unit-testable with mocked dependencies.
7. Controllers must not depend on Flask response objects.
8. Configuration must always come from environment-aware settings.
9. Never hardcode DB vendor assumptions.
10. Public DTOs must not expose private fields.
11. Anonymous report handling must be enforced centrally.
12. CSV export must reuse the same public filtering semantics as the table view.
13. Status transition logic must be centralized, not duplicated across routes/components.
14. File storage and email sending must be abstracted behind helper/services that can be mocked.
15. Frontend components must use a dedicated API client layer.
16. Frontend pages must expose stable selectors for Selenium.
17. Keep the code easy to read for new contributors and reviewers.
18. Prefer readability and maintainability over maximum abstraction.

---

## 21. Suggested implementation order

A recommended implementation order is:

1. backend app factory, config, DB wiring, OpenAPI setup
2. auth and user registration/login/profile basics
3. categories and report core entity
4. report submission with photo upload and geo-location data
5. public map/table/detail endpoints
6. React public pages consuming those APIs
7. operator workflow and status updates
8. follow system and notifications
9. messaging
10. CSV export
11. public statistics
12. private admin statistics and configuration
13. backend test suite completion
14. frontend component tests
15. Selenium end-to-end suite
16. Dockerfiles and Compose evolution for MySQL

This order is coherent with the official functional decomposition and work breakdown.

---

## 22. Acceptance criteria for the generated codebase

The generated codebase is acceptable only if all the following are true:

- backend is Flask-based;
- APIs are documented with Swagger / OpenAPI;
- frontend is React-based;
- SQLite works in the default setup;
- configuration already supports switching to MySQL without code redesign;
- backend uses routes/controllers/services/repositories separation;
- frontend uses an API abstraction layer;
- public and private features are clearly separated;
- report anonymity is enforced correctly;
- photo count rule is enforced correctly;
- status lifecycle is implemented explicitly;
- notification logic is testable;
- messaging is testable;
- code is organized for backend pytest tests and frontend Selenium tests;
- coverage configuration is present and allows exclusions for low-value folders;
- Dockerization is anticipated structurally, even if completed later.

---

## 23. Final note

When there is a trade-off between:

- architectural cleverness and testability,
- abstraction and readability,
- compactness and clarity,

choose:

- **testability**,
- **readability**,
- **layer isolation**,
- **configuration-driven infrastructure**.

This project must remain both a working system and a maintainable reference codebase.


