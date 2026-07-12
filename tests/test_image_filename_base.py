"""Tests for image filename base helpers."""

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication, QDateEdit

from harrix_swiss_knife.apps.common.widgets.image_filename_row import (
    EMPTY_TEMPLATE_DATE,
    compute_image_filename_base,
)
from harrix_swiss_knife.apps.common.widgets.path_drop_helpers import (
    infer_image_filename_base,
    slugify_image_filename_base,
)


def test_slugify_image_filename_base_normalizes_text() -> None:
    assert slugify_image_filename_base('Double B "Coffee"') == "double_b_coffee"
    assert slugify_image_filename_base("Joe's #1 Cafe") == "joe_s_1_cafe"
    assert slugify_image_filename_base("  Flat   white  ") == "flat_white"
    assert slugify_image_filename_base("Кофейня") == "кофейня"
    assert slugify_image_filename_base("") == ""


def test_infer_image_filename_base_from_numbered_paths() -> None:
    paths = ["img/my_cafe_01.jpg", "img/my_cafe_02.png"]
    assert infer_image_filename_base(paths) == "my_cafe"


def test_infer_image_filename_base_from_single_unnumbered_path() -> None:
    assert infer_image_filename_base(["img/photo.jpg"]) == "photo"


def test_infer_image_filename_base_returns_none_for_empty_paths() -> None:
    assert infer_image_filename_base([]) is None
    assert infer_image_filename_base(["", "  "]) is None


def test_compute_image_filename_base_uses_today_for_empty_template_date() -> None:
    app = QApplication.instance() or QApplication([])
    del app
    date_edit = QDateEdit()
    date_edit.setDate(EMPTY_TEMPLATE_DATE)
    base = compute_image_filename_base(date_edit=date_edit, source_widget=None)
    assert base == QDate.currentDate().toString("yyyy-MM-dd")


def test_compute_image_filename_base_uses_actual_date_when_set() -> None:
    app = QApplication.instance() or QApplication([])
    del app
    date_edit = QDateEdit()
    date_edit.setDate(QDate.fromString("2026-07-06", "yyyy-MM-dd"))
    base = compute_image_filename_base(date_edit=date_edit, source_widget=None)
    assert base == "2026-07-06"
