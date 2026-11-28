"""Tests for Vector Icons folder library combo sticky Add footer."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.icons.folder_library_combo import FolderLibraryCombo


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_folder_library_combo_emits_add_folder_requested(qapp: QApplication) -> None:
    """Footer click asks the host to open another icons folder."""
    assert qapp is not None
    combo = FolderLibraryCombo()
    combo.addItem("Demo", r"D:\icons\demo")
    handler = MagicMock()
    combo.add_folder_requested.connect(handler)
    combo.show()
    combo.showPopup()
    qapp.processEvents()
    combo._attach_or_show_footer()
    footer = combo._footer
    assert footer is not None
    assert footer.text() == "+ Add folder…"
    assert combo._footer_attached
    footer.click()
    handler.assert_called_once()
    combo.hidePopup()
    combo.close()
    combo.deleteLater()
