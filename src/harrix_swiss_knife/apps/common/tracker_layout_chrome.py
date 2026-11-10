"""Shared soft-panel / quiet chrome for tracker multi-column layouts.

Mirrors the Finance Transactions declutter: columns separate by surface, not by
idle splitter hairlines or GroupBox underlines.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QWidget

from harrix_swiss_knife.apps.common.ui_chrome import MUTED_TEXT
from harrix_swiss_knife.fluent.theme import bind_theme, css, mix, palette_for
from harrix_swiss_knife.fluent.tokens import SPACE_XS

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

# Left field captions (Description:, Date:, …) — same column width as Currency exchange.
FIELD_LABEL_WIDTH = 90


def apply_tracker_column_surfaces(
    host: QWidget,
    *,
    soft_panes: Sequence[tuple[QWidget, str]],
    content_panes: Sequence[tuple[QWidget, str]] = (),
    quiet_boxes: Iterable[Any] = (),
) -> None:
    """Paint soft/content panes and quiet GroupBoxes once (caller may theme-bind)."""
    _apply_column_surfaces(host, soft_panes=soft_panes, content_panes=content_panes)
    for box in quiet_boxes:
        quiet_group_box(box)


def install_tracker_column_chrome(
    host: QWidget,
    *,
    soft_panes: Sequence[tuple[QWidget, str]],
    content_panes: Sequence[tuple[QWidget, str]] = (),
    quiet_boxes: Iterable[Any] = (),
    theme_flag: str = "_tracker_column_chrome_theme_bound",
) -> None:
    """Apply soft left/middle panels and quiet GroupBoxes; rebind on theme change.

    Args:

    - `host` (`QWidget`): Window that owns the panes (theme bind target).
    - `soft_panes` (`Sequence[tuple[QWidget, str]]`): Form / list columns with
      soft card fill. Each tuple is `(widget, objectName)`.
    - `content_panes` (`Sequence[tuple[QWidget, str]]`): Table / chart columns
      kept transparent. Defaults to empty.
    - `quiet_boxes` (`Iterable[Any]`): `QGroupBox` widgets that should lose the
      Fluent title underline. Defaults to empty.
    - `theme_flag` (`str`): Attribute name used to bind theme once per host.

    """

    def refresh() -> None:
        apply_tracker_column_surfaces(
            host,
            soft_panes=soft_panes,
            content_panes=content_panes,
            quiet_boxes=quiet_boxes,
        )

    refresh()
    if not getattr(host, theme_flag, False):
        bind_theme(host, refresh)
        setattr(host, theme_flag, True)


def polish_left_field_labels(host: Any, pairs: Sequence[tuple[str, str]]) -> None:
    """Put muted fixed-width captions to the left of form fields.

    Args:

    - `host` (`Any`): Window owning the labels.
    - `pairs` (`Sequence[tuple[str, str]]`): `(attribute_name, caption)` rows.

    """
    for name, text in pairs:
        label = getattr(host, name, None)
        if not isinstance(label, QLabel):
            continue
        label.setText(text)
        label.setStyleSheet(f"color: {MUTED_TEXT}; font-weight: 600;")
        label.setMinimumWidth(FIELD_LABEL_WIDTH)
        label.setFixedWidth(FIELD_LABEL_WIDTH)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)


def quiet_group_box(group: Any, *, untitled: bool = False) -> None:
    """Remove the Fluent GroupBox bottom hairline from a titled section."""
    name = group.objectName() or "groupBox"
    margin_top = "0px" if untitled else "1.2em"
    padding_top = f"{SPACE_XS}px" if untitled else "2px"
    title_rule = (
        f"QGroupBox#{name}::title {{ height: 0px; width: 0px; padding: 0px; margin: 0px; }}" if untitled else ""
    )
    group.setStyleSheet(
        f"""
        QGroupBox#{name} {{
            background: transparent;
            border: none;
            margin-top: {margin_top};
            padding-top: {padding_top};
            padding-bottom: 4px;
            border-radius: 0px;
        }}
        {title_rule}
        """,
    )


def soft_panel_css(host: QWidget) -> str:
    """Return the soft entry-column fill used by Finance Transactions."""
    palette = palette_for(host)
    return css(mix(palette.window_bg, palette.card_bg))


def _apply_column_surfaces(
    host: QWidget,
    *,
    soft_panes: Sequence[tuple[QWidget, str]],
    content_panes: Sequence[tuple[QWidget, str]],
) -> None:
    panel = soft_panel_css(host)
    for widget, name in soft_panes:
        widget.setObjectName(name)
        if isinstance(widget, QFrame):
            widget.setFrameShape(QFrame.Shape.NoFrame)
        widget.setAutoFillBackground(False)
        kind = "QFrame" if isinstance(widget, QFrame) else "QWidget"
        widget.setStyleSheet(f"{kind}#{name} {{ background: {panel}; border: none; }}")
    for widget, name in content_panes:
        widget.setObjectName(name)
        widget.setAutoFillBackground(False)
        kind = "QFrame" if isinstance(widget, QFrame) else "QWidget"
        widget.setStyleSheet(f"{kind}#{name} {{ background: transparent; border: none; }}")
