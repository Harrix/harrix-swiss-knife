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
- [🔧 Function `python_group`](#-function-python_group)
- [🔧 Function `python_isort_ruff_sort`](#-function-python_isort_ruff_sort)
- [🔧 Function `python_isort_ruff_sort_docs`](#-function-python_isort_ruff_sort_docs)
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
    if any(line.startswith("❌ Error") for line in action.result_lines):
        sys.exit(1)
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
    if any(line.startswith("❌ Error") for line in action.result_lines):
        sys.exit(1)
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
    if any(line.startswith("❌ Error") for line in action.result_lines):
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
    cli()
```

</details>
