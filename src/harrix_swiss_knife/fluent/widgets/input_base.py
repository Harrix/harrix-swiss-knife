"""Single-line Fluent text box."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QLineEdit,
    QWidget,
)

from harrix_swiss_knife.fluent.style import (
    line_edit_qss,
)
from harrix_swiss_knife.fluent.theme import bind_theme, palette_for
from harrix_swiss_knife.fluent.tokens import (
    CONTROL_HEIGHT,
    CONTROL_HEIGHT_COMPACT,
)


class FluentLineEdit(QLineEdit):
    """Single-line Fluent text box with an optional clear button."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        placeholder: str = "",
        clearable: bool = True,
        compact: bool = False,
    ) -> None:
        """Create a text box.

        Args:

        - `parent` (`QWidget | None`): Optional parent.
        - `placeholder` (`str`): Placeholder text.
        - `clearable` (`bool`): Show a clear button while non-empty. Defaults to `True`.
        - `compact` (`bool`): Use the compact control height (title bars, toolbars). Defaults to `False`.

        """
        super().__init__(parent)
        self._height = CONTROL_HEIGHT_COMPACT if compact else CONTROL_HEIGHT
        self.setPlaceholderText(placeholder)
        self.setClearButtonEnabled(clearable)
        if compact:
            self.setFixedHeight(self._height)
        else:
            self.setMinimumHeight(self._height)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome for the current palette."""
        self.setStyleSheet(line_edit_qss(palette_for(self), height=self._height))
