"""Common utilities and shared modules for applications."""

from __future__ import annotations

import importlib
from typing import Any

from .common import _safe_identifier
from .ui_helpers import (
    apply_white_editor_background,
    enumerate_stripped_non_empty_lines,
    iter_stripped_non_empty_lines,
)

__all__ = [
    "AppWindowMixin",
    "AvifManager",
    "ChartOperationsBase",
    "DateMixin",
    "TableOperations",
    "ValidationMixin",
    "_safe_identifier",
    "achievement_dialog",
    "apply_white_editor_background",
    "avif_manager",
    "enumerate_stripped_non_empty_lines",
    "iter_stripped_non_empty_lines",
    "message_box",
    "qt_mixins",
    "requires_database",
    "run_app_main",
]

_LAZY_MODULES = frozenset({"achievement_dialog", "avif_manager", "message_box", "qt_mixins"})
_LAZY_ATTRS: dict[str, tuple[str, str]] = {
    "AppWindowMixin": (".qt_main_window", "AppWindowMixin"),
    "AvifManager": (".avif_manager", "AvifManager"),
    "ChartOperationsBase": (".chart_operations", "ChartOperationsBase"),
    "DateMixin": (".qt_mixins", "DateMixin"),
    "TableOperations": (".qt_mixins", "TableOperations"),
    "ValidationMixin": (".qt_mixins", "ValidationMixin"),
    "requires_database": (".db_guard", "requires_database"),
    "run_app_main": (".app_entry", "run_app_main"),
}


def __getattr__(name: str) -> Any:
    if name in _LAZY_MODULES:
        return importlib.import_module(f"{__name__}.{name}")
    if name in _LAZY_ATTRS:
        module_name, attr_name = _LAZY_ATTRS[name]
        module = importlib.import_module(module_name, __name__)
        return getattr(module, attr_name)
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
