# Task 5 - Backend Black-Box Testing

## Current testing phase
At this stage, the operational design and contract definition work has already been completed, while the system implementation is still being developed by the implementation team.

For this reason, the black-box tests produced in this task are not expected to run successfully yet. The corresponding implementation is not available, so the current goal is to design the test cases in parallel with development, using the published signatures, model structure, expected outputs, and documented exceptions as the testing contract.

This parallel work is useful because it allows the testing activity to start before code delivery. When the implementation becomes available, the drafted test suite will be completed with the required execution setup, data preparation, fixtures, and environment configuration, and it will then be used as the basis for the actual test execution.

## Deliverables to produce
Complete the following deliverables:

- **`../doc/deliverable/05_BlackBoxReport.md`**
- **the pytest draft files under `../src/backend/tests/blackbox/`**

Use the stub implementation provided under:

- **`../src/backend/participium/`**

You may add short notes or helper comments in the test files, but **do not replace the provided stubs with a real implementation**.

## Baseline scope reference
Work only on the material provided under:

- **`../src/backend/`**

For this task, `src/backend` contains only the signatures and the minimal model stubs needed to understand the test inputs and outputs.

The available Python files are a specification artifact for black-box test design, not a working backend.

## General guidance

### Treat the provided stubs as a contract
Use the available service, core, and model stubs to understand:
- the input parameters,
- the explicit return type,
- the documented exceptions,
- the objects involved in each method,
- the data that would need to exist for a meaningful test.

### Focus on test design
The goal is to design and write black-box test cases, not to execute them against a working system.

Each test file must therefore show:
- how the target method would be called,
- which assertions would be checked on the returned result,
- which exception type would be expected in failing cases.

### Keep setup assumptions explicit
In testing, a fixture is the data or system state that must already exist before the method under test is called. This is different from testing a standalone function that depends only on its explicit input parameters. In this task, many methods belong to a larger system and may depend on users, reports, categories, tokens, messages, notifications, uploaded files, or specific object states already being present. Fixtures are used to make those assumptions explicit: they describe which data would need to be created, loaded, or configured so that the test case is meaningful.

If a test case would require preloaded users, reports, categories, tokens, messages, notifications, or uploaded files, describe that setup explicitly in the `Fixture` column of the report.

Inside the pytest file, you may also leave short comments or illustrative fixture placeholders to explain what data would later need to be created.

### Cover valid and invalid scenarios
The test set should include:
- normal successful cases,
- invalid-input cases,
- exception-oriented cases,
- equivalence partitioning,
- boundary value analysis where meaningful.

---

## 1) Black-Box Analysis Report

### What you must provide
Complete the stub tables in:

- **`../doc/deliverable/05_BlackBoxReport.md`**

For each target, fill the corresponding table rows with:
- a test case ID,
- one column value for each input parameter,
- the expected result,
- the fixture/data context required for the case.

### Expectations
The report should:
- make the tested inputs explicit,
- document the expected output or exception type,
- state clearly when a case depends on preloaded data,
- remain compact and directly useful as a black-box specification.

---

## 2) Pytest Test Draft

### What you must provide
Write the black-box test draft under:

- **`../src/backend/tests/blackbox/`**

Create one file per target method. The recommended file names are:

- **`test_verify_email.py`**
- **`test_authenticate.py`**
- **`test_parse_date.py`**
- **`test_status_flow.py`**
- **`test_create_report.py`**
- **`test_update_status.py`**
- **`test_public_reports.py`**
- **`test_send_message.py`**
- **`test_verify_password.py`**
- **`test_create_notification.py`**
- **`test_update_profile.py`**

Each file must use normal pytest syntax, including `assert` and `pytest.raises(...)`.

### Expectations
The pytest draft should:
- mirror the behaviours documented in the report,
- call the provided stub methods using the published signatures,
- show assertions on the returned object when a case is successful,
- show exception handling by type when a case is invalid,
- remain readable and easy to extend later.

At this stage the file is not expected to run successfully, because the implementation is intentionally not provided yet.

---

## 3) Reference Material

### Model and service stubs
The provided stubs under `participium/` show only the structure needed to understand the involved objects and import paths.

They are present only to support test writing and code organization.

### Example tests
`test_verify_email.py` already contains simple examples based on `verify_email` to show the intended style for:
- direct method invocation,
- `assert` on the returned object,
- `pytest.raises(...)` for expected exceptions.

These examples are illustrative and should be used as a starting point for the other files.
