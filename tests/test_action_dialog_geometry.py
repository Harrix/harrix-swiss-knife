"""Tests for adaptive action dialog geometry."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QVBoxLayout,
)

from harrix_swiss_knife.actions.dialog_geometry import (
    MIN_DIALOG_HEIGHT,
    apply_adaptive_dialog_size,
    fit_widget_height,
    list_content_height,
)
from harrix_swiss_knife.actions.dialog_widgets import DragDropFileDialog, StandardActionDialog

_DEFAULT = QSize(1024, 768)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _build_list_dialog(choices: list[str]) -> tuple[StandardActionDialog, QSize]:
    dialog = StandardActionDialog(_DEFAULT)
    dialog.setWindowTitle("Test")
    layout = QVBoxLayout()
    layout.addWidget(QLabel("Choose"))

    list_widget = QListWidget()
    list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    for choice in choices:
        list_widget.addItem(QListWidgetItem(choice))
    fit_widget_height(
        list_widget,
        list_content_height(list_widget),
        maximum=_DEFAULT.height() - 160,
    )
    layout.addWidget(list_widget)

    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    layout.addWidget(buttons)
    dialog.setLayout(layout)

    size = apply_adaptive_dialog_size(dialog, layout, target=_DEFAULT, stretch_row=1)
    dialog.set_target_size(size)
    return dialog, size


def test_few_items_dialog_is_shorter_than_default(qapp: QApplication) -> None:  # noqa: ARG001
    dialog, size = _build_list_dialog(["One", "Two", "Three"])
    try:
        assert size.width() == _DEFAULT.width()
        assert size.height() < _DEFAULT.height()
        assert size.height() >= MIN_DIALOG_HEIGHT
        assert dialog.minimumWidth() == _DEFAULT.width()
    finally:
        dialog.close()


def test_many_items_dialog_reaches_default_height(qapp: QApplication) -> None:  # noqa: ARG001
    choices = [f"Item {index}" for index in range(80)]
    dialog, size = _build_list_dialog(choices)
    try:
        assert size.width() == _DEFAULT.width()
        assert size.height() == _DEFAULT.height()
    finally:
        dialog.close()


def test_drag_drop_dialog_starts_compact(qapp: QApplication) -> None:  # noqa: ARG001
    dialog = DragDropFileDialog(
        "Select images to optimize",
        "",
        "Image files (*.png)",
        _DEFAULT,
        with_resize_option=True,
    )
    try:
        assert dialog.width() == _DEFAULT.width() or dialog.size().width() == _DEFAULT.width()
        assert dialog.height() < _DEFAULT.height()
        assert dialog.height() >= MIN_DIALOG_HEIGHT
        assert dialog.files_list.isHidden()
        assert dialog.drop_area.minimumHeight() == 150
    finally:
        dialog.close()


def test_drag_drop_dialog_shows_files_list_after_add(qapp: QApplication) -> None:  # noqa: ARG001
    dialog = DragDropFileDialog("Select files", "", "All Files (*)", _DEFAULT)
    try:
        dialog.add_files(["C:/tmp/a.png", "C:/tmp/b.png"])
        assert not dialog.files_list.isHidden()
        assert dialog.files_list.count() == 2
        assert dialog.height() <= _DEFAULT.height()
    finally:
        dialog.close()


def test_apply_adaptive_dialog_size_keeps_width(qapp: QApplication) -> None:  # noqa: ARG001
    dialog = QDialog()
    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel("Title"))
    list_widget = QListWidget()
    list_widget.addItem("Only one")
    fit_widget_height(list_widget, list_content_height(list_widget), maximum=608)
    layout.addWidget(list_widget)
    layout.addWidget(QDialogButtonBox(QDialogButtonBox.StandardButton.Ok))

    size = apply_adaptive_dialog_size(dialog, layout, target=_DEFAULT, stretch_row=1)
    try:
        assert size.width() == 1024
        assert MIN_DIALOG_HEIGHT <= size.height() <= 768
    finally:
        dialog.close()
