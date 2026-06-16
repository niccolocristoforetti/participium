import pytest


MARKER_NAME = "implementation_bug"


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        f"{MARKER_NAME}(reason): documents an implementation bug revealed by a failing test"
    )
    config._participium_bug_reports = []


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    if not report.failed:
        return

    marker = item.get_closest_marker(MARKER_NAME)

    if marker is None:
        return

    reason = marker.kwargs.get("reason")

    if reason is None and marker.args:
        reason = marker.args[0]

    if reason is None:
        reason = "No implementation bug description provided."

    item.config._participium_bug_reports.append((report.nodeid, reason))


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    bug_reports = getattr(config, "_participium_bug_reports", [])

    if not bug_reports:
        return

    terminalreporter.section("Implementation bugs reported by failing tests")

    for nodeid, reason in bug_reports:
        terminalreporter.line(f"{nodeid}:\n {reason}")
