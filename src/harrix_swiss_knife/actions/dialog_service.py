"""Dialog service used by actions.

This module extracts dialog-related responsibilities from `ActionBase`.
It provides a single place for common Qt dialogs and shared geometry policy.
"""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QSize, Qt, QTimer
from PySide6.QtGui import QFont, QGuiApplication, QIcon, QPainter, QShowEvent, QTextDocument
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common import message_box

if TYPE_CHECKING:
    from collections.abc import Callable


class ActionDialogService:
    """Dialog builder/service for `ActionBase`-like actions."""

    def __init__(
        self,
        *,
        default_size: QSize,
        add_line: Callable[[str], None],
        show_toast: Callable[[str], None],
        create_emoji_icon: Callable[[str, int], QIcon],
    ) -> None:
        """Create service with UI callbacks injected from `ActionBase`."""
        self._default_size = default_size
        self._add_line = add_line
        self._show_toast = show_toast
        self._create_emoji_icon = create_emoji_icon

    def create_emoji_icon(self, emoji: str, size: int = 64) -> QIcon:
        """Create icon via injected icon factory (kept for convenience)."""
        return self._create_emoji_icon(emoji, size)

    def get_checkbox_selection(
        self,
        title: str,
        label: str,
        choices: list[str],
        default_selected: list[str] | None = None,
        *,
        enable_extension_filter: bool = False,
    ) -> list[str] | None:
        """Return checkbox-selected items, or None on cancel."""
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self._default_size, parent)
        dialog.setWindowTitle(title)

        layout = QVBoxLayout()

        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMinimumHeight(self._default_size.height() - 200)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        checkboxes_container = QWidget()
        checkboxes_layout = QVBoxLayout(checkboxes_container)

        checkboxes: list[QCheckBox] = []
        for choice in choices:
            checkbox = QCheckBox(choice)
            font = checkbox.font()
            font.setPointSize(11)
            checkbox.setFont(font)

            if default_selected and choice in default_selected:
                checkbox.setChecked(True)

            checkboxes.append(checkbox)
            checkboxes_layout.addWidget(checkbox)

        checkboxes_layout.addStretch()

        scroll_area.setWidget(checkboxes_container)
        layout.addWidget(scroll_area)

        selection_buttons_layout = QHBoxLayout()

        select_all_button = QPushButton("✅ Select All")
        deselect_all_button = QPushButton("❌ Deselect All")
        extension_filter_button = QPushButton("🧩 Select by extension…")
        extension_filter_button.setVisible(enable_extension_filter)

        def select_all() -> None:
            for checkbox in checkboxes:
                checkbox.setChecked(True)

        def deselect_all() -> None:
            for checkbox in checkboxes:
                checkbox.setChecked(False)

        def _extension_key_for_choice(choice: str) -> str:
            return Path(choice).suffix.lower()

        def _build_extension_stats() -> tuple[list[str], dict[str, int]]:
            counts: dict[str, int] = {}
            for choice in choices:
                ext = _extension_key_for_choice(choice)
                counts[ext] = counts.get(ext, 0) + 1

            sorted_exts = sorted(counts.keys(), key=lambda ext: (-(counts[ext]), ext))
            return sorted_exts, counts

        def select_by_extension() -> None:
            sorted_exts, counts = _build_extension_stats()
            if not sorted_exts:
                return

            ext_dialog = _StandardActionDialog(self._default_size, dialog)
            ext_dialog.setWindowTitle("Select extensions")

            ext_layout = QVBoxLayout()
            ext_label = QLabel("Choose extension states: checked = select all, unchecked = deselect all, mixed = keep.")
            ext_layout.addWidget(ext_label)

            ext_scroll_area = QScrollArea()
            ext_scroll_area.setWidgetResizable(True)
            ext_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            ext_scroll_area.setMinimumHeight(self._default_size.height() - 200)
            ext_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            ext_container = QWidget()
            ext_container_layout = QVBoxLayout(ext_container)

            ext_checkboxes: dict[str, QCheckBox] = {}
            for ext in sorted_exts:
                total = counts[ext]
                checked_count = sum(
                    1
                    for checkbox in checkboxes
                    if _extension_key_for_choice(checkbox.text()) == ext and checkbox.isChecked()
                )
                if checked_count == 0:
                    state = Qt.CheckState.Unchecked
                elif checked_count == total:
                    state = Qt.CheckState.Checked
                else:
                    state = Qt.CheckState.PartiallyChecked

                ext_name = ext or "(no extension)"
                ext_checkbox = QCheckBox(f"{ext_name} ({total})")
                ext_checkbox.setTristate(True)
                ext_checkbox.setCheckState(state)
                ext_checkboxes[ext] = ext_checkbox
                ext_container_layout.addWidget(ext_checkbox)

            ext_container_layout.addStretch()
            ext_scroll_area.setWidget(ext_container)
            ext_layout.addWidget(ext_scroll_area)

            ext_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            ext_buttons.accepted.connect(ext_dialog.accept)
            ext_buttons.rejected.connect(ext_dialog.reject)
            ext_layout.addWidget(ext_buttons)
            ext_dialog.setLayout(ext_layout)
            self._finalize_standard_dialog_geometry(ext_dialog, ext_layout, stretch_row=1)

            if ext_dialog.exec() != QDialog.DialogCode.Accepted:
                return

            for ext, ext_checkbox in ext_checkboxes.items():
                state = ext_checkbox.checkState()
                if state == Qt.CheckState.PartiallyChecked:
                    continue
                target_checked = state == Qt.CheckState.Checked
                for checkbox in checkboxes:
                    if _extension_key_for_choice(checkbox.text()) == ext:
                        checkbox.setChecked(target_checked)

        select_all_button.clicked.connect(select_all)
        deselect_all_button.clicked.connect(deselect_all)
        extension_filter_button.clicked.connect(select_by_extension)

        selection_buttons_layout.addWidget(select_all_button)
        selection_buttons_layout.addWidget(deselect_all_button)
        selection_buttons_layout.addWidget(extension_filter_button)
        selection_buttons_layout.addStretch()

        layout.addLayout(selection_buttons_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            selected_choices = [checkbox.text() for checkbox in checkboxes if checkbox.isChecked()]
            if not selected_choices:
                self._add_line("❌ No items were selected.")
                return None
            return selected_choices

        self._add_line("❌ Dialog was canceled.")
        return None

    def get_choice_from_icons(
        self,
        title: str,
        label: str,
        choices: list[tuple[str, str]],
        icon_size: int = 64,
    ) -> str | None:
        """Return selected choice title from icon grid, or None on cancel."""
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        list_widget: QListWidget | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal list_widget

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            lw = QListWidget()
            lw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            lw.setMinimumHeight(self._default_size.height() - 160)
            lw.setViewMode(QListWidget.ViewMode.IconMode)
            lw.setResizeMode(QListWidget.ResizeMode.Adjust)
            lw.setMovement(QListWidget.Movement.Static)
            lw.setSpacing(16)
            lw.setIconSize(QSize(icon_size, icon_size))
            lw.setWordWrap(True)
            lw.setUniformItemSizes(False)
            lw.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

            for icon_emoji, choice_title in choices:
                item = QListWidgetItem(choice_title, lw)
                item.setData(Qt.ItemDataRole.UserRole, choice_title)
                item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

                icon = self._create_emoji_icon(icon_emoji, icon_size)
                item.setIcon(icon)

            if lw.count() > 0:
                lw.setCurrentRow(0)

            lw.itemDoubleClicked.connect(dialog.accept)
            layout.addWidget(lw)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            list_widget = lw

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if list_widget is None:
                self._add_line("❌ No item was selected.")
                return None
            current_item = list_widget.currentItem()
            if current_item:
                return current_item.data(Qt.ItemDataRole.UserRole)
            self._add_line("❌ No item was selected.")
            return None

        self._add_line("❌ Dialog was canceled.")
        return None

    def get_choice_from_list(self, title: str, label: str, choices: list[str]) -> str | None:
        """Return selected item from list, or None on cancel."""
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        list_widget: QListWidget | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal list_widget

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            lw = QListWidget()
            lw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            lw.setMinimumHeight(self._default_size.height() - 160)

            font = lw.font()
            font.setPointSize(12)
            lw.setFont(font)

            for choice in choices:
                lw.addItem(QListWidgetItem(choice))

            if lw.count() > 0:
                lw.setCurrentRow(0)

            lw.itemDoubleClicked.connect(dialog.accept)
            layout.addWidget(lw)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            list_widget = lw

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if list_widget is None:
                self._add_line("❌ No item was selected.")
                return None
            current_item = list_widget.currentItem()
            if current_item:
                return current_item.text()
            self._add_line("❌ No item was selected.")
            return None

        self._add_line("❌ Dialog was canceled.")
        return None

    def get_choice_from_list_with_descriptions(
        self,
        title: str,
        label: str,
        choices: list[tuple[str, str]],
    ) -> str | None:
        """Return selected item from list with descriptions, or None on cancel."""
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        list_widget: QListWidget | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal list_widget

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            lw = QListWidget()
            lw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            lw.setMinimumHeight(self._default_size.height() - 160)

            delegate = ChoiceWithDescriptionDelegate()
            lw.setItemDelegate(delegate)

            for choice, description in choices:
                formatted_description = description.replace("\n", "\n  ")
                item_text = f"{choice}\n  {formatted_description}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, choice)
                lw.addItem(item)

            if lw.count() > 0:
                lw.setCurrentRow(0)

            lw.itemDoubleClicked.connect(dialog.accept)
            layout.addWidget(lw)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            list_widget = lw

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if list_widget is None:
                self._add_line("❌ No item was selected.")
                return None
            current_item = list_widget.currentItem()
            if current_item:
                return current_item.data(Qt.ItemDataRole.UserRole)
            self._add_line("❌ No item was selected.")
            return None

        self._add_line("❌ Dialog was canceled.")
        return None

    def get_existing_directory(self, title: str, default_path: str) -> Path | None:
        """Return selected directory path, or None if cancelled."""
        folder_path = QFileDialog.getExistingDirectory(None, title, default_path)
        if not folder_path:
            self._add_line("❌ Folder was not selected.")
            return None
        return Path(folder_path)

    def get_folder_with_choice_option(self, folders_list: list[str], default_path: str) -> Path | None:
        """Pick folder from list or browse for directory."""
        select_folder = "📁 Select folder …"
        display_folders = [f"📁 {folder}" for folder in folders_list]
        full_list = [select_folder, *display_folders]

        selected_folder = self.get_choice_from_list(select_folder, "Folders", full_list)
        if not selected_folder:
            return None

        if selected_folder == select_folder:
            return self.get_existing_directory(select_folder, default_path)

        clean_folder_path = selected_folder.replace("📁 ", "", 1)
        return Path(clean_folder_path)

    def get_open_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        """Return selected filename, or None if cancelled."""
        filename, _ = QFileDialog.getOpenFileName(None, title, default_path, filter_)
        if not filename:
            self._add_line("❌ No file was selected.")
            return None
        return Path(filename)

    def get_open_filenames(self, title: str, default_path: str, filter_: str) -> list[Path] | None:
        """Return selected filenames, or None if cancelled."""
        dialog = DragDropFileDialog(title, default_path, filter_, self._default_size)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            filenames = dialog.get_selected_files()
            if not filenames:
                self._add_line("❌ No files were selected.")
                return None
            return [Path(filename) for filename in filenames]
        self._add_line("❌ No files were selected.")
        return None

    def get_open_filenames_with_resize(
        self,
        title: str,
        default_path: str,
        filter_: str,
    ) -> tuple[list[Path] | None, bool, str | None]:
        """Return filenames plus resize options, or (None, False, None) if cancelled."""
        dialog = DragDropFileDialog(title, default_path, filter_, self._default_size, with_resize_option=True)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            filenames = dialog.get_selected_files()
            if not filenames:
                self._add_line("❌ No files were selected.")
                return None, False, None
            paths = [Path(f) for f in filenames]
            resize_enabled = dialog.get_resize_enabled()
            max_size = dialog.get_max_size()
            return paths, resize_enabled, max_size
        self._add_line("❌ No files were selected.")
        return None, False, None

    def get_save_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        """Return save target filename, or None if cancelled."""
        filename, _ = QFileDialog.getSaveFileName(None, title, default_path, filter_)
        if not filename:
            self._add_line("❌ No file was selected.")
            return None
        return Path(filename)

    def get_text_input(self, title: str, label: str, default_value: str | None = None) -> str | None:
        """Return entered text, or None on cancel/empty."""
        text, ok = QInputDialog.getText(None, title, label, text=default_value or "")
        if not (ok and text):
            self._add_line("❌ Text was not entered.")
            return None
        return text

    def get_text_input_with_auto(
        self,
        title: str,
        label: str,
        auto_generator: Callable[[], str] | None = None,
        auto_button_text: str = "🤖 Auto",
    ) -> str | None:
        """Return text input, optionally generated by callback, or None on cancel/empty."""
        if auto_generator is None:
            return self.get_text_input(title, label)

        line_edit: QLineEdit | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal line_edit

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            input_layout = QHBoxLayout()

            le = QLineEdit()
            le.setMinimumHeight(32)
            input_layout.addWidget(le)

            auto_button = QPushButton(auto_button_text)

            def on_auto_clicked() -> None:
                try:
                    auto_text = auto_generator()
                    le.setText(auto_text)
                except Exception as e:
                    self._add_line(f"❌ Error generating auto text: {e}")

            auto_button.clicked.connect(on_auto_clicked)
            input_layout.addWidget(auto_button)

            layout.addLayout(input_layout)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            line_edit = le

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if line_edit is None:
                self._add_line("❌ Text was not entered.")
                return None
            text = line_edit.text().strip()
            if not text:
                self._add_line("❌ Text was not entered.")
                return None
            return text

        self._add_line("❌ Dialog was canceled.")
        return None

    def get_text_textarea(self, title: str, label: str, default_text: str | None = None) -> str | None:
        """Return multi-line text, or None on cancel/empty."""
        text_edit: QPlainTextEdit | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal text_edit

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            te = QPlainTextEdit()
            te.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            te.setMinimumHeight(self._default_size.height() - 160)
            if default_text is not None:
                te.setPlainText(default_text)
            layout.addWidget(te)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            text_edit = te

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if text_edit is None:
                self._add_line("❌ Text was not entered.")
                return None
            text = text_edit.toPlainText()
            if not text.strip():
                self._add_line("❌ Text was not entered.")
                return None
            return text
        self._add_line("❌ Dialog was canceled.")
        return None

    def get_yes_no_question(self, title: str, message: str) -> bool:
        """Return True for Yes, False otherwise."""
        reply = message_box.question(
            None,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def show_about_dialog(
        self,
        *,
        title: str = "About",
        app_name: str = "Harrix Swiss Knife",
        version: str = "1.0.0",
        description: str = "",
        author: str = "",
        license_text: str = "",
        github: str = "",
    ) -> str | None:
        """Show about dialog and return rendered text if accepted."""
        about_text = f"# {app_name}\n\n"

        if version:
            about_text += f"Version: {version}\n\n"
        if description:
            about_text += f"{description}\n\n"
        if author:
            about_text += f"Author: {author}\n\n"
        if license_text:
            about_text += f"License: {license_text}\n\n"
        if github:
            about_text += f"GitHub: <{github}>\n\n"

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            text_browser = QTextBrowser()
            text_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            text_browser.setMinimumHeight(self._default_size.height() - 160)
            text_browser.setMarkdown(about_text)
            text_browser.setOpenExternalLinks(True)

            font = QFont("JetBrains Mono", 10)
            text_browser.setFont(font)

            layout.addWidget(text_browser)

            button_layout = QHBoxLayout()
            copy_button = QPushButton("Copy to Clipboard")

            def click_copy_button() -> None:
                QGuiApplication.clipboard().setText(about_text)
                self._show_toast("About information copied to Clipboard")

            copy_button.clicked.connect(click_copy_button)
            button_layout.addWidget(copy_button)

            ok_button = QPushButton("OK")
            ok_button.clicked.connect(dialog.accept)
            button_layout.addWidget(ok_button)

            layout.addLayout(button_layout)

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=0)
        return about_text if result == QDialog.DialogCode.Accepted else None

    def show_action_output_log_browser(
        self,
        entries: list[tuple[Path, str]],
        *,
        on_file_selected: Callable[[Path], None] | None = None,
    ) -> None:
        """Show a split view: log file list (left) and UTF-8 preview (right).

        ``entries`` are ``(path, description)`` pairs; ``description`` is shown under the file name.
        ``on_file_selected`` is invoked whenever the list selection changes (before loading preview text).
        """
        if not entries:
            self._add_line("❌ No log files to browse.")
            return

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            splitter = QSplitter(Qt.Orientation.Horizontal)

            list_widget = QListWidget()
            list_widget.setMinimumWidth(280)
            list_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
            list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            list_widget.setItemDelegate(ChoiceWithDescriptionDelegate())

            for path, description in entries:
                formatted_description = description.replace("\n", "\n  ")
                item_text = f"{path.name}\n  {formatted_description}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, str(path.resolve()))
                list_widget.addItem(item)

            preview = QPlainTextEdit()
            preview.setReadOnly(True)
            preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            preview_font = QFont("JetBrains Mono")
            preview_font.setPointSize(9)
            preview.setFont(preview_font)

            def load_preview(current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
                if current is None:
                    preview.setPlainText("")
                    return
                raw = current.data(Qt.ItemDataRole.UserRole)
                if not raw:
                    preview.setPlainText("")
                    return
                path_obj = Path(str(raw))
                if on_file_selected is not None:
                    on_file_selected(path_obj)
                try:
                    preview.setPlainText(path_obj.read_text(encoding="utf8"))
                except UnicodeDecodeError as e:
                    preview.setPlainText(f"(Could not decode file as UTF-8: {e})")
                except OSError as e:
                    preview.setPlainText(f"(Could not read file: {e})")

            list_widget.currentItemChanged.connect(load_preview)

            splitter.addWidget(list_widget)
            splitter.addWidget(preview)
            splitter.setSizes([320, 704])

            layout.addWidget(splitter)

            button_layout = QHBoxLayout()
            copy_button = QPushButton("Copy to Clipboard")

            def click_copy_button() -> None:
                QGuiApplication.clipboard().setText(preview.toPlainText())
                self._show_toast("Copied to Clipboard")

            copy_button.clicked.connect(click_copy_button)
            button_layout.addWidget(copy_button)
            button_layout.addStretch()

            close_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
            close_box.rejected.connect(dialog.reject)
            button_layout.addWidget(close_box)

            layout.addLayout(button_layout)

            if list_widget.count() > 0:
                list_widget.setCurrentRow(0)

        self._exec_standard_dialog("Recent action logs", _build, stretch_row=0)

    def show_instructions(self, instructions: str, title: str = "Instructions") -> str | None:
        """Show instructions dialog and return text if accepted."""

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            text_browser = QTextBrowser()
            text_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            text_browser.setMinimumHeight(self._default_size.height() - 160)
            text_browser.setPlainText(instructions)

            font = QFont("JetBrains Mono", 10)
            text_browser.setFont(font)

            layout.addWidget(text_browser)

            button_layout = QHBoxLayout()
            copy_button = QPushButton("Copy to Clipboard")

            def click_copy_button() -> None:
                QGuiApplication.clipboard().setText(instructions)
                self._show_toast("Instructions copied to Clipboard")

            copy_button.clicked.connect(click_copy_button)
            button_layout.addWidget(copy_button)

            ok_button = QPushButton("OK")
            ok_button.clicked.connect(dialog.accept)
            button_layout.addWidget(ok_button)

            layout.addLayout(button_layout)

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=0)
        return instructions if result == QDialog.DialogCode.Accepted else None

    def show_text_multiline(self, text: str, title: str = "Result") -> str | None:
        """Show read-only multi-line text dialog and return text if accepted."""

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            text_edit = QPlainTextEdit()
            text_edit.setPlainText(text)
            text_edit.setReadOnly(True)
            text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            text_edit.setMinimumHeight(self._default_size.height() - 120)

            font = QFont("JetBrains Mono")
            font.setPointSize(9)
            text_edit.setFont(font)

            layout.addWidget(text_edit)

            button_layout = QHBoxLayout()
            copy_button = QPushButton("Copy to Clipboard")

            def click_copy_button() -> None:
                QGuiApplication.clipboard().setText(text_edit.toPlainText())
                self._show_toast("Copied to Clipboard")

            copy_button.clicked.connect(click_copy_button)
            button_layout.addWidget(copy_button)

            ok_button = QPushButton("OK")
            ok_button.clicked.connect(dialog.accept)
            button_layout.addWidget(ok_button)

            layout.addLayout(button_layout)

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=0)
        return text if result == QDialog.DialogCode.Accepted else None

    def _exec_standard_dialog(
        self,
        title: str,
        build: Callable[[QDialog, QVBoxLayout], None],
        *,
        parent: QWidget | None = None,
        stretch_row: int | None = 1,
    ) -> tuple[int, QDialog]:
        """Create, size, and execute a standard action dialog."""
        dialog_parent = QApplication.activeWindow() if parent is None else parent
        dialog = _StandardActionDialog(self._default_size, dialog_parent)
        dialog.setWindowTitle(title)

        layout = QVBoxLayout()
        build(dialog, layout)

        dialog.setLayout(layout)
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=stretch_row)
        result = dialog.exec()
        return result, dialog

    def _finalize_standard_dialog_geometry(
        self,
        dialog: QDialog,
        layout: QVBoxLayout,
        *,
        stretch_row: int | None = 1,
    ) -> None:
        """Apply default dialog sizing and optional stretch row."""
        target = self._default_size
        if stretch_row is not None:
            layout.setStretch(stretch_row, 1)
        dialog.setMinimumSize(target)
        dialog.resize(target)

        def _enforce() -> None:
            dialog.setMinimumSize(target)
            dialog.resize(target)

        QTimer.singleShot(0, _enforce)


class ChoiceWithDescriptionDelegate(QStyledItemDelegate):
    """Custom delegate for displaying choices with descriptions in different font sizes."""

    MIN_LINES_FOR_DESCRIPTION = 2

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Render choice title + description with rich text."""
        painter.save()

        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text:
            painter.restore()
            return

        lines = text.split("\n")
        if len(lines) < self.MIN_LINES_FOR_DESCRIPTION:
            super().paint(painter, option, index)
            painter.restore()
            return

        choice = lines[0]
        description = "\n".join(lines[1:]).strip()

        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = option.state & QStyle.StateFlag.State_MouseOver

        if is_selected:
            painter.fillRect(option.rect, option.palette.highlight())
            text_color = option.palette.highlightedText().color()
        elif is_hovered:
            painter.fillRect(option.rect, option.palette.alternateBase())
            text_color = option.palette.text().color()
        else:
            text_color = option.palette.text().color()

        # Escape HTML and preserve line breaks
        escaped_choice = escape(choice)
        escaped_description = escape(description).replace("\n", "<br>")

        html_content = (
            f'<div style="font-family: Arial, sans-serif; color: {text_color.name()};">'
            f'<div style="font-size: 12pt; font-weight: bold; margin-bottom: 2px;">'
            f"{escaped_choice}"
            f"</div>"
            f'<div style="font-size: 9pt; font-style: italic; color: {text_color.name()}; '
            f'opacity: 0.7; margin-left: 10px; white-space: pre-wrap;">'
            f"{escaped_description}"
            f"</div>"
            f"</div>"
        )

        doc = QTextDocument()
        doc.setHtml(html_content)
        doc.setTextWidth(option.rect.width())

        painter.translate(option.rect.topLeft())
        doc.drawContents(painter)

        painter.restore()

    def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        """Return size hint for rich-text item."""
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text:
            return super().sizeHint(option, index)

        lines = text.split("\n")
        if len(lines) < self.MIN_LINES_FOR_DESCRIPTION:
            return super().sizeHint(option, index)

        choice = lines[0]
        description = "\n".join(lines[1:]).strip()

        escaped_choice = escape(choice)
        escaped_description = escape(description).replace("\n", "<br>")

        html_content = f"""
        <div style="font-family: Arial, sans-serif;">
            <div style="font-size: 12pt; font-weight: bold; margin-bottom: 2px;">
                {escaped_choice}
            </div>
            <div style="font-size: 9pt; font-style: italic; color: #666666; margin-left: 10px; white-space: pre-wrap;">
                {escaped_description}
            </div>
        </div>
        """

        doc = QTextDocument()
        doc.setHtml(html_content)
        doc.setTextWidth(option.rect.width())

        doc_size = doc.size()
        return QSize(int(doc_size.width()), int(doc_size.height()) + 5)


class DragDropFileDialog(QDialog):
    """Custom dialog with drag-and-drop support for file selection."""

    def __init__(
        self,
        title: str,
        default_path: str,
        filter_: str,
        target_size: QSize,
        parent: QWidget | None = None,
        *,
        with_resize_option: bool = False,
    ) -> None:
        """Create file-selection dialog with optional resize controls."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setAcceptDrops(True)
        self.setMinimumSize(target_size)
        self.resize(target_size)

        self.default_path = default_path
        self.filter_ = filter_
        self.selected_files: list[str] = []
        self.with_resize_option = with_resize_option

        self.setup_ui()

    def add_files(self, file_paths: list[str]) -> None:
        """Add files to selection list (deduplicated)."""
        for file_path in file_paths:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.files_list.addItem(file_path)

    def clear_files(self) -> None:
        """Clear selected files list."""
        self.selected_files.clear()
        self.files_list.clear()

    def get_max_size(self) -> str | None:
        """Return max size string, or None if resize disabled/empty."""
        if not self.get_resize_enabled() or not hasattr(self, "max_size_edit"):
            return None
        text = self.max_size_edit.text().strip()
        return text or None

    def get_resize_enabled(self) -> bool:
        """Return True when resize checkbox enabled and checked."""
        if not self.with_resize_option or not hasattr(self, "resize_checkbox"):
            return False
        return self.resize_checkbox.isChecked()

    def get_selected_files(self) -> list[str]:
        """Return selected file paths."""
        return self.selected_files

    def select_files(self) -> None:
        """Open native file dialog and add selected files."""
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select Files", self.default_path, self.filter_)
        if filenames:
            self.add_files(filenames)

    def setup_ui(self) -> None:
        """Build widget layout for drag-drop file selection."""
        layout = QVBoxLayout(self)

        title_label = QLabel("Select files for processing")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        self.drop_area = QLabel("Drag files here or click 'Select Files' button")
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                background-color: #f9f9f9;
                color: #666;
                font-size: 12px;
            }
            QLabel:hover {
                border-color: #007acc;
                background-color: #f0f8ff;
            }
        """)
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setMinimumHeight(150)
        layout.addWidget(self.drop_area)

        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(100)
        layout.addWidget(self.files_list)

        if self.with_resize_option:
            resize_layout = QHBoxLayout()
            self.resize_checkbox = QCheckBox("Resize images (max size, px)")
            self.resize_checkbox.setChecked(False)
            resize_layout.addWidget(self.resize_checkbox)
            self.max_size_edit = QLineEdit()
            self.max_size_edit.setPlaceholderText("1024")
            self.max_size_edit.setText("1024")
            self.max_size_edit.setEnabled(False)

            def toggle_max_size_edit(checked: bool) -> None:  # noqa: FBT001
                self.max_size_edit.setEnabled(checked)

            self.resize_checkbox.toggled.connect(toggle_max_size_edit)
            resize_layout.addWidget(self.max_size_edit)
            resize_layout.addStretch()
            layout.addLayout(resize_layout)

        buttons_layout = QHBoxLayout()

        self.select_files_btn = QPushButton("Select Files")
        self.select_files_btn.clicked.connect(self.select_files)
        buttons_layout.addWidget(self.select_files_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_files)
        buttons_layout.addWidget(self.clear_btn)

        buttons_layout.addStretch()

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        buttons_layout.addWidget(self.button_box)

        layout.addLayout(buttons_layout)


class _StandardActionDialog(QDialog):
    """QDialog that reapplies target size when shown (Windows may ignore initial `resize()`)."""

    def __init__(self, target_size: QSize, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._target_size = target_size

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        self.setMinimumSize(self._target_size)
        self.resize(self._target_size)
