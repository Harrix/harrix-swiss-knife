"""Autocomplete proxy model and helpers for food name input."""

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QWidget


class FoodNameAutocompleteProxyModel(QSortFilterProxyModel):
    """Proxy model for food name autocomplete with exact/starts-with/contains ordering."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the proxy model."""
        super().__init__(parent)
        self.filter_text = ""
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:  # noqa: N802
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

        if text.startswith(filter_lower):
            return True

        return filter_lower in text

    def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Sort by match tier, then alphabetically (case-insensitive) within tier."""
        if not self.filter_text:
            left_data = self.sourceModel().data(source_left, Qt.ItemDataRole.DisplayRole)
            right_data = self.sourceModel().data(source_right, Qt.ItemDataRole.DisplayRole)
            if left_data is None or right_data is None:
                return False
            left_lower = str(left_data).lower()
            right_lower = str(right_data).lower()
            if left_lower != right_lower:
                return left_lower < right_lower
            return source_left.row() < source_right.row()

        filter_lower = self.filter_text.lower()
        left_data = self.sourceModel().data(source_left, Qt.ItemDataRole.DisplayRole)
        right_data = self.sourceModel().data(source_right, Qt.ItemDataRole.DisplayRole)

        if left_data is None or right_data is None:
            return False

        left_tier = _match_tier(str(left_data), filter_lower)
        right_tier = _match_tier(str(right_data), filter_lower)

        if left_tier != right_tier:
            return left_tier < right_tier

        left_lower = str(left_data).lower()
        right_lower = str(right_data).lower()
        if left_lower != right_lower:
            return left_lower < right_lower

        return source_left.row() < source_right.row()

    def set_filter_text(self, text: str) -> None:
        """Set the filter text and trigger re-filtering and sorting."""
        self.filter_text = text
        self.invalidateFilter()
        self.sort(0)


def _match_tier(text: str, filter_text: str) -> int:
    """Return sort tier: 0 exact, 1 starts-with, 2 contains."""
    filter_lower = filter_text.lower()
    text_lower = text.lower()
    if text_lower == filter_lower:
        return 0
    if text_lower.startswith(filter_lower):
        return 1
    return 2
