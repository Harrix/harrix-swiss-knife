"""Tests for bundled Roboto and JetBrains Mono fonts."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication, QLabel, QLineEdit

from harrix_swiss_knife.qt_app_font import (
    APP_FONT_FAMILY,
    MONO_FONT_FAMILY,
    OVERLAY_LINE_EDIT_STYLE,
    apply_mono_font,
    apply_ui_font_scale,
    bundled_font_paths,
    bundled_font_resource_paths,
    current_ui_font_scale,
    install_app_fonts,
    load_jetbrains_mono_fonts,
    load_roboto_fonts,
    scale_explicit_widget_font,
    style_overlay_line_edit,
)


def test_bundled_font_files_exist() -> None:
    paths = bundled_font_paths()
    names = {path.name for path in paths}
    assert len(paths) == 10
    assert all(path.suffix == ".ttf" for path in paths)
    assert "Roboto-Regular.ttf" in names
    assert "Roboto-Medium.ttf" in names
    assert "Roboto-Bold.ttf" in names
    assert "Roboto-Italic.ttf" in names
    assert "JetBrainsMono-Regular.ttf" in names


def test_bundled_font_resources_exist() -> None:
    paths = bundled_font_resource_paths()
    assert len(paths) == 10
    assert any(path.endswith("Roboto-Regular.ttf") for path in paths)
    assert any(path.endswith("JetBrainsMono-Regular.ttf") for path in paths)


def test_install_app_fonts_sets_roboto() -> None:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    assert load_roboto_fonts()
    assert load_jetbrains_mono_fonts()
    app.setProperty("_hskAppFontInstalled", None)
    install_app_fonts(app)
    assert app.font().family() == APP_FONT_FAMILY
    install_app_fonts(app)
    assert app.font().family() == APP_FONT_FAMILY


def test_install_app_fonts_sets_base_point_size() -> None:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    assert load_roboto_fonts()
    app.setProperty("_hskAppFontInstalled", None)
    before = app.font().pointSizeF()
    install_app_fonts(app, base_point_size=14)
    assert app.font().family() == APP_FONT_FAMILY
    assert abs(app.font().pointSizeF() - 14.0) < 0.01
    if before > 0:
        assert abs(current_ui_font_scale() - (14.0 / before)) < 0.01


def test_scale_explicit_widget_font_multiplies_point_size_once() -> None:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    previous = app.property("_hskUiFontScale")
    app.setProperty("_hskUiFontScale", 0.8)
    label = QLabel()
    font = label.font()
    font.setPointSize(20)
    label.setFont(font)
    scale_explicit_widget_font(label)
    assert abs(label.font().pointSizeF() - 16.0) < 0.01
    scale_explicit_widget_font(label)
    assert abs(label.font().pointSizeF() - 16.0) < 0.01
    apply_ui_font_scale(label)
    assert abs(label.font().pointSizeF() - 16.0) < 0.01
    assert current_ui_font_scale() == 0.8
    label.close()
    app.setProperty("_hskUiFontScale", previous)


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


def test_style_overlay_line_edit_matches_quick_paste_look() -> None:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    edit = QLineEdit()
    before = edit.font().pointSize()
    style_overlay_line_edit(edit)
    assert edit.font().family() == MONO_FONT_FAMILY
    assert edit.styleSheet() == OVERLAY_LINE_EDIT_STYLE
    assert edit.minimumHeight() >= edit.fontMetrics().height()
    if before > 0:
        assert edit.font().pointSize() >= before
    edit.close()
