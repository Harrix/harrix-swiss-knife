"""Tests for CSV and Excel table export helpers."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common.table_export import (
    collect_display_table,
    column_letters,
    sanitize_sheet_name,
    write_table_csv,
    write_table_xlsx,
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


def test_column_letters() -> None:
    assert column_letters(0) == "A"
    assert column_letters(25) == "Z"
    assert column_letters(26) == "AA"
    assert column_letters(27) == "AB"


def test_sanitize_sheet_name() -> None:
    assert sanitize_sheet_name("Food log") == "Food log"
    assert sanitize_sheet_name("A:B/C") == "A_B_C"
    assert sanitize_sheet_name("") == "Table"
    assert len(sanitize_sheet_name("x" * 40)) == 31


def test_write_table_csv_quotes_cells(tmp_path: Path) -> None:
    path = tmp_path / "table.csv"
    write_table_csv(path, ["Name", "Note"], [["Push-up", 'He said "hi"']], delimiter=";")
    assert path.read_text(encoding="utf-8") == '"Name";"Note"\n"Push-up";"He said ""hi"""\n'


def test_write_table_xlsx_contains_sheet_and_text(tmp_path: Path) -> None:
    path = tmp_path / "table.xlsx"
    write_table_xlsx(path, ["Name", "Value"], [["Squat", "80"]], sheet_name="Process")
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        assert "xl/workbook.xml" in names
        assert "xl/worksheets/sheet1.xml" in names
        workbook = archive.read("xl/workbook.xml").decode("utf-8")
        sheet = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")
    assert 'name="Process"' in workbook
    assert "Squat" in sheet
    assert "80" in sheet
    assert 't="inlineStr"' in sheet


def test_collect_display_table_reads_headers_and_cells(qapp: QApplication) -> None:  # noqa: ARG001
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Exercise", "Type"])
    model.appendRow([QStandardItem("Squat"), QStandardItem("Barbell")])
    headers, rows = collect_display_table(model)
    assert headers == ["Exercise", "Type"]
    assert rows == [["Squat", "Barbell"]]
