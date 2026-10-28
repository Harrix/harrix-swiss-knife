"""Gallery of every Fluent widget, grouped by category.

Run with `python -m harrix_swiss_knife.fluent.gallery`.

Each showcase control has a context menu to copy its object name or class name.

"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, QPoint, QPointF, QRectF, Qt, QTime
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QMenu, QTableWidgetItem, QTreeWidgetItem, QVBoxLayout, QWidget

from harrix_swiss_knife.fluent import widgets as fw
from harrix_swiss_knife.fluent.theme import FluentTheme, ThemeMode
from harrix_swiss_knife.fluent.tokens import SPACE_L, SPACE_M, SPACE_XL
from harrix_swiss_knife.qt_app_font import install_app_fonts
from harrix_swiss_knife.qt_flow_layout import FlowLayout

if TYPE_CHECKING:
    from collections.abc import Callable

_GALLERY_SIZE = (1200, 820)
_SHOWCASE_COUNTS: dict[str, int] = {}
_PROP_SHOWCASE = "_hskShowcaseLabel"


def build_gallery() -> fw.FluentNavigationWindow:
    """Build the gallery window with one page per widget category."""
    _SHOWCASE_COUNTS.clear()
    theme_button = fw.FluentIconButton("sun" if FluentTheme.instance().is_dark() else "moon", tooltip="Toggle theme")
    theme_button.setObjectName("themeToggleButton")
    window = fw.FluentNavigationWindow("Fluent gallery", install_caption=False)
    _install_main_menu(window, theme_button)
    window.install_caption(trailing_widgets=[theme_button])
    theme_button.clicked.connect(lambda: _toggle_gallery_theme(theme_button))
    window.resize(*_GALLERY_SIZE)
    pages = (
        ("basic", "Basic input", "mouse-pointer-click", _basic_page()),
        ("text", "Text and selection", "text-cursor-input", _text_page()),
        ("display", "Status and info", "info", _display_page()),
        ("cards", "Cards", "layout-grid", _cards_page()),
        ("navigation", "Navigation", "navigation", _navigation_page()),
        ("views", "Collections", "list", _views_page()),
        ("dialogs", "Dialogs and flyouts", "message-square", _dialogs_page(window)),
        ("pickers", "Date and time", "calendar", _pickers_page()),
        ("editors", "Editors", "code", _editors_page()),
    )
    for key, text, icon, page in pages:
        window.add_page(key, text, page, icon=icon)
    _register_showcase(theme_button, "themeToggleButton")
    return window


def _basic_page() -> QWidget:
    menu = fw.FluentMenu()
    menu.add_lucide_action("Copy", "copy")
    menu.add_lucide_action("Paste", "clipboard")
    return _page(
        "Basic input",
        [
            _section(
                "Buttons",
                fw.FluentPushButton("Standard"),
                fw.FluentPrimaryButton("Accent", icon="check"),
                fw.FluentTransparentButton("Subtle"),
                fw.FluentPillButton("Pill"),
                fw.FluentToggleButton("Toggle"),
                fw.FluentHyperlinkButton("Hyperlink", "https://github.com"),
                fw.FluentDropDownButton("Drop-down", menu=menu),
                fw.FluentIconButton("settings", tooltip="Settings"),
                fw.FluentToolButton("Tool", icon="wrench"),
                fw.FluentCopyButton("copied text", label="Copy"),
            ),
            _section("Toggles", fw.FluentToggleSwitch(), fw.FluentCheckBox("Check box"), fw.FluentRadioButton("Radio")),
            _section("Rating and slider", fw.FluentRatingControl(), fw.FluentSlider()),
        ],
    )


def _cards_page() -> QWidget:
    grid = fw.FluentCardGrid()
    for index in range(6):
        grid.add_card(
            fw.FluentCommandCard(f"Command {index + 1}", "Short description of what it does", icon="terminal")
        )
    reminder = fw.FluentReminderCard("Standup", "Today 10:00", text="Daily sync")
    return _page(
        "Cards",
        [
            _section("Command cards", grid, flow=False),
            _section(
                "Other cards",
                fw.FluentPopularCard("Popular", "Hover for details", icon="star", details="Details shown on hover"),
                fw.FluentImageCard("Image card", "Caption"),
                fw.FluentAcrylicUrlCard("Harrix", "https://github.com/Harrix", icon="globe"),
            ),
            _section(
                "Promotion",
                fw.FluentPromotionCard("Harrix Swiss Knife", "Fluent widgets", action_text="Open"),
                flow=False,
            ),
            _section("Reminder", reminder, flow=False),
            _section("Expander", _expander(), flow=False),
        ],
    )


def _copy_text(value: str) -> None:
    clipboard = QGuiApplication.clipboard()
    if clipboard is not None:
        clipboard.setText(value)


def _dialogs_page(window: QWidget) -> QWidget:
    def button(text: str, action: Callable[[], object]) -> fw.FluentPushButton:
        widget = fw.FluentPushButton(text)
        widget.clicked.connect(action)
        return widget

    popconfirm_button = fw.FluentPushButton("Popconfirm")
    popconfirm_button.clicked.connect(lambda: fw.FluentPopconfirm("Delete this item?", popconfirm_button).popup())
    flyout_button = fw.FluentPushButton("Flyout")
    flyout_button.clicked.connect(lambda: fw.FluentFlyout(flyout_button, fw.BodyLabel("Flyout content")).popup())
    tip_button = fw.FluentPushButton("Teaching tip")
    tip_button.clicked.connect(
        lambda: fw.FluentTeachingTip(tip_button, "Tip", "Teaching tips point at a control.").show_tip()
    )
    drawer = fw.FluentDrawerArea(window, title="Drawer")
    drawer.content_layout.addWidget(fw.BodyLabel("Drawer content"))
    sheet = fw.FluentSheetPanel(window)
    sheet.content_layout.addWidget(fw.SubtitleLabel("Bottom sheet"))
    tooltip_button = fw.FluentPushButton("Fluent tooltip")
    tooltip_button.setToolTip("Fluent tooltip text")
    fw.install_fluent_tooltip(tooltip_button)
    return _page(
        "Dialogs and flyouts",
        [
            _section(
                "Dialogs",
                button(
                    "Content dialog",
                    lambda: fw.FluentContentDialog("Delete file?", "This cannot be undone.", window).open(),
                ),
                button("Message", lambda: fw.FluentMessageDialog.inform(window, "Info", "Saved")),
                button("Input", lambda: fw.FluentInputDialog.get_text(window, "Rename", "New name")),
                button("Color", lambda: fw.FluentColorDialog.get_color(None, window)),
                button("Wizard", lambda: _wizard(window).exec()),
                popconfirm_button,
                flyout_button,
                tip_button,
                tooltip_button,
            ),
            _section(
                "Notifications",
                fw.FluentMessageButton(
                    "Message bar", title="Saved", message="All changes saved", severity=fw.Severity.SUCCESS
                ),
                button("Toast", lambda: fw.FluentToast("Toast", "Shown at the screen corner").show_toast()),
                button(
                    "Snackbar", lambda: fw.FluentSnackbar("Item archived", window, action_text="Undo").show_snackbar()
                ),
                button("Drawer", drawer.open_drawer),
                button("Sheet", sheet.open_sheet),
            ),
            _section(
                "Info bars",
                fw.FluentInfoBar("Info", "Informational message"),
                fw.FluentInfoBar("Success", "Done", severity=fw.Severity.SUCCESS),
                fw.FluentInfoBar("Warning", "Check settings", severity=fw.Severity.CAUTION),
                fw.FluentInfoBar("Error", "Something failed", severity=fw.Severity.CRITICAL),
                flow=False,
            ),
        ],
    )


def _display_page() -> QWidget:
    timeline = fw.FluentTimeline()
    timeline.add_entry(fw.TimelineEntry("09:00", "Started", "Project created"))
    timeline.add_entry(fw.TimelineEntry("12:30", "Reviewed", severity=fw.Severity.SUCCESS))
    ring = fw.FluentProgressRing(show_text=True)
    ring.set_value(64)
    busy_ring = fw.FluentProgressRing()
    busy_ring.set_busy(busy=True)
    bar = fw.FluentProgressBar()
    bar.set_value(40)
    bar.setFixedWidth(240)
    lcd = fw.FluentLCDNumber()
    lcd.display(2026)
    countdown = fw.FluentCountdown(seconds=3 * 3600 + 125)
    return _page(
        "Status and info",
        [
            _section(
                "Badges and tags",
                fw.FluentInfoBadge(value=5),
                fw.FluentInfoBadge(),
                fw.FluentInfoBadge(icon="check", severity=fw.Severity.SUCCESS),
                fw.FluentTag("Neutral"),
                fw.FluentTag("Closable", closable=True, severity=fw.Severity.ACCENT),
                fw.FluentTag("Checkable", checkable=True),
                fw.FluentPersonPicture(name="Anton Sergienko"),
                fw.FluentPersonPicture(),
            ),
            _section("Progress", bar, ring, busy_ring, fw.FluentSkeleton(shape=fw.SkeletonShape.CIRCLE)),
            _section(
                "Stats",
                fw.FluentStatCard("Visitors", "12 480", trend=fw.Trend.UP, trend_text="12%", icon="users"),
                fw.FluentStatCard("Errors", "3", trend=fw.Trend.DOWN, trend_text="2", description="Last 24 hours"),
                fw.FluentDashboardGauge(unit="%", title="CPU", caution=70, critical=90),
            ),
            _section("Steps", fw.FluentSteps(steps=["Account", "Profile", "Done"]), flow=False),
            _section("Timeline", timeline, flow=False),
            _section("Numbers and codes", lcd, countdown, fw.FluentQRCode("https://github.com/Harrix")),
            _section("Dividers", fw.FluentDivider(), fw.FluentDivider(text="Section"), flow=False),
        ],
    )


def _editors_page() -> QWidget:
    code = fw.FluentCodeEditor()
    code.setPlainText('def hello(name: str) -> str:\n    """Greet."""\n    return f"Hello, {name}!"  # comment\n')
    code.setFixedHeight(160)
    markdown = fw.FluentMarkdownViewer(markdown="# Title\n\nSome **bold** text and `code`.\n\n- One\n- Two\n")
    markdown.setFixedHeight(160)
    chat = QWidget()
    chat_layout = QVBoxLayout(chat)
    chat_layout.addWidget(fw.FluentChatBubble("Hi! How are you?", sender="Anna", time="10:01"))
    chat_layout.addWidget(fw.FluentChatBubble("Great, thanks!", side=fw.BubbleSide.OUTGOING, time="10:02"))
    terminal = fw.FluentTerminalWidget()
    terminal.setFixedHeight(180)
    log_view = fw.FluentLogView()
    log_view.append_record(20, "12:00:00  INFO     Started")
    log_view.append_record(30, "12:00:05  WARNING  Slow response")
    log_view.setFixedHeight(140)
    return _page(
        "Editors",
        [
            _section("Code editor", code, flow=False),
            _section("Markdown", markdown, flow=False),
            _section("Chat", chat, flow=False),
            _section("Terminal", terminal, flow=False),
            _section("Log", log_view, flow=False),
        ],
    )


def _expander() -> QWidget:
    expander = fw.FluentExpander("Advanced", caption="More options", icon="sliders-horizontal")
    expander.content_layout.addWidget(fw.FluentToggleSwitch())
    return expander


def _install_main_menu(window: fw.FluentNavigationWindow, theme_button: fw.FluentIconButton) -> None:
    """Add File and View to the caption. Must run before `install_caption`."""
    bar = window.menuBar()
    bar.setNativeMenuBar(False)
    file_menu = bar.addMenu("&File")
    close_action = file_menu.addAction("Close")
    close_action.triggered.connect(window.close)
    view_menu = bar.addMenu("&View")
    theme_action = view_menu.addAction("Toggle theme")
    theme_action.triggered.connect(lambda: _toggle_gallery_theme(theme_button))


def _navigation_page() -> QWidget:
    tabs = fw.FluentTabWidget()
    tabs.add_tab(fw.BodyLabel("First page"), "First")
    tabs.add_tab(fw.BodyLabel("Second page"), "Second")
    tabs.setMinimumHeight(140)
    command_bar = fw.FluentCommandBar()
    for text, icon in (("New", "plus"), ("Edit", "pencil"), ("Share", "share-2"), ("Delete", "trash-2")):
        command_bar.add_command(text, icon)
    ribbon = fw.FluentRibbonBar()
    home = ribbon.add_tab("Home")
    ribbon.add_tab("Insert")
    group = ribbon.add_group(home, "Clipboard")
    group.add_button("Paste", "clipboard")
    group.add_button("Copy", "copy")
    toolbar = fw.FluentToolBar()
    toolbar.add_lucide_action("Bold", "bold")
    toolbar.add_lucide_action("Italic", "italic")
    menu_bar = fw.FluentMenuBar()
    file_menu = menu_bar.add_fluent_menu("File")
    file_menu.add_lucide_action("Open", "folder-open")
    nav = fw.FluentNavigationBar(collapsible=False)
    nav.add_header("Section")
    nav.add_item("home", "Home", icon="house")
    nav.add_item("docs", "Documents", icon="file-text")
    nav.setFixedSize(240, 140)
    return _page(
        "Navigation",
        [
            _section("Breadcrumb", fw.FluentBreadcrumb(items=["Home", "Documents", "Notes"]), flow=False),
            _section("Pivot", fw.FluentPivot(items=["All", "Unread", "Flagged"]), flow=False),
            _section("Pagination", fw.FluentPagination(pages=12), flow=False),
            _section("Navigation bar", nav, flow=False),
            _section("Tabs", tabs, flow=False),
            _section("Command bar", command_bar, flow=False),
            _section("Menu bar and tool bar", menu_bar, toolbar, flow=False),
            _section("Ribbon", ribbon, flow=False),
            _section("Status bar", fw.FluentStatusBar(), flow=False),
        ],
    )


def _page(title: str, sections: list[QWidget]) -> QWidget:
    page = QWidget()
    column = QVBoxLayout(page)
    column.setContentsMargins(SPACE_XL + SPACE_M, SPACE_L, SPACE_XL + SPACE_M, SPACE_XL)
    column.setSpacing(SPACE_XL)
    column.addWidget(fw.TitleLabel(title, page))
    for section in sections:
        column.addWidget(section)
    column.addStretch(1)
    return page


def _pickers_page() -> QWidget:
    return _page(
        "Date and time",
        [
            _section(
                "Pickers",
                fw.FluentCalendarPicker(date=QDate.currentDate()),
                fw.FluentDatePicker(),
                fw.FluentTimePicker(time=QTime(9, 30)),
            ),
            _section("Calendar", fw.FluentCalendar(), flow=False),
            _section("Roller", fw.FluentRoller(items=[str(value) for value in range(1, 31)], looping=True)),
        ],
    )


def _register_showcase(widget: QWidget, label: str | None = None) -> QWidget:
    """Tag `widget` for the gallery and attach the copy-name context menu."""
    class_name = type(widget).__name__
    count = _SHOWCASE_COUNTS.get(class_name, 0) + 1
    _SHOWCASE_COUNTS[class_name] = count
    name = label or (class_name if count == 1 else f"{class_name}_{count}")
    if not widget.objectName():
        widget.setObjectName(name)
    widget.setProperty(_PROP_SHOWCASE, name)
    widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    widget.customContextMenuRequested.connect(lambda pos, host=widget: _show_showcase_menu(host, pos))
    return widget


def _section(title: str, *widgets: QWidget, flow: bool = True) -> QWidget:
    box = QWidget()
    column = QVBoxLayout(box)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(SPACE_M)
    column.addWidget(fw.StrongBodyLabel(title, box))
    holder = QWidget(box)
    layout = FlowLayout(holder, margin=0, h_spacing=SPACE_M, v_spacing=SPACE_M) if flow else QVBoxLayout(holder)
    if not flow:
        layout.setContentsMargins(0, 0, 0, 0)
    for widget in widgets:
        widget.setParent(holder)
        _register_showcase(widget)
        layout.addWidget(widget)
    column.addWidget(holder)
    return box


def _show_showcase_menu(widget: QWidget, pos: QPoint) -> None:
    label = str(widget.property(_PROP_SHOWCASE) or widget.objectName() or type(widget).__name__)
    class_name = type(widget).__qualname__
    module_name = type(widget).__module__
    menu = QMenu(widget)
    copy_name = menu.addAction(f"Copy object name ({label})")
    copy_class = menu.addAction(f"Copy class name ({class_name})")
    copy_qual = menu.addAction("Copy module.Class")
    chosen = menu.exec(widget.mapToGlobal(pos))
    if chosen is copy_name:
        _copy_text(label)
    elif chosen is copy_class:
        _copy_text(class_name)
    elif chosen is copy_qual:
        _copy_text(f"{module_name}.{class_name}")


def _text_page() -> QWidget:
    tree = fw.FluentTreeSelect()
    tree.add_branch(["Documents", "Work", "Report.md"])
    tree.add_branch(["Documents", "Home", "List.md"])
    return _page(
        "Text and selection",
        [
            _section(
                "Text boxes",
                fw.FluentLineEdit(placeholder="Text"),
                fw.FluentSearchLineEdit(),
                fw.FluentPasswordBox(),
                fw.FluentSuggestBox(suggestions=["Apple", "Banana", "Cherry"]),
                fw.FluentAutoComplete(suggestions=["Python", "PySide6", "Qt"]),
            ),
            _section("Numbers", fw.FluentSpinBox(), fw.FluentDoubleSpinBox(), fw.FluentNumberBox()),
            _section(
                "Choices",
                fw.FluentComboBox(items=["One", "Two", "Three"]),
                fw.FluentEditableComboBox(items=["Red", "Green"]),
                fw.FluentMultiSelectComboBox(items=["A", "B", "C"]),
                tree,
                fw.FluentKeyBinder(binding="Ctrl+K"),
                fw.FluentSelectorBar(items=["Day", "Week", "Month"]),
            ),
            _section("Code input", fw.FluentCaptcha()),
            _section(
                "Multi-line",
                fw.FluentPlainTextEdit(placeholder="Plain text"),
                fw.FluentTextEdit(placeholder="Rich text"),
            ),
            _section("Transfer", fw.FluentTransfer(source=["One", "Two", "Three"]), flow=False),
        ],
    )


def _toggle_gallery_theme(theme_button: fw.FluentIconButton) -> None:
    """Flip light and dark for this window only, and update the caption icon."""
    mode = FluentTheme.instance().toggle(persist=False)
    theme_button.set_icon_name("sun" if mode == ThemeMode.DARK else "moon")


def _views_page() -> QWidget:
    list_widget = fw.FluentListWidget()
    list_widget.addItems([f"Item {index}" for index in range(1, 8)])
    list_widget.setCurrentRow(1)
    list_widget.setFixedHeight(180)
    table = fw.FluentTableWidget(4, 3)
    table.setHorizontalHeaderLabels(["Name", "Size", "Type"])
    for row in range(4):
        for column, value in enumerate((f"File {row}", f"{row * 10} KB", "md")):
            table.setItem(row, column, QTableWidgetItem(value))
    table.setFixedHeight(200)
    tree = fw.FluentTreeWidget()
    tree.setHeaderLabels(["Name"])
    parent = QTreeWidgetItem(tree, ["Folder"])
    QTreeWidgetItem(parent, ["File.txt"])
    tree.expandAll()
    tree.setFixedHeight(140)
    virtual = fw.FluentVirtualList(count=100_000, provider=lambda row: f"Row {row + 1}")
    virtual.setFixedHeight(160)
    scene = fw.FluentGraphicsScene()
    first = fw.FluentGraphicsItem("Start", QRectF(0, 0, 140, 56))
    second = fw.FluentGraphicsItem("Finish", QRectF(0, 0, 140, 56))
    second.setPos(QPointF(220, 90))
    scene.addItem(first)
    scene.addItem(second)
    scene.addItem(fw.FluentGraphicsLineItem(first, second))
    graphics = fw.FluentGraphicsView(scene)
    graphics.setFixedHeight(220)
    return _page(
        "Collections",
        [
            _section("List", list_widget, flow=False),
            _section("Table", table, flow=False),
            _section("Tree", tree, flow=False),
            _section("Virtual list (100 000 rows)", virtual, flow=False),
            _section("Graphics", graphics, flow=False),
            _section("Carousel", fw.FluentPromotionView(), flow=False),
        ],
    )


def _wizard(window: QWidget) -> fw.FluentWizard:
    wizard = fw.FluentWizard("Setup", window, steps=["Welcome", "Options", "Finish"])
    for text in ("Welcome", "Choose options", "All set"):
        wizard.add_page(fw.BodyLabel(text))
    return wizard


def main() -> int:
    """Show the gallery."""
    existing = QApplication.instance()
    app = existing if isinstance(existing, QApplication) else QApplication(sys.argv)
    install_app_fonts(app)
    FluentTheme.instance().load_from_config()
    window = build_gallery()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
