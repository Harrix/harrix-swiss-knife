"""Tests for UIC surrogate-escape rewriting and tracker UI load."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication, QMainWindow

from harrix_swiss_knife.apps.common.uic_compile import (
    combine_utf16_surrogates,
    install_safe_qt_translate,
    rewrite_uic_source,
)
from harrix_swiss_knife.apps.finance.window import Ui_MainWindow as FinanceUi
from harrix_swiss_knife.apps.fitness.window import Ui_MainWindow

_APPS_ROOT = Path(__file__).resolve().parents[1] / "src" / "harrix_swiss_knife" / "apps"


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_rewrite_uic_source_combines_emoji_surrogate_pair() -> None:
    """Combine a high+low UTF-16 surrogate pair from `pyside6-uic` into one code point."""
    source = 'u"\\ud83d\\udccb Show All Set Records"'
    rewritten = rewrite_uic_source(source)
    assert "\\ud83d" not in rewritten
    assert "\\U0001f4cb" in rewritten
    value = ast.literal_eval(rewritten.removeprefix("u"))
    assert value == "📋 Show All Set Records"


def test_generated_window_py_files_have_no_surrogate_pair_escapes() -> None:
    """Generated UIC modules must not contain UTF-16 surrogate pair escapes."""
    for app_name in ("finance", "fitness", "food", "habits"):
        text = (_APPS_ROOT / app_name / "window.py").read_text(encoding="utf-8")
        assert rewrite_uic_source(text) == text, f"{app_name}/window.py still has UTF-16 surrogate escapes"


def test_combine_utf16_surrogates_broom_emoji() -> None:
    """Runtime strings with UTF-16 surrogate pairs become a real emoji."""
    raw = chr(0xD83E) + chr(0xDDF9)
    assert combine_utf16_surrogates(raw) == "🧹"


def test_install_safe_qt_translate_accepts_surrogate_emoji(qapp: QApplication) -> None:  # noqa: ARG001
    """`translate` must accept UIC-style surrogate emoji after the patch."""
    install_safe_qt_translate()
    raw = chr(0xD83E) + chr(0xDDF9)
    assert QCoreApplication.translate("MainWindow", raw, None) == "🧹"


def test_fitness_setup_ui_does_not_raise_on_translate(qapp: QApplication) -> None:  # noqa: ARG001
    """Regression: emoji labels in Fitness `retranslateUi` must be valid UTF-8."""
    install_safe_qt_translate()
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    assert "Show All Set Records" in ui.actionShow_All_Set_Records.text()


def test_finance_setup_ui_does_not_raise_on_translate(qapp: QApplication) -> None:  # noqa: ARG001
    """Regression: broom emoji on Finance clear-filter must be valid UTF-8."""
    install_safe_qt_translate()
    window = QMainWindow()
    ui = FinanceUi()
    ui.setupUi(window)
    assert ui.pushButton_clear_filter.text()
