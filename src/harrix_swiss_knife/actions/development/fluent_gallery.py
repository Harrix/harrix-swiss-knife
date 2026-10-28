"""Open the in-repo Fluent widget showcase gallery."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from shiboken6 import isValid

from harrix_swiss_knife.actions.common.base import ActionBase

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


class OnFluentGallery(ActionBase):
    """Open a stand-alone window with every Fluent widget and copy-name menus."""

    icon = "🧩"
    title = "Fluent widget gallery"
    gallery_window: ClassVar[QWidget | None] = None

    @classmethod
    def clear_gallery_window(cls, *_args: object) -> None:
        """Drop the cached gallery window after Qt destroys it."""
        cls.gallery_window = None

    @ActionBase.handle_exceptions("fluent gallery")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Show the Fluent gallery, reusing the existing window when still valid."""
        window = OnFluentGallery.gallery_window
        if window is not None and isValid(window):
            window.show()
            window.raise_()
            window.activateWindow()
            self.add_line("✅ Fluent widget gallery is already open")
            return

        from harrix_swiss_knife.fluent.gallery import build_gallery  # noqa: PLC0415
        from harrix_swiss_knife.fluent.theme import FluentTheme  # noqa: PLC0415

        FluentTheme.instance().load_from_config()
        window = build_gallery()
        window.destroyed.connect(OnFluentGallery.clear_gallery_window)
        OnFluentGallery.gallery_window = window
        window.show()
        window.raise_()
        window.activateWindow()
        self.add_line("✅ Fluent widget gallery opened")
