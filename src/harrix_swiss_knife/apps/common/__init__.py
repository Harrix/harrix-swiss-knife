"""Common utilities and shared modules for applications."""

from . import avif_manager, message_box, qt_mixins
from .app_entry import run_app_main
from .avif_manager import AvifManager
from .chart_operations import ChartOperationsBase
from .common import _safe_identifier
from .db_guard import requires_database
from .qt_main_window import AppWindowMixin
from .qt_mixins import DateMixin, TableOperations, ValidationMixin
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
    "apply_white_editor_background",
    "avif_manager",
    "enumerate_stripped_non_empty_lines",
    "iter_stripped_non_empty_lines",
    "message_box",
    "qt_mixins",
    "requires_database",
    "run_app_main",
]
