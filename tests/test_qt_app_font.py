"""Tests for the bundled JetBrains Mono application font."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.qt_app_font import (
    APP_FONT_FAMILY,
    bundled_font_paths,
    install_app_fonts,
    load_jetbrains_mono_fonts,
)


def test_bundled_jetbrains_mono_files_exist() -> None:
    paths = bundled_font_paths()
    assert len(paths) == 5
    assert all(path.suffix == ".ttf" for path in paths)
    assert any(path.name == "JetBrainsMono-Regular.ttf" for path in paths)


def test_install_app_fonts_sets_jetbrains_mono() -> None:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    assert load_jetbrains_mono_fonts()
    install_app_fonts(app)
    assert app.font().family() == APP_FONT_FAMILY
    install_app_fonts(app)
    assert app.font().family() == APP_FONT_FAMILY
