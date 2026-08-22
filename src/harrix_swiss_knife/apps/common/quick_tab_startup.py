"""Quick-tab startup checkbox shared by Finance, Food, and Fitness."""

from __future__ import annotations

import logging
from typing import Any

import harrix_pylib as h
from PySide6.QtWidgets import QCheckBox, QTabWidget, QVBoxLayout, QWidget

from harrix_swiss_knife.apps.common.apps_config import (
    QuickTabAppName,
    get_open_quick_tab_on_startup,
    set_open_quick_tab_on_startup,
    startup_tab_index,
)
from harrix_swiss_knife.paths import get_config_path_str

logger = logging.getLogger(__name__)

_CHECKBOX_STYLE = """
QCheckBox {
    color: #6B7280;
    padding: 4px 12px 8px 12px;
    spacing: 8px;
}
"""


def apply_open_quick_tab_preference(
    tab_widget: QTabWidget,
    *,
    app: QuickTabAppName,
    config: dict[str, Any],
) -> None:
    """Select Quick or the second tab from the stored preference."""
    index = startup_tab_index(open_quick=get_open_quick_tab_on_startup(config, app))
    if 0 <= index < tab_widget.count():
        tab_widget.setCurrentIndex(index)


def install_open_quick_tab_checkbox(
    window: QWidget,
    *,
    app: QuickTabAppName,
    tab_layout: QVBoxLayout,
    tab_widget: QTabWidget,
) -> QCheckBox:
    """Add the startup checkbox and select Quick or the second tab.

    Args:

    - `window` (`QWidget`): App main window; may expose `_app_config`.
    - `app` (`QuickTabAppName`): `finance`, `food`, or `fitness`.
    - `tab_layout` (`QVBoxLayout`): Layout of the first tab.
    - `tab_widget` (`QTabWidget`): App tab widget.

    Returns:

    - `QCheckBox`: The installed preference checkbox.

    """
    config = _window_config(window)
    checkbox = QCheckBox("Open Quick tab on startup")
    checkbox.setObjectName(f"{app}OpenQuickTabOnStartup")
    checkbox.setChecked(get_open_quick_tab_on_startup(config, app))
    checkbox.setStyleSheet(_CHECKBOX_STYLE)
    checkbox.toggled.connect(lambda checked: _on_open_quick_tab_toggled(window, app, checked=checked))
    tab_layout.addWidget(checkbox)
    apply_open_quick_tab_preference(tab_widget, config=config, app=app)
    return checkbox


def _on_open_quick_tab_toggled(window: QWidget, app: QuickTabAppName, *, checked: bool) -> None:
    config = getattr(window, "_app_config", None)
    live_config = config if isinstance(config, dict) else None
    try:
        set_open_quick_tab_on_startup(app, enabled=checked, config=live_config)
    except (OSError, TypeError, ValueError):
        logger.exception("Failed to save Quick-tab startup preference for %s", app)


def _window_config(window: QWidget) -> dict[str, Any]:
    config = getattr(window, "_app_config", None)
    if isinstance(config, dict):
        return config
    loaded = h.dev.config_load(get_config_path_str())
    return loaded if isinstance(loaded, dict) else {}
