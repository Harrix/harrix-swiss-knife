"""Save offscreen grabs of the five chart tabs in light and dark themes.

Run from the repo root with the project virtualenv:

    Python `scripts/grab_chart_pages.py`

Images land in `build/chart-grabs/`. The script forces the offscreen Qt
platform so it does not open real Windows. Tracker databases are whatever
the apps already use; a missing database is reported and that tab is skipped.

"""

# ruff: noqa: INP001

from __future__ import annotations

import os
import traceback
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("HSK_MUTE_SOUNDS", "1")

ROOT = Path(__file__).resolve().parents[1]

from PySide6.QtWidgets import QApplication, QTabWidget  # noqa: E402

from harrix_swiss_knife.fluent.theme import FluentTheme, ThemeMode  # noqa: E402

_SIZES = ((1600, 1000), (1280, 800))
_OUT = ROOT / "build" / "chart-grabs"


def _grab(app: QApplication, window: object, stem: str, width: int, height: int) -> None:
    resize = getattr(window, "resize", None)
    show = getattr(window, "show", None)
    grab = getattr(window, "grab", None)
    if not callable(resize) or not callable(show) or not callable(grab):
        return
    resize(width, height)
    show()
    for _ in range(8):
        app.processEvents()
    path = _OUT / f"{stem}-{width}x{height}.png"
    grab().save(str(path))
    close = getattr(window, "close", None)
    if callable(close):
        close()
    app.processEvents()


def _open(factory: object, tab: str) -> object:
    window = factory(hide_on_close=True)  # type: ignore[operator]
    _select_tab(window, tab)
    return window


def _select_tab(window: object, title: str) -> bool:
    find = getattr(window, "findChildren", None)
    if not callable(find):
        return False
    for tabs in find(QTabWidget):
        for index in range(tabs.count()):
            if tabs.tabText(index) == title:
                tabs.setCurrentIndex(index)
                return True
    return False


def main() -> None:
    """Grab Finance, Fitness, Food, Habits Charts, and TickTick."""
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication([])
    _OUT.mkdir(parents=True, exist_ok=True)

    from harrix_swiss_knife.apps.finance.main import MainWindow as FinanceWindow  # noqa: PLC0415
    from harrix_swiss_knife.apps.fitness.main import MainWindow as FitnessWindow  # noqa: PLC0415
    from harrix_swiss_knife.apps.food.main import MainWindow as FoodWindow  # noqa: PLC0415
    from harrix_swiss_knife.apps.habits.main import MainWindow as HabitsWindow  # noqa: PLC0415

    pages = (
        ("finance-charts", FinanceWindow, "Charts"),
        ("fitness-charts", FitnessWindow, "Charts"),
        ("food-charts", FoodWindow, "Charts"),
        ("habits-charts", HabitsWindow, "Charts"),
        ("habits-ticktick", HabitsWindow, "TickTick"),
    )
    theme = FluentTheme.instance()
    previous = theme.mode()
    try:
        for mode, mode_name in ((ThemeMode.LIGHT, "light"), (ThemeMode.DARK, "dark")):
            theme.set_mode(mode, persist=False)
            for stem, factory, tab in pages:
                for width, height in _SIZES:
                    try:
                        window = _open(factory, tab)
                        _grab(app, window, f"{mode_name}-{stem}", width, height)
                        print(f"saved {mode_name} {stem} {width}x{height}")
                    except Exception:
                        print(f"skip {mode_name} {stem} {width}x{height}")
                        traceback.print_exc()
    finally:
        theme.set_mode(previous, persist=False)


if __name__ == "__main__":
    main()
