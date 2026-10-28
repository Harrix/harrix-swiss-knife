"""Install Fluent chrome on tracker apps and overlay dialogs.

Call `install_fluent_app_window` after `setupUi` (or equivalent layout build)
and before `install_win11_caption`. It opts the window into light/dark theme,
applies Mica so the wallpaper tint shows through, replaces legacy white-surface /
CTA stylesheets with Fluent tokens, restyles inputs / tables / tabs / menus, and
keeps everything in sync when the theme changes.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import (
    QAbstractButton,
    QAbstractItemView,
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QDateEdit,
    QGroupBox,
    QHeaderView,
    QLineEdit,
    QListView,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QStatusBar,
    QTabBar,
    QTableView,
    QTableWidget,
    QTabWidget,
    QTextEdit,
    QWidget,
)

from harrix_swiss_knife.fluent.style import (
    chrome_bottom_color,
    chrome_top_color,
    combo_box_qss,
    date_edit_qss,
    line_edit_qss,
    list_item_hover,
    list_item_selected,
    menu_qss,
    push_button_qss,
    scroll_bar_qss,
    semantic_button_qss,
    spin_box_qss,
    text_edit_qss,
    wallpaper_fill,
    wallpaper_qss,
)
from harrix_swiss_knife.fluent.theme import bind_theme, css, enable_fluent_theme, mix, palette_for, to_qpalette
from harrix_swiss_knife.fluent.tokens import (
    CONTROL_HEIGHT,
    CONTROL_HEIGHT_COMPACT,
    ICON_SIZE,
    RADIUS_CARD,
    RADIUS_CONTROL,
    SPACE_S,
)
from harrix_swiss_knife.qt_flat_scrollbar import apply_flat_scrollbars
from harrix_swiss_knife.win11_backdrop import SystemBackdrop, try_apply_system_backdrop

if TYPE_CHECKING:
    from harrix_swiss_knife.fluent.tokens import FluentPalette

_PROP_BOUND = "_hskFluentAppChromeBound"
_PROP_CANVAS = "_hskFluentCanvas"
_TABLE_TEXT = "#1a1a1a"
_KEEP_LARGE_FONT = frozenset(
    {
        "label_today_expense",
    },
)
# First solid fill in a button stylesheet maps to a Fluent role.
# Text-only uses of these hexes (calendar links) must not match.
_FILL_KINDS = {
    "3aaf9d": "mint",
    "038387": "mint",
    "026a6d": "mint",
    "79b1d1": "info",
    "4caf50": "success",
    "2e7d32": "success",
    "cc584c": "danger",
    "c42b1c": "danger",
    "2e86b7": "accent",
    "005fb8": "accent",
    "1a5f7a": "accent",
}
_KIND_MARKERS = (
    ("button_cta_mint", "mint"),
    ("button_cta_green", "success"),
    ("button_cta_cyan", "info"),
    ("hsk-fluent-mint", "mint"),
    ("hsk-fluent-info", "info"),
    ("hsk-fluent-success", "success"),
    ("hsk-fluent-danger", "danger"),
    ("hsk-fluent-cta", "accent"),
    ("button_cta_", "accent"),
)
_SECONDARY_MARKERS = (
    "#f5f5f5",
    "#ececec",
    "button_secondary",
)


def install_fluent_app_window(window: QWidget) -> None:
    """Opt `window` into Fluent theme, Mica, and standardized control chrome."""
    enable_fluent_theme(window)
    try_apply_system_backdrop(window, backdrop=SystemBackdrop.MICA)
    if not window.property(_PROP_BOUND):
        bind_theme(window, lambda: refresh_fluent_app_window(window))
        window.setProperty(_PROP_BOUND, True)  # noqa: FBT003
    refresh_fluent_app_window(window)


def refresh_fluent_app_window(window: QWidget) -> None:
    """Re-apply Fluent surfaces, controls, lists, tables, and buttons."""
    palette = palette_for(window)
    _apply_fluent_surfaces(window, palette)
    _normalize_control_metrics(window)
    _restyle_inputs(window, palette)
    _restyle_tables(window, palette)
    _restyle_tabs(window, palette)
    _apply_fluent_list_selection(window, palette)
    _restyle_buttons(window, palette)
    apply_flat_scrollbars(window)
    window.update()


def _apply_fluent_list_selection(root: QWidget, palette: FluentPalette) -> None:
    for view in root.findChildren(QListView):
        _style_item_view(view, palette)
    for view in root.findChildren(QListWidget):
        _style_item_view(view, palette)


def _apply_fluent_surfaces(window: QWidget, palette: FluentPalette) -> None:
    """Replace opaque white chrome with translucent Fluent layers so Mica shows."""
    window.setStyleSheet(_fluent_surface_qss(palette))
    # setStyleSheet polishes the widget and can replace the palette with the system one.
    window.setPalette(to_qpalette(palette, window.palette()))
    window.setAutoFillBackground(False)

    for child in window.findChildren(QWidget):
        name = child.objectName()
        child_sheet = child.styleSheet() or ""
        if not child_sheet:
            continue
        lowered = child_sheet.lower()
        clear_sheet = False
        if child.property(_PROP_CANVAS) or (
            name
            and f"#{name}" in child_sheet
            and ("#ffffff" in lowered or "background-color: white" in lowered)
            and not isinstance(child, (QAbstractButton, QAbstractItemView, QLineEdit, QAbstractSpinBox, QComboBox))
        ):
            _paint_canvas(child, palette)
            continue
        if ("background-color: #ffffff" in lowered and isinstance(child, (QGroupBox, QStatusBar))) or (
            name and "listview" in name.lower() and ("#e8f5e8" in lowered or "background-color: white" in lowered)
        ):
            clear_sheet = True
        # Drop one-off tint fills on inputs (e.g. amount spin soft-blue).
        if isinstance(child, (QLineEdit, QAbstractSpinBox, QComboBox, QDateEdit)) and (
            "#e8f4fc" in lowered or "#3aaf9d" in lowered or "background-color: #" in lowered
        ):
            clear_sheet = True
        if clear_sheet and not isinstance(child, QPushButton):
            child.setStyleSheet("")
    status = window.findChild(QStatusBar)
    if status is not None:
        color = chrome_bottom_color(palette)
        text = mix(palette.window_bg, palette.text_primary)
        status_palette = status.palette()
        for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive):
            status_palette.setColor(group, QPalette.ColorRole.Window, color)
            status_palette.setColor(group, QPalette.ColorRole.WindowText, text)
        status.setPalette(status_palette)
        status.setAutoFillBackground(True)


def _apply_list_palette(view: QAbstractItemView, palette: FluentPalette) -> None:
    qp = view.palette()
    text = mix(palette.window_bg, palette.text_primary)
    highlight = list_item_selected(palette)
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive, QPalette.ColorGroup.Disabled):
        qp.setColor(group, QPalette.ColorRole.Highlight, highlight)
        qp.setColor(group, QPalette.ColorRole.HighlightedText, text)
    view.setPalette(qp)


def _button_kind(sheet: str) -> str | None:
    """Map the first solid button fill to a Fluent role."""
    lowered = sheet.lower()
    for marker, kind in _KIND_MARKERS:
        if marker in lowered:
            return kind
    index = lowered.find("background-color:")
    key = "background-color:"
    if index < 0:
        index = lowered.find("background:")
        key = "background:"
    if index < 0:
        return None
    chunk = lowered[index + len(key) : index + len(key) + 28]
    if "transparent" in chunk or "#fff" in chunk or "white" in chunk:
        return None
    for hex_key, kind in _FILL_KINDS.items():
        if hex_key in chunk:
            return kind
    return None


def _card_color(palette: FluentPalette) -> QColor:
    """Return an opaque card fill. Translucent tokens paint as white on a light style."""
    if palette.dark:
        return QColor(palette.solid_tertiary_bg)
    return QColor(palette.solid_quarternary_bg)


def _clear_viewport(view: QAbstractItemView, palette: FluentPalette) -> None:
    """Paint the list viewport with the window gradient instead of the system base."""
    text = css(mix(palette.window_bg, palette.text_primary))
    view.setAutoFillBackground(False)
    viewport = view.viewport()
    viewport.setAutoFillBackground(False)
    viewport.setStyleSheet(f"background: {wallpaper_fill(palette)}; color: {text};")


def _fluent_surface_qss(palette: FluentPalette) -> str:
    text = css(mix(palette.window_bg, palette.text_primary))
    secondary = css(mix(palette.window_bg, palette.text_secondary))
    divider = css(mix(palette.window_bg, palette.divider))
    hover = css(list_item_hover(palette))
    status = chrome_bottom_color(palette).name()
    bar = chrome_top_color(palette).name()
    return f"""
/* hsk-fluent-surfaces */
{wallpaper_qss(palette)}
QLabel, QCheckBox, QRadioButton {{
 color: {text};
 background: transparent;
}}
QGroupBox {{
 background: transparent;
 border: none;
 border-bottom: 1px solid {divider};
 border-radius: 0px;
 margin-top: 10px;
 padding-top: 2px;
 padding-bottom: 4px;
 color: {text};
 font-weight: 600;
}}
QGroupBox::title {{
 subcontrol-origin: margin;
 subcontrol-position: top left;
 left: 0px;
 padding: 0px;
 background: transparent;
 color: {text};
}}
{menu_qss(palette)}
QStatusBar {{ background: {status}; color: {text}; border: none; }}
QStatusBar QLabel {{ color: {text}; background: transparent; }}
QSplitter::handle:horizontal {{
 width: 1px;
 background: {divider};
}}
QSplitter::handle:vertical {{
 height: 1px;
 background: {divider};
}}
QMenuBar {{
 background: {bar};
 color: {text};
}}
QMenuBar::item {{
 background: transparent;
 padding: 4px 10px;
 border-radius: {RADIUS_CONTROL}px;
}}
QMenuBar::item:selected {{ background: {hover}; }}
QMenuBar::item:disabled {{ color: {secondary}; }}
"""


def _lock_control_height(widget: QWidget) -> None:
    """Keep filter fields at the compact Fluent height so a row can fit."""
    widget.setMinimumHeight(CONTROL_HEIGHT_COMPACT)
    widget.setMaximumHeight(CONTROL_HEIGHT_COMPACT)


def _normalize_control_metrics(root: QWidget) -> None:
    """Reset ad-hoc fonts and oversized button heights to Fluent control metrics."""
    app = QApplication.instance()
    base_font = app.font() if isinstance(app, QApplication) else QFont()
    for widget in root.findChildren(QWidget):
        name = widget.objectName()
        if name in _KEEP_LARGE_FONT:
            continue
        if isinstance(widget, (QLineEdit, QAbstractSpinBox, QComboBox, QDateEdit, QPushButton)):
            font = QFont(base_font)
            font.setBold(False)
            widget.setFont(font)
        if isinstance(widget, QPushButton) and not _skip_fluent_button(widget):
            if widget.minimumHeight() > CONTROL_HEIGHT:
                widget.setMinimumHeight(CONTROL_HEIGHT)
            if 0 < widget.maximumHeight() < CONTROL_HEIGHT:
                widget.setMaximumHeight(CONTROL_HEIGHT)
        if isinstance(widget, QAbstractButton) and widget.iconSize().width() > ICON_SIZE:
            widget.setIconSize(QSize(ICON_SIZE, ICON_SIZE))


def _paint_canvas(widget: QWidget, palette: FluentPalette) -> None:
    """Paint the window gradient on a structural panel that used to be flat white."""
    name = widget.objectName()
    if not name:
        name = f"hskCanvas{id(widget)}"
        widget.setObjectName(name)
    text = css(mix(palette.window_bg, palette.text_primary))
    widget.setStyleSheet(f"QWidget#{name} {{ background: {wallpaper_fill(palette)}; color: {text}; border: none; }}")
    widget.setAutoFillBackground(False)
    widget.setProperty(_PROP_CANVAS, True)  # noqa: FBT003


def _paint_viewport(view: QAbstractItemView, color: QColor, text: QColor) -> None:
    """Fill the scroll viewport so empty rows are not the system white."""
    viewport = view.viewport()
    tuned = viewport.palette()
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive):
        tuned.setColor(group, QPalette.ColorRole.Base, color)
        tuned.setColor(group, QPalette.ColorRole.Text, text)
    viewport.setPalette(tuned)
    viewport.setAutoFillBackground(True)
    view.setPalette(tuned)


def _restyle_buttons(root: QWidget, palette: FluentPalette) -> None:
    secondary = push_button_qss(palette)
    for button in root.findChildren(QPushButton):
        if _skip_fluent_button(button):
            continue
        sheet = button.styleSheet() or ""
        kind = _button_kind(sheet) or button.property("_hskFluentButton")
        if isinstance(kind, str) and kind in {"accent", "mint", "info", "success", "danger"}:
            button.setStyleSheet(f"/* hsk-fluent-{kind} */\n{semantic_button_qss(palette, kind)}")
            button.setMinimumHeight(CONTROL_HEIGHT_COMPACT)
            button.setMaximumHeight(CONTROL_HEIGHT)
            button.setProperty("_hskFluentButton", kind)
        elif any(marker.lower() in sheet.lower() for marker in _SECONDARY_MARKERS):
            button.setStyleSheet(secondary)
            button.setMinimumHeight(CONTROL_HEIGHT_COMPACT)
            button.setMaximumHeight(CONTROL_HEIGHT)
            button.setProperty("_hskFluentButton", "secondary")
        elif kind == "secondary":
            button.setStyleSheet(secondary)


def _restyle_inputs(root: QWidget, palette: FluentPalette) -> None:
    line = line_edit_qss(palette, height=CONTROL_HEIGHT_COMPACT)
    spin = spin_box_qss(palette, height=CONTROL_HEIGHT_COMPACT)
    combo = combo_box_qss(palette, height=CONTROL_HEIGHT_COMPACT)
    for edit in root.findChildren(QLineEdit):
        if edit.parentWidget() is not None and isinstance(edit.parentWidget(), QAbstractSpinBox):
            continue
        if edit.parentWidget() is not None and isinstance(edit.parentWidget(), QComboBox):
            continue
        edit.setStyleSheet(line)
        _lock_control_height(edit)
    for box in root.findChildren(QAbstractSpinBox):
        if isinstance(box, QDateEdit):
            continue
        box.setStyleSheet(spin)
        _lock_control_height(box)
    for box in root.findChildren(QComboBox):
        box.setStyleSheet(combo)
        _lock_control_height(box)
    for box in root.findChildren(QDateEdit):
        box.setStyleSheet(date_edit_qss(palette, height=CONTROL_HEIGHT_COMPACT))
        _lock_control_height(box)
    for edit in root.findChildren(QPlainTextEdit):
        edit.setStyleSheet(text_edit_qss(palette, "QPlainTextEdit"))
    for edit in root.findChildren(QTextEdit):
        edit.setStyleSheet(text_edit_qss(palette, "QTextEdit"))


def _restyle_tables(root: QWidget, palette: FluentPalette) -> None:
    for table in root.findChildren(QTableView):
        _style_table(table, palette)
    for table in root.findChildren(QTableWidget):
        _style_table(table, palette)


def _restyle_tabs(root: QWidget, palette: FluentPalette) -> None:
    hover = css(list_item_hover(palette))
    selected = css(list_item_selected(palette))
    text = css(mix(palette.window_bg, palette.text_primary))
    accent = css(palette.accent)
    for tabs in root.findChildren(QTabWidget):
        name = tabs.objectName() or "tabWidget"
        tabs.setDocumentMode(True)
        tabs.setStyleSheet(
            f"""
QTabWidget#{name}::pane {{
 background: transparent;
 border: none;
 top: -1px;
}}
QTabWidget#{name} > QTabBar::tab {{
 background: transparent;
 color: {text};
 border: none;
 border-radius: {RADIUS_CONTROL}px;
 padding: 6px 12px;
 margin-right: 2px;
 min-height: {CONTROL_HEIGHT - 8}px;
}}
QTabWidget#{name} > QTabBar::tab:hover {{ background: {hover}; }}
QTabWidget#{name} > QTabBar::tab:selected {{
 background: {selected};
 color: {text};
}}
QTabWidget#{name} > QTabBar::tab:selected {{
 border-bottom: 2px solid {accent};
 border-bottom-left-radius: 0;
 border-bottom-right-radius: 0;
}}
""",
        )
    for bar in root.findChildren(QTabBar):
        if isinstance(bar.parentWidget(), QTabWidget):
            continue
        bar.setStyleSheet(
            f"""
QTabBar::tab {{
 background: transparent;
 color: {text};
 border: none;
 border-radius: {RADIUS_CONTROL}px;
 padding: 6px 12px;
 margin-right: 2px;
}}
QTabBar::tab:hover {{ background: {hover}; }}
QTabBar::tab:selected {{
 background: {selected};
 border-bottom: 2px solid {accent};
}}
""",
        )


def _skip_fluent_button(button: QWidget) -> bool:
    """Leave calendar chips and in-cell controls on their own stylesheet."""
    if button.property("_hskSkipFluentButton"):
        return True
    parent = button.parentWidget()
    while parent is not None:
        if parent.metaObject().className() == "SoftCalendarWidget" or parent.inherits("QAbstractItemView"):
            return True
        parent = parent.parentWidget()
    return False


def _style_item_view(view: QAbstractItemView, palette: FluentPalette) -> None:
    selector = view.metaObject().className()
    name = view.objectName()
    target = f"{selector}#{name}" if name else selector
    hover = css(list_item_hover(palette))
    selected = css(list_item_selected(palette))
    text = css(mix(palette.window_bg, palette.text_primary))
    view.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
    view.setSpacing(0)
    view.setStyleSheet(
        f"""
{target} {{
 background: transparent;
 color: {text};
 border: none;
 outline: none;
}}
{target}::item {{
 border-radius: {RADIUS_CONTROL}px;
 padding: 1px 8px;
 margin: 0px;
 color: {text};
}}
{target}::item:hover {{ background: {hover}; }}
{target}::item:selected {{ background: {selected}; color: {text}; }}
{target}::item:selected:hover {{ background: {selected}; }}
{scroll_bar_qss(palette)}
""",
    )
    _apply_list_palette(view, palette)
    _clear_viewport(view, palette)


def _style_table(table: QTableView, palette: FluentPalette) -> None:
    selector_base = table.metaObject().className()
    name = table.objectName()
    selector = f"{selector_base}#{name}" if name else selector_base
    secondary = css(mix(palette.window_bg, palette.text_secondary))
    divider = css(mix(palette.window_bg, palette.divider))
    card = _card_color(palette)
    stroke = css(palette.card_stroke)
    table.setShowGrid(False)
    table.setAlternatingRowColors(False)
    header = table.horizontalHeader()
    header.setHighlightSections(False)
    header.setDefaultAlignment(header.defaultAlignment())
    if isinstance(header, QHeaderView):
        header.setMinimumHeight(CONTROL_HEIGHT)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(CONTROL_HEIGHT + SPACE_S)
    table.setStyleSheet(
        f"""
{selector} {{
 background: {card.name()};
 color: {_TABLE_TEXT};
 border: 1px solid {stroke};
 border-radius: {RADIUS_CARD}px;
 outline: none;
 gridline-color: transparent;
}}
{selector} QHeaderView::section {{
 background: transparent;
 color: {secondary};
 border: none;
 border-bottom: 1px solid {divider};
 padding: 0px 8px;
 min-height: {CONTROL_HEIGHT}px;
 font-weight: 600;
}}
{scroll_bar_qss(palette)}
""",
    )
    # No ::item background: that stylesheet replaces the model's row tint.
    _paint_viewport(table, card, QColor(_TABLE_TEXT))
