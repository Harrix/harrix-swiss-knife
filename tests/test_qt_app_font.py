"""Tests for bundled Fira Sans and JetBrains Mono fonts."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication, QLabel

from harrix_swiss_knife.qt_app_font import (
    APP_FONT_FAMILY,
    MONO_FONT_FAMILY,
    apply_mono_font,
    bundled_font_paths,
    bundled_font_resource_paths,
    install_app_fonts,
    load_fira_sans_fonts,
    load_jetbrains_mono_fonts,
)


def test_bundled_font_files_exist() -> None:
    paths = bundled_font_paths()
    names = {path.name for path in paths}
    assert len(paths) == 10
    assert all(path.suffix == ".ttf" for path in paths)
    assert "FiraSans-Regular.ttf" in names
    assert "JetBrainsMono-Regular.ttf" in names


def test_bundled_font_resources_exist() -> None:
    paths = bundled_font_resource_paths()
    assert len(paths) == 10
    assert any(path.endswith("FiraSans-Regular.ttf") for path in paths)
    assert any(path.endswith("JetBrainsMono-Regular.ttf") for path in paths)


def test_install_app_fonts_sets_fira_sans() -> None:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    assert load_fira_sans_fonts()
    assert load_jetbrains_mono_fonts()
    app.setProperty("_hskAppFontInstalled", None)
    install_app_fonts(app)
    assert app.font().family() == APP_FONT_FAMILY
    install_app_fonts(app)
    assert app.font().family() == APP_FONT_FAMILY


def test_apply_mono_font_sets_jetbrains_mono() -> None:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    label = QLabel()
    apply_mono_font(label)
    assert label.font().family() == MONO_FONT_FAMILY
    label.close()
