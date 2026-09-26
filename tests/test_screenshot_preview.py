"""Tests for screenshot preview dated paths, canvas, and tabbed window."""

from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest
from PySide6.QtCore import QPoint, QPointF, QRect, QStandardPaths, Qt
from PySide6.QtGui import QColor, QImage, QKeyEvent, QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QFileDialog, QPushButton, QStyle, QTabWidget

from harrix_swiss_knife.apps.common.qt_main_window import compute_app_window_geometry
from harrix_swiss_knife.screenshot import preview_dialog as preview_dialog_module
from harrix_swiss_knife.screenshot.annotations import (
    Annotation,
    AnnotationDocument,
    AnnotationStyle,
    AnnotationTool,
)
from harrix_swiss_knife.screenshot.dated_image_path import images_folder, next_dated_image_path
from harrix_swiss_knife.screenshot.preview_canvas import _ZOOM_STEP, ScreenshotPreviewCanvas
from harrix_swiss_knife.screenshot.preview_dialog import (
    _MIN_WINDOW_WIDTH,
    ScreenshotPreviewWindow,
    _half_pixel_size,
    _is_ctrl_s,
    _max_side_pixel_size,
    _ReduceSizeDialog,
    show_screenshot_preview,
)
from harrix_swiss_knife.screenshot.tool_colors import load_tool_colors, save_tool_colors


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


@pytest.fixture(autouse=True)
def _reset_preview_singleton() -> Iterator[None]:
    window = preview_dialog_module._preview_holder["window"]
    preview_dialog_module._preview_holder["window"] = None
    if window is not None:
        window.close()
        window.deleteLater()
    QApplication.processEvents()
    yield
    window = preview_dialog_module._preview_holder["window"]
    preview_dialog_module._preview_holder["window"] = None
    if window is not None:
        window.close()
        window.deleteLater()
    QApplication.processEvents()


def test_images_folder_under_project_root() -> None:
    assert images_folder(Path("D:/proj")) == Path("D:/proj/temp/images")


def test_next_dated_image_path_starts_at_01(tmp_path: Path) -> None:
    path = next_dated_image_path(tmp_path, today=date(2026, 8, 29))
    assert path.name == "2026-08-29_01.png"
    assert path.parent == tmp_path.resolve()


def test_next_dated_image_path_skips_existing_indices(tmp_path: Path) -> None:
    (tmp_path / "2026-08-29_01.png").write_bytes(b"x")
    (tmp_path / "2026-08-29_02.jpg").write_bytes(b"x")
    (tmp_path / "2026-08-28_99.png").write_bytes(b"x")
    path = next_dated_image_path(tmp_path, today=date(2026, 8, 29))
    assert path.name == "2026-08-29_03.png"


def test_crop_tool_selects_full_image_by_default(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(40, 20, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.red)
    canvas = ScreenshotPreviewCanvas(image)
    canvas.resize(200, 100)
    document = AnnotationDocument(image)
    canvas.set_document(document)
    canvas.set_tool(AnnotationTool.CROP)
    assert canvas.crop_mode
    assert canvas.crop_pending
    assert canvas._crop_rect == QRect(0, 0, 40, 20)
    canvas.close()


def test_confirm_full_image_crop_keeps_annotations(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(40, 20, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.white)
    canvas = ScreenshotPreviewCanvas(image)
    canvas.resize(200, 100)
    document = AnnotationDocument(image)
    document.begin_draft(
        Annotation(
            tool=AnnotationTool.LINE,
            points=[QPointF(2, 2), QPointF(10, 10)],
            style=AnnotationStyle(),
        )
    )
    assert document.commit_draft()
    canvas.set_document(document)
    canvas.set_tool(AnnotationTool.CROP)
    assert canvas.confirm_crop()
    assert not canvas.crop_mode
    assert document.base_image.width() == 40
    assert document.base_image.height() == 20
    assert len(document.annotations) == 1
    canvas.close()


def _widget_pos_for_image_pixel(canvas: ScreenshotPreviewCanvas, x: float, y: float) -> QPointF:
    rect = canvas._image_rect()
    width, height = canvas._source_size()
    return QPointF(
        rect.left() + (x + 0.5) / width * rect.width(),
        rect.top() + (y + 0.5) / height * rect.height(),
    )


def test_eyedropper_zoom_draws_unsmoothed_pixels(qapp: QApplication) -> None:
    image = QImage(2, 1, QImage.Format.Format_RGB32)
    image.setPixelColor(0, 0, QColor("#ff0000"))
    image.setPixelColor(1, 0, QColor("#0000ff"))
    canvas = ScreenshotPreviewCanvas(image)
    canvas.resize(200, 100)
    canvas.set_document(AnnotationDocument(image))
    canvas.zoom_by(40.0)
    canvas.set_tool(AnnotationTool.NONE)
    assert not canvas._crisp_source_pixels()
    canvas.set_tool(AnnotationTool.EYEDROPPER)
    qapp.processEvents()
    assert canvas._crisp_source_pixels()
    rect = canvas._image_rect()
    grabbed = canvas.grab()
    pixels = grabbed.toImage()
    ratio = grabbed.devicePixelRatio()
    pixel_w = rect.width() / 2.0
    y = int(rect.center().y() * ratio)
    left_x = int((rect.left() + pixel_w - 2) * ratio)
    right_x = int((rect.left() + pixel_w + 2) * ratio)
    left = pixels.pixelColor(left_x, y)
    right = pixels.pixelColor(right_x, y)
    assert (left.red(), left.green(), left.blue()) == (255, 0, 0)
    assert (right.red(), right.green(), right.blue()) == (0, 0, 255)
    canvas.close()


def test_each_drawing_tool_keeps_its_own_color(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored = {
        "arrow": "#111111",
        "rectangle": "#de2b26",
        "ellipse": "#de2b26",
        "line": "#de2b26",
        "pen": "#de2b26",
        "text": "#222222",
        "highlight": "#ffe14a",
    }

    def save(colors: dict[str, str]) -> None:
        stored.clear()
        stored.update(colors)

    monkeypatch.setattr(preview_dialog_module, "load_tool_colors", lambda _text_color: dict(stored))
    monkeypatch.setattr(preview_dialog_module, "save_tool_colors", save)
    image = QImage(20, 10, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.white)
    window = show_screenshot_preview(image)
    assert AnnotationTool.HIGHLIGHT in window._tool_buttons
    assert window._annotation_color.name() == "#222222"
    window._set_tool(AnnotationTool.HIGHLIGHT)
    assert window._annotation_color.name() == "#ffe14a"
    window._set_annotation_color(QColor("#00aa00"))
    assert stored["highlight"] == "#00aa00"
    assert stored["text"] == "#222222"
    assert stored["arrow"] == "#111111"
    window._set_tool(AnnotationTool.ARROW)
    assert window._annotation_color.name() == "#111111"
    window._set_tool(AnnotationTool.HIGHLIGHT)
    assert window._annotation_color.name() == "#00aa00"
    window._set_tool(AnnotationTool.TEXT)
    assert window._annotation_color.name() == "#222222"
    window.close()


def test_tool_colors_roundtrip_in_config_temp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "config.json").write_text("{}", encoding="utf-8")
    (config_dir / "config-temp.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(preview_dialog_module.h.dev, "get_project_root", lambda: tmp_path)
    colors = load_tool_colors("#336699")
    assert colors["text"] == "#336699"
    assert colors["highlight"] == "#ffe14a"
    colors["highlight"] = "#00aa00"
    colors["arrow"] = "#111111"
    save_tool_colors(colors)
    loaded = load_tool_colors("#000000")
    assert loaded["highlight"] == "#00aa00"
    assert loaded["arrow"] == "#111111"
    assert loaded["text"] == "#336699"


def test_eyedropper_samples_visible_pixel(qapp: QApplication) -> None:
    image = QImage(20, 10, QImage.Format.Format_RGB32)
    image.fill(QColor("#112233"))
    image.setPixelColor(4, 3, QColor("#ff8800"))
    canvas = ScreenshotPreviewCanvas(image)
    canvas.resize(200, 100)
    document = AnnotationDocument(image)
    canvas.set_document(document)
    canvas.set_tool(AnnotationTool.EYEDROPPER)
    qapp.processEvents()
    color = canvas.sample_color_at(_widget_pos_for_image_pixel(canvas, 4, 3))
    assert color is not None
    assert color.name() == "#ff8800"
    assert canvas.sample_color_at(QPointF(-20, -20)) is None
    canvas.close()


def test_preview_window_eyedropper_copies_color_without_changing_tool(
    qapp: QApplication,
) -> None:
    image = QImage(20, 10, QImage.Format.Format_RGB32)
    image.fill(QColor("#112233"))
    image.setPixelColor(4, 3, QColor("#aabbcc"))
    window = show_screenshot_preview(image)
    tool_color = window._annotation_color.name()
    window._set_tool(AnnotationTool.EYEDROPPER)
    tab = window._current_tab()
    assert tab is not None
    style_color = tab.canvas._style.color.name()
    qapp.processEvents()
    _left_click(tab.canvas, _widget_pos_for_image_pixel(tab.canvas, 4, 3))
    assert window._annotation_color.name() == tool_color
    assert tab.canvas._style.color.name() == style_color
    clipboard = qapp.clipboard()
    assert clipboard is not None
    assert clipboard.text() == "#aabbcc"
    window.close()


def test_double_click_restores_zoom_then_fits_small_image(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(40, 20, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.red)
    canvas = ScreenshotPreviewCanvas(image)
    canvas.resize(400, 200)
    canvas.zoom_by(2.0, anchor=QPointF(200, 100))
    _double_click(canvas, QPointF(200, 100))
    assert canvas.zoom == pytest.approx(1.0)
    native = canvas._image_rect()
    assert native.width() == pytest.approx(40.0)
    assert native.height() == pytest.approx(20.0)
    _double_click(canvas, QPointF(200, 100))
    fitted = canvas._image_rect()
    assert fitted.width() == pytest.approx(400.0, abs=1.0)
    assert fitted.height() == pytest.approx(200.0, abs=1.0)
    _double_click(canvas, QPointF(200, 100))
    assert canvas.zoom == pytest.approx(1.0)
    canvas.close()


def test_double_click_restores_large_image_without_upscaling(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(800, 400, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.blue)
    canvas = ScreenshotPreviewCanvas(image)
    canvas.resize(200, 200)
    canvas.zoom_by(3.0, anchor=QPointF(100, 100))
    _double_click(canvas, QPointF(100, 100))
    rect = canvas._image_rect()
    assert rect.width() == pytest.approx(200.0, abs=1.0)
    assert rect.height() == pytest.approx(100.0, abs=1.0)
    _double_click(canvas, QPointF(100, 100))
    again = canvas._image_rect()
    assert again.width() == pytest.approx(rect.width())
    assert again.height() == pytest.approx(rect.height())
    canvas.close()


def test_ctrl_plus_and_minus_zoom_like_wheel(qapp: QApplication) -> None:
    image = QImage(40, 20, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.red)
    window = show_screenshot_preview(image)
    window.show()
    qapp.processEvents()
    tab = window._current_tab()
    assert tab is not None
    assert tab.canvas.zoom == pytest.approx(1.0)
    QTest.keyClick(window, Qt.Key.Key_Plus, Qt.KeyboardModifier.ControlModifier)
    assert tab.canvas.zoom == pytest.approx(_ZOOM_STEP)
    QTest.keyClick(window, Qt.Key.Key_Minus, Qt.KeyboardModifier.ControlModifier)
    assert tab.canvas.zoom == pytest.approx(1.0)
    QTest.keyClick(
        window,
        Qt.Key.Key_Equal,
        Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier,
    )
    assert tab.canvas.zoom == pytest.approx(_ZOOM_STEP)
    QTest.keyClick(window, Qt.Key.Key_Minus, Qt.KeyboardModifier.ControlModifier)
    assert tab.canvas.zoom == pytest.approx(1.0)
    window.close()


def test_preview_canvas_zoom_changes_factor(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(40, 20, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.red)
    canvas = ScreenshotPreviewCanvas(image)
    canvas.resize(200, 100)
    assert canvas.zoom == 1.0
    canvas.zoom_by(2.0, anchor=QPointF(100, 50))
    assert canvas.zoom == pytest.approx(2.0)
    canvas.close()


def test_view_menu_restores_original_size_and_fits_small_image(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(40, 20, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.red)
    canvas = ScreenshotPreviewCanvas(image)
    canvas.resize(400, 200)
    assert [action.text() for action in canvas._view_menu().actions()] == ["Fit to view"]
    canvas.zoom_by(2.0, anchor=QPointF(200, 100))
    menu = canvas._view_menu()
    assert [action.text() for action in menu.actions()] == ["Original size", "Fit to view"]
    menu.actions()[0].trigger()
    assert canvas.zoom == pytest.approx(1.0)
    rect = canvas._image_rect()
    assert rect.width() == pytest.approx(40.0)
    assert rect.height() == pytest.approx(20.0)
    canvas._view_menu().actions()[0].trigger()
    fitted = canvas._image_rect()
    assert fitted.width() == pytest.approx(400.0, abs=1.0)
    assert fitted.height() == pytest.approx(200.0, abs=1.0)
    canvas.close()


def test_fit_to_view_scales_large_image_down(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(800, 400, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.blue)
    canvas = ScreenshotPreviewCanvas(image)
    canvas.resize(200, 200)
    canvas.zoom_by(3.0, anchor=QPointF(100, 100))
    canvas.fit_to_view()
    rect = canvas._image_rect()
    assert rect.width() == pytest.approx(200.0, abs=1.0)
    assert rect.height() == pytest.approx(100.0, abs=1.0)
    canvas.reset_to_original_size()
    restored = canvas._image_rect()
    assert restored.width() == pytest.approx(rect.width())
    assert restored.height() == pytest.approx(rect.height())
    canvas.close()


def test_preview_canvas_does_not_upscale_small_image(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(40, 20, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.red)
    canvas = ScreenshotPreviewCanvas(image)
    canvas.resize(400, 300)
    rect = canvas._image_rect()
    assert rect.width() == pytest.approx(40.0)
    assert rect.height() == pytest.approx(20.0)
    canvas.close()


def test_is_ctrl_s_accepts_key_s_and_yeru(qapp: QApplication) -> None:  # noqa: ARG001
    event_s = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_S, Qt.KeyboardModifier.ControlModifier)
    assert _is_ctrl_s(event_s)
    event_yeru = QKeyEvent(QKeyEvent.Type.KeyPress, 0x042B, Qt.KeyboardModifier.ControlModifier)
    assert _is_ctrl_s(event_yeru)
    event_plain = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_S, Qt.KeyboardModifier.NoModifier)
    assert not _is_ctrl_s(event_plain)


def test_preview_window_saves_dated_png_and_updates_title(
    qapp: QApplication,  # noqa: ARG001
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image = QImage(8, 8, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.blue)
    monkeypatch.setattr(
        "harrix_swiss_knife.screenshot.preview_dialog.h.dev.get_project_root",
        lambda: tmp_path,
    )
    window = show_screenshot_preview(image)
    assert window.windowTitle() == "Screenshot"
    window._save_to_images()
    saved = tmp_path / "temp" / "images"
    files = list(saved.glob("*.png"))
    assert len(files) == 1
    assert files[0].stem.endswith("_01")
    assert window.windowTitle() == f"Screenshot — {files[0].name}"
    window.close()


def test_preview_window_saves_dated_png_to_desktop(
    qapp: QApplication,  # noqa: ARG001
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    image = QImage(8, 8, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.green)
    monkeypatch.setattr(
        QStandardPaths,
        "writableLocation",
        lambda _location: str(desktop),
    )
    window = show_screenshot_preview(image)
    desktop_buttons = [button for button in window.findChildren(QPushButton) if button.text() == "Save to desktop"]
    assert len(desktop_buttons) == 1
    save_all = [button for button in window.findChildren(QPushButton) if button.text() == "Save all to desktop"]
    assert len(save_all) == 1
    assert not save_all[0].isVisible()
    window._save_to_desktop()
    screenshots = desktop / "Screenshots"
    files = sorted(screenshots.glob("*.png"))
    assert len(files) == 1
    assert files[0].stem.endswith("_01")
    assert window.windowTitle() == f"Screenshot — {files[0].name}"
    assert str(files[0]) in window._status.text()
    first_path = files[0]
    first_mtime = first_path.stat().st_mtime_ns
    window._save_to_desktop()
    files = sorted(screenshots.glob("*.png"))
    assert files == [first_path]
    assert first_path.stat().st_mtime_ns >= first_mtime
    window.close()


def test_save_as_remembers_last_directory(
    qapp: QApplication,  # noqa: ARG001
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "config.json").write_text("{}", encoding="utf-8")
    shots = tmp_path / "shots"
    shots.mkdir()
    (config_dir / "config-temp.json").write_text(
        json.dumps({"screenshot_last_save_dir": shots.as_posix()}),
        encoding="utf-8",
    )
    monkeypatch.setattr(preview_dialog_module.h.dev, "get_project_root", lambda: tmp_path)
    suggested: list[str] = []
    chosen = shots

    def dialog(*args: object) -> tuple[str, str]:
        start = str(args[2])
        suggested.append(start)
        return str(chosen / "kept.png"), ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", dialog)
    image = QImage(8, 8, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.blue)
    window = show_screenshot_preview(image)
    window._save_as()
    assert Path(suggested[0]) == shots / "screenshot.png"
    assert (shots / "kept.png").is_file()
    stored = json.loads((config_dir / "config-temp.json").read_text(encoding="utf-8"))
    assert stored["screenshot_last_save_dir"] == shots.resolve().as_posix()

    window._save_as()
    assert Path(suggested[1]).resolve() == (shots / "kept.png").resolve()

    other = tmp_path / "other"
    other.mkdir()
    chosen = other
    window.add_image(image)
    window._save_as()
    assert Path(suggested[2]).parent == shots
    stored = json.loads((config_dir / "config-temp.json").read_text(encoding="utf-8"))
    assert stored["screenshot_last_save_dir"] == other.resolve().as_posix()

    missing = tmp_path / "gone"
    (config_dir / "config-temp.json").write_text(
        json.dumps({"screenshot_last_save_dir": missing.as_posix()}),
        encoding="utf-8",
    )
    window.add_image(image)
    window._save_as()
    assert suggested[3] == "screenshot.png"
    window.close()


def test_save_buttons_offer_format_menus(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(8, 8, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.white)
    window = show_screenshot_preview(image)
    labels = ["PNG", "JPEG", "AVIF high quality", "AVIF optimized"]
    for text in ("Save as…", "Save to desktop", "Save all to desktop"):
        button = next(item for item in window.findChildren(QPushButton) if item.text() == text)
        menu = button.menu()
        assert menu is not None
        assert [action.text() for action in menu.actions()] == labels
        assert all(not action.icon().isNull() for action in menu.actions())
        assert menu.style().pixelMetric(QStyle.PixelMetric.PM_SmallIconSize, None, menu) == 24
    window.close()


def test_reduce_size_button_offers_menu_and_halves_image(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(40, 20, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.red)
    window = show_screenshot_preview(image)
    button = next(item for item in window.findChildren(QPushButton) if item.text() == "Reduce size…")
    menu = button.menu()
    assert menu is not None
    assert [action.text() for action in menu.actions()] == ["Half size", "Max 1024 px", "Custom size…"]
    assert all(not action.icon().isNull() for action in menu.actions())
    menu.actions()[0].trigger()
    tab = window._current_tab()
    assert tab is not None
    assert tab.document.base_image.width() == 20
    assert tab.document.base_image.height() == 10
    assert window._status.text() == "Reduced to 20 x 10"
    window.close()


def test_reduce_size_max_side_and_custom_dialog(qapp: QApplication) -> None:  # noqa: ARG001
    assert _half_pixel_size(40, 20) == (20, 10)
    assert _half_pixel_size(1, 1) is None
    assert _max_side_pixel_size(2000, 1000, 1024) == (1024, 512)
    assert _max_side_pixel_size(800, 600, 1024) is None
    dialog = _ReduceSizeDialog(200, 100)
    dialog._width.setValue(100)
    assert dialog.size_pixels() == (100, 50)
    assert dialog._ok.isEnabled()
    dialog.close()


def test_recognize_button_offers_recognition_menu(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(8, 8, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.white)
    window = show_screenshot_preview(image)
    button = next(item for item in window.findChildren(QPushButton) if item.text() == "Recognize…")
    menu = button.menu()
    assert menu is not None
    assert [action.text() for action in menu.actions()] == [
        "Recognize text (AI)",
        "Recognize table (AI)",
        "Recognize text (OCR)",
        "OCR + translate",
    ]
    assert all(not action.icon().isNull() for action in menu.actions())
    gone = {"Recognize text (AI)", "Recognize table (AI)", "Recognize text (OCR)", "OCR + translate"}
    assert not any(item.text() in gone for item in window.findChildren(QPushButton))
    window.close()


def test_preview_window_saves_jpeg_and_avif_formats(
    qapp: QApplication,  # noqa: ARG001
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    monkeypatch.setattr(QStandardPaths, "writableLocation", lambda _location: str(desktop))
    qualities: list[bool] = []

    def fake_avif(
        source: Path,
        output_folder: Path,
        _project_root: Path,
        *,
        quality: bool = False,
        max_size: int | None = None,
    ) -> str:
        del max_size
        qualities.append(quality)
        destination = Path(output_folder) / f"{Path(source).stem}.avif"
        destination.write_bytes(b"avif")
        return "ok"

    monkeypatch.setattr("harrix_swiss_knife.screenshot.preview_dialog.process_png_to_avif", fake_avif)
    image = QImage(8, 8, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.yellow)
    window = show_screenshot_preview(image)
    window._save_to_desktop("jpeg")
    screenshots = desktop / "Screenshots"
    jpeg_files = list(screenshots.glob("*.jpg"))
    assert len(jpeg_files) == 1
    assert jpeg_files[0].stat().st_size > 0
    window._save_to_desktop("avif_optimized")
    window._save_to_desktop("avif_hq")
    assert qualities == [False, True]
    assert len(list(screenshots.glob("*.avif"))) == 1
    assert len(list(screenshots.glob("*.png"))) == 0
    window.close()


def test_preview_window_save_all_to_desktop(
    qapp: QApplication,  # noqa: ARG001
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    monkeypatch.setattr(
        QStandardPaths,
        "writableLocation",
        lambda _location: str(desktop),
    )
    first = QImage(8, 8, QImage.Format.Format_RGB32)
    first.fill(Qt.GlobalColor.red)
    second = QImage(10, 10, QImage.Format.Format_RGB32)
    second.fill(Qt.GlobalColor.blue)
    window = show_screenshot_preview(first)
    show_screenshot_preview(second)
    save_all = next(button for button in window.findChildren(QPushButton) if button.text() == "Save all to desktop")
    assert save_all.isVisible()
    window._save_all_to_desktop()
    screenshots = desktop / "Screenshots"
    files = sorted(screenshots.glob("*.png"))
    assert len(files) == 2
    assert {path.stem[-3:] for path in files} == {"_01", "_02"}
    tabs = window.findChild(QTabWidget)
    assert tabs is not None
    assert tabs.count() == 2
    assert tabs.tabText(0) == files[0].name
    assert tabs.tabText(1) == files[1].name
    assert "Saved 2 images" in window._status.text()
    window.close()


def test_preview_window_uses_app_geometry_not_image_size(qapp: QApplication) -> None:
    image = QImage(40, 20, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.red)
    window = show_screenshot_preview(image)
    qapp.processEvents()
    qapp.processEvents()
    screen = window.screen()
    assert screen is not None
    available = screen.availableGeometry()
    target = compute_app_window_geometry(available)
    if target is None:
        assert bool(window.windowState() & Qt.WindowState.WindowMaximized)
    else:
        assert window.width() >= target.width() - 80
        assert window.height() >= target.height() - 80
    window.close()


def test_show_screenshot_preview_adds_tabs(qapp: QApplication) -> None:
    first = QImage(8, 8, QImage.Format.Format_RGB32)
    first.fill(Qt.GlobalColor.red)
    second = QImage(10, 10, QImage.Format.Format_RGB32)
    second.fill(Qt.GlobalColor.green)
    window = show_screenshot_preview(first)
    show_screenshot_preview(second)
    qapp.processEvents()
    tabs = window.findChild(QTabWidget)
    assert tabs is not None
    assert tabs.count() == 2
    bar = tabs.tabBar()
    assert bar.isVisible()
    assert bar.mapToGlobal(QPoint(0, 0)).y() < window._tools_host.mapToGlobal(QPoint(0, 0)).y()
    assert not bar.drawBase()
    assert not bar.autoFillBackground()
    assert "background: transparent" in bar.styleSheet()
    window.close()


def test_preview_window_title_follows_tab_saved_name(
    qapp: QApplication,  # noqa: ARG001
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "harrix_swiss_knife.screenshot.preview_dialog.h.dev.get_project_root",
        lambda: tmp_path,
    )
    first = QImage(8, 8, QImage.Format.Format_RGB32)
    first.fill(Qt.GlobalColor.red)
    second = QImage(8, 8, QImage.Format.Format_RGB32)
    second.fill(Qt.GlobalColor.blue)
    window = show_screenshot_preview(first)
    window._save_to_images()
    saved_title = window.windowTitle()
    assert saved_title.startswith("Screenshot — ")
    show_screenshot_preview(second)
    assert window.windowTitle() == "Screenshot"
    tabs = window.findChild(QTabWidget)
    assert tabs is not None
    tabs.setCurrentIndex(0)
    assert window.windowTitle() == saved_title
    window.close()


def test_preview_resave_reuses_same_dated_path(
    qapp: QApplication,  # noqa: ARG001
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Repeated Save / Save to desktop overwrites the same file instead of allocating a new name."""
    monkeypatch.setattr(
        "harrix_swiss_knife.screenshot.preview_dialog.h.dev.get_project_root",
        lambda: tmp_path,
    )
    desktop = tmp_path / "Desktop"
    monkeypatch.setattr(
        ScreenshotPreviewWindow,
        "_desktop_folder",
        lambda _self: desktop,
    )
    image = QImage(8, 8, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.red)
    window = show_screenshot_preview(image)
    window._save_to_images()
    images_dir = images_folder(tmp_path)
    first_images = sorted(images_dir.glob("*.png"))
    assert len(first_images) == 1
    first_path = first_images[0]
    first_mtime = first_path.stat().st_mtime_ns
    window._save_to_images()
    second_images = sorted(images_dir.glob("*.png"))
    assert second_images == first_images
    assert first_path.stat().st_mtime_ns >= first_mtime

    window._save_to_desktop()
    window._save_all_to_desktop()
    desktop_files = sorted(desktop.glob("*.png"))
    assert len(desktop_files) == 1
    window._save_to_desktop()
    assert sorted(desktop.glob("*.png")) == desktop_files
    window.close()


def test_preview_footer_wraps_buttons_and_keeps_full_width_status(qapp: QApplication) -> None:
    image = QImage(8, 8, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.cyan)
    window = show_screenshot_preview(image)
    window.resize(520, 400)
    qapp.processEvents()
    assert window._status.width() >= window.centralWidget().width() - 40
    for button in window._action_buttons:
        assert button.width() >= button.sizeHint().width() - 2
        assert "…" not in button.text() or button.text().endswith("…")
        assert button.width() >= button.fontMetrics().horizontalAdvance(button.text()[:8])
    # Narrow window: buttons still keep their natural width (wrap instead of clip).
    window.resize(_MIN_WINDOW_WIDTH, 400)
    qapp.processEvents()
    for button in window._action_buttons:
        assert button.width() >= button.sizeHint().width() - 2
    assert window._buttons.heightForWidth(window._buttons.geometry().width()) >= button.sizeHint().height()
    window.close()


def test_screenshot_preview_dialog_alias() -> None:
    assert ScreenshotPreviewWindow is preview_dialog_module.ScreenshotPreviewDialog


def _double_click(canvas: ScreenshotPreviewCanvas, pos: QPointF) -> None:
    canvas.mouseDoubleClickEvent(
        QMouseEvent(
            QMouseEvent.Type.MouseButtonDblClick,
            pos,
            canvas.mapToGlobal(pos.toPoint()),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
    )


def _left_click(canvas: ScreenshotPreviewCanvas, pos: QPointF) -> None:
    global_pos = canvas.mapToGlobal(pos.toPoint())
    canvas.mousePressEvent(
        QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            pos,
            global_pos,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
    )
    canvas.mouseReleaseEvent(
        QMouseEvent(
            QMouseEvent.Type.MouseButtonRelease,
            pos,
            global_pos,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
    )


def test_preview_canvas_selects_and_deletes_arrow(qapp: QApplication) -> None:
    image = QImage(100, 80, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.white)
    canvas = ScreenshotPreviewCanvas(image)
    canvas.resize(100, 80)
    document = AnnotationDocument(image)
    document.begin_draft(
        Annotation(
            tool=AnnotationTool.ARROW,
            points=[QPointF(10, 40), QPointF(80, 40)],
            style=AnnotationStyle(),
        )
    )
    assert document.commit_draft()
    canvas.set_document(document)
    canvas.set_tool(AnnotationTool.ARROW)
    qapp.processEvents()
    _left_click(canvas, QPointF(45, 40))
    assert canvas.selected_index == 0
    assert canvas.delete_selected()
    assert document.annotations == []
    assert canvas.selected_index is None
    canvas.close()


def test_preview_canvas_selects_arrow_after_tool_switch(qapp: QApplication) -> None:
    image = QImage(200, 160, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.white)
    canvas = ScreenshotPreviewCanvas(image)
    canvas.resize(100, 80)
    document = AnnotationDocument(image)
    document.begin_draft(
        Annotation(
            tool=AnnotationTool.ARROW,
            points=[QPointF(20, 80), QPointF(160, 80)],
            style=AnnotationStyle(),
        )
    )
    assert document.commit_draft()
    canvas.set_document(document)
    canvas.set_tool(AnnotationTool.ARROW)
    qapp.processEvents()
    _left_click(canvas, QPointF(50, 40))
    assert canvas.selected_index == 0
    canvas.set_tool(AnnotationTool.RECTANGLE)
    canvas.set_tool(AnnotationTool.ARROW)
    canvas.clear_selection()
    qapp.processEvents()
    _left_click(canvas, QPointF(50, 40))
    assert canvas.selected_index == 0
    assert len(document.annotations) == 1
    canvas.close()
