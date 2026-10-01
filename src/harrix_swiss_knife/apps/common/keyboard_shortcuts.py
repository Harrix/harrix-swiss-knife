"""Non-modal keyboard-shortcuts help and documented QShortcut helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from weakref import WeakKeyDictionary

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from shiboken6 import isValid

from harrix_swiss_knife.qt_lucide_icon import apply_lucide_action_icon, create_lucide_icon

if TYPE_CHECKING:
    from collections.abc import Callable

_CATEGORY_PROPERTY = "hsk_shortcut_category"
_open_help_dialogs: WeakKeyDictionary[QWidget, KeyboardShortcutsDialog] = WeakKeyDictionary()


class KeyboardShortcutsDialog(QDialog):
    """Non-modal table of keyboard shortcuts that can stay open while using the app."""

    def __init__(
        self,
        parent: QWidget | None,
        *,
        title: str,
        entries: list[ShortcutHelpEntry],
    ) -> None:
        """Build the help window."""
        super().__init__(parent)
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, on=True)
        self.setWindowTitle(title)
        self.setMinimumSize(520, 360)
        self.resize(640, 480)

        root = QVBoxLayout(self)
        hint = QLabel("This window is non-modal — keep it open while you work.", self)
        hint.setWordWrap(True)
        root.addWidget(hint)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filter:", self))
        self._filter = QLineEdit(self)
        self._filter.setPlaceholderText("Search keys or actions…")
        self._filter.setClearButtonEnabled(True)
        self._filter.textChanged.connect(self._apply_filter)
        filter_row.addWidget(self._filter, stretch=1)
        root.addLayout(filter_row)

        self._table = QTableWidget(0, 3, self)
        self._table.setHorizontalHeaderLabels(["Category", "Shortcut", "Action"])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        root.addWidget(self._table, stretch=1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close_btn = QPushButton("Close", self)
        close_btn.setIcon(create_lucide_icon("x", 16))
        close_btn.clicked.connect(self.close)
        buttons.addWidget(close_btn)
        root.addLayout(buttons)

        self._entries: list[ShortcutHelpEntry] = []
        self.set_entries(entries)

    def set_entries(self, entries: list[ShortcutHelpEntry]) -> None:
        """Replace the shortcut list and refresh the table."""
        self._entries = sort_shortcut_help(list(entries))
        self._apply_filter(self._filter.text())

    def _apply_filter(self, text: str) -> None:
        needle = text.strip().casefold()
        rows = [
            entry
            for entry in self._entries
            if not needle
            or needle in entry.category.casefold()
            or needle in entry.keys.casefold()
            or needle in entry.description.casefold()
        ]
        self._table.setRowCount(len(rows))
        for row, entry in enumerate(rows):
            self._table.setItem(row, 0, QTableWidgetItem(entry.category))
            self._table.setItem(row, 1, QTableWidgetItem(entry.keys))
            self._table.setItem(row, 2, QTableWidgetItem(entry.description))


@dataclass(frozen=True, slots=True)
class ShortcutHelpEntry:
    """One row in the keyboard-shortcuts help window."""

    keys: str
    description: str
    category: str = "General"


def add_keyboard_shortcuts_help_action(
    menu: Any,
    parent: QWidget,
    *,
    before: QAction | None = None,
    slot: Callable[[], None],
) -> QAction:
    """Insert a Help → Keyboard shortcuts action and return it."""
    action = QAction("Keyboard shortcuts", parent)
    apply_lucide_action_icon(action, "keyboard")
    action.triggered.connect(slot)
    if before is not None:
        menu.insertAction(before, action)
    else:
        menu.addAction(action)
    return action


def collect_documented_shortcuts(widget: QWidget) -> list[ShortcutHelpEntry]:
    """Collect help rows from `QShortcut` children that have `whatsThis` descriptions."""
    entries: list[ShortcutHelpEntry] = []
    for shortcut in widget.findChildren(QShortcut):
        description = shortcut.whatsThis().strip()
        if not description:
            continue
        category = str(shortcut.property(_CATEGORY_PROPERTY) or "").strip() or "General"
        keys = key_sequence_display(shortcut.key())
        if not keys:
            continue
        entries.append(ShortcutHelpEntry(keys=keys, description=description, category=category))
    return merge_shortcut_help(entries)


def default_tracker_app_shortcut_help() -> list[ShortcutHelpEntry]:
    """Shared shortcuts for Finance / Food / Fitness / Habits main Windows."""
    return [
        ShortcutHelpEntry("Ctrl+C", "Copy selected table cells to the clipboard", "Tables"),
        ShortcutHelpEntry("Enter", "Activate Add when an add control is focused", "Forms"),
        ShortcutHelpEntry("F1", "Show this keyboard shortcuts help", "Help"),
    ]


def install_documented_shortcut(
    parent: QWidget,
    sequence: QKeySequence | QKeySequence.StandardKey | str,
    slot: Callable[[], None],
    *,
    description: str,
    category: str = "General",
    registry: list[ShortcutHelpEntry] | None = None,
    context: Qt.ShortcutContext = Qt.ShortcutContext.WindowShortcut,
) -> QShortcut:
    """Create a `QShortcut`, store help metadata on it, and optionally append to `registry`."""
    key_seq = to_key_sequence(sequence)
    shortcut = QShortcut(key_seq, parent)
    shortcut.setContext(context)
    shortcut.activated.connect(slot)
    shortcut.setWhatsThis(description)
    shortcut.setProperty(_CATEGORY_PROPERTY, category)
    if registry is not None:
        registry.append(
            ShortcutHelpEntry(
                keys=key_sequence_display(key_seq),
                description=description,
                category=category,
            ),
        )
    return shortcut


def key_sequence_display(sequence: QKeySequence | QKeySequence.StandardKey | str) -> str:
    """Return a readable shortcut string for help tables."""
    if isinstance(sequence, QKeySequence.StandardKey):
        bindings = QKeySequence.keyBindings(sequence)
        if bindings:
            return bindings[0].toString(QKeySequence.SequenceFormat.NativeText)
        return QKeySequence(sequence).toString(QKeySequence.SequenceFormat.NativeText)
    if isinstance(sequence, str):
        return QKeySequence(sequence).toString(QKeySequence.SequenceFormat.NativeText)
    text = sequence.toString(QKeySequence.SequenceFormat.NativeText).strip()
    return text or sequence.toString(QKeySequence.SequenceFormat.PortableText)


def merge_shortcut_help(*groups: list[ShortcutHelpEntry]) -> list[ShortcutHelpEntry]:
    """Merge groups, dropping duplicate (category, keys, description) rows."""
    seen: set[tuple[str, str, str]] = set()
    merged: list[ShortcutHelpEntry] = []
    for group in groups:
        for entry in group:
            key = (entry.category, entry.keys.casefold(), entry.description.casefold())
            if key in seen:
                continue
            seen.add(key)
            merged.append(entry)
    return merged


def show_keyboard_shortcuts_help(
    parent: QWidget | None,
    title: str,
    entries: list[ShortcutHelpEntry],
) -> KeyboardShortcutsDialog:
    """Show or raise a non-modal shortcuts window for `parent`."""
    owner = parent if isinstance(parent, QWidget) else None
    if owner is not None:
        existing = _open_help_dialogs.get(owner)
        if existing is not None and isValid(existing):
            existing.set_entries(entries)
            existing.setWindowTitle(title)
            existing.show()
            existing.raise_()
            existing.activateWindow()
            return existing

    dialog = KeyboardShortcutsDialog(owner, title=title, entries=entries)
    if owner is not None:
        _open_help_dialogs[owner] = dialog

        def _forget(_obj: object = None, *, forgotten: QWidget = owner) -> None:
            current = _open_help_dialogs.get(forgotten)
            if current is dialog:
                _open_help_dialogs.pop(forgotten, None)

        dialog.destroyed.connect(_forget)
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()
    return dialog


def sort_shortcut_help(entries: list[ShortcutHelpEntry]) -> list[ShortcutHelpEntry]:
    """Sort by category, then keys, then description."""
    return sorted(
        entries, key=lambda item: (item.category.casefold(), item.keys.casefold(), item.description.casefold())
    )


def to_key_sequence(sequence: QKeySequence | QKeySequence.StandardKey | str) -> QKeySequence:
    """Normalize supported sequence forms to `QKeySequence`."""
    if isinstance(sequence, QKeySequence.StandardKey):
        return QKeySequence(sequence)
    if isinstance(sequence, str):
        return QKeySequence(sequence)
    return sequence
