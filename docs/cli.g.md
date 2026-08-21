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
- [🔧 Function `android_group`](#-function-android_group)
- [🔧 Function `android_build`](#-function-android_build)
- [🔧 Function `android_check`](#-function-android_check)
- [🔧 Function `android_format`](#-function-android_format)
- [🔧 Function `android_setup`](#-function-android_setup)
- [🔧 Function `dev_group`](#-function-dev_group)
- [🔧 Function `dev_action_usage`](#-function-dev_action_usage)
- [🔧 Function `dev_build_install_zips`](#-function-dev_build_install_zips)
- [🔧 Function `dev_install_cli`](#-function-dev_install_cli)
- [🔧 Function `dev_install_harrix_notes_explorer_hsk`](#-function-dev_install_harrix_notes_explorer_hsk)
- [🔧 Function `dev_install_private_data`](#-function-dev_install_private_data)
- [🔧 Function `dev_pack_private_data`](#-function-dev_pack_private_data)
- [🔧 Function `file_group`](#-function-file_group)
- [🔧 Function `file_discard_git_changes`](#-function-file_discard_git_changes)
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
- [🔧 Function `markdown_optimize_images_folder`](#-function-markdown_optimize_images_folder)
- [🔧 Function `markdown_regenerate_g_md`](#-function-markdown_regenerate_g_md)
- [🔧 Function `private_data_group`](#-function-private_data_group)
- [🔧 Function `private_data_export`](#-function-private_data_export)
- [🔧 Function `private_data_import`](#-function-private_data_import)
- [🔧 Function `python_group`](#-function-python_group)
- [🔧 Function `python_check`](#-function-python_check)
- [🔧 Function `python_check_all`](#-function-python_check_all)
- [🔧 Function `python_check_project`](#-function-python_check_project)
- [🔧 Function `python_harrix_check`](#-function-python_harrix_check)
- [🔧 Function `python_ruff_sort`](#-function-python_ruff_sort)
- [🔧 Function `python_ruff_sort_docs`](#-function-python_ruff_sort_docs)
- [🔧 Function `site_group`](#-function-site_group)
- [🔧 Function `site_add_submodule`](#-function-site_add_submodule)
- [🔧 Function `site_fix_article_links`](#-function-site_fix_article_links)
- [🔧 Function `site_pull_submodules`](#-function-site_pull_submodules)
- [🔧 Function `site_slice_html_template`](#-function-site_slice_html_template)
- [🔧 Function `text_group`](#-function-text_group)
- [🔧 Function `text_fix_text_with_ai`](#-function-text_fix_text_with_ai)
- [🔧 Function `vscode_group`](#-function-vscode_group)
- [🔧 Function `vscode_check`](#-function-vscode_check)
- [🔧 Function `vscode_format`](#-function-vscode_format)
- [🔧 Function `vscode_sync_notes_explorer`](#-function-vscode_sync_notes_explorer)
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

## 🔧 Function `android_group`

```python
def android_group() -> None
```

Android project build, format, quality checks, and SDK setup.

<details>
<summary>Code:</summary>

```python
def android_group() -> None:
```

</details>

## 🔧 Function `android_build`

```python
def android_build(args: tuple[str, ...], *, build_all: bool) -> None
```

Build Android APK for FOLDER (`debug`/[`release`](apps/common/audio_recording/recorder.g.md#%EF%B8%8F-method-release), or `android_build_variant` from config).

Examples: `hsk android build ./android`, `hsk android build ./android debug`,
`hsk android build debug` (FOLDER defaults to `.`),
`hsk android build --all`, `hsk android build --all debug`.

<details>
<summary>Code:</summary>

```python
def android_build(args: tuple[str, ...], *, build_all: bool) -> None:
    folder, variant = _parse_android_build_cli_args(args, require_folder=not build_all)
    action = OnAndroidBuild()
    action(folder_path=folder, variant=variant, build_all=build_all, noninteractive=True)
    _finish_timed_action(action)
```

</details>

## 🔧 Function `android_check`

```python
def android_check(folder: Path) -> None
```

Run Spotless check, Detekt, and Android Lint (`qualityCheck`) in FOLDER.

<details>
<summary>Code:</summary>

```python
def android_check(folder: Path) -> None:
    action = OnAndroidCheck()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)
```

</details>

## 🔧 Function `android_format`

```python
def android_format(folder: Path) -> None
```

Format Android Kotlin/Gradle sources via Spotless (ktlint) in FOLDER.

<details>
<summary>Code:</summary>

```python
def android_format(folder: Path) -> None:
    action = OnAndroidFormat()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)
```

</details>

## 🔧 Function `android_setup`

```python
def android_setup(*, install_android_studio: bool) -> None
```

Install JDK 17 and Android SDK for the `android/` module.

<details>
<summary>Code:</summary>

```python
def android_setup(*, install_android_studio: bool) -> None:
    action = OnAndroidSetupSdk()
    action(install_android_studio=install_android_studio, noninteractive=True)
    _finish_timed_action(action)
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

## 🔧 Function `dev_action_usage`

```python
def dev_action_usage() -> None
```

Show sorted action invocation statistics (unused first).

<details>
<summary>Code:</summary>

```python
def dev_action_usage() -> None:
    action = OnShowActionUsageStats()
    action(noninteractive=True)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `dev_build_install_zips`

```python
def dev_build_install_zips(*, no_wipe: bool, skip_binaries: bool, skip_installers: bool, skip_repos: bool, skip_uv_cache: bool, no_exes: bool, no_zips: bool, no_open: bool, clean_logs: bool) -> None
```

Run the Python installer-EXE pipeline (Windows) and optionally open `install/`.

<details>
<summary>Code:</summary>

```python
def dev_build_install_zips(
    *,
    no_wipe: bool,
    skip_binaries: bool,
    skip_installers: bool,
    skip_repos: bool,
    skip_uv_cache: bool,
    no_exes: bool,
    no_zips: bool,
    no_open: bool,
    clean_logs: bool,
) -> None:
    action = OnBuildInstallZips()
    action(
        noninteractive=True,
        no_wipe=no_wipe,
        skip_binaries=skip_binaries,
        skip_installers=skip_installers,
        skip_repos=skip_repos,
        skip_uv_cache=skip_uv_cache,
        no_exes=no_exes,
        no_zips=no_zips,
        no_open=no_open,
        clean_logs=clean_logs,
    )
    _finish_timed_action(action)
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
    action(noninteractive=True)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `dev_install_harrix_notes_explorer_hsk`

```python
def dev_install_harrix_notes_explorer_hsk(editor: str, *, with_public: bool) -> None
```

Install HSK into EDITOR; sync public repo via OnSyncHarrixNotesExplorer first (Windows only).

<details>
<summary>Code:</summary>

```python
def dev_install_harrix_notes_explorer_hsk(editor: str, *, with_public: bool) -> None:
    action = OnInstallHarrixNotesExplorerExtension()
    action(editor=editor, noninteractive=True, with_public=with_public)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `dev_install_private_data`

```python
def dev_install_private_data(zip_path: Path | None, *, api_keys: bool, fitness: bool) -> None
```

Alias for `private-data import`.

<details>
<summary>Code:</summary>

```python
def dev_install_private_data(zip_path: Path | None, *, api_keys: bool, fitness: bool) -> None:
    _invoke_transfer_private_data(mode="import", zip_path=zip_path, api_keys=api_keys, fitness=fitness)
```

</details>

## 🔧 Function `dev_pack_private_data`

```python
def dev_pack_private_data(zip_path: Path | None, *, api_keys: bool, fitness: bool) -> None
```

Alias for `private-data export`.

<details>
<summary>Code:</summary>

```python
def dev_pack_private_data(zip_path: Path | None, *, api_keys: bool, fitness: bool) -> None:
    _invoke_transfer_private_data(mode="export", zip_path=zip_path, api_keys=api_keys, fitness=fitness)
```

</details>

## 🔧 Function `file_group`

```python
def file_group() -> None
```

File-operation commands.

<details>
<summary>Code:</summary>

```python
def file_group() -> None:
```

</details>

## 🔧 Function `file_discard_git_changes`

```python
def file_discard_git_changes(folder: Path, *, status_only: bool) -> None
```

Discard uncommitted changes in all Git repos under FOLDER (same as tray action).

<details>
<summary>Code:</summary>

```python
def file_discard_git_changes(folder: Path, *, status_only: bool) -> None:
    action = OnDiscardGitChanges()
    action(folder_path=folder, noninteractive=True, status_only=status_only)
    _finish_timed_action(action)
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
def markdown_beautify_md(folder: Path, prose_wrap: str, print_width: int, *, apply_prose_fixes: bool, format_code_blocks: bool) -> None
```

Beautify Markdown under FOLDER (same as tray action Beautify MD in …).

<details>
<summary>Code:</summary>

```python
def markdown_beautify_md(
    folder: Path,
    prose_wrap: str,
    print_width: int,
    *,
    apply_prose_fixes: bool,
    format_code_blocks: bool,
) -> None:
    action = OnBeautifyMd()
    action(
        folder_path=folder,
        noninteractive=True,
        prose_wrap=prose_wrap.lower(),
        print_width=print_width,
        apply_prose_fixes=apply_prose_fixes,
        format_code_blocks=format_code_blocks,
    )
    _finish_timed_action(action)
```

</details>

## 🔧 Function `markdown_beautify_regenerate_g_md`

```python
def markdown_beautify_regenerate_g_md(folder: Path, prose_wrap: str, print_width: int, *, apply_prose_fixes: bool, format_code_blocks: bool) -> None
```

Beautify Markdown under FOLDER and regenerate `g.md` (same as tray action).

<details>
<summary>Code:</summary>

```python
def markdown_beautify_regenerate_g_md(
    folder: Path,
    prose_wrap: str,
    print_width: int,
    *,
    apply_prose_fixes: bool,
    format_code_blocks: bool,
) -> None:
    action = OnBeautifyMdAndRegenerateGMd()
    action(
        folder_path=folder,
        noninteractive=True,
        prose_wrap=prose_wrap.lower(),
        print_width=print_width,
        apply_prose_fixes=apply_prose_fixes,
        format_code_blocks=format_code_blocks,
    )
    _finish_timed_action(action)
```

</details>

## 🔧 Function `markdown_check`

```python
def markdown_check(folder: Path, rules: tuple[str, ...], *, include_g_md: bool) -> None
```

Check MD files in FOLDER with Harrix rules (same as tray action, all rules by default).

<details>
<summary>Code:</summary>

```python
def markdown_check(folder: Path, rules: tuple[str, ...], *, include_g_md: bool) -> None:
    rule_ids = {r.strip() for r in rules if r.strip()} or None
    action = OnCheckMd()
    action(folder_path=folder, rule_ids=rule_ids, include_g_md=include_g_md, noninteractive=True)
    _finish_timed_action(action)
```

</details>

## 🔧 Function `markdown_edit_from_template`

```python
def markdown_edit_from_template(template_name: str | None) -> None
```

Edit an existing Markdown entry using a markdown_templates entry.

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

List markdown_templates as JSON (ID + title + path_target).

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

## 🔧 Function `markdown_optimize_images_folder`

```python
def markdown_optimize_images_folder(folder: Path, max_size: int | None) -> None
```

Optimize images referenced by Markdown files under FOLDER (PNG/AVIF size comparison).

<details>
<summary>Code:</summary>

```python
def markdown_optimize_images_folder(folder: Path, max_size: int | None) -> None:
    action = OnOptimizeImagesInMd()
    action(folder_path=folder, max_size=max_size, noninteractive=True)
    _finish_timed_action(action)
```

</details>

## 🔧 Function `markdown_regenerate_g_md`

```python
def markdown_regenerate_g_md(folder: Path, prose_wrap: str, print_width: int, *, apply_prose_fixes: bool, format_code_blocks: bool) -> None
```

Delete `.g.md`, regenerate, and beautify only `.g.md` (source `.md` unchanged).

<details>
<summary>Code:</summary>

```python
def markdown_regenerate_g_md(
    folder: Path,
    prose_wrap: str,
    print_width: int,
    *,
    apply_prose_fixes: bool,
    format_code_blocks: bool,
) -> None:
    action = OnRegenerateGMd()
    action(
        folder_path=folder,
        noninteractive=True,
        prose_wrap=prose_wrap.lower(),
        print_width=print_width,
        apply_prose_fixes=apply_prose_fixes,
        format_code_blocks=format_code_blocks,
    )
    _finish_timed_action(action)
```

</details>

## 🔧 Function `private_data_group`

```python
def private_data_group() -> None
```

Export or import personal API keys and fitness catalog/images.

<details>
<summary>Code:</summary>

```python
def private_data_group() -> None:
```

</details>

## 🔧 Function `private_data_export`

```python
def private_data_export(zip_path: Path | None, *, api_keys: bool, fitness: bool, api_key_files: tuple[str, ...]) -> None
```

Pack selected private data into a personal ZIP (workouts not included).

<details>
<summary>Code:</summary>

```python
def private_data_export(
    zip_path: Path | None,
    *,
    api_keys: bool,
    fitness: bool,
    api_key_files: tuple[str, ...],
) -> None:
    _invoke_transfer_private_data(
        mode="export",
        zip_path=zip_path,
        api_keys=api_keys or bool(api_key_files),
        fitness=fitness,
        api_key_files=api_key_files,
    )
```

</details>

## 🔧 Function `private_data_import`

```python
def private_data_import(zip_path: Path | None, *, api_keys: bool, fitness: bool) -> None
```

Install selected private data; overlay images and upsert catalog (keeps workouts).

<details>
<summary>Code:</summary>

```python
def private_data_import(zip_path: Path | None, *, api_keys: bool, fitness: bool) -> None:
    _invoke_transfer_private_data(mode="import", zip_path=zip_path, api_keys=api_keys, fitness=fitness)
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

Full check (ty, ruff, pytest, Harrix PY/MD) for one project FOLDER.

<details>
<summary>Code:</summary>

```python
def python_check(folder: Path) -> None:
    action = OnCheckPythonProject()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)
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
    _finish_timed_action(action)
```

</details>

## 🔧 Function `python_check_project`

```python
def python_check_project(folder: Path) -> None
```

Alias for `check` (backward compatibility).

<details>
<summary>Code:</summary>

```python
def python_check_project(folder: Path) -> None:
    action = OnCheckPythonProject()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)
```

</details>

## 🔧 Function `python_harrix_check`

```python
def python_harrix_check(folder: Path) -> None
```

Harrix PY rules and docstring Markdown check (incl. private; errors point at `.py`).

<details>
<summary>Code:</summary>

```python
def python_harrix_check(folder: Path) -> None:
    action = OnHarrixCheckPython()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)
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
    action = OnSortRuffFmtPythonCode()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)
```

</details>

## 🔧 Function `python_ruff_sort_docs`

```python
def python_ruff_sort_docs(folder: Path, *, apply_prose_fixes: bool) -> None
```

Ruff sort, ruff format, sort code, generate docs and format Markdown (same as tray action).

<details>
<summary>Code:</summary>

```python
def python_ruff_sort_docs(folder: Path, *, apply_prose_fixes: bool) -> None:
    action = OnSortRuffFmtDocsPythonCode()
    action(folder_path=folder, noninteractive=True, apply_prose_fixes=apply_prose_fixes)
    _finish_timed_action(action)
```

</details>

## 🔧 Function `site_group`

```python
def site_group() -> None
```

Site repository and content submodule commands.

<details>
<summary>Code:</summary>

```python
def site_group() -> None:
```

</details>

## 🔧 Function `site_add_submodule`

```python
def site_add_submodule(folder: Path) -> None
```

Add content FOLDER as a Git submodule of `path_site_repo`.

<details>
<summary>Code:</summary>

```python
def site_add_submodule(folder: Path) -> None:
    action = OnAddSiteContentSubmodule()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)
```

</details>

## 🔧 Function `site_fix_article_links`

```python
def site_fix_article_links(folder: Path) -> None
```

Fix titles in site article dual links in FOLDER.

<details>
<summary>Code:</summary>

```python
def site_fix_article_links(folder: Path) -> None:
    action = OnFixSiteArticleLinkTitles()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)
```

</details>

## 🔧 Function `site_pull_submodules`

```python
def site_pull_submodules(folder: Path | None) -> None
```

Pull `origin main` in each submodule (`path_site_repo` or FOLDER).

<details>
<summary>Code:</summary>

```python
def site_pull_submodules(folder: Path | None) -> None:
    action = OnPullSiteSubmodules()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)
```

</details>

## 🔧 Function `site_slice_html_template`

```python
def site_slice_html_template(dist_folder: Path, theme_folder: Path, source_html: str) -> None
```

Slice built HTML template DIST_FOLDER into THEME_FOLDER for pyssg.

<details>
<summary>Code:</summary>

```python
def site_slice_html_template(dist_folder: Path, theme_folder: Path, source_html: str) -> None:
    action = OnSliceHtmlTemplate()
    action(
        folder_path=dist_folder,
        output_path=theme_folder,
        source_html=source_html,
        noninteractive=True,
    )
    _finish_timed_action(action)
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
    action(noninteractive=True)
    _exit_if_action_failed(action)
```

</details>

## 🔧 Function `vscode_group`

```python
def vscode_group() -> None
```

VS Code extension format, quality checks, and public-repo sync.

<details>
<summary>Code:</summary>

```python
def vscode_group() -> None:
```

</details>

## 🔧 Function `vscode_check`

```python
def vscode_check() -> None
```

Run Biome check for `vscode/harrix-notes-explorer-hsk/`.

<details>
<summary>Code:</summary>

```python
def vscode_check() -> None:
    action = OnVscodeCheck()
    action(noninteractive=True)
    _finish_timed_action(action)
```

</details>

## 🔧 Function `vscode_format`

```python
def vscode_format() -> None
```

Format VS Code extension sources via Biome (`npm run format`).

<details>
<summary>Code:</summary>

```python
def vscode_format() -> None:
    action = OnVscodeFormat()
    action(noninteractive=True)
    _finish_timed_action(action)
```

</details>

## 🔧 Function `vscode_sync_notes_explorer`

```python
def vscode_sync_notes_explorer() -> None
```

Sync `vscode/harrix-notes-explorer-hsk` into public `path_harrix_notes_explorer` repo.

<details>
<summary>Code:</summary>

```python
def vscode_sync_notes_explorer() -> None:
    action = OnSyncHarrixNotesExplorer()
    action(noninteractive=True)
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
