"""Autocomplete proxy model and helpers for transaction description input."""

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QWidget

from harrix_swiss_knife.keyboard_layout_search import autocomplete_match_tier, text_matches_autocomplete


class DescriptionAutocompleteProxyModel(QSortFilterProxyModel):
    """Proxy model for description autocomplete with exact/starts-with/contains ordering."""

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

        return text_matches_autocomplete(str(data), self.filter_text)

    def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Sort by match tier, then preserve source order within each tier."""
        if not self.filter_text:
            return source_left.row() < source_right.row()

        left_data = self.sourceModel().data(source_left, Qt.ItemDataRole.DisplayRole)
        right_data = self.sourceModel().data(source_right, Qt.ItemDataRole.DisplayRole)

        if left_data is None or right_data is None:
            return False

        left_tier = _match_tier(str(left_data), self.filter_text)
        right_tier = _match_tier(str(right_data), self.filter_text)

        if left_tier != right_tier:
            return left_tier < right_tier

        return source_left.row() < source_right.row()

    def set_filter_text(self, text: str) -> None:
        """Set the filter text and trigger re-filtering and sorting."""
        self.filter_text = text
        self.invalidateFilter()
        self.sort(0)


def dedupe_descriptions_for_autocomplete(descriptions: list[str]) -> list[str]:
    """Return unique descriptions preserving first-seen order."""
    return list(dict.fromkeys(descriptions))


def _match_tier(text: str, filter_text: str) -> int:
    """Return sort tier: 0 exact, 1 starts-with, 2 contains (EN/RU layout tolerant)."""
    tier = autocomplete_match_tier(text, filter_text)
    return 2 if tier is None else tier
