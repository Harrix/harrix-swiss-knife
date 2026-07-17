"""Dialog service used by actions.

This module extracts dialog-related responsibilities from `ActionBase`.
It provides a single place for common Qt dialogs and shared geometry policy.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import (
    QFont,
    QGuiApplication,
    QIcon,
)
from PySide6.QtWidgets import (
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
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.actions.action_log_browser import build_action_output_log_browser
from harrix_swiss_knife.actions.dialog_widgets import (
    ChoiceWithDescriptionDelegate,
    DragDropFileDialog,
    StandardActionDialog,
)
from harrix_swiss_knife.actions.text_diff_dialog import build_text_diff_side_by_side
from harrix_swiss_knife.actions.text_result_dialog import (
    CANCEL_BUTTON_EMOJI,
    OK_BUTTON_EMOJI,
    REMOVE_PARAGRAPHS_DIALOG_CODE,
    RERUN_BUTTON_EMOJI,
    RERUN_BUTTON_LABEL,
    RERUN_DIALOG_CODE,
    REWRITE_DIALOG_CODE,
    add_copy_button,
    add_ok_button,
    append_result_action_buttons,
)
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.qt_action_card_grid import configure_action_card_grid
from harrix_swiss_knife.qt_emoji_icon import (
    COPY_BUTTON_EMOJI,
    DEFAULT_EMOJI_BUTTON_ICON_SIZE,
    apply_emoji_dialog_buttons,
    make_emoji_push_button,
)

COMMIT_OFFER_CREATE_CODE = 10
COMMIT_OFFER_COPY_CODE = 11

if TYPE_CHECKING:
    from collections.abc import Callable


class ActionDialogService:
    """Dialog builder/service for `ActionBase`-like actions."""

    def __init__(
        self,
        *,
        default_size: QSize,
        compact_size: QSize,
        add_line: Callable[[str], None],
        show_toast: Callable[[str], None],
        create_emoji_icon: Callable[[str, int], QIcon],
    ) -> None:
        """Create service with UI callbacks injected from `ActionBase`."""
        self._default_size = default_size
        self._compact_size = compact_size
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
        disabled_choices: list[str] | None = None,
    ) -> list[str] | None:
        """Return checkbox-selected items, or None on cancel."""
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        disabled_set = set(disabled_choices or ())

        parent = QApplication.activeWindow()
        dialog = StandardActionDialog(self._default_size, parent)
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

            if choice in disabled_set:
                checkbox.setEnabled(False)
                checkbox.setChecked(False)
            elif default_selected and choice in default_selected:
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
                if checkbox.isEnabled():
                    checkbox.setChecked(True)

        def deselect_all() -> None:
            for checkbox in checkboxes:
                if checkbox.isEnabled():
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

            ext_dialog = StandardActionDialog(self._default_size, dialog)
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
            self._apply_emoji_dialog_buttons(ext_buttons)
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
                    if checkbox.isEnabled() and _extension_key_for_choice(checkbox.text()) == ext:
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
        self._apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            selected_choices = [
                checkbox.text() for checkbox in checkboxes if checkbox.isEnabled() and checkbox.isChecked()
            ]
            if not selected_choices:
                return None
            return selected_choices

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
            configure_action_card_grid(lw, min_height=self._default_size.height() - 160)

            for icon_emoji, choice_title in choices:
                item = QListWidgetItem(choice_title, lw)
                item.setData(Qt.ItemDataRole.UserRole, choice_title)
                item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

                icon = self._create_emoji_icon(icon_emoji, icon_size)
                item.setIcon(icon)

            if lw.count() > 0:
                lw.setCurrentRow(0)

            lw.itemClicked.connect(lambda _item: dialog.accept())
            layout.addWidget(lw)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            list_widget = lw

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if list_widget is None:
                return None
            current_item = list_widget.currentItem()
            if current_item:
                return current_item.data(Qt.ItemDataRole.UserRole)
            return None

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
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            list_widget = lw

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if list_widget is None:
                return None
            current_item = list_widget.currentItem()
            if current_item:
                return current_item.text()
            return None

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
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            list_widget = lw

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if list_widget is None:
                return None
            current_item = list_widget.currentItem()
            if current_item:
                return current_item.data(Qt.ItemDataRole.UserRole)
            return None

        return None

    def get_existing_directory(self, title: str, default_path: str) -> Path | None:
        """Return selected directory path, or None if cancelled."""
        folder_path = QFileDialog.getExistingDirectory(None, title, default_path)
        if not folder_path:
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
            return None
        return Path(filename)

    def get_open_filenames(self, title: str, default_path: str, filter_: str) -> list[Path] | None:
        """Return selected filenames, or None if cancelled."""
        dialog = DragDropFileDialog(title, default_path, filter_, self._default_size)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            filenames = dialog.get_selected_files()
            if not filenames:
                return None
            return [Path(filename) for filename in filenames]
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
                return None, False, None
            paths = [Path(f) for f in filenames]
            resize_enabled = dialog.get_resize_enabled()
            max_size = dialog.get_max_size()
            return paths, resize_enabled, max_size
        return None, False, None

    def get_path_input(self, title: str, label: str, default_value: str | None = None) -> str | None:
        """Return entered path, with an optional folder browse button."""
        line_edit: QLineEdit | None = None

        def _get_start_folder(path_text: str) -> str:
            path = Path(path_text).expanduser()
            if path.is_dir():
                return str(path)
            if path.parent.exists():
                return str(path.parent)
            return ""

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal line_edit

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            input_layout = QHBoxLayout()

            le = QLineEdit()
            le.setMinimumHeight(32)
            le.setText(default_value or "")
            input_layout.addWidget(le)

            browse_button = QPushButton("📁 Browse folder...")

            def on_browse_clicked() -> None:
                folder_path = QFileDialog.getExistingDirectory(
                    dialog,
                    "Select folder",
                    _get_start_folder(le.text().strip() or default_value or ""),
                )
                if folder_path:
                    le.setText(folder_path)

            browse_button.clicked.connect(on_browse_clicked)
            input_layout.addWidget(browse_button)

            layout.addLayout(input_layout)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            line_edit = le

        result, _dialog = self._exec_compact_dialog(title, _build)

        if result != QDialog.DialogCode.Accepted or line_edit is None:
            return None

        text = line_edit.text().strip()
        if not text:
            return None
        return text

    def get_save_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        """Return save target filename, or None if cancelled."""
        filename, _ = QFileDialog.getSaveFileName(None, title, default_path, filter_)
        if not filename:
            return None
        return Path(filename)

    def get_text_input(self, title: str, label: str, default_value: str | None = None) -> str | None:
        """Return entered text, or None on cancel/empty."""
        text, ok = QInputDialog.getText(None, title, label, text=default_value or "")
        if not (ok and text):
            return None
        return text

    def get_text_input_with_auto(
        self,
        title: str,
        label: str,
        auto_generator: Callable[[], str] | None = None,
        auto_button_text: str = "🤖 Auto",
        validator: Callable[[str], str | None] | None = None,
    ) -> str | None:
        """Return text input, optionally generated by callback, or None on cancel."""
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
            try:
                le.setText(auto_generator())
            except Exception as e:
                self._add_line(f"❌ Error generating auto text: {e}")
            input_layout.addWidget(le)

            auto_button = make_emoji_push_button(
                auto_button_text.removeprefix("🤖 ").strip() or "Auto",
                "🤖",
            )

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
            self._apply_emoji_dialog_buttons(buttons)

            def try_accept() -> None:
                text = le.text().strip()
                if not text:
                    message_box.warning(dialog, title, "Name must not be empty.")
                    return
                if validator is not None:
                    error = validator(text)
                    if error:
                        message_box.warning(dialog, title, error)
                        return
                le.setText(text)
                dialog.accept()

            buttons.accepted.connect(try_accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            line_edit = le

        result, _dialog = self._exec_compact_dialog(title, _build)

        if result == QDialog.DialogCode.Accepted:
            if line_edit is None:
                return None
            return line_edit.text().strip()

        return None

    def get_text_textarea(
        self,
        title: str,
        label: str,
        default_text: str | None = None,
    ) -> str | None:
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
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            text_edit = te

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if text_edit is None:
                return None
            text = text_edit.toPlainText()
            if not text.strip():
                return None
            return text
        return None

    def get_yes_no_question(self, title: str, message: str, *, default_yes: bool = False) -> bool:
        """Return True for Yes, False otherwise."""
        default_button = QMessageBox.StandardButton.Yes if default_yes else QMessageBox.StandardButton.No
        reply = message_box.question(
            None,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            default_button,
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
            copy_button = make_emoji_push_button("Copy to Clipboard", COPY_BUTTON_EMOJI)

            def click_copy_button() -> None:
                QGuiApplication.clipboard().setText(about_text)
                self._show_toast("About information copied to Clipboard")

            copy_button.clicked.connect(click_copy_button)
            button_layout.addWidget(copy_button)

            ok_button = make_emoji_push_button("OK", OK_BUTTON_EMOJI)
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
        """Show a split view: log file list (left) and UTF-8 preview (right)."""
        if not entries:
            self._add_line("❌ No log files to browse.")
            return

        self._exec_standard_dialog(
            "Recent action logs",
            build_action_output_log_browser(
                entries,
                on_file_selected=on_file_selected,
                show_toast=self._show_toast,
            ),
            stretch_row=0,
        )

    def show_git_commit_offer(
        self,
        commit_message: str,
        *,
        repo_path: Path | None = None,
    ) -> int:
        """Offer to create a Git commit or copy the suggested commit message to the clipboard."""
        dialog_parent = QApplication.activeWindow()
        dialog = QDialog(dialog_parent)
        dialog.setWindowTitle("Git commit")

        layout = QVBoxLayout()

        intro = "Create a git commit with the suggested commit message?"
        if repo_path is not None:
            intro += f"\n\nRepository:\n{repo_path}"
        else:
            intro += "\n\n⚠️ Git repository not found for the changed files."

        label_widget = QLabel(intro)
        label_widget.setWordWrap(True)
        layout.addWidget(label_widget)

        message_label = QLabel("Commit message:")
        layout.addWidget(message_label)

        message_edit = QLineEdit(commit_message)
        message_edit.setReadOnly(True)
        layout.addWidget(message_edit)

        button_layout = QHBoxLayout()
        create_button = make_emoji_push_button("Create commit", "✅")
        create_button.setEnabled(repo_path is not None)
        create_button.clicked.connect(lambda: dialog.done(COMMIT_OFFER_CREATE_CODE))
        button_layout.addWidget(create_button)

        copy_button = make_emoji_push_button("Copy commit message", "📋")
        copy_button.clicked.connect(lambda: dialog.done(COMMIT_OFFER_COPY_CODE))
        button_layout.addWidget(copy_button)

        close_button = make_emoji_push_button("Close", CANCEL_BUTTON_EMOJI)
        close_button.clicked.connect(dialog.reject)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.setMinimumWidth(min(self._default_size.width(), 640))
        dialog.adjustSize()
        result = dialog.exec()

        if result == COMMIT_OFFER_COPY_CODE:
            QGuiApplication.clipboard().setText(commit_message)
            self._show_toast("Commit message copied to Clipboard")

        return result

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
            copy_button = make_emoji_push_button("Copy to Clipboard", COPY_BUTTON_EMOJI)

            def click_copy_button() -> None:
                QGuiApplication.clipboard().setText(instructions)
                self._show_toast("Instructions copied to Clipboard")

            copy_button.clicked.connect(click_copy_button)
            button_layout.addWidget(copy_button)

            ok_button = make_emoji_push_button("OK", OK_BUTTON_EMOJI)
            ok_button.clicked.connect(dialog.accept)
            button_layout.addWidget(ok_button)

            layout.addLayout(button_layout)

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=0)
        return instructions if result == QDialog.DialogCode.Accepted else None

    def show_text_diff_side_by_side(
        self,
        before_text: str,
        after_text: str,
        title: str = "Diff (Before/After)",
        *,
        rerun_button: bool = False,
        rerun_button_label: str = RERUN_BUTTON_LABEL,
        rerun_button_emoji: str = RERUN_BUTTON_EMOJI,
        remove_paragraphs_button: bool = False,
    ) -> tuple[str | None, int]:
        """Show read-only before/after diff with inline change highlighting."""
        result, _dialog = self._exec_standard_dialog(
            title,
            build_text_diff_side_by_side(
                before_text,
                after_text,
                self._default_size,
                self._show_toast,
                rerun_button=rerun_button,
                rerun_button_label=rerun_button_label,
                rerun_button_emoji=rerun_button_emoji,
                remove_paragraphs_button=remove_paragraphs_button,
            ),
            stretch_row=0,
        )
        if result in (RERUN_DIALOG_CODE, REMOVE_PARAGRAPHS_DIALOG_CODE):
            return after_text, result
        return (after_text if result == QDialog.DialogCode.Accepted else None, result)

    def show_text_multiline(
        self,
        text: str,
        title: str = "Result",
        *,
        rerun_button: bool = False,
        rerun_button_label: str = RERUN_BUTTON_LABEL,
        rerun_button_emoji: str = RERUN_BUTTON_EMOJI,
        rewrite_button: bool = False,
        remove_paragraphs_button: bool = False,
    ) -> str | None | tuple[str | None, int]:
        """Show read-only multi-line text dialog and return text if accepted."""
        has_action_buttons = rerun_button or rewrite_button or remove_paragraphs_button

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

            def click_copy_button() -> None:
                QGuiApplication.clipboard().setText(text_edit.toPlainText())
                self._show_toast("Copied to Clipboard")

            add_copy_button(button_layout, click_copy_button)

            append_result_action_buttons(
                dialog,
                button_layout,
                rerun_button=rerun_button,
                rerun_button_label=rerun_button_label,
                rerun_button_emoji=rerun_button_emoji,
                rewrite_button=rewrite_button,
                remove_paragraphs_button=remove_paragraphs_button,
            )

            add_ok_button(dialog, button_layout)

            layout.addLayout(button_layout)

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=0)
        if has_action_buttons:
            if result in (RERUN_DIALOG_CODE, REWRITE_DIALOG_CODE, REMOVE_PARAGRAPHS_DIALOG_CODE):
                return text, result
            return (text if result == QDialog.DialogCode.Accepted else None, result)
        return text if result == QDialog.DialogCode.Accepted else None

    def _apply_emoji_dialog_buttons(self, buttons: QDialogButtonBox) -> None:
        """Set emoji icons on standard QDialogButtonBox buttons."""
        apply_emoji_dialog_buttons(buttons, icon_size=DEFAULT_EMOJI_BUTTON_ICON_SIZE)

    def _exec_compact_dialog(
        self,
        title: str,
        build: Callable[[QDialog, QVBoxLayout], None],
        *,
        parent: QWidget | None = None,
    ) -> tuple[int, QDialog]:
        """Create and execute a compact dialog sized for simple input forms."""
        dialog_parent = QApplication.activeWindow() if parent is None else parent
        dialog = QDialog(dialog_parent)
        dialog.setWindowTitle(title)

        layout = QVBoxLayout()
        build(dialog, layout)

        dialog.setLayout(layout)
        dialog.setMinimumWidth(self._compact_size.width())
        dialog.adjustSize()
        dialog.resize(max(dialog.sizeHint().width(), self._compact_size.width()), dialog.sizeHint().height())
        result = dialog.exec()
        return result, dialog

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
        dialog = StandardActionDialog(self._default_size, dialog_parent)
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
