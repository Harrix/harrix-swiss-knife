"""Tests for custom action SVG icons used in the GUI."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import qt_action_icon as action_icon_mod
from harrix_swiss_knife.actions.apps.food import OnFood
from harrix_swiss_knife.actions.apps.habits import OnHabits
from harrix_swiss_knife.actions.apps.icons import OnIcons
from harrix_swiss_knife.actions.development.exit_ import OnExit
from harrix_swiss_knife.actions.development.npm_manage_packages import OnNpmManagePackages
from harrix_swiss_knife.actions.development.settings_editor import OnSettingsEditor
from harrix_swiss_knife.actions.development.setup_data_for_hsk import OnSetupDataForHsk
from harrix_swiss_knife.actions.development.transfer_private_data import OnTransferPrivateData
from harrix_swiss_knife.actions.development.view_recent_action_logs import OnViewRecentActionLogs
from harrix_swiss_knife.actions.files.check_musicbee_playlists import OnCheckMusicBeePlaylists
from harrix_swiss_knife.actions.files.close_all_adobe import OnCloseAllAdobe
from harrix_swiss_knife.actions.files.extract_zip_archives import OnExtractZipArchives
from harrix_swiss_knife.actions.files.lock_disks import OnLockDisks
from harrix_swiss_knife.actions.files.remove_empty_folders import OnRemoveEmptyFolders
from harrix_swiss_knife.actions.images.open_images import OnOpenImages
from harrix_swiss_knife.actions.images.open_optimized_images import OnOpenOptimizedImages
from harrix_swiss_knife.actions.images.optimize_clipboard import OnOptimizeClipboard
from harrix_swiss_knife.actions.images.optimize_clipboard_dialog import OnOptimizeClipboardDialog
from harrix_swiss_knife.actions.images.screenshot_region import OnScreenshotRegion
from harrix_swiss_knife.actions.images.screenshot_region_clipboard import OnScreenshotRegionClipboard
from harrix_swiss_knife.actions.images.screenshot_region_translate import OnScreenshotRegionTranslate
from harrix_swiss_knife.actions.site.add_site_content_submodule import OnAddSiteContentSubmodule
from harrix_swiss_knife.actions.vscode.install_harrix_notes_explorer_extension import (
    OnInstallHarrixNotesExplorerExtension,
)
from harrix_swiss_knife.menu_list_markdown import generate_markdown_from_menu_structure
from harrix_swiss_knife.menu_structure import get_menu_structure
from harrix_swiss_knife.qt_action_icon import (
    action_svg_path,
    create_action_icon,
    create_menu_icon,
    resolve_ui_icon_spec,
)

_ACTION_SVG_CASES: tuple[tuple[type, str, str], ...] = (
    (OnAddSiteContentSubmodule, "📦", "object__box.svg"),
    (OnCheckMusicBeePlaylists, "🎵", "object__note.svg"),
    (OnCloseAllAdobe, "🛑", "symbol__stop.svg"),
    (OnExit, "×", "symbol__not.svg"),  # noqa: RUF001
    (OnExtractZipArchives, "📦", "object__box.svg"),
    (OnFood, "🍔", "food__hamburger.svg"),
    (OnHabits, "✅", "symbol__ok.svg"),
    (OnIcons, "🎨", "object__palette.svg"),
    (OnInstallHarrixNotesExplorerExtension, "📦", "object__box.svg"),
    (OnLockDisks, "🔒", "object__lock.svg"),
    (OnNpmManagePackages, "📦", "object__box.svg"),
    (OnOpenImages, "📂", "it__folder.svg"),
    (OnOpenOptimizedImages, "📂", "it__folder.svg"),
    (OnOptimizeClipboard, "🚀", "space__rocket-with-window.svg"),
    (OnOptimizeClipboardDialog, "🚀", "space__rocket-with-window.svg"),
    (OnRemoveEmptyFolders, "🗑️", "it__trash.svg"),
    (OnScreenshotRegion, "📷", "it__camera.svg"),
    (OnScreenshotRegionClipboard, "📷", "it__camera.svg"),
    (OnScreenshotRegionTranslate, "📷", "it__camera.svg"),
    (OnSettingsEditor, "⚙️", "object__gear.svg"),
    (OnSetupDataForHsk, "📁", "it__folder.svg"),
    (OnTransferPrivateData, "📦", "object__box.svg"),
    (OnViewRecentActionLogs, "📋", "object__tablet.svg"),
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


@pytest.mark.parametrize(("action_cls", "emoji", "svg_name"), _ACTION_SVG_CASES)
def test_action_keeps_emoji_and_resolves_svg(action_cls: type, emoji: str, svg_name: str) -> None:
    assert action_cls.icon == emoji
    assert action_cls.icon_svg == svg_name
    assert resolve_ui_icon_spec(action_cls) == svg_name
    assert action_svg_path(svg_name) is not None


def test_on_icons_markdown_uses_emoji_not_svg() -> None:
    lines = generate_markdown_from_menu_structure(get_menu_structure())
    assert "- 🎨 Vector Icons" in lines
    joined = "\n".join(lines)
    for _action_cls, _emoji, svg_name in _ACTION_SVG_CASES:
        assert svg_name not in joined


def test_resolve_ui_icon_spec_falls_back_to_emoji_when_svg_missing() -> None:
    class _MissingSvg:
        icon = "🎨"
        icon_svg = "not-a-real-action-icon.svg"

    assert resolve_ui_icon_spec(_MissingSvg) == "🎨"


def test_action_svg_path_accepts_palette_and_rejects_unsafe_names() -> None:
    path = action_svg_path("object__palette.svg")
    assert path is not None
    assert path.name == "object__palette.svg"
    assert action_svg_path("object__palette") == path
    assert action_svg_path("../object__palette.svg") is None
    assert action_svg_path("not-a-real-action-icon.svg") is None


def test_create_action_icon_for_on_icons_is_not_empty(qapp: QApplication) -> None:
    assert qapp is not None
    action_icon_mod._CACHE.clear()
    icon = create_action_icon(OnIcons, 24)
    assert not icon.isNull()
    raster = create_menu_icon("object__palette.svg", 24, device_pixel_ratio=1.0)
    pixmap = raster.pixmap(QSize(24, 24), 1.0)
    image = pixmap.toImage()
    found = False
    for y in range(image.height()):
        for x in range(image.width()):
            if QColor(image.pixelColor(x, y)).alpha() >= 32:
                found = True
                break
        if found:
            break
    action_icon_mod._CACHE.clear()
    assert found


def test_create_menu_icon_uses_device_pixel_ratio(qapp: QApplication) -> None:
    assert qapp is not None
    action_icon_mod._CACHE.clear()
    icon = create_menu_icon("object__palette.svg", 20, device_pixel_ratio=2.0)
    pixmap = icon.pixmap(QSize(20, 20), 2.0)
    action_icon_mod._CACHE.clear()
    assert pixmap.devicePixelRatio() == 2.0
    assert pixmap.width() == 40
    assert pixmap.height() == 40
