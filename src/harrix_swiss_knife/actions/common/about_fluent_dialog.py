"""Fluent About dialog for Harrix Swiss Knife."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget

from harrix_swiss_knife.fluent.tokens import SPACE_L, SPACE_S, SPACE_XS
from harrix_swiss_knife.fluent.widgets.button_base import FluentPushButton
from harrix_swiss_knife.fluent.widgets.dialog_base import FluentDialog
from harrix_swiss_knife.fluent.widgets.text import (
    BodyLabel,
    CaptionLabel,
    FluentHyperlinkLabel,
    StrongBodyLabel,
    TitleLabel,
)

if TYPE_CHECKING:
    from collections.abc import Callable

_ABOUT_LOGO_SIZE = 96
_ABOUT_LOGO_RESOURCE = ":/assets/logo.svg"


class FluentAboutDialog(FluentDialog):
    """Centered logo, Fluent type ramp, Copy and OK footer."""

    def __init__(
        self,
        *,
        app_name: str,
        version: str,
        description: str,
        author: str,
        license_text: str,
        github: str,
        parent: QWidget | None = None,
        window_title: str = "About",
        on_copied: Callable[[], None] | None = None,
    ) -> None:
        """Build the About content and a Copy button beside OK."""
        super().__init__(window_title, "", parent, primary_text="OK", secondary_text="")
        self._on_copied = on_copied
        self._clipboard_text = _clipboard_text(
            app_name=app_name,
            version=version,
            description=description,
            author=author,
            license_text=license_text,
            github=github,
        )

        self._body.title_label.hide()
        self._body.content_label.hide()
        self.content_layout.setSpacing(SPACE_S)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        logo = QLabel(self)
        logo.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        logo.setPixmap(QIcon(_ABOUT_LOGO_RESOURCE).pixmap(_ABOUT_LOGO_SIZE, _ABOUT_LOGO_SIZE))
        logo.setFixedHeight(_ABOUT_LOGO_SIZE + SPACE_XS)
        self.content_layout.addWidget(logo)

        name = TitleLabel(app_name, self)
        name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        name.setWordWrap(True)
        self.content_layout.addWidget(name)

        if version:
            version_label = CaptionLabel(f"Version {version}", self)
            version_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.content_layout.addWidget(version_label)

        self.content_layout.addSpacing(SPACE_S)

        if description:
            body = BodyLabel(description.replace("\n", " ").strip(), self)
            body.setWordWrap(True)
            body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.content_layout.addWidget(body)
            self.content_layout.addSpacing(SPACE_L)

        if author:
            self._add_meta_row("Author", author)
        if license_text:
            self._add_meta_row("License", license_text)
        if github:
            self.content_layout.addWidget(StrongBodyLabel("GitHub", self))
            link = FluentHyperlinkLabel(github, github, self)
            link.setWordWrap(True)
            self.content_layout.addWidget(link)

        copy_button = FluentPushButton("Copy", self._body.footer, icon="copy")
        copy_button.clicked.connect(self._copy_to_clipboard)
        self._body.footer.row.insertWidget(0, copy_button, 1)

    def clipboard_text(self) -> str:
        """Return the plain-text About block used for Copy."""
        return self._clipboard_text

    def _add_meta_row(self, label: str, value: str) -> None:
        self.content_layout.addWidget(StrongBodyLabel(label, self))
        value_label = BodyLabel(value, self)
        value_label.setWordWrap(True)
        self.content_layout.addWidget(value_label)
        self.content_layout.addSpacing(SPACE_S)

    def _copy_to_clipboard(self) -> None:
        QGuiApplication.clipboard().setText(self._clipboard_text)
        if self._on_copied is not None:
            self._on_copied()


def _clipboard_text(
    *,
    app_name: str,
    version: str,
    description: str,
    author: str,
    license_text: str,
    github: str,
) -> str:
    lines = [app_name, ""]
    if version:
        lines.extend([f"Version: {version}", ""])
    if description:
        lines.extend([description.strip(), ""])
    if author:
        lines.append(f"Author: {author}")
    if license_text:
        lines.append(f"License: {license_text}")
    if github:
        lines.append(f"GitHub: {github}")
    return "\n".join(lines).strip() + "\n"
