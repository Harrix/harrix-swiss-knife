---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `image_table.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ExtractedTable`](#%EF%B8%8F-class-extractedtable)
  - [⚙️ Method `column_count (property)`](#%EF%B8%8F-method-column_count-property)
- [🏛️ Class `TableCell`](#%EF%B8%8F-class-tablecell)
- [🔧 Function `copy_tables_to_clipboard`](#-function-copy_tables_to_clipboard)
- [🔧 Function `parse_tables_response`](#-function-parse_tables_response)
- [🔧 Function `suggest_xlsx_filename`](#-function-suggest_xlsx_filename)
- [🔧 Function `tables_to_html`](#-function-tables_to_html)
- [🔧 Function `tables_to_tsv`](#-function-tables_to_tsv)
- [🔧 Function `write_tables_xlsx`](#-function-write_tables_xlsx)

</details>

## 🏛️ Class `ExtractedTable`

```python
class ExtractedTable
```

A table extracted from an image, with optional caption and column widths.

<details>
<summary>Code:</summary>

```python
class ExtractedTable:

    title: str = ""
    rows: list[list[TableCell]] = field(default_factory=list)
    column_widths: list[float] = field(default_factory=list)

    @property
    def column_count(self) -> int:
        """Return the number of columns, counting colspans."""
        return max((_row_width(row) for row in self.rows), default=0)
```

</details>

### ⚙️ Method `column_count (property)`

```python
def column_count(self) -> int
```

Return the number of columns, counting colspans.

<details>
<summary>Code:</summary>

```python
def column_count(self) -> int:
        return max((_row_width(row) for row in self.rows), default=0)
```

</details>

## 🏛️ Class `TableCell`

```python
class TableCell
```

One table cell, optionally spanning several rows or columns.

<details>
<summary>Code:</summary>

```python
class TableCell:

    text: str
    bold: bool = False
    fill: str | None = None
    color: str | None = None
    align: str = "left"
    colspan: int = 1
    rowspan: int = 1
```

</details>

## 🔧 Function `copy_tables_to_clipboard`

```python
def copy_tables_to_clipboard(tables: list[ExtractedTable]) -> None
```

Copy tables as TSV plus HTML so Excel can paste cells and colors.

<details>
<summary>Code:</summary>

```python
def copy_tables_to_clipboard(tables: list[ExtractedTable]) -> None:
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
```

</details>

## 🔧 Function `parse_tables_response`

```python
def parse_tables_response(text: str) -> list[ExtractedTable]
```

Parse an AI JSON response into one or more extracted tables.

<details>
<summary>Code:</summary>

```python
def parse_tables_response(text: str) -> list[ExtractedTable]:
    payload = _extract_json_object(text)
    if payload is None:
        return []
    raw_tables = payload.get("tables")
    if isinstance(raw_tables, list):
        tables = [_coerce_table(item) for item in raw_tables if isinstance(item, dict)]
        return [table for table in tables if table.rows]
    table = _coerce_table(payload)
    return [table] if table.rows else []
```

</details>

## 🔧 Function `suggest_xlsx_filename`

```python
def suggest_xlsx_filename(images: list[Path], tables: list[ExtractedTable]) -> str
```

Suggest an `.xlsx` filename from the table title or the first image.

<details>
<summary>Code:</summary>

```python
def suggest_xlsx_filename(images: list[Path], tables: list[ExtractedTable]) -> str:
    if tables and tables[0].title:
        cleaned = _UNSAFE_FILENAME.sub("_", tables[0].title).strip(" ._")
        if cleaned:
            return f"{cleaned[:80]}.xlsx"
    if len(images) == 1:
        return f"{images[0].stem}.xlsx"
    return "table.xlsx"
```

</details>

## 🔧 Function `tables_to_html`

```python
def tables_to_html(tables: list[ExtractedTable]) -> str
```

Return HTML fragments for Excel-friendly paste.

<details>
<summary>Code:</summary>

```python
def tables_to_html(tables: list[ExtractedTable]) -> str:
    return "".join(_table_html(table) for table in tables)
```

</details>

## 🔧 Function `tables_to_tsv`

```python
def tables_to_tsv(tables: list[ExtractedTable]) -> str
```

Return tab-separated text for a plain Excel paste.

<details>
<summary>Code:</summary>

```python
def tables_to_tsv(tables: list[ExtractedTable]) -> str:
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
```

</details>

## 🔧 Function `write_tables_xlsx`

```python
def write_tables_xlsx(path: Path, tables: list[ExtractedTable]) -> None
```

Write one styled worksheet per table.

<details>
<summary>Code:</summary>

```python
def write_tables_xlsx(path: Path, tables: list[ExtractedTable]) -> None:
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
```

</details>
