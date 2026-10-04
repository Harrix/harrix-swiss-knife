"""Tests for quick launcher dialog layout helpers."""

import pytest
from PySide6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from harrix_swiss_knife.actions.common.quick_launcher_dialog import QuickLauncherDialog, _layout_spacing_total
from harrix_swiss_knife.qt_action_card_grid import (
    CARD_GRID_CELL_HEIGHT,
    CARD_ICON_SIZE,
    CARD_TEXT_AREA_HEIGHT,
    configure_action_card_grid,
    resolve_action_card_grid_metrics,
    sync_action_card_grid,
)
from harrix_swiss_knife.qt_command_section import style_transparent_icon_grid
from harrix_swiss_knife.qt_markdown_choice_cards import IconChoiceCard, populate_icon_choice_cards


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_layout_spacing_total_without_markdown_panel(qapp: QApplication) -> None:  # noqa: ARG001
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setSpacing(12)

    # header, actions, divider, footer → 3 spacings
    assert _layout_spacing_total(layout, split=False) == 36
    # actions, divider, footer → 2 spacings
    assert _layout_spacing_total(layout, split=False, has_fallback_header=False) == 24


def test_layout_spacing_total_with_markdown_panel(qapp: QApplication) -> None:  # noqa: ARG001
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setSpacing(12)

    # header, actions, divider, markdown, footer → 4 spacings
    assert _layout_spacing_total(layout, split=True) == 48
    # actions, divider, markdown, footer → 3 spacings
    assert _layout_spacing_total(layout, split=True, has_fallback_header=False) == 36


def test_action_card_metrics_shrink_mildly_to_fit_extra_column() -> None:
    assert resolve_action_card_grid_metrics(992, 7) == (134, 61)
    assert resolve_action_card_grid_metrics(1028, 7) == (140, 64)
    assert resolve_action_card_grid_metrics(640, 4) == (154, 64)


def test_quick_launcher_hint_and_size_grip_share_footer(qapp: QApplication) -> None:  # noqa: ARG001
    dialog = QuickLauncherDialog()
    footer = dialog._content_layout.itemAt(dialog._content_layout.count() - 1).layout()

    assert footer is not None
    assert footer.indexOf(dialog._hint) >= 0
    assert footer.indexOf(dialog._size_grip) >= 0
    if dialog._win11_caption:
        assert dialog.findChild(QWidget, "captionBar") is not None
        assert dialog.findChild(QWidget, "captionButtonRow") is not None
        assert dialog._close_button is None
    else:
        assert dialog._close_button is not None
    dialog.close()


def test_action_card_grid_grows_for_wrapped_captions(qapp: QApplication) -> None:
    host = QWidget()
    host.resize(220, 320)
    grid = QListWidget(host)
    configure_action_card_grid(grid)
    grid.setGeometry(0, 0, 200, 300)
    QListWidgetItem("Screenshot region (OCR + translate)", grid)
    host.show()
    qapp.processEvents()

    sync_action_card_grid(grid)
    qapp.processEvents()

    item = grid.item(0)
    assert item is not None
    assert grid.gridSize().height() > CARD_ICON_SIZE + CARD_TEXT_AREA_HEIGHT - 20
    assert item.sizeHint().height() == grid.gridSize().height()
    assert grid.visualItemRect(item).height() >= item.sizeHint().height() - 2
    # Caption needs more than the default one-line text strip under a shrunk icon.
    assert grid.gridSize().height() - grid.iconSize().height() > CARD_TEXT_AREA_HEIGHT
    host.close()


def test_icon_choice_cards_grow_for_wrapped_titles(qapp: QApplication) -> None:
    host = QWidget()
    host.resize(460, 360)
    grid = QListWidget(host)
    configure_action_card_grid(grid)
    style_transparent_icon_grid(grid)
    grid.setGeometry(0, 0, 440, 320)
    populate_icon_choice_cards(
        grid,
        [
            ("📚", "Book"),
            ("📑", "New Marp presentation"),
        ],
    )
    host.show()
    qapp.processEvents()
    sync_action_card_grid(grid)
    qapp.processEvents()

    long_item = grid.item(1)
    assert long_item is not None
    card = grid.itemWidget(long_item)
    assert isinstance(card, IconChoiceCard)
    assert grid.gridSize().height() > CARD_GRID_CELL_HEIGHT
    assert long_item.sizeHint().height() == grid.gridSize().height()
    assert card.height() == grid.gridSize().height()
    assert card.height() >= card.preferred_height(grid.gridSize().width(), grid.iconSize().width())
    host.close()
