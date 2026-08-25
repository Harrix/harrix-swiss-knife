"""Export Qt table models to CSV or Excel (.xlsx)."""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Literal
from xml.sax.saxutils import escape

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog

from harrix_swiss_knife.apps.common import message_box

if TYPE_CHECKING:
    from PySide6.QtCore import QAbstractItemModel
    from PySide6.QtWidgets import QWidget

_FILTER_CSV = "CSV (*.csv)"
_FILTER_XLSX = "Excel (*.xlsx)"
_INVALID_SHEET_CHARS = set(r":\/?*[]")


def collect_display_table(model: QAbstractItemModel) -> tuple[list[str], list[list[str]]]:
    """Return header labels and display-role cell text from `model`."""
    columns = model.columnCount()
    headers = [
        str(model.headerData(col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) or "")
        for col in range(columns)
    ]
    rows = [[str(model.data(model.index(row, col)) or "") for col in range(columns)] for row in range(model.rowCount())]
    return headers, rows


def column_letters(index: int) -> str:
    """Return the Excel column letters for a 0-based index (`A`, `B`, … `AA`)."""
    if index < 0:
        msg = "Column index must be >= 0"
        raise ValueError(msg)
    result = ""
    number = index + 1
    while number:
        number, remainder = divmod(number - 1, 26)
        result = chr(65 + remainder) + result
    return result


def export_table_via_dialog(
    parent: QWidget,
    model: QAbstractItemModel | None,
    *,
    prefer: Literal["csv", "xlsx"] = "csv",
    title: str = "Save Table",
    sheet_name: str = "Table",
    csv_delimiter: str = ";",
) -> Path | None:
    """Ask for a path and write the table as CSV or Excel.

    Args:

    - `parent` (`QWidget`): Dialog parent.
    - `model` (`QAbstractItemModel | None`): Table to export.
    - `prefer` (`Literal["csv", "xlsx"]`): Format shown first in the dialog. Defaults to `"csv"`.
    - `title` (`str`): Save-dialog title. Defaults to `"Save Table"`.
    - `sheet_name` (`str`): Excel sheet name. Defaults to `"Table"`.
    - `csv_delimiter` (`str`): CSV delimiter. Defaults to `";"`.

    Returns:

    - `Path | None`: Written file, or `None` when the user cancels or export fails.

    """
    if model is None:
        message_box.warning(parent, "Error", "No data to export")
        return None

    name_filter = f"{_FILTER_XLSX};;{_FILTER_CSV}" if prefer == "xlsx" else f"{_FILTER_CSV};;{_FILTER_XLSX}"
    filename_str, selected_filter = QFileDialog.getSaveFileName(parent, title, "", name_filter)
    if not filename_str:
        return None

    path = Path(filename_str)
    fmt = _format_from_path_or_filter(path, selected_filter, prefer)
    if path.suffix.lower() not in {".csv", ".xlsx"}:
        path = path.with_suffix(".xlsx" if fmt == "xlsx" else ".csv")

    try:
        headers, rows = collect_display_table(model)
        if fmt == "xlsx":
            write_table_xlsx(path, headers, rows, sheet_name=sheet_name)
        else:
            write_table_csv(path, headers, rows, delimiter=csv_delimiter)
    except Exception as exc:
        message_box.warning(parent, "Export Error", f"Failed to export table: {exc}")
        return None
    return path


def sanitize_sheet_name(name: str) -> str:
    """Return a valid Excel sheet name (max 31 characters)."""
    cleaned = "".join("_" if char in _INVALID_SHEET_CHARS else char for char in name.strip()) or "Table"
    return cleaned[:31]


def write_table_csv(
    path: Path,
    headers: list[str],
    rows: list[list[str]],
    *,
    delimiter: str = ";",
) -> None:
    """Write a semicolon-style CSV with quoted cells."""
    with path.open("w", encoding="utf-8", newline="") as file:
        file.write(delimiter.join(_csv_cell(value) for value in headers) + "\n")
        for row in rows:
            file.write(delimiter.join(_csv_cell(value) for value in row) + "\n")


def write_table_xlsx(
    path: Path,
    headers: list[str],
    rows: list[list[str]],
    *,
    sheet_name: str = "Table",
) -> None:
    """Write a minimal Office Open XML workbook Excel can open."""
    sheet = sanitize_sheet_name(sheet_name)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _CONTENT_TYPES)
        archive.writestr("_rels/.rels", _ROOT_RELS)
        archive.writestr("xl/workbook.xml", _workbook_xml(sheet))
        archive.writestr("xl/_rels/workbook.xml.rels", _WORKBOOK_RELS)
        archive.writestr("xl/styles.xml", _STYLES)
        archive.writestr("xl/worksheets/sheet1.xml", _sheet_xml(headers, rows))


def _csv_cell(value: str) -> str:
    escaped = str(value).replace('"', '""')
    return f'"{escaped}"'


def _format_from_path_or_filter(
    path: Path,
    selected_filter: str,
    prefer: Literal["csv", "xlsx"],
) -> Literal["csv", "xlsx"]:
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        return "xlsx"
    if suffix == ".csv":
        return "csv"
    if "xlsx" in selected_filter.lower():
        return "xlsx"
    if "csv" in selected_filter.lower():
        return "csv"
    return prefer


def _sheet_xml(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
        "<sheetData>",
    ]
    lines.append(_xml_row(1, headers))
    for offset, row in enumerate(rows, start=2):
        lines.append(_xml_row(offset, row))
    lines.extend(["</sheetData>", "</worksheet>"])
    return "".join(lines)


def _workbook_xml(sheet_name: str) -> str:
    name = escape(sheet_name, {'"': "&quot;"})
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<sheets><sheet name="{name}" sheetId="1" r:id="rId1"/></sheets>'
        "</workbook>"
    )


def _xml_escape_text(value: str) -> str:
    return escape(value, {'"': "&quot;"})


def _xml_row(row_number: int, values: list[str]) -> str:
    cells: list[str] = []
    for col, value in enumerate(values):
        ref = f"{column_letters(col)}{row_number}"
        text = _xml_escape_text(str(value))
        cells.append(f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{text}</t></is></c>')
    return f'<row r="{row_number}">{"".join(cells)}</row>'


_CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" '
    'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/xl/workbook.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    '<Override PartName="/xl/worksheets/sheet1.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
    '<Override PartName="/xl/styles.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
    "</Types>"
)

_ROOT_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
    'Target="xl/workbook.xml"/>'
    "</Relationships>"
)

_WORKBOOK_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
    'Target="worksheets/sheet1.xml"/>'
    '<Relationship Id="rId2" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
    'Target="styles.xml"/>'
    "</Relationships>"
)

_STYLES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
    '<fills count="2"><fill><patternFill patternType="none"/></fill>'
    '<fill><patternFill patternType="gray125"/></fill></fills>'
    '<borders count="1"><border/></borders>'
    '<cellStyleXfs count="1"><xf/></cellStyleXfs>'
    '<cellXfs count="1"><xf/></cellXfs>'
    "</styleSheet>"
)
