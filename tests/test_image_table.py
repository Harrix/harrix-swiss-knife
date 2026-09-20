"""Tests for AI table extraction from images."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.common.image_table import (
    _layout_table,
    copy_tables_to_clipboard,
    parse_tables_response,
    suggest_xlsx_filename,
    tables_to_html,
    tables_to_tsv,
    write_tables_xlsx,
)
from harrix_swiss_knife.integrations.bothub.image_table import (
    DEFAULT_IMAGE_TABLE_MODEL,
    build_image_table_prompt,
    get_image_table_model,
    get_image_table_prompt_template,
)

_SAMPLE_JSON = """
{
  "title": "Ответственный за реализацию проекта",
  "rows": [
    {
      "cells": [
        {"text": "ФИО полностью", "bold": true, "fill": "#5B8DB8", "color": "#FFFFFF"},
        {"text": "Должность", "bold": true, "fill": "#5B8DB8", "color": "#FFFFFF"},
        {"text": "Телефон", "bold": true, "fill": "#5B8DB8", "color": "#FFFFFF"},
        {"text": "Email", "bold": true, "fill": "#5B8DB8", "color": "#FFFFFF"}
      ]
    },
    {
      "cells": [
        {"text": "Сергиенко Антон Борисович"},
        {"text": "учитель"},
        {"text": false},
        {"text": "sergienko_ab@1532.msk.ru"}
      ]
    }
  ]
}
"""


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_parse_tables_response_keeps_false_as_text() -> None:
    tables = parse_tables_response(_SAMPLE_JSON)
    assert len(tables) == 1
    table = tables[0]
    assert table.title == "Ответственный за реализацию проекта"
    assert table.rows[0][0].bold
    assert table.rows[0][0].fill == "#5B8DB8"
    assert table.rows[1][2].text == "false"
    assert table.rows[1][3].text == "sergienko_ab@1532.msk.ru"


def test_parse_tables_response_reads_fenced_json_and_tables_array() -> None:
    text = """```json
{"tables": [{"title": "A", "rows": [["One", "Two"]]}]}
```"""
    tables = parse_tables_response(text)
    assert len(tables) == 1
    assert tables[0].title == "A"
    assert [cell.text for cell in tables[0].rows[0]] == ["One", "Two"]
    assert tables[0].rows[0][0].bold


def test_tables_to_tsv_and_html_include_title_and_colors() -> None:
    tables = parse_tables_response(_SAMPLE_JSON)
    tsv = tables_to_tsv(tables)
    html = tables_to_html(tables)
    assert tsv.splitlines()[0] == "Ответственный за реализацию проекта"
    assert "учитель" in tsv
    assert "false" in tsv
    assert "#5B8DB8" in html
    assert "sergienko_ab@1532.msk.ru" in html


def test_write_tables_xlsx_writes_styles_and_text(tmp_path: Path) -> None:
    tables = parse_tables_response(_SAMPLE_JSON)
    path = tmp_path / "table.xlsx"
    write_tables_xlsx(path, tables)
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        assert "xl/styles.xml" in names
        workbook = archive.read("xl/workbook.xml").decode("utf-8")
        sheet = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")
        styles = archive.read("xl/styles.xml").decode("utf-8")
    assert "Ответственный" in workbook
    assert "Сергиенко" in sheet
    assert "false" in sheet
    assert "FF5B8DB8" in styles
    assert "mergeCell" in sheet


def test_suggest_xlsx_filename_uses_title(tmp_path: Path) -> None:
    tables = parse_tables_response(_SAMPLE_JSON)
    image = tmp_path / "shot.png"
    assert suggest_xlsx_filename([image], tables).endswith(".xlsx")
    assert "Ответственный" in suggest_xlsx_filename([image], tables)


def test_layout_inserts_columns_before_sidebar_rowspan() -> None:
    tables = parse_tables_response(
        """
{
  "title": "",
  "rows": [
    {"cells": [
      {"text": "Left header", "colspan": 2, "bold": true},
      {"text": "Sidebar", "rowspan": 3, "fill": "#5B8DB8"}
    ]},
    {"cells": [{"text": "A"}, {"text": "B"}]},
    {"cells": [{"text": "C"}, {"text": "D"}, {"text": "E"}]}
  ]
}
"""
    )
    grid, _merges = _layout_table(tables[0])
    texts = [[cell.text if cell is not None else None for cell in row] for row in grid]
    assert all(row[-1] == "Sidebar" for row in texts)
    assert texts[-1][:3] == ["C", "D", "E"]
    html = tables_to_html(tables)
    assert html.count("Sidebar") == 1
    assert 'rowspan="3"' in html


def test_get_image_table_model_defaults_to_gpt_5_6() -> None:
    assert get_image_table_model({}) == DEFAULT_IMAGE_TABLE_MODEL
    assert get_image_table_model({"ai": {"image_table_model": "gpt-5.6"}}) == "gpt-5.6"
    assert get_image_table_model({"ai": {"provider": "openrouter"}}) == f"openai/{DEFAULT_IMAGE_TABLE_MODEL}"


def test_get_image_table_prompt_template_falls_back_to_default() -> None:
    config = {"prompts": {"image_table_to_excel": "Extract table JSON"}}
    assert get_image_table_prompt_template(config) == "Extract table JSON"
    default = get_image_table_prompt_template({})
    assert default is not None
    assert "Return JSON only" in default


def test_build_image_table_prompt_requires_api_key() -> None:
    config = {"prompts": {"image_table_to_excel": "Extract table"}, "bothub": {"api_key": ""}}
    with pytest.raises(ValueError, match="API key"):
        build_image_table_prompt(config)


def test_copy_tables_to_clipboard_sets_text(qapp: QApplication) -> None:  # noqa: ARG001
    tables = parse_tables_response(_SAMPLE_JSON)
    copy_tables_to_clipboard(tables)
    clipboard = QGuiApplication.clipboard()
    assert clipboard is not None
    assert "учитель" in clipboard.text()
    assert "false" in clipboard.text()
