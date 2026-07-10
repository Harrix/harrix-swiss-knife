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
- [🔧 Function `dev_group`](#-function-dev_group)
- [🔧 Function `dev_install_cli`](#-function-dev_install_cli)
- [🔧 Function `dev_install_harrix_notes_explorer_hsk`](#-function-dev_install_harrix_notes_explorer_hsk)
- [🔧 Function `markdown_group`](#-function-markdown_group)
- [🔧 Function `markdown_add_from_template`](#-function-markdown_add_from_template)
- [🔧 Function `markdown_beautify_md`](#-function-markdown_beautify_md)
- [🔧 Function `markdown_beautify_regenerate_g_md`](#-function-markdown_beautify_regenerate_g_md)
- [🔧 Function `markdown_check`](#-function-markdown_check)
- [🔧 Function `markdown_edit_from_template`](#-function-markdown_edit_from_template)
- [🔧 Function `markdown_list_templates`](#-function-markdown_list_templates)
- [🔧 Function `markdown_new_cases_note`](#-function-markdown_new_cases_note)
- [🔧 Function `markdown_new_diary_note`](#-function-markdown_new_diary_note)
- [🔧 Function `markdown_new_dream_note`](#-function-markdown_new_dream_note)
- [🔧 Function `markdown_new_note`](#-function-markdown_new_note)
- [🔧 Function `markdown_new_note_with_images`](#-function-markdown_new_note_with_images)
- [🔧 Function `python_group`](#-function-python_group)
- [🔧 Function `python_check`](#-function-python_check)
- [🔧 Function `python_check_all`](#-function-python_check_all)
- [🔧 Function `python_ruff_sort`](#-function-python_ruff_sort)
- [🔧 Function `python_ruff_sort_docs`](#-function-python_ruff_sort_docs)
- [🔧 Function `text_group`](#-function-text_group)
- [🔧 Function `text_fix_text_with_ai`](#-function-text_fix_text_with_ai)
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

## 🔧 Function `dev_group`

```python
def dev_group() -> None
```

Development-related commands.

<details>
<summary>Code:</summary>

```python
def dev_group() -> None:
```

</details>

## 🔧 Function `dev_install_cli`

```python
def dev_install_cli() -> None
```

Install global `hsk` CLI on PATH (`uv tool install -e`).

<details>
<summary>Code:</summary>

```python
def dev_install_cli() -> None:
    action = OnInstallCli()
    action()
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `dev_install_harrix_notes_explorer_hsk`

```python
def dev_install_harrix_notes_explorer_hsk(editor: str) -> None
```

Install Harrix Notes Explorer (HSK) into EDITOR; sync public repo when configured (Windows only).

<details>
<summary>Code:</summary>

```python
def dev_install_harrix_notes_explorer_hsk(editor: str, *, with_public: bool) -> None:
    action = OnInstallHarrixNotesExplorerExtension()
    action(editor=editor, noninteractive=True, with_public=with_public)
    _exit_if_action_failed(action)
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

## 🔧 Function `markdown_add_from_template`

```python
def markdown_add_from_template(template_name: str | None) -> None
```

Add Markdown using a markdown_templates entry.

<details>
<summary>Code:</summary>

```python
def markdown_add_from_template(template_name: str | None) -> None:
    _ensure_qt_app()
    action = OnNewMarkdown()
    templates = action.config.get("markdown_templates", {})
    if not isinstance(templates, dict):
        templates = {}
    resolved = _resolve_template_name(templates, template_name)
    action.execute_from_template(resolved, suppress_result_ui=True)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `markdown_beautify_md`

```python
def markdown_beautify_md(folder: Path, prose_wrap: str, print_width: int) -> None
```

Beautify Markdown under FOLDER (same as tray action Beautify MD in …).

<details>
<summary>Code:</summary>

```python
def markdown_beautify_md(folder: Path, prose_wrap: str, print_width: int) -> None:
    action = OnBeautifyMdFolder()
    action(
        folder_path=folder,
        noninteractive=True,
        prose_wrap=prose_wrap.lower(),
        print_width=print_width,
    )
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `markdown_beautify_regenerate_g_md`

```python
def markdown_beautify_regenerate_g_md(folder: Path, prose_wrap: str, print_width: int) -> None
```

Beautify Markdown under FOLDER and regenerate .g.md (same as tray action).

<details>
<summary>Code:</summary>

```python
def markdown_beautify_regenerate_g_md(folder: Path, prose_wrap: str, print_width: int) -> None:
    action = OnBeautifyMdFolderAndRegenerateGMd()
    action(
        folder_path=folder,
        noninteractive=True,
        prose_wrap=prose_wrap.lower(),
        print_width=print_width,
    )
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `markdown_check`

```python
def markdown_check(folder: Path, rules: tuple[str, ...]) -> None
```

Check MD files in FOLDER with Harrix rules (same as tray action, all rules by default).

<details>
<summary>Code:</summary>

```python
def markdown_check(folder: Path, rules: tuple[str, ...]) -> None:
    rule_ids = {r.strip() for r in rules if r.strip()} or None
    action = OnCheckMdFolder()
    action(folder_path=folder, rule_ids=rule_ids, noninteractive=True)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `markdown_edit_from_template`

```python
def markdown_edit_from_template(template_name: str | None) -> None
```

Edit an existing markdown entry using a markdown_templates entry.

<details>
<summary>Code:</summary>

```python
def markdown_edit_from_template(template_name: str | None) -> None:
    _ensure_qt_app()
    action = OnNewMarkdown()
    templates = action.config.get("markdown_templates", {})
    if not isinstance(templates, dict):
        templates = {}
    resolved = _resolve_template_name(templates, template_name)
    action.execute_edit_from_template(resolved, suppress_result_ui=True)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `markdown_list_templates`

```python
def markdown_list_templates() -> None
```

List markdown_templates as JSON (id + title + path_target).

<details>
<summary>Code:</summary>

```python
def markdown_list_templates() -> None:
    action = OnNewMarkdown()
    templates = action.config.get("markdown_templates", {})

    items: list[dict[str, object]] = []
    for name, cfg in templates.items():
        if not isinstance(cfg, dict):
            continue
        items.append(
            {
                "id": _template_id(str(name)),
                "title": name,
                "path_target": cfg.get("path_target"),
            }
        )

    click.echo(json.dumps(items, ensure_ascii=False))
```

</details>

## 🔧 Function `markdown_new_cases_note`

```python
def markdown_new_cases_note(folder: Path | None) -> None
```

Create a new cases note for the current month (same as tray action).

<details>
<summary>Code:</summary>

```python
def markdown_new_cases_note(folder: Path | None) -> None:
    _ensure_qt_app()
    action = OnNewMarkdown()
    action.execute_new_diary_cases(cases_folder=folder)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `markdown_new_diary_note`

```python
def markdown_new_diary_note(folder: Path | None) -> None
```

Create a new diary note for the current date (same as tray action).

<details>
<summary>Code:</summary>

```python
def markdown_new_diary_note(folder: Path | None) -> None:
    _ensure_qt_app()
    action = OnNewMarkdown()
    action.execute_new_diary(diary_folder=folder)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `markdown_new_dream_note`

```python
def markdown_new_dream_note(folder: Path | None) -> None
```

Create a new dream note for the current date (same as tray action).

<details>
<summary>Code:</summary>

```python
def markdown_new_dream_note(folder: Path | None) -> None:
    _ensure_qt_app()
    action = OnNewMarkdown()
    action.execute_new_diary_dream(dream_folder=folder)
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

Python project checks and formatting (Harrix check, ruff sort, ruff format).

<details>
<summary>Code:</summary>

```python
def python_group() -> None:
```

</details>

## 🔧 Function `python_check`

```python
def python_check(folder: Path) -> None
```

Harrix PY rules check in FOLDER (same as tray action Harrix PY check in …).

<details>
<summary>Code:</summary>

```python
def python_check(folder: Path) -> None:
    action = OnCheckPythonFolder()
    action(folder_path=folder, noninteractive=True)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `python_check_all`

```python
def python_check_all() -> None
```

Full check (ty, ruff, pytest, Harrix PY/MD) for all paths_python_projects.

<details>
<summary>Code:</summary>

```python
def python_check_all() -> None:
    action = OnCheckPythonProjects()
    action(noninteractive=True)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `python_ruff_sort`

```python
def python_ruff_sort(folder: Path) -> None
```

Ruff sort, ruff format, sort code in PY files without docs step (same as tray action).

<details>
<summary>Code:</summary>

```python
def python_ruff_sort(folder: Path) -> None:
    action = OnSortRuffFmtPythonCodeFolder()
    action(folder_path=folder, noninteractive=True)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `python_ruff_sort_docs`

```python
def python_ruff_sort_docs(folder: Path) -> None
```

Ruff sort, ruff format, sort code, generate docs and format Markdown (same as tray action).

<details>
<summary>Code:</summary>

```python
def python_ruff_sort_docs(folder: Path) -> None:
    action = OnSortRuffFmtDocsPythonCodeFolder()
    action(folder_path=folder, noninteractive=True)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `text_group`

```python
def text_group() -> None
```

Text-related commands (AI, formatting, transformations).

<details>
<summary>Code:</summary>

```python
def text_group() -> None:
```

</details>

## 🔧 Function `text_fix_text_with_ai`

```python
def text_fix_text_with_ai() -> None
```

Fix text with AI via BotHub (opens a dialog for multi-line input).

<details>
<summary>Code:</summary>

```python
def text_fix_text_with_ai() -> None:
    _ensure_qt_app()
    action = OnFixTextWithAI()
    action(cli_sync=True)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `main`

```python
def main() -> None
```

Entry point for `hsk`.

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
