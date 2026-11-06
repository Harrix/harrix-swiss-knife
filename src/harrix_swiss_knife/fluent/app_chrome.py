"""Install Fluent chrome on tracker apps and overlay dialogs.

Tracker Windows call `prepare_fluent_app_window` before `install_win11_caption`
and `install_fluent_app_window` once the layout is complete. The install opts the
window into light/dark theme, replaces legacy white-surface / CTA stylesheets
with Fluent tokens, restyles inputs / tables / tabs / menus in a single pass, and
keeps everything in sync when the theme changes.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt, QTimer
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
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStatusBar,
    QTabBar,
    QTableView,
    QTableWidget,
    QTabWidget,
    QTextEdit,
    QWidget,
)

from harrix_swiss_knife.apps.common.day_bands import (
    install_day_band_vertical_header,
    refresh_day_bands,
    table_surface_color,
)
from harrix_swiss_knife.apps.common.table_models import enable_record_id_corner_sort, table_corner_button
from harrix_swiss_knife.apps.common.ui_chrome import (
    INPUT_BORDER,
    SELECTION_BG,
    SELECTION_HOVER,
    SELECTION_TEXT,
    SURFACE,
)
from harrix_swiss_knife.fluent.style import (
    chrome_bottom_color,
    chrome_top_color,
    combo_box_qss,
    date_edit_qss,
    fluent_tab_bar_qss,
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
    ICON_SIZE,
    RADIUS_CARD,
    RADIUS_CONTROL,
    SPACE_S,
)
from harrix_swiss_knife.fluent.widgets.navigation import polish_fluent_splitter
from harrix_swiss_knife.qt_flat_scrollbar import apply_flat_scrollbars
from harrix_swiss_knife.win11_backdrop import SystemBackdrop, try_apply_system_backdrop

if TYPE_CHECKING:
    from harrix_swiss_knife.fluent.tokens import FluentPalette

CAPTION_TABS_PROPERTY = "_hskCaptionTabs"
_PROP_BOUND = "_hskFluentAppChromeBound"
_PROP_CANVAS = "_hskFluentCanvas"
_MEDIA_PLATE_NAMES = frozenset({"label_exercise_avif", "label_exercise_avif_4", "label_exercise_avif_5"})
_MEDIA_LIST_NAMES = frozenset({"listView_exercises"})
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
    """Opt `window` into Fluent theme and standardized control chrome.

    Restyles the window once now and again only when the resolved theme changes.
    Call it after the layout is complete; `prepare_fluent_app_window` alone is
    enough for code that only needs `is_fluent_themed` (for example the caption).

    """
    if window.property(_PROP_BOUND):
        refresh_fluent_app_window(window)
        return
    # Mark first: the polish replay below re-enters through `install_fluent_dialog_chrome`.
    window.setProperty(_PROP_BOUND, True)  # noqa: FBT003
    prepare_fluent_app_window(window)
    if window.testAttribute(Qt.WidgetAttribute.WA_WState_Created):
        try_apply_system_backdrop(window, backdrop=SystemBackdrop.MICA)
    bind_theme(window, lambda: refresh_fluent_app_window(window))


def install_fluent_dialog_chrome(dialog: QWidget) -> bool:
    """Give `dialog` the same chrome as the app window that owns it.

    Only dialogs owned by a window that ran `install_fluent_app_window` are
    restyled, so Fluent widget-library dialogs keep their own controls.

    Returns:

    - `bool`: `True` when the chrome was installed now.

    """
    if dialog.property(_PROP_BOUND):
        return False
    owner = dialog.parentWidget()
    if owner is None or not owner.window().property(_PROP_BOUND):
        return False
    install_fluent_app_window(dialog)
    return True


def prepare_fluent_app_window(window: QWidget) -> None:
    """Mark `window` as Fluent-themed and swap in the Fluent window stylesheet.

    Children are restyled later by `install_fluent_app_window`. Replacing the
    legacy form stylesheet before anything is polished keeps the first (and most
    expensive) polish of the whole tree on the final rules.

    """
    from harrix_swiss_knife.qt_ui_effects import suspended_polish_filters  # noqa: PLC0415

    enable_fluent_theme(window)
    palette = palette_for(window)
    with suspended_polish_filters(window):
        _set_sheet(window, _fluent_surface_qss(palette))
        window.setPalette(to_qpalette(palette, window.palette()))
    window.setAutoFillBackground(False)


def refresh_fluent_app_window(window: QWidget) -> None:
    """Re-apply Fluent surfaces, controls, lists, tables, and buttons."""
    from harrix_swiss_knife.qt_ui_effects import suspended_polish_filters  # noqa: PLC0415

    palette = palette_for(window)
    with suspended_polish_filters(window):
        _apply_fluent_surfaces(window, palette)
        _normalize_control_metrics(window)
        _restyle_inputs(window, palette)
        _restyle_tables(window, palette)
        _restyle_tabs(window, palette)
        _apply_fluent_list_selection(window, palette)
        _restyle_buttons(window, palette)
        _restyle_splitters(window)
        apply_flat_scrollbars(window)
    window.update()


def _apply_fluent_list_selection(root: QWidget, palette: FluentPalette) -> None:
    for view in root.findChildren(QListView):
        _style_item_view(view, palette)
    for view in root.findChildren(QListWidget):
        _style_item_view(view, palette)


def _apply_fluent_surfaces(window: QWidget, palette: FluentPalette) -> None:
    """Replace opaque white chrome with translucent Fluent layers so Mica shows."""
    _set_sheet(window, _fluent_surface_qss(palette))
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
        if name in _MEDIA_PLATE_NAMES:
            continue
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
    for area in window.findChildren(QScrollArea):
        if "#ffffff" in area.styleSheet().lower():
            _set_sheet(area, "QScrollArea { background: transparent; border: none; }")
        viewport = area.viewport()
        if "#ffffff" in viewport.styleSheet().lower():
            _set_sheet(viewport, "")
        # setWidget turns autofill on, which paints a flat Window rect over the gradient.
        viewport.setAutoFillBackground(False)
        inner = area.widget()
        if inner is not None:
            inner.setAutoFillBackground(False)
    _apply_media_plates(window)
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


def _apply_media_plates(window: QWidget) -> None:
    """Keep exercise previews on a white plate so white GIF frames match the surface."""
    for name in _MEDIA_PLATE_NAMES:
        label = window.findChild(QLabel, name)
        if label is None:
            continue
        _set_sheet(
            label,
            f"QLabel#{name} {{ background-color: {SURFACE}; border: 1px solid {INPUT_BORDER}; }}",
        )
        label.setAutoFillBackground(True)


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


def _clear_viewport(view: QAbstractItemView, palette: FluentPalette) -> None:
    """Paint the list viewport with the window gradient instead of the system base."""
    text = css(mix(palette.window_bg, palette.text_primary))
    view.setAutoFillBackground(False)
    viewport = view.viewport()
    viewport.setAutoFillBackground(False)
    _set_sheet(viewport, f"background: {wallpaper_fill(palette)}; color: {text};")


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
 margin-top: 1.5em;
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


def _is_icon_grid(view: QAbstractItemView) -> bool:
    """Return whether `view` is a tile grid that owns its icon size and selection."""
    return isinstance(view, QListView) and view.viewMode() == QListView.ViewMode.IconMode


def _lock_control_height(widget: QWidget) -> None:
    """Keep inputs and CTAs at the standard Fluent control height."""
    widget.setFixedHeight(CONTROL_HEIGHT)


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
    """Let the window gradient show through a structural panel that used to be flat white."""
    name = widget.objectName()
    if not name:
        name = f"hskCanvas{id(widget)}"
        widget.setObjectName(name)
    text = css(mix(palette.window_bg, palette.text_primary))
    _set_sheet(widget, f"QWidget#{name} {{ background: transparent; color: {text}; border: none; }}")
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
            _set_sheet(button, f"/* hsk-fluent-{kind} */\n{semantic_button_qss(palette, kind)}")
            _lock_control_height(button)
            button.setProperty("_hskFluentButton", kind)
        elif any(marker.lower() in sheet.lower() for marker in _SECONDARY_MARKERS):
            _set_sheet(button, secondary)
            _lock_control_height(button)
            button.setProperty("_hskFluentButton", "secondary")
        elif kind == "secondary":
            _set_sheet(button, secondary)
            _lock_control_height(button)


def _restyle_inputs(root: QWidget, palette: FluentPalette) -> None:
    from harrix_swiss_knife.qt_lucide_icon import install_line_edit_clear_button  # noqa: PLC0415

    line = line_edit_qss(palette, height=CONTROL_HEIGHT)
    spin = spin_box_qss(palette, height=CONTROL_HEIGHT)
    combo = combo_box_qss(palette, height=CONTROL_HEIGHT)
    for edit in root.findChildren(QLineEdit):
        if edit.parentWidget() is not None and isinstance(edit.parentWidget(), QAbstractSpinBox):
            continue
        if edit.parentWidget() is not None and isinstance(edit.parentWidget(), QComboBox):
            continue
        # Replace Qt's stock clear glyph with the shared Lucide red `x`.
        if edit.isClearButtonEnabled():
            install_line_edit_clear_button(edit)
        _set_sheet(edit, line)
        _lock_control_height(edit)
    for box in root.findChildren(QAbstractSpinBox):
        if isinstance(box, QDateEdit):
            continue
        # Height is locked to CONTROL_HEIGHT so Lucide chevrons fit; CompactSpinBox
        # still keeps its narrow button geometry via QProxyStyle.
        _set_sheet(box, spin)
        _lock_control_height(box)
    for box in root.findChildren(QComboBox):
        _set_sheet(box, combo)
        _lock_control_height(box)
    date = date_edit_qss(palette, height=CONTROL_HEIGHT)
    for box in root.findChildren(QDateEdit):
        _set_sheet(box, date)
        _lock_control_height(box)
    plain = text_edit_qss(palette, "QPlainTextEdit")
    for edit in root.findChildren(QPlainTextEdit):
        _set_sheet(edit, plain)
    rich = text_edit_qss(palette, "QTextEdit")
    for edit in root.findChildren(QTextEdit):
        _set_sheet(edit, rich)


def _restyle_splitters(root: QWidget) -> None:
    """Apply Fluent wide-handle accent hairline chrome to every splitter under `root`."""
    for splitter in root.findChildren(QSplitter):
        polish_fluent_splitter(splitter)


def _restyle_tables(root: QWidget, palette: FluentPalette) -> None:
    for table in root.findChildren(QTableView):
        _style_table(table, palette)
        refresh_day_bands(table)
    for table in root.findChildren(QTableWidget):
        _style_table(table, palette)
        refresh_day_bands(table)


def _restyle_tabs(root: QWidget, palette: FluentPalette) -> None:
    for tabs in root.findChildren(QTabWidget):
        tabs.setDocumentMode(True)
        if tabs.property(CAPTION_TABS_PROPERTY):
            continue
        name = tabs.objectName() or "tabWidget"
        if not tabs.objectName():
            tabs.setObjectName(name)
        _set_sheet(
            tabs,
            f"QTabWidget#{name}::pane {{ background: transparent; border: none; top: -1px; }}"
            + fluent_tab_bar_qss(palette, f"QTabWidget#{name} > QTabBar", closable=tabs.tabsClosable()),
        )
    for bar in root.findChildren(QTabBar):
        if bar.property(CAPTION_TABS_PROPERTY):
            continue
        parent = bar.parentWidget()
        if isinstance(parent, QTabWidget) and parent.tabBar() is bar:
            continue
        _set_sheet(bar, fluent_tab_bar_qss(palette, closable=bar.tabsClosable()))


def _set_sheet(widget: QWidget, sheet: str) -> None:
    """Assign `sheet` only when it changed; each assignment re-polishes the subtree."""
    if widget.styleSheet() != sheet:
        widget.setStyleSheet(sheet)


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
    if _is_icon_grid(view):
        _clear_viewport(view, palette)
        return
    if view.objectName() in _MEDIA_LIST_NAMES:
        _style_media_list(view, palette)
        return
    name = view.objectName()
    selector = view.metaObject().className()
    target = f"{selector}#{name}" if name else selector
    hover = css(list_item_hover(palette))
    selected = css(list_item_selected(palette))
    text = css(mix(palette.window_bg, palette.text_primary))
    icon = view.iconSize()
    if icon.width() <= ICON_SIZE:
        view.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
    view.setSpacing(0)
    _set_sheet(
        view,
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


def _style_media_list(view: QAbstractItemView, palette: FluentPalette) -> None:
    """Keep a thumbnail list on white with the shared soft-blue selection."""
    name = view.objectName()
    selector = view.metaObject().className()
    target = f"{selector}#{name}" if name else selector
    icon = view.iconSize()
    if icon.width() <= ICON_SIZE:
        view.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
    _set_sheet(
        view,
        f"""
{target} {{
 background: {SURFACE};
 color: {SELECTION_TEXT};
 border: none;
 outline: none;
}}
{target}::item {{
 padding: 2px;
 margin: 0px;
 color: {SELECTION_TEXT};
 border-bottom: 1px solid #e0e0e0;
}}
{target}::item:hover {{ background: {SELECTION_HOVER}; }}
{target}::item:selected {{ background: {SELECTION_BG}; color: {SELECTION_TEXT}; }}
{target}::item:selected:hover {{ background: {SELECTION_BG}; }}
{scroll_bar_qss(palette)}
""",
    )
    tuned = view.palette()
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive, QPalette.ColorGroup.Disabled):
        tuned.setColor(group, QPalette.ColorRole.Highlight, QColor(SELECTION_BG))
        tuned.setColor(group, QPalette.ColorRole.HighlightedText, QColor(SELECTION_TEXT))
    view.setPalette(tuned)
    _paint_viewport(view, QColor(SURFACE), QColor(SELECTION_TEXT))


def _style_table(table: QTableView, palette: FluentPalette) -> None:
    selector_base = table.metaObject().className()
    name = table.objectName()
    selector = f"{selector_base}#{name}" if name else selector_base
    secondary = css(mix(palette.window_bg, palette.text_secondary))
    divider = css(mix(palette.window_bg, palette.divider))
    text = mix(palette.window_bg, palette.text_primary)
    surface = table_surface_color(palette)
    stroke = css(palette.card_stroke)
    table.setShowGrid(False)
    table.setAlternatingRowColors(False)
    header = table.horizontalHeader()
    header.setHighlightSections(False)
    header.setDefaultAlignment(header.defaultAlignment())
    if isinstance(header, QHeaderView):
        header.setMinimumHeight(CONTROL_HEIGHT)
    install_day_band_vertical_header(table)
    vertical = table.verticalHeader()
    vertical.setProperty("hskRecordIds", "true")
    _watch_record_id_header(table)
    _sync_record_id_header(table)
    id_point = table.font().pointSizeF()
    if id_point <= 0:
        id_point = 10.0
    id_point = max(8.0, id_point - 2.0)
    floor = CONTROL_HEIGHT + SPACE_S
    if vertical.defaultSectionSize() < floor:
        vertical.setDefaultSectionSize(floor)
    _set_sheet(
        table,
        f"""
{selector} {{
 background: {surface.name()};
 color: {css(text)};
 border: 1px solid {stroke};
 border-radius: {RADIUS_CARD}px;
 outline: none;
 gridline-color: transparent;
}}
{selector} QHeaderView {{ background: {surface.name()}; color: {secondary}; border: none; }}
{selector} QHeaderView::section {{
 background: {surface.name()};
 color: {secondary};
 border: none;
 border-bottom: 1px solid {divider};
 padding: 0px 8px;
 min-height: {CONTROL_HEIGHT}px;
 font-weight: 600;
}}
{selector} QHeaderView[hskRecordIds="true"]::section {{
 font-size: {id_point:.1f}pt;
 font-weight: 400;
 padding: 0px 4px;
}}
{selector} QTableCornerButton::section {{
 background: {surface.name()};
 color: {secondary};
 border: none;
 border-bottom: 1px solid {divider};
}}
{scroll_bar_qss(palette)}
""",
    )
    # No ::item background: that stylesheet replaces the model's row tint.
    _paint_viewport(table, surface, text)
    # Custom headers (word-wrap) paint from the palette, not from the section QSS.
    ink = mix(palette.window_bg, palette.text_secondary)
    tuned = header.palette()
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive):
        for role in (QPalette.ColorRole.Button, QPalette.ColorRole.Window, QPalette.ColorRole.Base):
            tuned.setColor(group, role, surface)
        for role in (QPalette.ColorRole.ButtonText, QPalette.ColorRole.WindowText, QPalette.ColorRole.Text):
            tuned.setColor(group, role, ink)
    header.setPalette(tuned)
    header.viewport().setPalette(tuned)
    vertical.setPalette(tuned)
    vertical.viewport().setPalette(tuned)
    corner = table_corner_button(table)
    if corner is not None:
        corner.setPalette(tuned)
        corner.setAutoFillBackground(True)
        corner.update()


def _sync_record_id_header(table: QTableView) -> None:
    """Show the vertical header once its labels are record ids, not row numbers.

    Chrome runs before tracker tables are filled. An empty model must not hide the
    header, or the ids never come back when the rows arrive.

    """
    model = table.model()
    if model is None or model.rowCount() <= 0:
        return
    vertical = table.verticalHeader()
    show = _table_shows_record_ids(table)
    vertical.setVisible(show)
    if not show:
        return
    enable_record_id_corner_sort(table)
    font = QFont(table.font())
    point = font.pointSizeF()
    if point > 0:
        font.setPointSizeF(max(8.0, point - 2.0))
    elif font.pixelSize() > 0:
        font.setPixelSize(max(10, font.pixelSize() - 3))
    font.setBold(False)
    vertical.setFont(font)
    metrics = vertical.fontMetrics()
    text_width = 0
    sample = min(model.rowCount(), 40)
    for row in range(sample):
        value = model.headerData(row, Qt.Orientation.Vertical, Qt.ItemDataRole.DisplayRole)
        text_width = max(text_width, metrics.horizontalAdvance("" if value is None else str(value)))
    width = max(text_width + 10, vertical.sizeHint().width())
    if width > vertical.minimumWidth():
        vertical.setMinimumWidth(width)


def _table_shows_record_ids(table: QTableView) -> bool:
    """Return whether the vertical header carries labels other than row numbers."""
    model = table.model()
    if model is None:
        return False
    sample = min(model.rowCount(), 8)
    for row in range(sample):
        value = model.headerData(row, Qt.Orientation.Vertical, Qt.ItemDataRole.DisplayRole)
        text = "" if value is None else str(value).strip()
        if text and text != str(row + 1):
            return True
    return False


def _watch_record_id_header(table: QTableView) -> None:
    """Re-check record-id labels when the table gains rows."""
    if table.property("hskRecordIdHeaderWatch"):
        return
    table.setProperty("hskRecordIdHeaderWatch", 1)

    def _defer_sync() -> None:
        try:
            _sync_record_id_header(table)
        except RuntimeError:
            return

    def _on_section_count_changed(_old_count: int, new_count: int) -> None:
        # sectionCountChanged is emitted inside setModel, before the view model is ready.
        if new_count > 0:
            QTimer.singleShot(0, _defer_sync)

    # PySide does not keep a Python slot alive by itself.
    table._hsk_record_id_header_slot = _defer_sync  # type: ignore[attr-defined]  # noqa: SLF001
    table._hsk_record_id_header_watch = _on_section_count_changed  # type: ignore[attr-defined]  # noqa: SLF001
    table.verticalHeader().sectionCountChanged.connect(_on_section_count_changed)
