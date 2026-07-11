"""Tests for date extraction from image filenames."""

from harrix_swiss_knife.apps.common.widgets.path_drop_helpers import (
    extract_date_from_filename,
    extract_dates_from_paths,
    resolve_date_from_image_batch,
)


def test_extract_date_from_iso_prefix_with_time() -> None:
    assert extract_date_from_filename("2026-07-10 14.27.19.jpg") == "2026-07-10"


def test_extract_date_from_iso_anywhere_in_stem() -> None:
    assert extract_date_from_filename("IMG_2025-06-01_photo.jpg") == "2025-06-01"


def test_extract_date_from_dot_format() -> None:
    assert extract_date_from_filename("photo_2026.07.10.jpg") == "2026-07-10"


def test_extract_date_from_compact_format() -> None:
    assert extract_date_from_filename("IMG_20260710.jpg") == "2026-07-10"


def test_extract_date_returns_none_for_unrecognized_name() -> None:
    assert extract_date_from_filename("cafe_photo.jpg") is None


def test_extract_dates_from_paths_sorts_unique() -> None:
    paths = ["2026-07-12 a.jpg", "2026-07-10 b.jpg", "2026-07-12 c.jpg"]
    assert extract_dates_from_paths(paths) == ["2026-07-10", "2026-07-12"]


def test_resolve_date_from_image_batch_fill_if_empty() -> None:
    dates = ["2026-07-10", "2026-07-12"]
    assert resolve_date_from_image_batch(dates, overwrite=False, current_is_empty=True) == "2026-07-10"
    assert resolve_date_from_image_batch(dates, overwrite=False, current_is_empty=False) is None


def test_resolve_date_from_image_batch_overwrite() -> None:
    dates = ["2026-07-10", "2026-07-12"]
    assert resolve_date_from_image_batch(dates, overwrite=True, current_is_empty=False) == "2026-07-12"
