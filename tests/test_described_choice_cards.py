"""Tests for described card scale that fits an almost-extra column."""

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtGui import QContextMenuEvent
from PySide6.QtWidgets import QApplication, QListWidget

from harrix_swiss_knife.qt_action_card_grid import CARD_SPACING
from harrix_swiss_knife.qt_described_choice_cards import (
    DESCRIBED_CARD_HEIGHT,
    DESCRIBED_CARD_MIN_SCALE,
    DESCRIBED_CARD_WIDTH,
    DescribedChoiceCard,
    add_described_action_card,
    configure_described_choice_card_grid,
    described_card_metrics_of,
    metrics_for_scale,
    populate_described_choice_cards,
    resolve_described_card_metrics,
)

LONG_TITLE = "Update and install Harrix Notes Explorer extensions for VSCode and Cursor editors"
LONG_DESCRIPTION = (
    "Build and sync the public Harrix Notes Explorer repository, install HSK, "
    "and optionally install the extension into both editors."
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _pitch(columns: int, cell_width: int = DESCRIBED_CARD_WIDTH) -> int:
    return columns * cell_width + (columns - 1) * CARD_SPACING


def test_resolve_keeps_full_size_when_extra_column_needs_strong_shrink() -> None:
    available = _pitch(5)
    metrics = resolve_described_card_metrics(available)
    assert metrics.scale == 1.0
    assert metrics.width == DESCRIBED_CARD_WIDTH


def test_resolve_shrinks_when_extra_column_almost_fits() -> None:
    # Just short of 6 full-size columns → mild shrink to fit 6.
    available = _pitch(6) - 24
    metrics = resolve_described_card_metrics(available)
    assert DESCRIBED_CARD_MIN_SCALE <= metrics.scale < 1.0
    assert _pitch(6, metrics.width) <= available


def test_resolve_full_size_when_exact_columns_fit() -> None:
    available = _pitch(6)
    metrics = resolve_described_card_metrics(available)
    assert metrics.scale == 1.0
    assert metrics.width == DESCRIBED_CARD_WIDTH


def test_metrics_for_scale_scales_icon_and_fonts() -> None:
    metrics = metrics_for_scale(0.9)
    assert metrics.icon_size < 48
    assert metrics.title_pt <= 11
    assert metrics.desc_pt <= 9
    assert metrics.height < 104


def test_grid_grows_cell_height_for_wrapped_texts(qapp: QApplication) -> None:  # noqa: ARG001
    grid = QListWidget()
    configure_described_choice_card_grid(grid)
    populate_described_choice_cards(grid, [("⬇️", LONG_TITLE, LONG_DESCRIPTION), ("✅", "Short", "Short hint")])

    metrics = described_card_metrics_of(grid)
    assert metrics.height > DESCRIBED_CARD_HEIGHT

    for index in range(grid.count()):
        item = grid.item(index)
        card = grid.itemWidget(item)
        assert isinstance(card, DescribedChoiceCard)
        assert card.content_height(metrics) <= metrics.height
        assert card.height() == metrics.height - CARD_SPACING
        assert item.sizeHint().height() == metrics.height


def test_grid_returns_to_base_height_for_short_texts(qapp: QApplication) -> None:  # noqa: ARG001
    grid = QListWidget()
    configure_described_choice_card_grid(grid)
    populate_described_choice_cards(grid, [("⬇️", LONG_TITLE, LONG_DESCRIPTION)])
    populate_described_choice_cards(grid, [("✅", "Short", "Short hint")])

    assert described_card_metrics_of(grid).height == DESCRIBED_CARD_HEIGHT


def test_card_context_menu_invokes_callback(qapp: QApplication) -> None:
    """Right-click on an item-widget card must reach the context-menu callback."""
    grid = QListWidget()
    configure_described_choice_card_grid(grid)
    received: list[tuple[object, QPoint]] = []
    payload = "action-payload"
    add_described_action_card(
        grid,
        icon="✅",
        title="Test",
        description="Hint",
        user_data=payload,
        on_context_menu=lambda data, pos: received.append((data, pos)),
    )

    item = grid.item(0)
    assert item is not None
    card = grid.itemWidget(item)
    assert isinstance(card, DescribedChoiceCard)

    global_pos = QPoint(120, 80)
    event = QContextMenuEvent(QContextMenuEvent.Reason.Mouse, QPoint(10, 10), global_pos)
    assert qapp.sendEvent(card, event)
    assert received == [(payload, global_pos)]
