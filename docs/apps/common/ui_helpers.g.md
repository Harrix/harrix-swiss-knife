---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ui_helpers.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_white_editor_background`](#-function-apply_white_editor_background)
- [🔧 Function `close_table_editor_if_open`](#-function-close_table_editor_if_open)
- [🔧 Function `enumerate_stripped_non_empty_lines`](#-function-enumerate_stripped_non_empty_lines)
- [🔧 Function `iter_stripped_non_empty_lines`](#-function-iter_stripped_non_empty_lines)
- [🔧 Function `reveal_in_file_explorer`](#-function-reveal_in_file_explorer)

</details>

## 🔧 Function `apply_white_editor_background`

```python
def apply_white_editor_background(editor: QWidget, widget_type_name: str | None = None) -> None
```

Apply an opaque white background stylesheet to an inline editor widget.

Args:

- `editor` (`QWidget`): The editor widget.
- `widget_type_name` (`str | None`): Explicit Qt widget class selector
  (e.g. `QComboBox`). When `None` the actual runtime class name is used.

<details>
<summary>Code:</summary>

```python
def apply_white_editor_background(editor: QWidget, widget_type_name: str | None = None) -> None:
    selector = widget_type_name or type(editor).__name__
    editor.setStyleSheet(f"{selector} {{ background-color: white; }}")
```

</details>

## 🔧 Function `close_table_editor_if_open`

```python
def close_table_editor_if_open(view: QAbstractItemView) -> None
```

Close an open inline cell editor before replacing the table model.

Args:

- `view` (`QAbstractItemView`): Table or list view that may have an active editor.

<details>
<summary>Code:</summary>

```python
def close_table_editor_if_open(view: QAbstractItemView) -> None:
    editor = _active_table_editor(view)
    if editor is None:
        return

    view.closeEditor(editor, QAbstractItemDelegate.EndEditHint.SubmitModelCache)
```

</details>

## 🔧 Function `enumerate_stripped_non_empty_lines`

```python
def enumerate_stripped_non_empty_lines(text: str, start: int = 1) -> Iterator[tuple[int, str]]
```

Yield `(line_number, stripped_line)` pairs for non-empty lines in `text`.

Line numbers correspond to positions in the original text (including blank
lines), so they remain useful for user-facing error messages.

Args:

- `text` (`str`): Input text.
- `start` (`int`): Starting index for the line counter. Defaults to `1`.

Yields:

- `tuple[int, str]`: Original 1-based line number and stripped content.

<details>
<summary>Code:</summary>

```python
def enumerate_stripped_non_empty_lines(text: str, start: int = 1) -> Iterator[tuple[int, str]]:
    for line_num, raw_line in enumerate(text.splitlines(), start):
        stripped = raw_line.strip()
        if stripped:
            yield line_num, stripped
```

</details>

## 🔧 Function `iter_stripped_non_empty_lines`

```python
def iter_stripped_non_empty_lines(text: str) -> Iterator[str]
```

Yield stripped, non-empty lines from `text`.

Args:

- `text` (`str`): Input text.

Yields:

- `str`: Each non-empty stripped line.

<details>
<summary>Code:</summary>

```python
def iter_stripped_non_empty_lines(text: str) -> Iterator[str]:
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped:
            yield stripped
```

</details>

## 🔧 Function `reveal_in_file_explorer`

```python
def reveal_in_file_explorer(path: Path | str) -> None
```

Open the system file manager with `path` selected when possible.

Raises:

- `FileNotFoundError`: When `path` does not exist.
- `OSError`: When the file manager cannot be started.

<details>
<summary>Code:</summary>

```python
def reveal_in_file_explorer(path: Path | str) -> None:
    target = Path(path).resolve()
    if not target.exists():
        msg = f"Path not found: {target}"
        raise FileNotFoundError(msg)

    if sys.platform == "win32":
        # Trailing comma after /select is required by explorer.exe.
        subprocess.run(
            ["explorer", "/select,", str(target)],  # noqa: S607
            check=False,
        )
        return

    if sys.platform == "darwin":
        subprocess.run(["open", "-R", str(target)], check=False)  # noqa: S607
        return

    folder = target if target.is_dir() else target.parent
    subprocess.run(["xdg-open", str(folder)], check=False)  # noqa: S607
```

</details>
