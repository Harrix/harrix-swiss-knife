"""Console entry point for Harrix Swiss Knife actions (Click)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import cast

import click
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.android import OnAndroidBuild, OnAndroidCheck, OnAndroidFormat, OnAndroidSetupSdk
from harrix_swiss_knife.actions.development import (
    OnInstallCli,
    OnShowActionUsageStats,
    OnTransferPrivateData,
)
from harrix_swiss_knife.actions.files import OnDiscardGitChanges
from harrix_swiss_knife.actions.markdown import (
    OnBeautifyMd,
    OnBeautifyMdAndRegenerateGMd,
    OnCheckMd,
    OnNewMarkdown,
    OnOptimizeImagesInMd,
    OnRegenerateGMd,
)
from harrix_swiss_knife.actions.python import (
    OnCheckPythonProject,
    OnCheckPythonProjects,
    OnHarrixCheckPython,
    OnSortRuffFmtDocsPythonCode,
    OnSortRuffFmtPythonCode,
)
from harrix_swiss_knife.actions.site import (
    OnAddSiteContentSubmodule,
    OnFixSiteArticleLinkTitles,
    OnPullSiteSubmodules,
    OnSliceHtmlTemplate,
)
from harrix_swiss_knife.actions.text import OnFixTextWithAI
from harrix_swiss_knife.actions.vscode import (
    OnInstallHarrixNotesExplorerExtension,
    OnSyncHarrixNotesExplorer,
    OnVscodeCheck,
    OnVscodeFormat,
)
from harrix_swiss_knife.paths import get_project_root


@click.group()
def cli() -> None:
    """Harrix Swiss Knife CLI."""


@cli.group("android")
def android_group() -> None:
    """Android project build, format, quality checks, and SDK setup."""


@android_group.command("build")
@click.option(
    "--all",
    "build_all",
    is_flag=True,
    help="Build and install all projects from paths_android_projects sequentially.",
)
@click.argument("args", nargs=-1)
def android_build(args: tuple[str, ...], *, build_all: bool) -> None:
    """Build Android APK for FOLDER (`debug`/`release`, or `android_build_variant` from config).

    Examples: `hsk android build ./android`, `hsk android build ./android debug`,
    `hsk android build debug` (FOLDER defaults to `.`),
    `hsk android build --all`, `hsk android build --all debug`.

    """
    folder, variant = _parse_android_build_cli_args(args, require_folder=not build_all)
    action = OnAndroidBuild()
    action(folder_path=folder, variant=variant, build_all=build_all, noninteractive=True)
    _finish_timed_action(action)


@android_group.command("check")
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def android_check(folder: Path) -> None:
    """Run Spotless check, Detekt, and Android Lint (`qualityCheck`) in FOLDER."""
    action = OnAndroidCheck()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)


@android_group.command("format")
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def android_format(folder: Path) -> None:
    """Format Android Kotlin/Gradle sources via Spotless (ktlint) in FOLDER."""
    action = OnAndroidFormat()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)


@android_group.command("setup")
@click.option(
    "--android-studio",
    "install_android_studio",
    is_flag=True,
    help="Also install Android Studio via winget (optional; needs admin).",
)
def android_setup(*, install_android_studio: bool) -> None:
    """Install JDK 17 and Android SDK for the `android/` module."""
    action = OnAndroidSetupSdk()
    action(install_android_studio=install_android_studio, noninteractive=True)
    _finish_timed_action(action)


@cli.group("dev")
def dev_group() -> None:
    """Development-related commands."""


@dev_group.command("action-usage")
def dev_action_usage() -> None:
    """Show sorted action invocation statistics (unused first)."""
    action = OnShowActionUsageStats()
    action(noninteractive=True)
    _exit_if_action_failed(action)


@dev_group.command("install-cli")
def dev_install_cli() -> None:
    """Install global `hsk` CLI on PATH (`uv tool install -e`)."""
    action = OnInstallCli()
    action(noninteractive=True)
    _exit_if_action_failed(action)


@dev_group.command("install-harrix-notes-explorer-hsk")
@click.argument(
    "editor",
    type=click.Choice(
        OnInstallHarrixNotesExplorerExtension.CLI_EDITOR_CHOICES,
        case_sensitive=False,
    ),
)
@click.option(
    "--with-public",
    is_flag=True,
    help="Also install public harrix-notes-explorer from path_harrix_notes_explorer after HSK.",
)
def dev_install_harrix_notes_explorer_hsk(editor: str, *, with_public: bool) -> None:
    """Install HSK into EDITOR; sync public repo via OnSyncHarrixNotesExplorer first (Windows only)."""
    action = OnInstallHarrixNotesExplorerExtension()
    action(editor=editor, noninteractive=True, with_public=with_public)
    _exit_if_action_failed(action)


@dev_group.command("install-private-data", hidden=True)
@click.option(
    "--zip",
    "zip_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Input ZIP path (default: install/private-data-harrix-swiss-knife.zip).",
)
@click.option("--api-keys", is_flag=True, help="Import API keys only if this flag is set with --fitness omitted.")
@click.option("--fitness", is_flag=True, help="Import exercise catalog and images only if this flag is set.")
def dev_install_private_data(zip_path: Path | None, *, api_keys: bool, fitness: bool) -> None:
    """Alias for `private-data import`."""
    _invoke_transfer_private_data(mode="import", zip_path=zip_path, api_keys=api_keys, fitness=fitness)


@dev_group.command("pack-private-data", hidden=True)
@click.option(
    "--zip",
    "zip_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Output ZIP path (default: install/private-data-harrix-swiss-knife.zip).",
)
@click.option("--api-keys", is_flag=True, help="Include API keys only if this flag is set with --fitness omitted.")
@click.option("--fitness", is_flag=True, help="Include exercise catalog and images only if this flag is set.")
def dev_pack_private_data(zip_path: Path | None, *, api_keys: bool, fitness: bool) -> None:
    """Alias for `private-data export`."""
    _invoke_transfer_private_data(mode="export", zip_path=zip_path, api_keys=api_keys, fitness=fitness)


@cli.group("file")
def file_group() -> None:
    """File-operation commands."""


@file_group.command("discard-git-changes")
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--status",
    "status_only",
    is_flag=True,
    default=False,
    help="Only list repositories with uncommitted changes; do not discard.",
)
def file_discard_git_changes(folder: Path, *, status_only: bool) -> None:
    """Discard uncommitted changes in all Git repos under FOLDER (same as tray action)."""
    action = OnDiscardGitChanges()
    action(folder_path=folder, noninteractive=True, status_only=status_only)
    _finish_timed_action(action)


@cli.group("md")
def markdown_group() -> None:
    """Markdown-related commands."""


@markdown_group.command("add-from-template")
@click.option(
    "--template",
    "template_name",
    type=str,
    default=None,
    help="Template id (without emoji), or full template name from config.",
)
def markdown_add_from_template(template_name: str | None) -> None:
    """Add Markdown using a markdown_templates entry."""
    _ensure_qt_app()
    action = OnNewMarkdown()
    templates = action.config.get("markdown_templates", {})
    if not isinstance(templates, dict):
        templates = {}
    resolved = _resolve_template_name(templates, template_name)
    action.execute_from_template(resolved, suppress_result_ui=True)
    _exit_if_action_failed(action)


@markdown_group.command("beautify-md")
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--prose-wrap",
    type=click.Choice(["always", "never", "preserve"], case_sensitive=False),
    default="preserve",
    show_default=True,
    help="Prettier proseWrap: wrap prose only when always.",
)
@click.option(
    "--print-width",
    type=click.IntRange(1),
    default=80,
    show_default=True,
    help="Prettier printWidth (used when --prose-wrap is always).",
)
@click.option(
    "--no-prose-fixes",
    "apply_prose_fixes",
    is_flag=True,
    flag_value=False,
    default=True,
    help="Disable mechanical MdChecker autofixes in MdFormatter (enabled by default).",
)
@click.option(
    "--no-format-code-blocks",
    "format_code_blocks",
    is_flag=True,
    flag_value=False,
    default=True,
    help="Disable formatting of fenced code block bodies (e.g. ```latex) in MdFormatter.",
)
def markdown_beautify_md(
    folder: Path,
    prose_wrap: str,
    print_width: int,
    *,
    apply_prose_fixes: bool,
    format_code_blocks: bool,
) -> None:
    """Beautify Markdown under FOLDER (same as tray action Beautify MD in …)."""
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


@markdown_group.command("beautify-regenerate-g-md")
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--prose-wrap",
    type=click.Choice(["always", "never", "preserve"], case_sensitive=False),
    default="preserve",
    show_default=True,
    help="Prettier proseWrap: wrap prose only when always.",
)
@click.option(
    "--print-width",
    type=click.IntRange(1),
    default=80,
    show_default=True,
    help="Prettier printWidth (used when --prose-wrap is always).",
)
@click.option(
    "--no-prose-fixes",
    "apply_prose_fixes",
    is_flag=True,
    flag_value=False,
    default=True,
    help="Disable mechanical MdChecker autofixes in MdFormatter (enabled by default).",
)
@click.option(
    "--no-format-code-blocks",
    "format_code_blocks",
    is_flag=True,
    flag_value=False,
    default=True,
    help="Disable formatting of fenced code block bodies (e.g. ```latex) in MdFormatter.",
)
def markdown_beautify_regenerate_g_md(
    folder: Path,
    prose_wrap: str,
    print_width: int,
    *,
    apply_prose_fixes: bool,
    format_code_blocks: bool,
) -> None:
    """Beautify Markdown under FOLDER and regenerate `g.md` (same as tray action)."""
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


@markdown_group.command("check")
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--rule",
    "rules",
    multiple=True,
    help="Rule id to check (e.g. H001). Repeatable. Default: all rules.",
)
@click.option(
    "--include-g-md",
    is_flag=True,
    help="Also check .g.md files (skipped by default).",
)
def markdown_check(folder: Path, rules: tuple[str, ...], *, include_g_md: bool) -> None:
    """Check MD files in FOLDER with Harrix rules (same as tray action, all rules by default)."""
    rule_ids = {r.strip() for r in rules if r.strip()} or None
    action = OnCheckMd()
    action(folder_path=folder, rule_ids=rule_ids, include_g_md=include_g_md, noninteractive=True)
    _finish_timed_action(action)


@markdown_group.command("edit-from-template")
@click.option(
    "--template",
    "template_name",
    type=str,
    default=None,
    help="Template id (without emoji), or full template name from config.",
)
def markdown_edit_from_template(template_name: str | None) -> None:
    """Edit an existing Markdown entry using a markdown_templates entry."""
    _ensure_qt_app()
    action = OnNewMarkdown()
    templates = action.config.get("markdown_templates", {})
    if not isinstance(templates, dict):
        templates = {}
    resolved = _resolve_template_name(templates, template_name)
    action.execute_edit_from_template(resolved, suppress_result_ui=True)
    _exit_if_action_failed(action)


@markdown_group.command("list-templates")
def markdown_list_templates() -> None:
    """List markdown_templates as JSON (ID + title + path_target)."""
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


@markdown_group.command("new-cases-note")
@click.option(
    "--folder",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Cases root folder; default uses path_cases from config.",
)
def markdown_new_cases_note(folder: Path | None) -> None:
    """Create a new cases note for the current month (same as tray action)."""
    _ensure_qt_app()
    action = OnNewMarkdown()
    action.execute_new_diary_cases(cases_folder=folder)
    _exit_if_action_failed(action)


@markdown_group.command("new-diary-note")
@click.option(
    "--folder",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Diary root folder; default uses path_diary from config.",
)
def markdown_new_diary_note(folder: Path | None) -> None:
    """Create a new diary note for the current date (same as tray action)."""
    _ensure_qt_app()
    action = OnNewMarkdown()
    action.execute_new_diary(diary_folder=folder)
    _exit_if_action_failed(action)


@markdown_group.command("new-dream-note")
@click.option(
    "--folder",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Dream journal root folder; default uses path_dream from config.",
)
def markdown_new_dream_note(folder: Path | None) -> None:
    """Create a new dream note for the current date (same as tray action)."""
    _ensure_qt_app()
    action = OnNewMarkdown()
    action.execute_new_diary_dream(dream_folder=folder)
    _exit_if_action_failed(action)


@markdown_group.command("new-note")
@click.option(
    "--folder",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Target folder; with --name, skips save/template dialogs (first beginning template).",
)
@click.option(
    "--name",
    type=str,
    default=None,
    help="Note stem (without .md); requires --folder.",
)
def markdown_new_note(folder: Path | None, name: str | None) -> None:
    """Create a new note (interactive, or --folder + --name for VS Code / automation)."""
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


@markdown_group.command("new-note-with-images")
@click.option(
    "--folder",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Target folder; with --name, skips save/template dialogs (first beginning template).",
)
@click.option(
    "--name",
    type=str,
    default=None,
    help="Note stem (without .md); requires --folder.",
)
def markdown_new_note_with_images(folder: Path | None, name: str | None) -> None:
    """Create a new note with images (interactive, or --folder + --name)."""
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


@markdown_group.command("optimize-images-folder")
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--max-size",
    type=click.IntRange(1),
    default=None,
    help="Max width or height in pixels; images larger on either side are resized. Omit for no limit.",
)
def markdown_optimize_images_folder(folder: Path, max_size: int | None) -> None:
    """Optimize images referenced by Markdown files under FOLDER (PNG/AVIF size comparison)."""
    action = OnOptimizeImagesInMd()
    action(folder_path=folder, max_size=max_size, noninteractive=True)
    _finish_timed_action(action)


@markdown_group.command("regenerate-g-md")
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--prose-wrap",
    type=click.Choice(["always", "never", "preserve"], case_sensitive=False),
    default="preserve",
    show_default=True,
    help="Prettier proseWrap: wrap prose only when always.",
)
@click.option(
    "--print-width",
    type=click.IntRange(1),
    default=80,
    show_default=True,
    help="Prettier printWidth (used when --prose-wrap is always).",
)
@click.option(
    "--no-prose-fixes",
    "apply_prose_fixes",
    is_flag=True,
    flag_value=False,
    default=True,
    help="Disable mechanical MdChecker autofixes in MdFormatter (enabled by default).",
)
@click.option(
    "--no-format-code-blocks",
    "format_code_blocks",
    is_flag=True,
    flag_value=False,
    default=True,
    help="Disable formatting of fenced code block bodies (e.g. ```latex) in MdFormatter.",
)
def markdown_regenerate_g_md(
    folder: Path,
    prose_wrap: str,
    print_width: int,
    *,
    apply_prose_fixes: bool,
    format_code_blocks: bool,
) -> None:
    """Delete `.g.md`, regenerate, and beautify only `.g.md` (source `.md` unchanged)."""
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


@dev_group.group("private-data")
def private_data_group() -> None:
    """Export or import personal API keys and fitness catalog/images."""


@private_data_group.command("export")
@click.option(
    "--zip",
    "zip_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Output ZIP path (default: install/private-data-harrix-swiss-knife.zip).",
)
@click.option(
    "--api-keys",
    is_flag=True,
    help="Include API keys. Omit both --api-keys and --fitness to include every part.",
)
@click.option(
    "--fitness",
    is_flag=True,
    help="Include exercise catalog and images. Omit both flags to include every part.",
)
def private_data_export(zip_path: Path | None, *, api_keys: bool, fitness: bool) -> None:
    """Pack selected private data into a personal ZIP (workouts not included)."""
    _invoke_transfer_private_data(mode="export", zip_path=zip_path, api_keys=api_keys, fitness=fitness)


@private_data_group.command("import")
@click.option(
    "--zip",
    "zip_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Input ZIP path (default: install/private-data-harrix-swiss-knife.zip).",
)
@click.option(
    "--api-keys",
    is_flag=True,
    help="Import API keys. Omit both --api-keys and --fitness to import parts present in the ZIP.",
)
@click.option(
    "--fitness",
    is_flag=True,
    help="Import exercise catalog and images. Omit both flags to import parts present in the ZIP.",
)
def private_data_import(zip_path: Path | None, *, api_keys: bool, fitness: bool) -> None:
    """Install selected private data; overlay images and upsert catalog (keeps workouts)."""
    _invoke_transfer_private_data(mode="import", zip_path=zip_path, api_keys=api_keys, fitness=fitness)


@cli.group("py")
def python_group() -> None:
    """Python project checks and formatting (Harrix check, ruff sort, ruff format)."""


@python_group.command("check")
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def python_check(folder: Path) -> None:
    """Full check (ty, ruff, pytest, Harrix PY/MD) for one project FOLDER."""
    action = OnCheckPythonProject()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)


@python_group.command("check-all")
def python_check_all() -> None:
    """Full check (ty, ruff, pytest, Harrix PY/MD) for all paths_python_projects."""
    action = OnCheckPythonProjects()
    action(noninteractive=True)
    _finish_timed_action(action)


@python_group.command("check-project", hidden=True)
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def python_check_project(folder: Path) -> None:
    """Alias for `check` (backward compatibility)."""
    action = OnCheckPythonProject()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)


@python_group.command("harrix-check")
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def python_harrix_check(folder: Path) -> None:
    """Harrix PY rules and docstring Markdown check (incl. private; errors point at `.py`)."""
    action = OnHarrixCheckPython()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)


@python_group.command("ruff-sort")
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def python_ruff_sort(folder: Path) -> None:
    """Ruff sort, ruff format, sort code in PY files without docs step (same as tray action)."""
    action = OnSortRuffFmtPythonCode()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)


@python_group.command("ruff-sort-docs")
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--no-prose-fixes",
    "apply_prose_fixes",
    is_flag=True,
    flag_value=False,
    default=True,
    help="Disable mechanical MdChecker autofixes in docstring/Markdown formatting (enabled by default).",
)
def python_ruff_sort_docs(folder: Path, *, apply_prose_fixes: bool) -> None:
    """Ruff sort, ruff format, sort code, generate docs and format Markdown (same as tray action)."""
    action = OnSortRuffFmtDocsPythonCode()
    action(folder_path=folder, noninteractive=True, apply_prose_fixes=apply_prose_fixes)
    _finish_timed_action(action)


@cli.group("site")
def site_group() -> None:
    """Site repository and content submodule commands."""


@site_group.command("add-submodule")
@click.argument(
    "folder",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def site_add_submodule(folder: Path) -> None:
    """Add content FOLDER as a Git submodule of `path_site_repo`."""
    action = OnAddSiteContentSubmodule()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)


@site_group.command("fix-article-links")
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def site_fix_article_links(folder: Path) -> None:
    """Fix titles in site article dual links in FOLDER."""
    action = OnFixSiteArticleLinkTitles()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)


@site_group.command("pull-submodules")
@click.argument(
    "folder",
    required=False,
    default=None,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def site_pull_submodules(folder: Path | None) -> None:
    """Pull `origin main` in each submodule (`path_site_repo` or FOLDER)."""
    action = OnPullSiteSubmodules()
    action(folder_path=folder, noninteractive=True)
    _finish_timed_action(action)


@site_group.command("slice-html-template")
@click.argument(
    "dist_folder",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.argument(
    "theme_folder",
    type=click.Path(file_okay=False, path_type=Path),
)
@click.option(
    "--source-html",
    default="article.html",
    show_default=True,
    help="Built HTML page used as the article shell.",
)
def site_slice_html_template(dist_folder: Path, theme_folder: Path, source_html: str) -> None:
    """Slice built HTML template DIST_FOLDER into THEME_FOLDER for pyssg."""
    action = OnSliceHtmlTemplate()
    action(
        folder_path=dist_folder,
        output_path=theme_folder,
        source_html=source_html,
        noninteractive=True,
    )
    _finish_timed_action(action)


@cli.group("text")
def text_group() -> None:
    """Text-related commands (AI, formatting, transformations)."""


@text_group.command("fix-text-with-ai")
def text_fix_text_with_ai() -> None:
    """Fix text with AI via BotHub (opens a dialog for multi-line input)."""
    _ensure_qt_app()
    action = OnFixTextWithAI()
    action(noninteractive=True)
    _exit_if_action_failed(action)


@cli.group("vscode")
def vscode_group() -> None:
    """VS Code extension format, quality checks, and public-repo sync."""


@vscode_group.command("check")
def vscode_check() -> None:
    """Run Biome check for `vscode/harrix-notes-explorer-hsk/`."""
    action = OnVscodeCheck()
    action(noninteractive=True)
    _finish_timed_action(action)


@vscode_group.command("format")
def vscode_format() -> None:
    """Format VS Code extension sources via Biome (`npm run format`)."""
    action = OnVscodeFormat()
    action(noninteractive=True)
    _finish_timed_action(action)


@vscode_group.command("sync-notes-explorer")
def vscode_sync_notes_explorer() -> None:
    """Sync `vscode/harrix-notes-explorer-hsk` into public `path_harrix_notes_explorer` repo."""
    action = OnSyncHarrixNotesExplorer()
    action(noninteractive=True)
    _exit_if_action_failed(action)


def _cli_action_failed(result_lines: list[object]) -> bool:
    """Return whether any output line reports failure (❌ prefix or check error count)."""
    for line in result_lines:
        if not isinstance(line, str):
            continue
        if line.strip().startswith("❌"):
            return True
        if "🔢 Count errors" in line:
            return True
    return False


def _ensure_qt_app() -> QApplication:
    """Ensure a QApplication exists (required for interactive dialogs)."""
    app = cast("QApplication | None", QApplication.instance())
    if app is None:
        app = QApplication(sys.argv)
    _set_qt_app_icon(app)
    return app


def _exit_if_action_failed(action: object) -> None:
    """Exit with code 1 when the action reported failure (lines already printed via `add_line`)."""
    lines = getattr(action, "result_lines", [])
    if not _cli_action_failed(lines):
        return
    sys.exit(1)


def _finish_timed_action(action: object) -> None:
    """Print elapsed time for long-running CLI actions, then exit on failure."""
    add_elapsed = getattr(action, "add_elapsed_time", None)
    if callable(add_elapsed):
        add_elapsed()
    _exit_if_action_failed(action)


def _invoke_transfer_private_data(
    *,
    mode: str,
    zip_path: Path | None,
    api_keys: bool,
    fitness: bool,
) -> None:
    """Run `OnTransferPrivateData` for CLI export/import (including hidden aliases)."""
    action = OnTransferPrivateData()
    kwargs: dict[str, object] = {
        "noninteractive": True,
        "mode": mode,
        "include_api_keys": api_keys,
        "include_fitness": fitness,
        "parts_specified": api_keys or fitness,
    }
    if zip_path is not None:
        kwargs["zip_path"] = zip_path
    action(**kwargs)
    _exit_if_action_failed(action)


def _parse_android_build_cli_args(
    args: tuple[str, ...],
    *,
    require_folder: bool = True,
) -> tuple[Path | None, str | None]:
    """Parse optional FOLDER and debug/release for ``hsk android build``."""
    variants = {name.lower() for name in OnAndroidBuild.CLI_VARIANTS}
    max_args = 2  # optional FOLDER + optional variant
    if len(args) > max_args:
        msg = "Expected at most FOLDER and variant (debug|release)."
        raise click.UsageError(msg)

    folder: Path | None = None
    variant: str | None = None
    for arg in args:
        if arg.lower() in variants and variant is None:
            variant = arg.lower()
            continue
        if folder is None:
            folder = Path(arg)
            continue
        msg = f"Unexpected argument: {arg!r}"
        raise click.UsageError(msg)

    if folder is None:
        if not require_folder:
            return None, variant
        folder = Path()
    if not folder.is_dir():
        msg = f"Folder does not exist: {folder}"
        raise click.BadParameter(msg, param_hint="FOLDER")
    return folder.resolve(), variant


def _resolve_template_name(templates: dict[object, object], template_arg: str | None) -> str | None:
    """Resolve CLI arg to actual markdown_templates key.

    Accepts:

    - exact config key (with emoji)
    - ID without leading emoji token (e.g. `Movie`)

    """
    if not template_arg:
        return None

    arg = str(template_arg).strip()
    if not arg:
        return None

    if arg in templates:
        return arg

    # Build id->name map.
    id_to_names: dict[str, list[str]] = {}
    for k in templates:
        if not isinstance(k, str):
            continue
        tid = _template_id(k)
        id_to_names.setdefault(tid, []).append(k)

    candidates = id_to_names.get(arg, [])
    if not candidates:
        msg = f'Unknown template "{arg}". Use "md list-templates" to see available ids.'
        raise click.UsageError(msg)
    if len(candidates) > 1:
        names = ", ".join(f'"{c}"' for c in candidates)
        msg = f'Template id "{arg}" is ambiguous. Matches: {names}.'
        raise click.UsageError(msg)
    return candidates[0]


def _set_qt_app_icon(app: QApplication) -> None:
    """Best-effort: set window icon for Qt dialogs spawned from CLI."""
    project_root = get_project_root()
    for rel in ("src/harrix_swiss_knife/assets/app.ico", "img/icon.ico"):
        icon_path = project_root / rel
        if icon_path.is_file():
            app.setWindowIcon(QIcon(str(icon_path)))
            return

    # Fallback: resource icon (available in packaged/tray apps).
    app.setWindowIcon(QIcon(":/assets/logo.svg"))


def _template_id(template_name: str) -> str:
    """Return template identifier without leading emoji token.

    Examples:

    - `🎬 Movie` -> `Movie`
    - `📺 Movie: series` -> `Movie: series`
    - `Movie` -> `Movie`

    """
    s = str(template_name).strip()
    if not s:
        return s
    first, sep, rest = s.partition(" ")
    # If the first token has no alphanumeric characters, treat it as an emoji/icon token.
    if first and not any(ch.isalnum() for ch in first) and sep:
        s = rest.strip()
    return " ".join(s.split())


def main() -> None:
    """Entry point for `hsk`."""
    # When spawned from GUI apps (VS Code/Cursor), stdio can be non-UTF on Windows.
    # Make CLI resilient to emoji/status lines.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")  # type: ignore[attr-defined]
    except Exception as e:
        # Best-effort only; avoid failing CLI if stdio is not reconfigurable.
        print(f"⚠️ Could not reconfigure stdio to UTF-8: {e}", file=sys.stderr)
    cli()


_USAGE_NAME_WITH_FOLDER = "--name is required when --folder is set."
_USAGE_FOLDER_WITH_NAME = "--folder is required when --name is set."
