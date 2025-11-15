"""Filtered ComboBox with smart search functionality."""

from PySide6.QtCore import Qt, QSortFilterProxyModel, QStringListModel
from PySide6.QtWidgets import QComboBox, QCompleter


class SmartFilterProxyModel(QSortFilterProxyModel):
    """Custom proxy model for smart filtering.

    Implements smart filtering logic:
    - First shows items that start with the filter text (case-insensitive)
    - Then shows items that contain the filter text in the middle (if length >= 2)
    - Case-insensitive matching
    """

    def __init__(self, parent=None):
        """Initialize the proxy model."""
        super().__init__(parent)
        self.filter_text = ""
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def filterAcceptsRow(self, source_row, source_parent):
        """Determine if a row should be accepted by the filter."""
        if not self.filter_text:
            return True

        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        data = source_model.data(index, Qt.ItemDataRole.DisplayRole)

        if data is None:
            return False

        text = str(data).lower()
        filter_lower = self.filter_text.lower()

        # Always accept items that start with filter text
        if text.startswith(filter_lower):
            return True

        # For filter text with 2+ chars, also accept items containing it anywhere
        if len(filter_lower) >= 2 and filter_lower in text:
            return True

        return False

    def lessThan(self, left, right):
        """Custom sorting to show starts-with matches first."""
        if not self.filter_text:
            # Default alphabetical sorting when no filter
            left_data = self.sourceModel().data(left, Qt.ItemDataRole.DisplayRole)
            right_data = self.sourceModel().data(right, Qt.ItemDataRole.DisplayRole)

            if left_data is None or right_data is None:
                return False

            return str(left_data).lower() < str(right_data).lower()

        filter_lower = self.filter_text.lower()

        left_data = self.sourceModel().data(left, Qt.ItemDataRole.DisplayRole)
        right_data = self.sourceModel().data(right, Qt.ItemDataRole.DisplayRole)

        if left_data is None or right_data is None:
            return False

        left_text = str(left_data).lower()
        right_text = str(right_data).lower()

        left_starts = left_text.startswith(filter_lower)
        right_starts = right_text.startswith(filter_lower)

        # Items starting with filter come first
        if left_starts and not right_starts:
            return True
        if right_starts and not left_starts:
            return False

        # Within same category (both start or both contain), sort alphabetically
        return left_text < right_text

    def set_filter_text(self, text):
        """Set the filter text and trigger re-filtering."""
        self.filter_text = text
        self.invalidateFilter()
        self.sort(0)


class FilteredComboBox(QComboBox):
    """ComboBox with smart filtering functionality.

    Features:
    - Shows matching items as you type
    - Case-insensitive filtering
    - Items starting with typed text appear first
    - Items containing typed text (>= 2 chars) appear after
    - Dropdown opens automatically when typing
    - Resets to full list when cleared
    - Allows entering custom text not in the list
    """

    def __init__(self, parent=None):
        """Initialize the filtered combobox."""
        super().__init__(parent)

        # Make it editable to allow typing
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        # Setup model and proxy
        self.string_model = QStringListModel()
        self.proxy_model = SmartFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.string_model)

        # Setup completer
        self.completer_widget = QCompleter(self.proxy_model, self)
        self.completer_widget.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer_widget.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer_widget.setFilterMode(Qt.MatchFlag.MatchContains)

        self.setCompleter(self.completer_widget)

        # Store original items for reset
        self._original_items = []
        self._is_programmatic_change = False

        # Connect signals
        self.lineEdit().textEdited.connect(self._on_text_edited)
        self.completer_widget.activated.connect(self._on_completion_activated)

    def addItems(self, texts):
        """Add multiple items to the combobox."""
        self._original_items = sorted(texts, key=str.lower)
        self.string_model.setStringList(self._original_items)
        # Add items to combobox itself (for when no filter is active)
        super().clear()
        super().addItems(self._original_items)

    def addItem(self, text):
        """Add a single item to the combobox."""
        self._original_items.append(text)
        self._original_items = sorted(self._original_items, key=str.lower)
        self.string_model.setStringList(self._original_items)
        super().clear()
        super().addItems(self._original_items)

    def clear(self):
        """Clear all items."""
        self._original_items = []
        self.string_model.setStringList([])
        super().clear()

    def setCurrentText(self, text):
        """Set current text (override to handle programmatic changes)."""
        self._is_programmatic_change = True
        super().setCurrentText(text)
        self._is_programmatic_change = False

    def _on_text_edited(self, text):
        """Handle text editing to show filtered dropdown."""
        if self._is_programmatic_change:
            return

        # Update filter
        self.proxy_model.set_filter_text(text)

        if text:
            # Show dropdown with filtered items
            self.completer_widget.setCompletionPrefix(text)
            self.completer_widget.complete()
        else:
            # Empty text - reset to full list and hide popup
            self.proxy_model.set_filter_text("")
            if self.completer_widget.popup().isVisible():
                self.completer_widget.popup().hide()

    def _on_completion_activated(self, text):
        """Handle completion selection."""
        self._is_programmatic_change = True
        self.setCurrentText(text)
        self._is_programmatic_change = False


def apply_smart_filtering(combobox: QComboBox) -> None:
    """Apply smart filtering to an existing QComboBox.

    This function converts a regular QComboBox into one with smart filtering:
    - Shows matching items as you type
    - Case-insensitive filtering
    - Items starting with typed text appear first
    - Items containing typed text (>= 2 chars) appear after
    - Dropdown opens automatically when typing
    - Allows entering custom text not in the list

    Args:
        combobox: The QComboBox to enhance with smart filtering

    Example:
        ```python
        combo = QComboBox()
        combo.addItems(["Apple", "Banana", "Cherry"])
        apply_smart_filtering(combo)
        ```
    """
    # Make it editable if not already
    if not combobox.isEditable():
        combobox.setEditable(True)

    # Allow custom text entry
    combobox.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

    # Get existing items and sort them
    items = [combobox.itemText(i) for i in range(combobox.count())]
    items_sorted = sorted(items, key=str.lower)

    # Setup model and proxy
    string_model = QStringListModel(items_sorted)
    proxy_model = SmartFilterProxyModel(combobox)
    proxy_model.setSourceModel(string_model)

    # Setup completer
    completer = QCompleter(proxy_model, combobox)
    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
    completer.setFilterMode(Qt.MatchFlag.MatchContains)

    combobox.setCompleter(completer)

    # Re-populate combobox with sorted items
    combobox.clear()
    combobox.addItems(items_sorted)

    # Store references to prevent garbage collection
    combobox._smart_filter_model = string_model
    combobox._smart_filter_proxy = proxy_model
    combobox._smart_filter_completer = completer
    combobox._smart_filter_items = items_sorted
    combobox._smart_filter_is_programmatic = False

    # Disconnect any existing text edited signals to avoid duplicates
    try:
        combobox.lineEdit().textEdited.disconnect()
    except:
        pass

    # Connect signals
    def on_text_edited(text):
        if hasattr(combobox, '_smart_filter_is_programmatic') and combobox._smart_filter_is_programmatic:
            return

        proxy_model.set_filter_text(text)

        if text:
            completer.setCompletionPrefix(text)
            completer.complete()
        else:
            proxy_model.set_filter_text("")
            if completer.popup().isVisible():
                completer.popup().hide()

    def on_completion_activated(text):
        combobox._smart_filter_is_programmatic = True
        combobox.setCurrentText(text)
        combobox._smart_filter_is_programmatic = False

    combobox.lineEdit().textEdited.connect(on_text_edited)
    completer.activated.connect(on_completion_activated)
