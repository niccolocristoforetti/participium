# Task 6 - Backend White-Box Testing

## Current testing phase

In this task, the goal is to inspect the source code of the assigned backend functions and design white-box tests directly from their internal control flow.

Unlike black-box testing, the reference is the implementation itself: read the target methods, identify their control-flow structure, and design tests from that structure.

## Deliverables to produce

Complete the following deliverables:

- **`../doc/deliverable/06_WhiteBoxReport.md`**
- **the pytest files under `../src/backend/tests/whitebox/`**

## Baseline scope reference

Work on the material provided under:

- **`../src/backend/`**

## General guidance

### Aim for structural coverage

The test set should be designed to support:

- node coverage,
- edge coverage,
- condition coverage,
- loop coverage when applicable,
- path coverage.

### Mock external collaborators

The code under test may call repositories, storage services, notification services, helper functions, or other collaborators.

When a dependency is outside the function under test, mock it. The tests should focus on the internal control flow of the selected method, not on database population or external system setup.

### Keep the target path explicit

Each test should make clear which structural path it is meant to cover and should assert on outputs, state changes, raised exceptions, or collaborator interactions.

---

## 1) White-Box Analysis Report

### What you must provide

Prepare the white-box analysis report in:

- **`../doc/deliverable/06_WhiteBoxReport.md`**

For each target method, complete the following sections:

- Control Flow Graph
- Atomic Conditions
- Structural Lower Bound
- Node Coverage
- Edge Coverage
- Condition Coverage
- Loop Coverage, when applicable
- Path Coverage
- Minimal Suite Test

### Expectations

The report should:

- include the control flow graph as an image link;
- identify atomic conditions and relevant structural elements;
- explain the coverage objective for nodes, edges, conditions, loops, and paths;
- summarize the minimal test suite needed to obtain the highest feasible structural coverage.

---

## 2) Pytest Test

### What you must provide

Write the white-box tests under:

- **`../src/backend/tests/whitebox/`**

The target files are:

- **`test_wb_create_report.py`**
- **`test_wb_resolve_recipient.py`**
- **`test_wb_notify_status_change.py`**
- **`test_wb_notification_counts.py`**
- **`test_wb_update_user.py`**

Each file must use normal pytest syntax, including `assert`, `pytest.raises(...)`, fixtures or helpers where useful, and mocked collaborators where needed.

### Expectations

The pytest tests should:

- reflect the internal control flow of the selected function;
- make the targeted paths explicit;
- mock every dependency that is outside the function under test;
- show assertions on outputs, state changes, raised exceptions, or collaborator effects.

---

## 3) Reference Material

### White-box targets

The selected targets are the five methods made available in the provided source files under `participium/services/`.

### Example with mocked collaborators

`test_wb_mark_message_notifications.py` provides a compact white-box example. It shows how to isolate external collaborators with mocks so that the test can focus on the internal logic of the target function.
