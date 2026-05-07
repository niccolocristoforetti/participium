# Task 8 - Postman API Acceptance Testing

## Current testing phase

The goal of this task is to prepare an external API acceptance test suite for the implemented Participium backend.

This task is different from the pytest-based black-box, white-box, and coverage-oriented tasks. Its purpose is to exercise the running backend from the outside, through HTTP requests, as a final acceptance check for the API behavior visible to a client.

## Deliverables to produce

Complete the following deliverables:

- **`../src/backend/postman/Participium.postman_collection.json`**
- **`../src/backend/postman/Participium.postman_environment.json`**

Do not produce a specific documentation deliverable for this task.

Do not commit generated Newman reports, screenshots, local Postman history, or machine-specific files. The exported collection and exported environment are the deliverables.

## Baseline scope reference

Work on the implemented backend and its published API contract.
The Swagger UI is available, when the backend is running with the default configuration, at:

- **`http://localhost:5050/api/docs/`**


## General guidance

### Treat the suite as external acceptance testing

The collection must interact with the running backend only through HTTP requests.

Do not call Python functions directly. Do not use Flask test clients. Do not access the database directly from scripts. Do not change the backend implementation to make the Postman suite pass.

The collection should assume the backend is started according to `../src/backend/README.md`, with the default seed data available unless the suite explicitly creates the data it needs through public API calls.

### Keep authentication explicit

The suite must verify role-based access control.

The backend may use session cookies or another authentication mechanism depending on the implementation. Use the mechanism exposed by the API. If the backend uses cookies, rely on Postman's cookie handling and log in again before executing requests that require a different role. If the backend exposes tokens, store them in environment variables and use them consistently.

Do not fake authorization headers or manually inject authentication data that the API itself did not return.

### Make the suite repeatable

The collection must be executable from top to bottom more than once against a local development backend.

Use unique values for data that may conflict across runs, such as usernames, emails, category names, and report titles. Store generated values in the environment from pre-request scripts when needed.

Created resources should be reused by later requests through environment variables.

---

## 1) Postman Environment

### What you must provide

Create and export the environment file:

- **`../src/backend/postman/Participium.postman_environment.json`**

### Expectations

The environment should include at least:

- `base_url`, with the default value `http://localhost:5050/api/v1`;
- credentials for the seeded demo users where useful:
  - `citizen@example.com` / `Citizen123!`
  - `operator@example.com` / `Operator123!`
  - `admin@example.com` / `Admin123!`
- dynamic variables populated during collection execution;
- fixed invalid identifiers for negative tests, for example a non-existing report id or category id.

Environment values that are generated during a run should start empty in the exported file.

Do not include personal credentials, private tokens, machine-specific paths, or local-only secrets.

---

## 2) Postman Collection

### What you must provide

Create and export the collection file:

- **`../src/backend/postman/Participium.postman_collection.json`**

### Required collection organization

Organize the collection into functional folders: the resulting structure must be clear, and the suite must remain easy to execute in a single ordered run.

### Required request coverage

The suite must cover the API behavior needed to validate the use-case preconditions, minimum guarantees, and success guarantees from the official documentation.

The Swagger documentation is the authoritative source for endpoint paths, methods, request bodies, query parameters, and response schemas.

### Test script expectations

Every request must include Postman tests in the `Tests` tab.

The tests should check, where meaningful:

- expected HTTP status code;
- JSON response shape;
- required fields and field types;
- domain values such as roles and report statuses;
- created or updated state by reading the resource again;
- collection/environment variable updates;
- authorization behavior for unauthenticated users and wrong roles;
- validation errors for invalid inputs;
- public/private data separation, especially anonymous reports and CSV export.

Do not limit tests to `pm.response.to.have.status(...)`. Status-code checks are necessary but not sufficient.

### Pre-request script expectations

Use pre-request scripts only to prepare data needed by the request or by a later assertion, for example:

- generating unique usernames or emails;
- generating unique category/report titles;
- choosing values from environment variables;
- preparing timestamps or filter values.

Do not hide assertions in pre-request scripts. Assertions belong in the `Tests` tab.

---

## 3) Optional Newman Execution

The exported collection should be executable with Newman.

Example command from the repository root:

```powershell
newman run src/backend/postman/Participium.postman_collection.json -e src/backend/postman/Participium.postman_environment.json
```

Newman execution is useful for local verification and possible later pipeline integration, but the deliverable for this task remains the exported collection and environment.

If the suite depends on the backend running with seed data, make that assumption visible in the collection or environment descriptions rather than relying on undocumented local state.

---

## 4) Quality Criteria

### Acceptance value

The collection should read as a coherent acceptance test campaign, not as a dump of manually captured requests.

It should demonstrate that the API supports the documented user workflows and rejects invalid or unauthorized operations according to the use-case guarantees.

### Maintainability

The suite should be maintainable:

- clear folder structure;
- meaningful request names;
- limited duplication;
- reusable environment variables;
- deterministic dynamic data;
- assertions that explain what behavior is being verified.

### Independence from implementation internals

The collection must validate externally observable behavior.

It should not depend on database row order unless the API contract guarantees it, should not assume private implementation details, and should not require manual database cleanup between normal local runs.

### Executability

Before submission, run the collection against the local backend and ensure that the intended successful requests pass and the intended negative requests fail in the expected controlled way.

Negative tests are successful when they assert the expected error response, such as `400`, `401`, `403`, `404`, or another status documented by the API.
