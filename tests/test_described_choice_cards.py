"""Tests for described card scale that fits an almost-extra column."""

from harrix_swiss_knife.qt_action_card_grid import CARD_SPACING
from harrix_swiss_knife.qt_described_choice_cards import (
    DESCRIBED_CARD_MIN_SCALE,
    DESCRIBED_CARD_WIDTH,
    metrics_for_scale,
    resolve_described_card_metrics,
)


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
