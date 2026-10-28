"""Base label for the Fluent type ramp."""

from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from harrix_swiss_knife.fluent.theme import bind_theme, css, fluent_font, palette_for
from harrix_swiss_knife.fluent.widgets.enums import TextRole, TextStyle


class FluentText(QLabel):
    """Label that uses one step of the Fluent type ramp and a theme text color."""

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        style: TextStyle = TextStyle.BODY,
        role: TextRole = TextRole.PRIMARY,
        word_wrap: bool = False,
    ) -> None:
        """Create a themed label.

        Args:

        - `text` (`str`): Label text.
        - `parent` (`QWidget | None`): Optional parent.
        - `style` (`TextStyle`): Type ramp entry. Defaults to `BODY`.
        - `role` (`TextRole`): Color role. Defaults to `PRIMARY`.
        - `word_wrap` (`bool`): Wrap long text. Defaults to `False`.

        """
        super().__init__(text, parent)
        self._style = style
        self._role = role
        self.setWordWrap(word_wrap)
        self._apply_font()
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply the text color for the current palette."""
        palette = palette_for(self)
        colors = {
            TextRole.PRIMARY: palette.text_primary,
            TextRole.SECONDARY: palette.text_secondary,
            TextRole.TERTIARY: palette.text_tertiary,
            TextRole.ACCENT: palette.accent_text,
            TextRole.DISABLED: palette.text_disabled,
        }
        self.setStyleSheet(f"QLabel {{ color: {css(colors[self._role])}; background: transparent; }}")

    def set_role(self, role: TextRole) -> None:
        """Switch the color role."""
        self._role = role
        self.refresh_theme()

    def set_text_style(self, style: TextStyle) -> None:
        """Switch the type ramp entry."""
        self._style = style
        self._apply_font()

    def text_style(self) -> TextStyle:
        """Return the type ramp entry."""
        return self._style

    def _apply_font(self) -> None:
        scale, weight = self._style.value
        app = QApplication.instance()
        base = app.font() if isinstance(app, QApplication) else QFont()
        self.setFont(fluent_font(base, scale, weight=weight))
