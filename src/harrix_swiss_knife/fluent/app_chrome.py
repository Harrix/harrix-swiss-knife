"""Install Fluent chrome on tracker apps and overlay dialogs.

Call `install_fluent_app_window` after `setupUi` (or equivalent layout build)
and before `install_win11_caption`. It opts the window into light/dark theme,
applies Mica so the wallpaper tint shows through, replaces legacy white-surface /
CTA stylesheets with Fluent tokens, restyles inputs / tables / tabs / menus, and
keeps everything in sync when the theme changes.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QFont, QPalette
from PySide6.QtWidgets import (
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
    accent_button_qss,
    combo_box_qss,
    line_edit_qss,
    list_item_hover,
    list_item_selected,
    menu_qss,
    push_button_qss,
    scroll_bar_qss,
    spin_box_qss,
    text_edit_qss,
)
from harrix_swiss_knife.fluent.theme import bind_theme, css, enable_fluent_theme, mix, palette_for
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT, RADIUS_CARD, RADIUS_CONTROL, SPACE_S
from harrix_swiss_knife.qt_flat_scrollbar import apply_flat_scrollbars
from harrix_swiss_knife.win11_backdrop import SystemBackdrop, try_apply_system_backdrop

if TYPE_CHECKING:
    from harrix_swiss_knife.fluent.tokens import FluentPalette

_PROP_BOUND = "_hskFluentAppChromeBound"
_KEEP_LARGE_FONT = frozenset(
    {
        "label_today_expense",
    },
)
# Legacy solid fills that should become Fluent AccentButton.
_ACCENT_MARKERS = (
    "#79b1d1",
    "#3aaf9d",
    "#4caf50",
    "#2e86b7",
    "#038387",
    "#026a6d",
    "button_cta_",
    "hsk-fluent-cta",
    "BUTTON_PRIMARY",
    "background-color: #005fb8",
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
    window.setAutoFillBackground(False)

    for child in window.findChildren(QWidget):
        name = child.objectName()
        child_sheet = child.styleSheet() or ""
        if not child_sheet:
            continue
        lowered = child_sheet.lower()
        clear_sheet = False
        if name and f"#{name}" in child_sheet and ("#ffffff" in lowered or "background-color: white" in lowered):
            child.setStyleSheet(f"QWidget#{name} {{ background-color: transparent; border: none; }}")
            child.setAutoFillBackground(False)
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
        if clear_sheet:
            child.setStyleSheet("")


def _apply_list_palette(view: QAbstractItemView, palette: FluentPalette) -> None:
    qp = view.palette()
    text = mix(palette.window_bg, palette.text_primary)
    highlight = list_item_selected(palette)
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive, QPalette.ColorGroup.Disabled):
        qp.setColor(group, QPalette.ColorRole.Highlight, highlight)
        qp.setColor(group, QPalette.ColorRole.HighlightedText, text)
    view.setPalette(qp)


def _fluent_surface_qss(palette: FluentPalette) -> str:
    text = css(mix(palette.window_bg, palette.text_primary))
    secondary = css(mix(palette.window_bg, palette.text_secondary))
    divider = css(mix(palette.window_bg, palette.divider))
    hover = css(list_item_hover(palette))
    card = css(palette.card_bg)
    return f"""
/* hsk-fluent-surfaces */
QMainWindow, QDialog {{
 background-color: transparent;
}}
QGroupBox {{
 background-color: {card};
 border: 1px solid {css(palette.card_stroke)};
 border-radius: {RADIUS_CONTROL}px;
 margin-top: 0.9em;
 padding-top: 6px;
 padding-bottom: 6px;
 color: {text};
}}
QGroupBox::title {{
 subcontrol-origin: margin;
 subcontrol-position: top left;
 left: 8px;
 padding: 0 4px;
 background-color: transparent;
 color: {text};
}}
{menu_qss(palette)}
QStatusBar {{ background: transparent; color: {text}; }}
QStatusBar QLabel {{ color: {text}; }}
QSplitter::handle:horizontal {{
 width: 1px;
 background: {divider};
}}
QSplitter::handle:vertical {{
 height: 1px;
 background: {divider};
}}
QMenuBar {{
 background: transparent;
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
        if isinstance(widget, QPushButton):
            if widget.minimumHeight() > CONTROL_HEIGHT + 2:
                widget.setMinimumHeight(CONTROL_HEIGHT)
            if widget.maximumHeight() < CONTROL_HEIGHT and widget.maximumHeight() > 0:
                widget.setMaximumHeight(16777215)


def _restyle_buttons(root: QWidget, palette: FluentPalette) -> None:
    accent = accent_button_qss(palette)
    secondary = push_button_qss(palette)
    for button in root.findChildren(QPushButton):
        sheet = button.styleSheet() or ""
        lowered = sheet.lower()
        if any(marker.lower() in lowered for marker in _ACCENT_MARKERS) or any(
            marker.lower() in sheet for marker in _ACCENT_MARKERS
        ):
            button.setStyleSheet(f"/* hsk-fluent-cta */\n{accent}")
            button.setMinimumHeight(CONTROL_HEIGHT)
            button.setProperty("_hskFluentButton", "accent")
        elif any(marker.lower() in lowered for marker in _SECONDARY_MARKERS):
            button.setStyleSheet(secondary)
            button.setMinimumHeight(CONTROL_HEIGHT)
            button.setProperty("_hskFluentButton", "secondary")
        elif button.property("_hskFluentButton") == "accent":
            button.setStyleSheet(f"/* hsk-fluent-cta */\n{accent}")
        elif button.property("_hskFluentButton") == "secondary":
            button.setStyleSheet(secondary)


def _restyle_inputs(root: QWidget, palette: FluentPalette) -> None:
    line = line_edit_qss(palette)
    spin = spin_box_qss(palette)
    combo = combo_box_qss(palette)
    for edit in root.findChildren(QLineEdit):
        if edit.parentWidget() is not None and isinstance(edit.parentWidget(), QAbstractSpinBox):
            continue
        if edit.parentWidget() is not None and isinstance(edit.parentWidget(), QComboBox):
            continue
        edit.setStyleSheet(line)
        edit.setMinimumHeight(CONTROL_HEIGHT)
    for box in root.findChildren(QAbstractSpinBox):
        box.setStyleSheet(spin)
        box.setMinimumHeight(CONTROL_HEIGHT)
    for box in root.findChildren(QComboBox):
        box.setStyleSheet(combo)
        box.setMinimumHeight(CONTROL_HEIGHT)
    for box in root.findChildren(QDateEdit):
        box.setStyleSheet(spin_box_qss(palette, "QDateEdit"))
        box.setMinimumHeight(CONTROL_HEIGHT)
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


def _style_item_view(view: QAbstractItemView, palette: FluentPalette) -> None:
    selector = view.metaObject().className()
    name = view.objectName()
    target = f"{selector}#{name}" if name else selector
    hover = css(list_item_hover(palette))
    selected = css(list_item_selected(palette))
    text = css(mix(palette.window_bg, palette.text_primary))
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
 padding: 6px 8px;
 margin: 1px 4px;
 color: {text};
}}
{target}::item:hover {{ background: {hover}; }}
{target}::item:selected {{ background: {selected}; color: {text}; }}
{target}::item:selected:hover {{ background: {selected}; }}
{scroll_bar_qss(palette)}
""",
    )
    _apply_list_palette(view, palette)


def _style_table(table: QTableView, palette: FluentPalette) -> None:
    selector_base = table.metaObject().className()
    name = table.objectName()
    selector = f"{selector_base}#{name}" if name else selector_base
    hover = css(list_item_hover(palette))
    selected = css(list_item_selected(palette))
    text = css(mix(palette.window_bg, palette.text_primary))
    secondary = css(mix(palette.window_bg, palette.text_secondary))
    divider = css(mix(palette.window_bg, palette.divider))
    card = css(palette.card_bg)
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
 background: {card};
 color: {text};
 border: 1px solid {stroke};
 border-radius: {RADIUS_CARD}px;
 outline: none;
 gridline-color: transparent;
}}
{selector}::item {{
 border: none;
 border-bottom: 1px solid {divider};
 padding: 0px 8px;
}}
{selector}::item:hover {{ background: {hover}; }}
{selector}::item:selected {{ background: {selected}; color: {text}; }}
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
