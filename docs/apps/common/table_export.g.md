---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `table_export.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `collect_display_table`](#-function-collect_display_table)
- [🔧 Function `column_letters`](#-function-column_letters)
- [🔧 Function `export_table_via_dialog`](#-function-export_table_via_dialog)
- [🔧 Function `sanitize_sheet_name`](#-function-sanitize_sheet_name)
- [🔧 Function `write_table_csv`](#-function-write_table_csv)
- [🔧 Function `write_table_xlsx`](#-function-write_table_xlsx)

</details>

## 🔧 Function `collect_display_table`

```python
def collect_display_table(model: QAbstractItemModel) -> tuple[list[str], list[list[str]]]
```

Return header labels and display-role cell text from `model`.

<details>
<summary>Code:</summary>

```python
def collect_display_table(model: QAbstractItemModel) -> tuple[list[str], list[list[str]]]:
    columns = model.columnCount()
    headers = [
        str(model.headerData(col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) or "")
        for col in range(columns)
    ]
    rows = [[str(model.data(model.index(row, col)) or "") for col in range(columns)] for row in range(model.rowCount())]
    return headers, rows
```

</details>

## 🔧 Function `column_letters`

```python
def column_letters(index: int) -> str
```

Return the Excel column letters for a 0-based index (`A`, `B`, … `AA`).

<details>
<summary>Code:</summary>

```python
def column_letters(index: int) -> str:
    if index < 0:
        msg = "Column index must be >= 0"
        raise ValueError(msg)
    result = ""
    number = index + 1
    while number:
        number, remainder = divmod(number - 1, 26)
        result = chr(65 + remainder) + result
    return result
```

</details>

## 🔧 Function `export_table_via_dialog`

```python
def export_table_via_dialog(parent: QWidget, model: QAbstractItemModel | None, *, prefer: Literal['csv', 'xlsx'] = 'csv', title: str = 'Save Table', sheet_name: str = 'Table', csv_delimiter: str = ';') -> Path | None
```

Ask for a path and write the table as CSV or Excel.

Args:

- `parent` (`QWidget`): Dialog parent.
- `model` (`QAbstractItemModel | None`): Table to export.
- `prefer` (`Literal["csv", "xlsx"]`): Format shown first in the dialog. Defaults to `"csv"`.
- `title` (`str`): Save-dialog title. Defaults to `"Save Table"`.
- `sheet_name` (`str`): Excel sheet name. Defaults to `"Table"`.
- `csv_delimiter` (`str`): CSV delimiter. Defaults to `";"`.

Returns:

- `Path | None`: Written file, or `None` when the user cancels or export fails.

<details>
<summary>Code:</summary>

```python
def export_table_via_dialog(
    parent: QWidget,
    model: QAbstractItemModel | None,
    *,
    prefer: Literal["csv", "xlsx"] = "csv",
    title: str = "Save Table",
    sheet_name: str = "Table",
    csv_delimiter: str = ";",
) -> Path | None:
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
```

</details>

## 🔧 Function `sanitize_sheet_name`

```python
def sanitize_sheet_name(name: str) -> str
```

Return a valid Excel sheet name (max 31 characters).

<details>
<summary>Code:</summary>

```python
def sanitize_sheet_name(name: str) -> str:
    cleaned = "".join("_" if char in _INVALID_SHEET_CHARS else char for char in name.strip()) or "Table"
    return cleaned[:31]
```

</details>

## 🔧 Function `write_table_csv`

```python
def write_table_csv(path: Path, headers: list[str], rows: list[list[str]], *, delimiter: str = ';') -> None
```

Write a semicolon-style CSV with quoted cells.

<details>
<summary>Code:</summary>

```python
def write_table_csv(
    path: Path,
    headers: list[str],
    rows: list[list[str]],
    *,
    delimiter: str = ";",
) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        file.write(delimiter.join(_csv_cell(value) for value in headers) + "\n")
        for row in rows:
            file.write(delimiter.join(_csv_cell(value) for value in row) + "\n")
```

</details>

## 🔧 Function `write_table_xlsx`

```python
def write_table_xlsx(path: Path, headers: list[str], rows: list[list[str]], *, sheet_name: str = 'Table') -> None
```

Write a minimal Office Open XML workbook Excel can open.

<details>
<summary>Code:</summary>

```python
def write_table_xlsx(
    path: Path,
    headers: list[str],
    rows: list[list[str]],
    *,
    sheet_name: str = "Table",
) -> None:
    sheet = sanitize_sheet_name(sheet_name)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _CONTENT_TYPES)
        archive.writestr("_rels/.rels", _ROOT_RELS)
        archive.writestr("xl/workbook.xml", _workbook_xml(sheet))
        archive.writestr("xl/_rels/workbook.xml.rels", _WORKBOOK_RELS)
        archive.writestr("xl/styles.xml", _STYLES)
        archive.writestr("xl/worksheets/sheet1.xml", _sheet_xml(headers, rows))
```

</details>
