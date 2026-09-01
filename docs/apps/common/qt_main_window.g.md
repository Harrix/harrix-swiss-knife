---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_main_window.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AppWindowMixin`](#%EF%B8%8F-class-appwindowmixin)
  - [⚙️ Method `on_about`](#%EF%B8%8F-method-on_about)
  - [⚙️ Method `on_exit`](#%EF%B8%8F-method-on_exit)
  - [⚙️ Method `on_reveal_database`](#%EF%B8%8F-method-on_reveal_database)
  - [⚙️ Method `on_settings`](#%EF%B8%8F-method-on_settings)
- [🔧 Function `apply_app_window_size_and_position`](#-function-apply_app_window_size_and_position)
- [🔧 Function `apply_restored_app_window_geometry`](#-function-apply_restored_app_window_geometry)
- [🔧 Function `compute_app_window_geometry`](#-function-compute_app_window_geometry)
- [🔧 Function `compute_maximize_pin_geometry`](#-function-compute_maximize_pin_geometry)
- [🔧 Function `compute_restore_window_geometry`](#-function-compute_restore_window_geometry)
- [🔧 Function `inset_restore_frame_rect`](#-function-inset_restore_frame_rect)
- [🔧 Function `resolve_window_menu_bar`](#-function-resolve_window_menu_bar)
- [🔧 Function `window_frame_escapes_work_area`](#-function-window_frame_escapes_work_area)
- [🔧 Function `window_frame_margins`](#-function-window_frame_margins)

</details>

## 🏛️ Class `AppWindowMixin`

```python
class AppWindowMixin
```

Mixin with common `QMainWindow` helpers shared across apps.

<details>
<summary>Code:</summary>

```python
class AppWindowMixin:

    about_app_name: ClassVar[str] = "Harrix Swiss Knife"
    about_description: ClassVar[str] = ""
    settings_app_id: ClassVar[str | None] = None
    defer_initial_show: ClassVar[bool] = False

    actionAbout: QAction  # noqa: N815
    actionExit: QAction  # noqa: N815
    db_manager: Any
    _hide_on_close: bool

    def on_about(self) -> None:
        """Show the About dialog with app information."""
        version = self._get_version_from_pyproject()
        description = type(self).about_description
        github_url = "https://github.com/harrix/harrix-swiss-knife"
        lines = [
            type(self).about_app_name,
            "",
            f"Version: {version}",
            "",
        ]
        if description:
            lines.extend([description, ""])
        lines.extend(
            [
                "Part of Harrix Swiss Knife.",
                "",
                "Author: Anton Sergienko (Harrix)",
                "License: MIT License",
                f"GitHub: {github_url}",
            ],
        )
        plain_text = "\n".join(lines)
        html_text = "<br>".join([*lines[:-1], f'GitHub: <a href="{github_url}">{github_url}</a>'])
        message_box.information(
            cast("QWidget", self),
            "About",
            html_text,
            rich_text=True,
            clipboard_text=plain_text,
        )

    def on_exit(self) -> None:
        """Close the application window."""
        self.close()  # type: ignore[attr-defined]

    def on_reveal_database(self) -> None:
        """Open the system file manager with this app's SQLite database selected."""
        db_path = self._resolve_database_path()
        if db_path is None:
            message_box.warning(
                cast("QWidget", self),
                "Database",
                "Database path is not available.",
            )
            return
        if not db_path.is_file():
            message_box.warning(
                cast("QWidget", self),
                "Database",
                f"Database file was not found:\n{db_path}",
            )
            return
        try:
            reveal_in_file_explorer(db_path)
        except (FileNotFoundError, OSError) as exc:
            message_box.warning(cast("QWidget", self), "Database", str(exc))

    def on_settings(self) -> None:
        """Open the settings editor for this app's `config.json` keys."""
        from harrix_swiss_knife.apps.common.settings_editor import SettingsEditorDialog  # noqa: PLC0415

        app_id = type(self).settings_app_id
        if not app_id:
            return
        dialog = SettingsEditorDialog(
            cast("QWidget", self),
            app_id=app_id,
            window_title=f"{type(self).about_app_name} settings",
        )
        apply_app_window_size_and_position(dialog)
        dialog.exec()

    def _apply_exit_about_menu_emojis(self) -> None:
        """Prefix Exit and About with emoji, then turn menu-bar prefixes into icons."""
        self.actionExit.setText(f"🚪 {self.actionExit.text()}")
        self.actionAbout.setText(f"ℹ️ {self.actionAbout.text()}")  # noqa: RUF001
        self._apply_menu_bar_emoji_icons()

    def _apply_menu_bar_emoji_icons(self) -> None:
        """Move leading emoji from File / Commands / Help action text onto icons."""
        menu_bar = resolve_window_menu_bar(cast("QWidget", self))
        if menu_bar is not None:
            apply_leading_emoji_icons(menu_bar)
        for name in ("menuFile", "menuCommands", "menuCommanda", "menuHelp"):
            menu = getattr(self, name, None)
            if isinstance(menu, QMenu):
                apply_leading_emoji_icons(menu)

    def _connect_exit_about_actions(self) -> None:
        """Wire Exit and About menu actions to their handlers."""
        self.actionExit.triggered.connect(self.on_exit)
        self.actionAbout.triggered.connect(self.on_about)
        self._setup_reveal_database_action()
        self._setup_settings_action()

    def _copy_table_selection_to_clipboard(self, table_view: QTableView) -> None:
        """Copy selected cells from `table_view` to clipboard as tab-separated text.

        Args:

        - `table_view` (`QTableView`): The table view to copy data from.

        """
        selection_model = table_view.selectionModel()
        if not selection_model or not selection_model.hasSelection():
            return

        selected_indexes = selection_model.selectedIndexes()
        if not selected_indexes:
            return

        selected_indexes.sort(key=lambda index: (index.row(), index.column()))

        rows_data: dict[int, dict[int, str]] = {}
        for index in selected_indexes:
            row = index.row()
            if row not in rows_data:
                rows_data[row] = {}

            cell_data = table_view.model().data(index, Qt.ItemDataRole.DisplayRole)
            rows_data[row][index.column()] = str(cell_data) if cell_data is not None else ""

        clipboard_text: list[str] = []
        for row in sorted(rows_data.keys()):
            row_data = rows_data[row]
            if row_data:
                min_col = min(row_data.keys())
                max_col = max(row_data.keys())
                clipboard_text.append("\t".join([row_data.get(col, "") for col in range(min_col, max_col + 1)]))

        if clipboard_text:
            final_text = "\n".join(clipboard_text)
            clipboard = QApplication.clipboard()
            if clipboard is not None:
                clipboard.setText(final_text)
                logger.info("%s", f"Copied {len(clipboard_text)} rows to clipboard")

    def _get_version_from_pyproject(self) -> str:
        """Get version from `pyproject.toml`.

        Returns:

        - `str`: Version string, or `Unknown` if it cannot be read.

        """
        try:
            pyproject_path = h.dev.get_project_root() / "pyproject.toml"
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)
            return data.get("project", {}).get("version", "Unknown")
        except Exception:
            logger.exception("⚠️ Warning: Could not read version from pyproject.toml")
            return "Unknown"

    def _handle_ctrl_c_for_tables(self, event: QKeyEvent, table_views: list[QTableView]) -> bool:
        """Copy table selection to clipboard on Ctrl+C if a table is focused.

        Args:

        - `event` (`QKeyEvent`): Key press event.
        - `table_views` (`list[QTableView]`): Candidate table views.

        Returns:

        - `bool`: `True` if the shortcut was handled, `False` otherwise.

        """
        if not (event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier):
            return False

        focused_widget = QApplication.focusWidget()
        for table_view in table_views:
            if focused_widget == table_view:
                self._copy_table_selection_to_clipboard(table_view)
                return True

        for table_view in table_views:
            if focused_widget and table_view.isAncestorOf(focused_widget):
                self._copy_table_selection_to_clipboard(table_view)
                return True

        return False

    def _hide_instead_of_close(self, event: QCloseEvent) -> bool:
        """Hide the window and return `True` when the launcher reuses this instance.

        Args:

        - `event` (`QCloseEvent`): The close event.

        Returns:

        - `bool`: `True` when the window was hidden instead of closed.

        """
        if not getattr(self, "_hide_on_close", False):
            return False
        event.ignore()
        self.hide()  # type: ignore[attr-defined]
        return True

    def _init_hide_on_close(self, *, hide_on_close: bool) -> None:
        """Remember close behavior; delete on close only when the window is not reused.

        Args:

        - `hide_on_close` (`bool`): When `True`, close hides the window for reuse.

        """
        self._hide_on_close = hide_on_close
        if not hide_on_close:
            self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)  # type: ignore[attr-defined]

    def _install_word_wrap_table_headers(
        self,
        *,
        skip: set[QTableView] | frozenset[QTableView] | None = None,
    ) -> None:
        """Enable wrapping titles on every `QTableView` in this window."""
        install_word_wrap_headers(cast("QWidget", self), skip=skip)

    def _place_menu_bar_on_tab_row(self) -> None:
        """Put the main menu on the same row as tabs (left of the tab bar).

        Moves menus from the `QMainWindow` menu bar into a bold compact
        `QMenuBar` with a vertical separator, set as the `QTabWidget`
        top-left corner widget, then collapses the original menu bar row.

        """
        apply_ui_font_scale(cast("QWidget", self))
        main_window = cast("QMainWindow", self)
        tab_widget = getattr(self, "tabWidget", None)
        if not isinstance(tab_widget, QTabWidget):
            return

        # UI files name the bar `menuBar`, which shadows `QMainWindow.menuBar()`.
        menu_bar = getattr(main_window, "menuBar", None)
        if isinstance(menu_bar, QMenuBar):
            old_bar = menu_bar
        elif callable(menu_bar):
            old_bar = menu_bar()
        else:
            return
        if old_bar is None:
            return

        corner_bar = QMenuBar()
        corner_bar.setNativeMenuBar(False)
        corner_bar.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        corner_bar.setStyleSheet(
            """
            QMenuBar {
                spacing: 0px;
                padding: 0px 2px;
                font-size: 9pt;
                font-weight: 700;
            }
            QMenuBar::item {
                padding: 2px 8px;
                margin: 0px;
                background: transparent;
            }
            """,
        )

        for action in list(old_bar.actions()):
            old_bar.removeAction(action)
            corner_bar.addAction(action)

        # Bold menu + vertical rule so it reads as chrome, not another tab.
        corner = QWidget(tab_widget)
        corner_layout = QHBoxLayout(corner)
        corner_layout.setContentsMargins(0, 0, 8, 0)
        corner_layout.setSpacing(4)
        corner_layout.addWidget(corner_bar)

        separator = QFrame(corner)
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setFixedWidth(6)
        corner_layout.addWidget(separator)

        tab_widget.setCornerWidget(corner, Qt.Corner.TopLeftCorner)

        # Keep the original bar as the QMainWindow menuBar (do not replace/delete it),
        # but collapse the reserved row.
        old_bar.hide()
        old_bar.setFixedHeight(0)

    def _prepare_layout_before_first_show(
        self,
        *layout_steps: Callable[[], None],
        standard_width: int = 1920,
    ) -> None:
        """Give the window its final size and run `layout_steps` before the first paint.

        A hidden widget reports no viewport width, so table columns sized at this
        point would use a dummy geometry and snap once the window appears.
        `WA_DontShowOnScreen` runs a real show and layout pass without mapping a
        window on screen, so every step below sees the final widths.

        Args:

        - `layout_steps` (`Callable[[], None]`): Layout calls to run off-screen,
          in order. Pending events are flushed before each one.
        - `standard_width` (`int`): Reference width used to decide between a
          maximized and a fixed layout. Defaults to `1920`.

        """
        widget = cast("QWidget", self)
        screen = widget.screen() or QApplication.primaryScreen()
        if screen is None:
            return
        available = screen.availableGeometry()
        left, top, right, bottom = window_frame_margins(widget)
        target = compute_app_window_geometry(
            available,
            standard_width=standard_width,
            frame_left=left,
            frame_top=top,
            frame_right=right,
            frame_bottom=bottom,
        )
        if target is None:
            widget.resize(
                max(1, available.width() - left - right),
                max(1, available.height() - top - bottom),
            )
        else:
            widget.setGeometry(target)
        widget.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
        try:
            widget.show()
            for step in layout_steps:
                QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
                step()
            QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
            widget.hide()
        finally:
            widget.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=False)

    def _resolve_database_path(self) -> Path | None:
        """Return the open SQLite database path when the app has one.

        Returns:

        - `Path | None`: Absolute path to the database file, or `None`.

        """
        db_manager = getattr(self, "db_manager", None)
        if db_manager is None:
            return None
        filename = getattr(db_manager, "_db_filename", None)
        if not filename:
            return None
        return Path(str(filename)).expanduser()

    def _setup_reveal_database_action(self) -> None:
        """Add File → Show database in folder for tracker apps with SQLite."""
        if not hasattr(self, "db_manager"):
            return
        menu_file = getattr(self, "menuFile", None)
        if menu_file is None:
            return
        menu = cast("QMenu", menu_file)
        action = QAction("Show database in folder", cast("QWidget", self))
        action.setObjectName("actionShowDatabaseInFolder")
        action.triggered.connect(self.on_reveal_database)
        menu.insertAction(self.actionExit, action)
        set_action_text_with_emoji_icon(action, "📂 Show database in folder")

    def _setup_settings_action(self) -> None:
        """Add File → Settings for apps that declare `settings_app_id`."""
        if not type(self).settings_app_id:
            return
        menu_file = getattr(self, "menuFile", None)
        if menu_file is None:
            return
        menu = cast("QMenu", menu_file)
        action = QAction("Settings", cast("QWidget", self))
        action.setObjectName("actionSettings")
        action.triggered.connect(self.on_settings)
        menu.insertAction(self.actionExit, action)
        set_action_text_with_emoji_icon(action, "⚙️ Settings")

    def _setup_window_size_and_position(self, *, standard_width: int = 1920) -> None:
        """Set window size and position based on screen resolution and characteristics.

        Args:

        - `standard_width` (`int`): Reference width used to decide between

        `showMaximized` and a fixed layout. Defaults to `1920`.

        """
        apply_app_window_size_and_position(cast("QWidget", self), standard_width=standard_width)

    def _show_placed_window(self, *, standard_width: int = 1920) -> None:
        """Show the window, then place or maximize it on the screen under the cursor."""
        widget = cast("QWidget", self)
        widget.show()
        apply_app_window_size_and_position(widget, standard_width=standard_width)

    def _validate_database_connection(self) -> bool:
        """Validate that database connection is available and open.

        Returns:

        - `bool`: `True` if database connection is valid, `False` otherwise.

        """
        if not getattr(self, "db_manager", None):
            logger.info("Database manager is None")
            return False

        if not self.db_manager.is_database_open():
            logger.warning("Database connection is not open")
            return False

        return True
```

</details>

### ⚙️ Method `on_about`

```python
def on_about(self) -> None
```

Show the About dialog with app information.

<details>
<summary>Code:</summary>

```python
def on_about(self) -> None:
        version = self._get_version_from_pyproject()
        description = type(self).about_description
        github_url = "https://github.com/harrix/harrix-swiss-knife"
        lines = [
            type(self).about_app_name,
            "",
            f"Version: {version}",
            "",
        ]
        if description:
            lines.extend([description, ""])
        lines.extend(
            [
                "Part of Harrix Swiss Knife.",
                "",
                "Author: Anton Sergienko (Harrix)",
                "License: MIT License",
                f"GitHub: {github_url}",
            ],
        )
        plain_text = "\n".join(lines)
        html_text = "<br>".join([*lines[:-1], f'GitHub: <a href="{github_url}">{github_url}</a>'])
        message_box.information(
            cast("QWidget", self),
            "About",
            html_text,
            rich_text=True,
            clipboard_text=plain_text,
        )
```

</details>

### ⚙️ Method `on_exit`

```python
def on_exit(self) -> None
```

Close the application window.

<details>
<summary>Code:</summary>

```python
def on_exit(self) -> None:
        self.close()  # type: ignore[attr-defined]
```

</details>

### ⚙️ Method `on_reveal_database`

```python
def on_reveal_database(self) -> None
```

Open the system file manager with this app's SQLite database selected.

<details>
<summary>Code:</summary>

```python
def on_reveal_database(self) -> None:
        db_path = self._resolve_database_path()
        if db_path is None:
            message_box.warning(
                cast("QWidget", self),
                "Database",
                "Database path is not available.",
            )
            return
        if not db_path.is_file():
            message_box.warning(
                cast("QWidget", self),
                "Database",
                f"Database file was not found:\n{db_path}",
            )
            return
        try:
            reveal_in_file_explorer(db_path)
        except (FileNotFoundError, OSError) as exc:
            message_box.warning(cast("QWidget", self), "Database", str(exc))
```

</details>

### ⚙️ Method `on_settings`

```python
def on_settings(self) -> None
```

Open the settings editor for this app's `config.json` keys.

<details>
<summary>Code:</summary>

```python
def on_settings(self) -> None:
        from harrix_swiss_knife.apps.common.settings_editor import SettingsEditorDialog  # noqa: PLC0415

        app_id = type(self).settings_app_id
        if not app_id:
            return
        dialog = SettingsEditorDialog(
            cast("QWidget", self),
            app_id=app_id,
            window_title=f"{type(self).about_app_name} settings",
        )
        apply_app_window_size_and_position(dialog)
        dialog.exec()
```

</details>

## 🔧 Function `apply_app_window_size_and_position`

```python
def apply_app_window_size_and_position(widget: QWidget, *, standard_width: int = 1920) -> None
```

Set widget size and position like food/finance/habits main Windows.

On a standard-aspect work area, maximize. On ultrawide screens, fit a
`standard_width` window into the available geometry and center it
horizontally. Uses the screen under the cursor so a scaled or secondary
display does not pin the window to the left.

`showMaximized()` on a hidden window often opens as a normal window on the
primary monitor. Pin a normal-sized client rect onto the target screen
first (inside the work area, with room for the title bar), then maximize
after the native window is mapped. Do not pin the client to the full work
area: that pushes the frame under the taskbar until maximize runs.

A `WindowStateChange` filter still corrects Restore if Windows remembers a
bad normal geometry from an older pin.

<details>
<summary>Code:</summary>

```python
def apply_app_window_size_and_position(widget: QWidget, *, standard_width: int = 1920) -> None:
    _install_restore_from_maximize_filter(widget, standard_width=standard_width)
    screen = QGuiApplication.screenAt(QCursor.pos()) or widget.screen() or QApplication.primaryScreen()
    if screen is None:
        return
    if isinstance(screen, QScreen):
        widget.setScreen(screen)
    available = screen.availableGeometry()
    left, top, right, bottom = window_frame_margins(widget)
    target = compute_app_window_geometry(
        available,
        standard_width=standard_width,
        frame_left=left,
        frame_top=top,
        frame_right=right,
        frame_bottom=bottom,
    )
    if target is None:
        # Map HWND to the cursor screen with a frame-safe normal size, then maximize.
        widget.setWindowState(widget.windowState() & ~Qt.WindowState.WindowMaximized)
        widget.setGeometry(
            compute_maximize_pin_geometry(
                available,
                standard_width=standard_width,
                frame_left=left,
                frame_top=top,
                frame_right=right,
                frame_bottom=bottom,
            ),
        )
        if widget.isVisible():
            QTimer.singleShot(0, lambda w=widget: _maximize_when_mapped(w))
        else:
            _install_maximize_on_first_show(widget)
        return
    widget.setWindowState(widget.windowState() & ~Qt.WindowState.WindowMaximized)
    widget.setGeometry(target)
```

</details>

## 🔧 Function `apply_restored_app_window_geometry`

```python
def apply_restored_app_window_geometry(widget: QWidget, *, standard_width: int = 1920) -> None
```

Place a restored window so its title bar stays inside the work area.

<details>
<summary>Code:</summary>

```python
def apply_restored_app_window_geometry(widget: QWidget, *, standard_width: int = 1920) -> None:
    available = _widget_work_area(widget)
    if available.width() <= 0 or available.height() <= 0:
        return
    left, top, right, bottom = window_frame_margins(widget)
    widget.setGeometry(
        compute_restore_window_geometry(
            available,
            standard_width=standard_width,
            frame_left=left,
            frame_top=top,
            frame_right=right,
            frame_bottom=bottom,
        ),
    )
```

</details>

## 🔧 Function `compute_app_window_geometry`

```python
def compute_app_window_geometry(available: QRect, *, standard_width: int = 1920, frame_left: int = 0, frame_top: int = 0, frame_right: int = 0, frame_bottom: int = 0) -> QRect | None
```

Return a centered client rect, or `None` when the window should maximize.

`setGeometry` is the client area, so `frame_*` must reserve the title bar
and borders. Otherwise the caption buttons sit above the work area.

Args:

- `available` (`QRect`): Work area of the target screen (excludes the taskbar).
- `standard_width` (`int`): Preferred window width on ultrawide screens.
  Defaults to `1920`.
- `frame_left` / `frame_top` / `frame_right` / `frame_bottom` (`int`):
  Window-frame extents in logical pixels.

Returns:

- `QRect | None`: Client geometry in global logical coordinates, or `None`
  to maximize.

<details>
<summary>Code:</summary>

```python
def compute_app_window_geometry(
    available: QRect,
    *,
    standard_width: int = 1920,
    frame_left: int = 0,
    frame_top: int = 0,
    frame_right: int = 0,
    frame_bottom: int = 0,
) -> QRect | None:
    if available.width() <= 0 or available.height() <= 0:
        return None

    aspect_ratio = available.width() / available.height()
    # Standard / near-standard screens (incl. scaled 1080p under 1920 logical px)
    # open maximized so the frame fills the work area without side gaps.
    if aspect_ratio <= _STANDARD_ASPECT_RATIO:
        return None

    inner_width = max(1, available.width() - max(0, frame_left) - max(0, frame_right))
    inner_height = max(1, available.height() - max(0, frame_top) - max(0, frame_bottom))
    window_width = min(standard_width, inner_width)
    x = available.x() + max(0, frame_left) + (inner_width - window_width) // 2
    y = available.y() + max(0, frame_top)
    return QRect(x, y, window_width, inner_height)
```

</details>

## 🔧 Function `compute_maximize_pin_geometry`

```python
def compute_maximize_pin_geometry(available: QRect, *, standard_width: int = 1920, frame_left: int = 0, frame_top: int = 0, frame_right: int = 0, frame_bottom: int = 0) -> QRect
```

Return a frame-safe client rect used to map the HWND before maximize.

The pin must stay inside the work area. Using the full work area as the
client rectangle makes the title bar and bottom border spill outside
(including under the taskbar) until `showMaximized` runs.

Args:

- `available` (`QRect`): Work area of the target screen (excludes the taskbar).
- `standard_width` (`int`): Preferred width used when deriving the pin.
  Defaults to `1920`.
- `frame_left` / `frame_top` / `frame_right` / `frame_bottom` (`int`):
  Window-frame extents in logical pixels.

Returns:

- `QRect`: Client geometry in global logical coordinates.

<details>
<summary>Code:</summary>

```python
def compute_maximize_pin_geometry(
    available: QRect,
    *,
    standard_width: int = 1920,
    frame_left: int = 0,
    frame_top: int = 0,
    frame_right: int = 0,
    frame_bottom: int = 0,
) -> QRect:
    return compute_restore_window_geometry(
        available,
        standard_width=standard_width,
        frame_left=frame_left,
        frame_top=frame_top,
        frame_right=frame_right,
        frame_bottom=frame_bottom,
    )
```

</details>

## 🔧 Function `compute_restore_window_geometry`

```python
def compute_restore_window_geometry(available: QRect, *, standard_width: int = 1920, frame_left: int = 0, frame_top: int = 0, frame_right: int = 0, frame_bottom: int = 0) -> QRect
```

Return a client rect that keeps the window frame inside the work area.

On screens that open maximized, restore still needs a normal size: the
inner work area after reserving the title bar and borders.

Args:

- `available` (`QRect`): Work area of the target screen (excludes the taskbar).
- `standard_width` (`int`): Preferred window width used on ultrawide screens.
  Defaults to `1920`.
- `frame_left` / `frame_top` / `frame_right` / `frame_bottom` (`int`):
  Window-frame extents in logical pixels.

Returns:

- `QRect`: Client geometry in global logical coordinates.

<details>
<summary>Code:</summary>

```python
def compute_restore_window_geometry(
    available: QRect,
    *,
    standard_width: int = 1920,
    frame_left: int = 0,
    frame_top: int = 0,
    frame_right: int = 0,
    frame_bottom: int = 0,
) -> QRect:
    target = compute_app_window_geometry(
        available,
        standard_width=standard_width,
        frame_left=frame_left,
        frame_top=frame_top,
        frame_right=frame_right,
        frame_bottom=frame_bottom,
    )
    if target is not None:
        return target
    inner_width = max(1, available.width() - max(0, frame_left) - max(0, frame_right))
    inner_height = max(1, available.height() - max(0, frame_top) - max(0, frame_bottom))
    return QRect(
        available.x() + max(0, frame_left),
        available.y() + max(0, frame_top),
        inner_width,
        inner_height,
    )
```

</details>

## 🔧 Function `inset_restore_frame_rect`

```python
def inset_restore_frame_rect(left: int, top: int, right: int, bottom: int, *, frame_x: int, title: int, frame_y: int) -> tuple[int, int, int, int] | None
```

Inset a Win32 restore frame so the caption stays inside the work area.

Args:

- `left` / `top` / `right` / `bottom` (`int`): Current restore frame
  (`WINDOWPLACEMENT.rcNormalPosition`).
- `frame_x` (`int`): Left/right border thickness in native pixels.
- `title` (`int`): Title-bar height in native pixels.
- `frame_y` (`int`): Bottom border thickness in native pixels.

Returns:

- `tuple[int, int, int, int] | None`: Inset `(left, top, right, bottom)`,
  or `None` when the rect is too small to inset.

<details>
<summary>Code:</summary>

```python
def inset_restore_frame_rect(
    left: int,
    top: int,
    right: int,
    bottom: int,
    *,
    frame_x: int,
    title: int,
    frame_y: int,
) -> tuple[int, int, int, int] | None:
    if right - left <= frame_x * 2 or bottom - top <= title + frame_y:
        return None
    return (left + frame_x, top + title, right - frame_x, bottom - frame_y)
```

</details>

## 🔧 Function `resolve_window_menu_bar`

```python
def resolve_window_menu_bar(window: QWidget) -> QMenuBar | None
```

Return the visible app menu bar, including the tab-row corner bar.

Generated UI files assign `self.menuBar` to a `QMenuBar`, which shadows
`QMainWindow.menuBar()`.

<details>
<summary>Code:</summary>

```python
def resolve_window_menu_bar(window: QWidget) -> QMenuBar | None:
    tab_widget = getattr(window, "tabWidget", None)
    if isinstance(tab_widget, QTabWidget):
        corner = tab_widget.cornerWidget(Qt.Corner.TopLeftCorner)
        if corner is not None:
            children = corner.findChildren(QMenuBar)
            if children:
                return children[0]
    menu_bar = getattr(window, "menuBar", None)
    if isinstance(menu_bar, QMenuBar):
        return menu_bar
    if callable(menu_bar):
        resolved = menu_bar()
        if isinstance(resolved, QMenuBar):
            return resolved
    return None
```

</details>

## 🔧 Function `window_frame_escapes_work_area`

```python
def window_frame_escapes_work_area(frame: QRect, available: QRect) -> bool
```

Return whether the title bar has moved above or left of the work area.

A few pixels of DWM shadow around a correctly placed window are ignored.

Args:

- `frame` (`QRect`): Outer window rectangle including the title bar.
- `available` (`QRect`): Work area of the target screen (excludes the taskbar).

Returns:

- `bool`: `True` when Restore would hide the caption buttons.

<details>
<summary>Code:</summary>

```python
def window_frame_escapes_work_area(frame: QRect, available: QRect) -> bool:
    if available.width() <= 0 or available.height() <= 0:
        return False
    return frame.top() < available.top() - _RESTORE_SNAP_SLACK or frame.left() < available.left() - _RESTORE_SNAP_SLACK
```

</details>

## 🔧 Function `window_frame_margins`

```python
def window_frame_margins(widget: QWidget) -> tuple[int, int, int, int]
```

Return `(left, top, right, bottom)` window-frame extents in logical pixels.

Uses the realized frame when the caption is already laid out. Otherwise
estimates from the widget style so an unshown window still leaves room
for Close / Maximize.

<details>
<summary>Code:</summary>

```python
def window_frame_margins(widget: QWidget) -> tuple[int, int, int, int]:
    flags = widget.windowFlags()
    if flags & Qt.WindowType.FramelessWindowHint:
        return (0, 0, 0, 0)

    if not (widget.windowState() & Qt.WindowState.WindowMaximized):
        frame = widget.frameGeometry()
        client = widget.geometry()
        left = client.x() - frame.x()
        top = client.y() - frame.y()
        right = frame.right() - client.right()
        bottom = frame.bottom() - client.bottom()
        if top > 0:
            return (max(0, left), top, max(0, right), max(0, bottom))

    style = widget.style()
    title = style.pixelMetric(QStyle.PixelMetric.PM_TitleBarHeight, widget=widget)
    border = style.pixelMetric(QStyle.PixelMetric.PM_DefaultFrameWidth, widget=widget)
    if title <= 0:
        title = _FALLBACK_TITLE_BAR_HEIGHT
    border = max(border, 0)
    return (border, title, border, border)
```

</details>
