import os
import shutil
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


_PLUGIN_PATH = Path(__file__).resolve().parents[2] / "participium_bug_report_plugin.py"
_SPEC = spec_from_file_location("_participium_bug_report_plugin_root", _PLUGIN_PATH)

if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Cannot load pytest plugin from {_PLUGIN_PATH}")

_PLUGIN = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_PLUGIN)

MARKER_NAME = _PLUGIN.MARKER_NAME
pytest_runtest_makereport = _PLUGIN.pytest_runtest_makereport
pytest_terminal_summary = _PLUGIN.pytest_terminal_summary


def pytest_configure(config):
    _PLUGIN.pytest_configure(config)
    _patch_chrome_driver_for_ci()


def _patch_chrome_driver_for_ci() -> None:
    driver_path = (
        os.getenv("CHROMEDRIVER_BIN")
        or os.getenv("CHROMEDRIVER_PATH")
        or shutil.which("chromedriver")
    )
    browser_path = (
        os.getenv("CHROME_BIN")
        or os.getenv("SE_BROWSER_PATH")
        or shutil.which("google-chrome")
        or shutil.which("chrome")
        or shutil.which("chromium")
        or shutil.which("chromium-browser")
    )

    if not driver_path and not browser_path:
        return

    try:
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.webdriver import WebDriver
    except ImportError:
        return

    if getattr(WebDriver.__init__, "_participium_ci_patched", False):
        return

    original_init = WebDriver.__init__

    def patched_init(self, options=None, service=None, keep_alive=True):
        options = options if options is not None else Options()

        if browser_path and not getattr(options, "binary_location", None):
            options.binary_location = browser_path

        existing_args = set(getattr(options, "_arguments", []))
        for argument in ("--no-sandbox", "--disable-dev-shm-usage"):
            if argument not in existing_args:
                options.add_argument(argument)

        if service is None and driver_path:
            service = Service(executable_path=driver_path)

        return original_init(self, options=options, service=service, keep_alive=keep_alive)

    patched_init._participium_ci_patched = True
    WebDriver.__init__ = patched_init
