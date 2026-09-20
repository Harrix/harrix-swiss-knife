"""Parse AI table JSON and export HTML / TSV / styled Excel."""

from __future__ import annotations

import json
import re
import sys
import zipfile
from dataclasses import dataclass, field
from html import escape
from typing import TYPE_CHECKING, Any
from xml.sax.saxutils import escape as xml_escape

from PySide6.QtCore import QByteArray, QMimeData
from PySide6.QtGui import QGuiApplication

from harrix_swiss_knife.apps.common.table_export import column_letters, sanitize_sheet_name

if TYPE_CHECKING:
    from pathlib import Path

_JSON_OBJECT = re.compile(r"\{[\s\S]*\}")
_HEX_COLOR = re.compile(r"^#?[0-9A-Fa-f]{6}$")
_ILLEGAL_XML = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")
_UNSAFE_FILENAME = re.compile(r'[<>:"/\\|?*]')
_DEFAULT_HEADER_FILL = "#5B8DB8"
_DEFAULT_HEADER_COLOR = "#FFFFFF"
_DEFAULT_BODY_FILL = "#FFFFFF"
_THIN_BORDER = "FFB0B0B0"


@dataclass(frozen=True, slots=True)
class ExtractedTable:
    """A table extracted from an image, with optional caption and column widths."""

    title: str = ""
    rows: list[list[TableCell]] = field(default_factory=list)
    column_widths: list[float] = field(default_factory=list)

    @property
    def column_count(self) -> int:
        """Return the number of columns, counting colspans."""
        return max((_row_width(row) for row in self.rows), default=0)


@dataclass(frozen=True, slots=True)
class TableCell:
    """One table cell, optionally spanning several rows or columns."""

    text: str
    bold: bool = False
    fill: str | None = None
    color: str | None = None
    align: str = "left"
    colspan: int = 1
    rowspan: int = 1


class _StyleBook:
    """Collect unique cell styles and emit `xl/styles.xml`."""

    def __init__(self) -> None:
        self._ids: dict[_Xf, int] = {}
        self._order: list[_Xf] = []
        self._fills: list[str] = []
        self._fonts: list[tuple[str, bool]] = [("000000", False)]

    def to_xml(self) -> str:
        """Return Office Open XML stylesheet with fills, fonts, borders, and xfs."""
        fill_xml = [
            '<fill><patternFill patternType="none"/></fill>',
            '<fill><patternFill patternType="gray125"/></fill>',
        ]
        fill_xml.extend(
            f'<fill><patternFill patternType="solid"><fgColor rgb="FF{rgb}"/></patternFill></fill>'
            for rgb in self._fills
        )
        font_xml = []
        for rgb, bold in self._fonts:
            bold_xml = "<b/>" if bold else ""
            font_xml.append(f'<font>{bold_xml}<sz val="11"/><color rgb="FF{rgb}"/><name val="Calibri"/></font>')
        xf_xml = ['<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1"/>']
        fill_ids = {rgb: index + 2 for index, rgb in enumerate(self._fills)}
        font_ids = {item: index for index, item in enumerate(self._fonts)}
        for xf in self._order:
            fill_id = fill_ids.get(xf.fill, 0)
            font_id = font_ids.get((xf.color, xf.bold), 0)
            xf_xml.append(
                f'<xf numFmtId="0" fontId="{font_id}" fillId="{fill_id}" borderId="1" xfId="0" '
                f'applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">'
                f'<alignment horizontal="{xf.align}" wrapText="1" vertical="center"/></xf>'
            )
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f'<fonts count="{len(font_xml)}">{"".join(font_xml)}</fonts>'
            f'<fills count="{len(fill_xml)}">{"".join(fill_xml)}</fills>'
            '<borders count="2"><border/><border>'
            f'<left style="thin"><color rgb="{_THIN_BORDER}"/></left>'
            f'<right style="thin"><color rgb="{_THIN_BORDER}"/></right>'
            f'<top style="thin"><color rgb="{_THIN_BORDER}"/></top>'
            f'<bottom style="thin"><color rgb="{_THIN_BORDER}"/></bottom>'
            "</border></borders>"
            '<cellStyleXfs count="1"><xf/></cellStyleXfs>'
            f'<cellXfs count="{len(xf_xml)}">{"".join(xf_xml)}</cellXfs>'
            "</styleSheet>"
        )

    def xf_id(self, cell: TableCell) -> int:
        """Return the 1-based cellXf ID for `cell` (0 is the unused default)."""
        fill = cell.fill.removeprefix("#").upper() if cell.fill else ""
        color = (cell.color or "#000000").removeprefix("#").upper()
        xf = _Xf(fill=fill, color=color, bold=cell.bold, align=cell.align)
        existing = self._ids.get(xf)
        if existing is not None:
            return existing
        if fill and fill not in self._fills:
            self._fills.append(fill)
        font = (color, cell.bold)
        if font not in self._fonts:
            self._fonts.append(font)
        xf_id = len(self._order) + 1
        self._ids[xf] = xf_id
        self._order.append(xf)
        return xf_id


@dataclass(frozen=True, slots=True)
class _Xf:
    """Excel cellXf key: fill RGB, font RGB, bold, and horizontal alignment."""

    fill: str
    color: str
    bold: bool
    align: str


def copy_tables_to_clipboard(tables: list[ExtractedTable]) -> None:
    """Copy tables as TSV plus HTML so Excel can paste cells and colors."""
    html = tables_to_html(tables)
    tsv = tables_to_tsv(tables)
    mime = QMimeData()
    mime.setText(tsv)
    mime.setHtml(_html_document(html))
    if sys.platform == "win32":
        mime.setData(
            'application/x-qt-windows-mime;value="HTML Format"',
            QByteArray(_cf_html_bytes(html)),
        )
    clipboard = QGuiApplication.clipboard()
    clipboard.setMimeData(mime)


def parse_tables_response(text: str) -> list[ExtractedTable]:
    """Parse an AI JSON response into one or more extracted tables."""
    payload = _extract_json_object(text)
    if payload is None:
        return []
    raw_tables = payload.get("tables")
    if isinstance(raw_tables, list):
        tables = [_coerce_table(item) for item in raw_tables if isinstance(item, dict)]
        return [table for table in tables if table.rows]
    table = _coerce_table(payload)
    return [table] if table.rows else []


def suggest_xlsx_filename(images: list[Path], tables: list[ExtractedTable]) -> str:
    """Suggest an `.xlsx` filename from the table title or the first image."""
    if tables and tables[0].title:
        cleaned = _UNSAFE_FILENAME.sub("_", tables[0].title).strip(" ._")
        if cleaned:
            return f"{cleaned[:80]}.xlsx"
    if len(images) == 1:
        return f"{images[0].stem}.xlsx"
    return "table.xlsx"


def tables_to_html(tables: list[ExtractedTable]) -> str:
    """Return HTML fragments for Excel-friendly paste."""
    return "".join(_table_html(table) for table in tables)


def tables_to_tsv(tables: list[ExtractedTable]) -> str:
    """Return tab-separated text for a plain Excel paste."""
    blocks: list[str] = []
    for table in tables:
        lines: list[str] = []
        if table.title:
            lines.append(table.title.replace("\t", " ").replace("\n", " "))
        for row in table.rows:
            cells: list[str] = []
            for cell in row:
                cells.append(cell.text.replace("\t", " ").replace("\n", " "))
                cells.extend([""] * max(cell.colspan - 1, 0))
            lines.append("\t".join(cells))
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def write_tables_xlsx(path: Path, tables: list[ExtractedTable]) -> None:
    """Write one styled worksheet per table."""
    if not tables:
        msg = "No table to save"
        raise ValueError(msg)
    book = _StyleBook()
    used_names: set[str] = set()
    sheets: list[tuple[str, str]] = []
    for index, table in enumerate(tables, start=1):
        name = _unique_sheet_name(table.title or f"Table {index}", used_names)
        sheets.append((name, _sheet_xml(table, book)))
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types_xml(len(sheets)))
        archive.writestr("_rels/.rels", _ROOT_RELS)
        archive.writestr("xl/workbook.xml", _workbook_xml([name for name, _xml in sheets]))
        archive.writestr("xl/_rels/workbook.xml.rels", _workbook_rels_xml(len(sheets)))
        archive.writestr("xl/styles.xml", book.to_xml())
        for index, (_name, xml) in enumerate(sheets, start=1):
            archive.writestr(f"xl/worksheets/sheet{index}.xml", xml)


def _align_value(value: object) -> str:
    text = str(value or "left").strip().lower()
    if text in {"center", "right"}:
        return text
    return "left"


def _bool_value(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _cell_from_mapping(raw: dict[str, Any], *, header: bool = False) -> TableCell:
    fill = _normalize_color(raw.get("fill"))
    color = _normalize_color(raw.get("color"))
    if header:
        fill = fill or _DEFAULT_HEADER_FILL
        color = color or _DEFAULT_HEADER_COLOR
    else:
        fill = fill or _DEFAULT_BODY_FILL
    return TableCell(
        text=_cell_text(raw.get("text", raw.get("value", ""))),
        bold=_bool_value(raw.get("bold")) or header,
        fill=fill,
        color=color,
        align=_align_value(raw.get("align")),
        colspan=max(1, _int_value(raw.get("colspan"), 1)),
        rowspan=max(1, _int_value(raw.get("rowspan"), 1)),
    )


def _cell_html(cell: TableCell, *, colspan: int | None = None, rowspan: int | None = None) -> str:
    styles = [
        "border:1px solid #b0b0b0",
        "padding:4px 8px",
        f"text-align:{cell.align}",
        "vertical-align:middle",
    ]
    if cell.fill:
        styles.append(f"background-color:{cell.fill}")
    if cell.color:
        styles.append(f"color:{cell.color}")
    if cell.bold:
        styles.append("font-weight:bold")
    span_cols = colspan if colspan is not None else cell.colspan
    span_rows = rowspan if rowspan is not None else cell.rowspan
    span = ""
    if span_cols > 1:
        span += f' colspan="{span_cols}"'
    if span_rows > 1:
        span += f' rowspan="{span_rows}"'
    tag = "th" if cell.bold else "td"
    return f'<{tag}{span} style="{";".join(styles)}">{escape(cell.text)}</{tag}>'


def _cell_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _cf_html_bytes(fragment: str) -> bytes:
    start_marker = b"<!--StartFragment-->"
    end_marker = b"<!--EndFragment-->"
    body = b"<html>\r\n<body>\r\n" + start_marker + fragment.encode("utf-8") + end_marker + b"\r\n</body>\r\n</html>"
    header_template = b"Version:0.9\r\nStartHTML:%010d\r\nEndHTML:%010d\r\nStartFragment:%010d\r\nEndFragment:%010d\r\n"
    dummy = header_template % (0, 0, 0, 0)
    start_html = len(dummy)
    start_fragment = start_html + body.find(start_marker) + len(start_marker)
    end_fragment = start_html + body.find(end_marker)
    end_html = start_html + len(body)
    return header_template % (start_html, end_html, start_fragment, end_fragment) + body


def _coerce_cells_row(raw_row: object, *, header: bool = False) -> list[TableCell]:
    if isinstance(raw_row, dict):
        cells = raw_row.get("cells", raw_row.get("row", []))
        if isinstance(cells, list):
            return [_coerce_one_cell(item, header=header) for item in cells]
        return []
    if isinstance(raw_row, list):
        return [_coerce_one_cell(item, header=header) for item in raw_row]
    return []


def _coerce_one_cell(raw: object, *, header: bool = False) -> TableCell:
    if isinstance(raw, dict):
        return _cell_from_mapping(raw, header=header)
    return TableCell(
        text=_cell_text(raw),
        bold=header,
        fill=_DEFAULT_HEADER_FILL if header else _DEFAULT_BODY_FILL,
        color=_DEFAULT_HEADER_COLOR if header else None,
    )


def _coerce_table(payload: dict[str, Any]) -> ExtractedTable:
    title = str(payload.get("title") or "").strip()
    column_widths = _column_widths(payload.get("columns"))
    raw_rows = payload.get("rows")
    if not isinstance(raw_rows, list):
        raw_rows = []
    headers = payload.get("headers")
    rows: list[list[TableCell]] = []
    if isinstance(headers, list) and headers:
        rows.append(_coerce_cells_row(headers, header=True))
    for index, raw_row in enumerate(raw_rows):
        header = not rows and index == 0 and not isinstance(headers, list)
        rows.append(_coerce_cells_row(raw_row, header=header))
    return ExtractedTable(title=title, rows=[row for row in rows if row], column_widths=column_widths)


def _column_widths(raw: object) -> list[float]:
    if not isinstance(raw, list):
        return []
    widths: list[float] = []
    for item in raw:
        if isinstance(item, dict):
            widths.append(max(8.0, float(item.get("width") or 12)))
            continue
        try:
            widths.append(max(8.0, float(item)))
        except (TypeError, ValueError):
            widths.append(12.0)
    return widths


def _content_types_xml(sheet_count: int) -> str:
    overrides = [
        (
            '<Override PartName="/xl/workbook.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        ),
        (
            '<Override PartName="/xl/styles.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        ),
    ]
    overrides.extend(
        (
            f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
        for index in range(1, sheet_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        f"{''.join(overrides)}</Types>"
    )


def _estimate_widths(table: ExtractedTable, grid: list[list[TableCell | None]]) -> list[float]:
    count = max(table.column_count, 1)
    widths = list(table.column_widths)
    while len(widths) < count:
        widths.append(12.0)
    for col in range(count):
        longest = 8
        if table.title:
            longest = max(longest, min(len(table.title), 40))
        for row in grid:
            cell = row[col] if col < len(row) else None
            if cell is not None:
                longest = max(longest, min(len(cell.text), 48))
        widths[col] = max(widths[col], min(48.0, longest * 1.15 + 2))
    return widths[:count]


def _extract_json_object(text: str) -> dict[str, Any] | None:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        match = _JSON_OBJECT.search(cleaned)
        if match is None:
            return None
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return data if isinstance(data, dict) else None


def _html_document(fragment: str) -> str:
    return f"<html><head><meta charset='utf-8'></head><body>{fragment}</body></html>"


def _int_value(value: object, default: int) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _is_origin(grid: list[list[TableCell | None]], row: int, col: int, cell: TableCell) -> bool:
    if row > 0 and col < len(grid[row - 1]) and grid[row - 1][col] is cell:
        return False
    return not (col > 0 and grid[row][col - 1] is cell)


def _is_rowspan_continuation(grid: list[list[TableCell | None]], row: int, col: int) -> bool:
    if row <= 0 or col >= len(grid[row]):
        return False
    cell = grid[row][col]
    if cell is None:
        return False
    return col < len(grid[row - 1]) and grid[row - 1][col] is cell


def _layout_table(
    table: ExtractedTable,
) -> tuple[list[list[TableCell | None]], list[tuple[int, int, int, int]]]:
    column_count = max(table.column_count, 1)
    grid: list[list[TableCell | None]] = []

    def pad(row: list[TableCell | None]) -> None:
        if len(row) < column_count:
            row.extend([None] * (column_count - len(row)))

    def ensure_row(index: int) -> None:
        while len(grid) <= index:
            grid.append([None] * column_count)
        pad(grid[index])

    def expand_columns(new_count: int) -> None:
        nonlocal column_count
        if new_count <= column_count:
            return
        extra = new_count - column_count
        column_count = new_count
        for row in grid:
            row.extend([None] * extra)

    def insert_column(at: int, *, stretch_before_row: int) -> None:
        nonlocal column_count
        column_count += 1
        for row_i, row in enumerate(grid):
            row.insert(at, None)
            if row_i < stretch_before_row and at > 0 and row[at - 1] is not None:
                row[at] = row[at - 1]

    def first_continuation(row_index: int, start: int = 0) -> int | None:
        return next(
            (col for col in range(start, column_count) if _is_rowspan_continuation(grid, row_index, col)),
            None,
        )

    for source_row in table.rows:
        row_index = 0
        while True:
            ensure_row(row_index)
            if any(item is None for item in grid[row_index]):
                break
            row_index += 1
        col_index = 0
        for cell in source_row:
            pad(grid[row_index])
            while col_index < column_count and grid[row_index][col_index] is not None:
                col_index += 1
            if col_index >= column_count:
                sidebar = first_continuation(row_index)
                if sidebar is not None:
                    insert_column(sidebar, stretch_before_row=row_index)
                    col_index = sidebar
                else:
                    expand_columns(col_index + cell.colspan)
            end_col = col_index + cell.colspan
            if end_col > column_count:
                sidebar = first_continuation(row_index, col_index)
                if sidebar is not None:
                    for _ in range(end_col - column_count):
                        insert_column(sidebar, stretch_before_row=row_index)
                    end_col = col_index + cell.colspan
                else:
                    expand_columns(end_col)
            end_row = row_index + cell.rowspan
            for fill_row in range(row_index, end_row):
                ensure_row(fill_row)
                pad(grid[fill_row])
                for fill_col in range(col_index, end_col):
                    grid[fill_row][fill_col] = cell
            col_index = end_col
    return grid, _merges_from_grid(grid)


def _merge_cells_xml(merges: list[tuple[int, int, int, int]], *, start_row: int) -> str:
    if not merges:
        return ""
    refs = []
    for start_r, start_c, end_r, end_c in merges:
        excel_start = start_row + start_r
        excel_end = start_row + end_r
        refs.append(f'<mergeCell ref="{column_letters(start_c)}{excel_start}:{column_letters(end_c)}{excel_end}"/>')
    return f'<mergeCells count="{len(refs)}">{"".join(refs)}</mergeCells>'


def _merges_from_grid(grid: list[list[TableCell | None]]) -> list[tuple[int, int, int, int]]:
    merges: list[tuple[int, int, int, int]] = []
    for row, cells in enumerate(grid):
        for col, cell in enumerate(cells):
            if cell is None or not _is_origin(grid, row, col, cell):
                continue
            rowspan, colspan = _span_from_grid(grid, row, col, cell)
            if rowspan > 1 or colspan > 1:
                merges.append((row, col, row + rowspan - 1, col + colspan - 1))
    return merges


def _normalize_color(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if not text.startswith("#"):
        text = f"#{text}"
    if not _HEX_COLOR.match(text):
        return None
    return text.upper()


def _row_width(row: list[TableCell]) -> int:
    return sum(max(cell.colspan, 1) for cell in row)


def _sheet_xml(table: ExtractedTable, book: _StyleBook) -> str:
    grid, merges = _layout_table(table)
    column_count = max((len(row) for row in grid), default=max(table.column_count, 1))
    start_row = 1
    xml_rows: list[str] = []
    excel_merges = list(merges)
    if table.title:
        title_cell = TableCell(text=table.title, bold=True, align="left")
        xml_rows.append(_xml_title_row(table.title, book.xf_id(title_cell)))
        if column_count > 1:
            excel_merges = [(row + 1, col, end_row + 1, end_col) for row, col, end_row, end_col in merges]
            excel_merges.insert(0, (0, 0, 0, column_count - 1))
        start_row = 2
    for grid_row, cells in enumerate(grid):
        excel_row = start_row + grid_row
        parts: list[str] = []
        for col, cell in enumerate(cells):
            if cell is None or not _is_origin(grid, grid_row, col, cell):
                continue
            ref = f"{column_letters(col)}{excel_row}"
            parts.append(
                f'<c r="{ref}" s="{book.xf_id(cell)}" t="inlineStr">'
                f'<is><t xml:space="preserve">{_xml_text(cell.text)}</t></is></c>'
            )
        xml_rows.append(f'<row r="{excel_row}">{"".join(parts)}</row>')
    widths = _estimate_widths(table, grid)
    col_xml = "".join(
        f'<col min="{index}" max="{index}" width="{width:.2f}" customWidth="true"/>'
        for index, width in enumerate(widths, start=1)
    )
    last_row = start_row + max(len(grid), 1) - 1
    if table.title:
        last_row = max(last_row, 1)
    dimension = f'<dimension ref="A1:{column_letters(column_count - 1)}{last_row}"/>'
    merge_xml = _merge_cells_xml(excel_merges, start_row=1)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"{dimension}<cols>{col_xml}</cols><sheetData>{''.join(xml_rows)}</sheetData>{merge_xml}</worksheet>"
    )


def _span_from_grid(grid: list[list[TableCell | None]], row: int, col: int, cell: TableCell) -> tuple[int, int]:
    colspan = 1
    while col + colspan < len(grid[row]) and grid[row][col + colspan] is cell:
        colspan += 1
    rowspan = 1
    while row + rowspan < len(grid) and col < len(grid[row + rowspan]) and grid[row + rowspan][col] is cell:
        rowspan += 1
    return rowspan, colspan


def _table_html(table: ExtractedTable) -> str:
    grid, _merges = _layout_table(table)
    column_count = max((len(row) for row in grid), default=max(table.column_count, 1))
    parts = [
        (
            '<table cellspacing="0" cellpadding="0" '
            'style="border-collapse:collapse;font-family:Calibri,sans-serif;margin-bottom:12px;">'
        )
    ]
    if table.title:
        parts.append(
            f'<tr><td colspan="{column_count}" style="font-weight:bold;padding:6px 8px;text-align:left;">'
            f"{escape(table.title)}</td></tr>"
        )
    for row_index, cells in enumerate(grid):
        parts.append("<tr>")
        for col_index, cell in enumerate(cells):
            if cell is None or not _is_origin(grid, row_index, col_index, cell):
                continue
            rowspan, colspan = _span_from_grid(grid, row_index, col_index, cell)
            parts.append(_cell_html(cell, colspan=colspan, rowspan=rowspan))
        parts.append("</tr>")
    parts.append("</table>")
    return "".join(parts)


def _unique_sheet_name(name: str, used: set[str]) -> str:
    base = sanitize_sheet_name(name)
    candidate = base
    index = 2
    used_folded = {item.casefold() for item in used}
    while candidate.casefold() in used_folded:
        suffix = f" {index}"
        candidate = sanitize_sheet_name(base[: 31 - len(suffix)] + suffix)
        index += 1
    used.add(candidate)
    return candidate


def _workbook_rels_xml(sheet_count: int) -> str:
    rels = [
        f'<Relationship Id="rId{index}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        f'Target="worksheets/sheet{index}.xml"/>'
        for index in range(1, sheet_count + 1)
    ]
    styles_id = sheet_count + 1
    rels.append(
        f'<Relationship Id="rId{styles_id}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{''.join(rels)}</Relationships>"
    )


def _workbook_xml(sheet_names: list[str]) -> str:
    sheet_tags = []
    for index, name in enumerate(sheet_names, start=1):
        sheet_tags.append(f'<sheet name="{_xml_text(name)}" sheetId="{index}" r:id="rId{index}"/>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheets>{''.join(sheet_tags)}</sheets></workbook>"
    )


def _xml_text(value: str) -> str:
    return xml_escape(_ILLEGAL_XML.sub("", value), {'"': "&quot;"})


def _xml_title_row(title: str, style_id: int) -> str:
    return (
        '<row r="1" ht="22" customHeight="true">'
        f'<c r="A1" s="{style_id}" t="inlineStr"><is><t xml:space="preserve">{_xml_text(title)}</t></is></c>'
        "</row>"
    )


_ROOT_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
    'Target="xl/workbook.xml"/>'
    "</Relationships>"
)
