"""Tests for TextImageSourceDialog image-path capture."""

from pathlib import Path

import pytest
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QApplication, QDialog

from harrix_swiss_knife.apps.common.dialogs.text_image_source_dialog import TextImageSourceDialog
from harrix_swiss_knife.apps.common.widgets.image_picker import ImagePickerMode


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _write_png(path: Path) -> None:
    image = QImage(2, 2, QImage.Format.Format_ARGB32)
    image.fill(QColor("white"))
    assert image.save(str(path))


def test_text_image_source_dialog_returns_selected_image_paths(qapp: QApplication, tmp_path: Path) -> None:
    """Accepting the images-only picker stores file paths for recognize actions."""
    assert qapp is not None
    png = tmp_path / "scan.png"
    _write_png(png)

    dialog = TextImageSourceDialog(
        None,
        title="Select scan images",
        show_text=False,
        show_images=True,
        images_required=True,
        image_mode=ImagePickerMode.MULTI,
        initial_image_paths=[str(png)],
    )
    dialog._on_accept()

    assert dialog.result() == int(QDialog.DialogCode.Accepted)
    assert [Path(path) for path in dialog.get_image_paths()] == [png]
