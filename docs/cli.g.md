---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `cli.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `cli`](#-function-cli)
- [🔧 Function `markdown_group`](#-function-markdown_group)
- [🔧 Function `markdown_beautify_regenerate_g_md`](#-function-markdown_beautify_regenerate_g_md)
- [🔧 Function `markdown_new_cases_note`](#-function-markdown_new_cases_note)
- [🔧 Function `markdown_new_diary_note`](#-function-markdown_new_diary_note)
- [🔧 Function `markdown_new_dream_note`](#-function-markdown_new_dream_note)
- [🔧 Function `markdown_new_note`](#-function-markdown_new_note)
- [🔧 Function `markdown_new_note_with_images`](#-function-markdown_new_note_with_images)
- [🔧 Function `python_group`](#-function-python_group)
- [🔧 Function `python_isort_ruff_sort`](#-function-python_isort_ruff_sort)
- [🔧 Function `python_isort_ruff_sort_docs`](#-function-python_isort_ruff_sort_docs)
- [🔧 Function `_cli_action_failed`](#-function-_cli_action_failed)
- [🔧 Function `_ensure_qt_app`](#-function-_ensure_qt_app)
- [🔧 Function `_exit_if_action_failed`](#-function-_exit_if_action_failed)
- [🔧 Function `main`](#-function-main)

</details>

## 🔧 Function `cli`

```python
def cli() -> None
```

Harrix Swiss Knife CLI.

<details>
<summary>Code:</summary>

```python
def cli() -> None:
```

</details>

## 🔧 Function `markdown_group`

```python
def markdown_group() -> None
```

Markdown-related commands.

<details>
<summary>Code:</summary>

```python
def markdown_group() -> None:
```

</details>

## 🔧 Function `markdown_beautify_regenerate_g_md`

```python
def markdown_beautify_regenerate_g_md(folder: Path) -> None
```

Beautify Markdown under FOLDER and regenerate .g.md (same as tray action).

<details>
<summary>Code:</summary>

```python
def markdown_beautify_regenerate_g_md(folder: Path) -> None:
    action = OnBeautifyMdFolderAndRegenerateGMd()
    action(folder_path=folder, noninteractive=True)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `markdown_new_cases_note`

```python
def markdown_new_cases_note() -> None
```

Create a new cases note for the current month (same as tray action).

<details>
<summary>Code:</summary>

```python
def markdown_new_cases_note() -> None:
    _ensure_qt_app()
    action = OnNewMarkdown()
    action.execute_new_diary_cases()
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `markdown_new_diary_note`

```python
def markdown_new_diary_note() -> None
```

Create a new diary note for the current date (same as tray action).

<details>
<summary>Code:</summary>

```python
def markdown_new_diary_note() -> None:
    _ensure_qt_app()
    action = OnNewMarkdown()
    action.execute_new_diary()
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `markdown_new_dream_note`

```python
def markdown_new_dream_note() -> None
```

Create a new dream note for the current date (same as tray action).

<details>
<summary>Code:</summary>

```python
def markdown_new_dream_note() -> None:
    _ensure_qt_app()
    action = OnNewMarkdown()
    action.execute_new_diary_dream()
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `markdown_new_note`

```python
def markdown_new_note(folder: Path | None, name: str | None) -> None
```

Create a new note (interactive, or --folder + --name for VS Code / automation).

<details>
<summary>Code:</summary>

```python
def markdown_new_note(folder: Path | None, name: str | None) -> None:
    _ensure_qt_app()
    action = OnNewMarkdown()
    if folder is not None:
        if not name or not name.strip():
            raise click.UsageError(_USAGE_NAME_WITH_FOLDER)
        action.execute_new_note_at(folder, name.strip(), is_with_images=False)
    else:
        if name:
            raise click.UsageError(_USAGE_FOLDER_WITH_NAME)
        action.execute_new_note()
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `markdown_new_note_with_images`

```python
def markdown_new_note_with_images(folder: Path | None, name: str | None) -> None
```

Create a new note with images (interactive, or --folder + --name).

<details>
<summary>Code:</summary>

```python
def markdown_new_note_with_images(folder: Path | None, name: str | None) -> None:
    _ensure_qt_app()
    action = OnNewMarkdown()
    if folder is not None:
        if not name or not name.strip():
            raise click.UsageError(_USAGE_NAME_WITH_FOLDER)
        action.execute_new_note_at(folder, name.strip(), is_with_images=True)
    else:
        if name:
            raise click.UsageError(_USAGE_FOLDER_WITH_NAME)
        action.execute_new_note_with_images()
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `python_group`

```python
def python_group() -> None
```

Python project formatting (isort, ruff, sort).

<details>
<summary>Code:</summary>

```python
def python_group() -> None:
```

</details>

## 🔧 Function `python_isort_ruff_sort`

```python
def python_isort_ruff_sort(folder: Path) -> None
```

isort, ruff format, sort code in PY files without docs step (same as tray action).

<details>
<summary>Code:</summary>

```python
def python_isort_ruff_sort(folder: Path) -> None:
    action = OnSortIsortFmtPythonCodeFolder()
    action(folder_path=folder, noninteractive=True)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `python_isort_ruff_sort_docs`

```python
def python_isort_ruff_sort_docs(folder: Path) -> None
```

isort, ruff format, sort code, generate docs and format Markdown (same as tray action).

<details>
<summary>Code:</summary>

```python
def python_isort_ruff_sort_docs(folder: Path) -> None:
    action = OnSortIsortFmtDocsPythonCodeFolder()
    action(folder_path=folder, noninteractive=True)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `_cli_action_failed`

```python
def _cli_action_failed(result_lines: list[object]) -> bool
```

Return whether any output line reports failure (❌ prefix, same as tray actions).

<details>
<summary>Code:</summary>

```python
def _cli_action_failed(result_lines: list[object]) -> bool:
    return any(isinstance(line, str) and line.strip().startswith("❌") for line in result_lines)
```

</details>

## 🔧 Function `_ensure_qt_app`

```python
def _ensure_qt_app() -> QApplication
```

Ensure a QApplication exists (required for interactive dialogs).

<details>
<summary>Code:</summary>

```python
def _ensure_qt_app() -> QApplication:
    app = cast("QApplication | None", QApplication.instance())
    if app is None:
        app = QApplication(sys.argv)
    return app
```

</details>

## 🔧 Function `_exit_if_action_failed`

```python
def _exit_if_action_failed(action: object) -> None
```

Exit with code 1 and print action lines to stderr when any line starts with ❌.

<details>
<summary>Code:</summary>

```python
def _exit_if_action_failed(action: object) -> None:
    lines = getattr(action, "result_lines", [])
    if not _cli_action_failed(lines):
        return
    for line in lines:
        print(line, file=sys.stderr)
    sys.exit(1)
```

</details>

## 🔧 Function `main`

```python
def main() -> None
```

Entry point for `harrix-swiss-knife-cli`.

<details>
<summary>Code:</summary>

```python
def main() -> None:
    # When spawned from GUI apps (VS Code/Cursor), stdio can be non-UTF on Windows.
    # Make CLI resilient to emoji/status lines.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")  # type: ignore[attr-defined]
    except Exception as e:
        # Best-effort only; avoid failing CLI if stdio is not reconfigurable.
        print(f"⚠️ Could not reconfigure stdio to UTF-8: {e}", file=sys.stderr)
    cli()
```

</details>
