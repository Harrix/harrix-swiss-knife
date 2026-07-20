"""Actions for Python development and Markdown file management."""

from __future__ import annotations

import contextlib
import re
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

import harrix_pylib as h
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QComboBox, QDateEdit, QDoubleSpinBox, QLineEdit, QSpinBox

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.common.markdown_commit import (
    build_commit_message_for_template,
    resolve_git_repo,
    run_git_commit,
)
from harrix_swiss_knife.actions.common.md_image_optimize import optimize_single_image_for_template
from harrix_swiss_knife.actions.dialog_service import COMMIT_OFFER_CREATE_CODE
from harrix_swiss_knife.filtered_combobox import apply_smart_filtering
from harrix_swiss_knife.template_dialog import TemplateDialog, TemplateField, TemplateParser
from harrix_swiss_knife.template_entry_browser import TemplateEntryBrowserGroup, TemplateExistingEntry

if TYPE_CHECKING:
    from collections.abc import Callable


class OnNewMarkdown(ActionBase):
    """Create new Markdown files using various templates and formats.

    This action provides a unified interface for creating different types of Markdown files.
    It shows a dialog with all available new Markdown commands, allowing the user to
    select which type of Markdown file they want to create.

    """

    icon = "📝"
    title = "New Markdown…"
    bold_title = True
    cli_available = True
    cli_hint = "md --help"
    quick_launcher = True

    _COMMANDS: ClassVar[list[tuple[str, str, str]]] = [
        ("✏️", "Edit from template", "_execute_edit_from_template"),
        ("✍️", "New article", "_execute_new_article"),
        ("📖", "New diary note", "_execute_new_diary"),
        ("🪶", "New memory", "_execute_new_memory"),
        ("💤", "New dream note", "_execute_new_diary_dream"),
        ("📋", "New cases note", "_execute_new_diary_cases"),
        ("📓", "New note", "_execute_new_note"),
        ("📓", "New note with images", "_execute_new_note_with_images"),
        ("❞", "New quotes", "_execute_new_quotes"),
    ]

    def build_picker_choices(self) -> tuple[list[tuple[str, str]], dict[str, tuple[str, str]]]:
        """Build sorted icon choices and dispatch map for the New Markdown picker."""
        templates = self.config.get("markdown_templates", {})

        choices: list[tuple[str, str]] = []
        action_map: dict[str, tuple[str, str]] = {}

        for template_name in templates:
            icon = template_name[0] if template_name else "📝"
            choices.append((icon, template_name))
            action_map[template_name] = ("template", template_name)

        for icon, title, method_name in self._COMMANDS:
            choices.append((icon, title))
            action_map[title] = ("method", method_name)

        choices.sort(key=lambda choice: _markdown_choice_sort_key(choice[1]))
        return choices, action_map

    @ActionBase.handle_exceptions("creating new markdown")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Create new Markdown files using various templates and formats."""
        choices, action_map = self.build_picker_choices()

        selected_choice = self.dialogs.get_choice_from_icons(
            "New Markdown",
            "Choose a command to create new Markdown content:",
            choices,
        )

        if not selected_choice:
            return

        self._dispatch_picker_choice(selected_choice, action_map)

    def execute_edit_from_template(self, template_name: str | None = None, *, suppress_result_ui: bool = False) -> None:
        """Edit an existing Markdown block using a configured template."""
        templates = self.config.get("markdown_templates", {})
        if (
            template_name
            and isinstance(templates.get(template_name), dict)
            and self._template_allows_edit_existing(templates[template_name])
        ):
            self._execute_from_template(template_name=template_name, suppress_result_ui=suppress_result_ui)
            return
        self._execute_edit_from_template(template_name=template_name, suppress_result_ui=suppress_result_ui)

    def execute_from_template(self, template_name: str | None = None, *, suppress_result_ui: bool = False) -> None:
        """Add Markdown content using configured `markdown_templates`."""
        self._execute_from_template(template_name=template_name, suppress_result_ui=suppress_result_ui)

    def execute_new_diary(self, diary_folder: Path | str | None = None) -> None:
        """Create new diary note (same as `New diary note` choice)."""
        self._execute_new_diary(diary_root=diary_folder)

    def execute_new_diary_cases(self, cases_folder: Path | str | None = None) -> None:
        """Create new cases note (same as `New cases note` choice)."""
        self._execute_new_diary_cases(cases_root=cases_folder)

    def execute_new_diary_dream(self, dream_folder: Path | str | None = None) -> None:
        """Create new dream note (same as `New dream note` choice)."""
        self._execute_new_diary_dream(dream_root=dream_folder)

    # Public wrappers (used by CLI).
    def execute_new_note(self) -> None:
        """Create new note (same as `New note` choice)."""
        self._execute_new_note(is_with_images=False)

    def execute_new_note_at(self, folder_path: Path, note_stem: str, *, is_with_images: bool = False) -> None:
        """Create a note under `folder_path` (non-interactive; first beginning template)."""
        self._execute_new_note(is_with_images=is_with_images, folder_path=folder_path, note_stem=note_stem)

    def execute_new_note_with_images(self) -> None:
        """Create new note with images (same as `New note with images` choice)."""
        self._execute_new_note(is_with_images=True)

    def execute_picker_choice(self, title: str) -> None:
        """Run a single New Markdown picker command by title (for quick launcher panel)."""
        _choices, action_map = self.build_picker_choices()
        self._dispatch_picker_choice(title, action_map)

    @staticmethod
    def _build_entry_browser_groups(
        template_config: dict[str, Any],
        template_content: str,
    ) -> list[TemplateEntryBrowserGroup]:
        """Build grouped existing entries for the template dialog browser."""
        path_layout = OnNewMarkdown._template_path_layout(template_config)
        path_target = template_config.get("path_target")
        if not path_target:
            return []

        path_target_path = Path(str(path_target).rstrip("/"))
        groups: list[TemplateEntryBrowserGroup] = []

        if path_layout == "city_note":
            if not path_target_path.is_dir():
                return []
            for city_dir in sorted(path_target_path.iterdir(), key=lambda path: path.name.lower()):
                if not city_dir.is_dir() or city_dir.name.startswith("."):
                    continue
                city_entries = [
                    TemplateExistingEntry(
                        kind="city_note",
                        label=note_md.parent.name,
                        note_md=str(note_md),
                    )
                    for note_md in h.md.iter_note_md_in_folder(city_dir)
                ]
                if city_entries:
                    groups.append(TemplateEntryBrowserGroup(label=city_dir.name, entries=tuple(city_entries)))
            return groups

        if path_layout == "single_file":
            md_files = [h.md.resolve_md_path(path_target_path)]
        else:
            md_files = OnNewMarkdown._list_template_year_md_files(path_target_path)

        for md_file in md_files:
            if not md_file.exists():
                continue
            content = md_file.read_text(encoding="utf-8")
            file_entries = TemplateParser.split_entries(content, template_content)
            if not file_entries:
                continue
            children = tuple(
                TemplateExistingEntry(
                    kind="file_block",
                    label=entry.display_title,
                    target_path=str(md_file),
                    block_start=entry.start,
                    block_end=entry.end,
                    display_title=entry.display_title,
                )
                for entry in file_entries
            )
            groups.append(TemplateEntryBrowserGroup(label=md_file.name, entries=children))

        return groups

    @staticmethod
    def _city_note_field_names(fields: list[TemplateField], template_config: dict[str, Any]) -> tuple[str, str]:
        """Return `(city_field, note_name_field)` from template `@` links or config fallbacks."""
        city_field: str | None = None
        name_field: str | None = None
        for field in fields:
            if field.field_link == TemplateParser.FIELD_LINK_SUBFOLDERS:
                city_field = field.name
            elif field.field_link == TemplateParser.FIELD_LINK_NOTE_NAME:
                name_field = field.name
        city = city_field or str(template_config.get("path_city_field") or "City")
        name = name_field or str(template_config.get("path_note_name_field") or "Title")
        return city, name

    @staticmethod
    def _cleanup_template_staging_dir(staging_dir: Path) -> None:
        """Remove a staging directory and empty staging parents."""
        with contextlib.suppress(OSError):
            if staging_dir.is_dir():
                shutil.rmtree(staging_dir)
        parent = staging_dir.parent
        if parent.name == ".hsk-template-staging" and parent.is_dir() and not any(parent.iterdir()):
            with contextlib.suppress(OSError):
                parent.rmdir()

    @staticmethod
    def _collect_image_paths_from_field_values(
        field_values: dict[str, str],
        fields: list[TemplateField],
    ) -> set[str]:
        """Return normalized image paths referenced in parsed or submitted field values."""
        paths: set[str] = set()
        for field in fields:
            if field.field_type == "image":
                value = (field_values.get(field.name) or "").strip()
                if value:
                    paths.add(value)
            elif field.field_type == "images":
                for part in (field_values.get(field.name) or "").split(","):
                    cleaned = part.strip()
                    if cleaned:
                        paths.add(cleaned)
        return paths

    def _commit_template_entry_edit(
        self,
        *,
        selected_entry: TemplateExistingEntry,
        selected_template: str,  # noqa: ARG002
        template_config: dict[str, Any],
        template_content: str,
        fields: list[TemplateField],
        field_values: dict[str, str],
        _maybe_show_result: Callable[[], None],
    ) -> None:
        """Save changes to an existing entry selected in the template dialog."""
        initial_field_values = self._load_template_entry_field_values(selected_entry, template_content, fields)
        if not initial_field_values:
            self.add_line("❌ Selected entry does not match the template structure.")
            _maybe_show_result()
            return

        result_markdown = TemplateParser.fill_template(template_content, field_values)

        if selected_entry.kind == "city_note":
            if not selected_entry.note_md:
                self.add_line("❌ Invalid city note entry.")
                _maybe_show_result()
                return
            note_md = Path(selected_entry.note_md)
            note_dir = note_md.parent
            existing_image_paths = self._collect_image_paths_from_field_values(initial_field_values, fields)
            result_markdown = self._optimize_template_images(
                template_config,
                fields,
                field_values,
                note_dir,
                result_markdown,
                skip_paths=existing_image_paths,
            )
            try:
                _, new_note_md, new_note_dir, _ = self._resolve_city_note_paths(fields, template_config, field_values)
            except ValueError as exc:
                self.add_line(f"❌ {exc}")
                _maybe_show_result()
                return

            target_md = note_md
            if new_note_md.resolve() != note_md.resolve():
                if new_note_md.exists():
                    self.add_line(f"❌ Target already exists: {new_note_md}")
                    _maybe_show_result()
                    return
                new_note_dir.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(note_dir), str(new_note_dir))
                target_md = new_note_md

            target_md.write_text(result_markdown.rstrip() + "\n", encoding="utf-8")
            h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{target_md}"')
            self.add_line(f"✅ Updated note at {target_md}")
            self.add_line("\nUpdated markdown:")
            self.add_line(result_markdown)
            _maybe_show_result()
            return

        if not selected_entry.target_path or selected_entry.block_start is None or selected_entry.block_end is None:
            self.add_line("❌ Invalid file entry.")
            _maybe_show_result()
            return

        target_path = Path(selected_entry.target_path)
        with Path.open(target_path, encoding="utf-8") as file_handle:
            file_content = file_handle.read()

        image_save_dir = h.md.resolve_md_path(target_path).parent
        existing_image_paths = self._collect_image_paths_from_field_values(initial_field_values, fields)
        result_markdown = self._optimize_template_images(
            template_config,
            fields,
            field_values,
            image_save_dir,
            result_markdown,
            skip_paths=existing_image_paths,
        )

        new_block = result_markdown.strip()
        if (
            selected_entry.block_end < len(file_content)
            and file_content[selected_entry.block_end : selected_entry.block_end + 1] == "\n"
        ):
            new_block += "\n"

        new_content = file_content[: selected_entry.block_start] + new_block + file_content[selected_entry.block_end :]
        with Path.open(target_path, "w", encoding="utf-8") as file_handle:
            file_handle.write(new_content)

        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{target_path}"')
        self.add_line(f"✅ Updated entry in {target_path}")
        self.add_line("\nUpdated markdown:")
        self.add_line(result_markdown)
        _maybe_show_result()

    @staticmethod
    def _create_template_staging_dir(path_target: Path) -> Path:
        """Create a temporary staging folder for images before the final note path is known."""
        staging = path_target / ".hsk-template-staging" / uuid.uuid4().hex
        staging.mkdir(parents=True, exist_ok=True)
        (staging / "img").mkdir(exist_ok=True)
        return staging

    def _dispatch_picker_choice(self, selected_choice: str, action_map: dict[str, tuple[str, str]]) -> None:
        selected_item = action_map.get(selected_choice)
        if not selected_item:
            self.add_line(f"❌ Unknown command selected: {selected_choice}")
            self.show_result()
            return

        item_type, item_value = selected_item

        if item_type == "template":
            self._execute_from_template(template_name=item_value)
        elif item_type == "method":
            method = getattr(self, item_value)
            method()

    def _execute_edit_city_note(
        self,
        *,
        selected_template: str,
        template_config: dict[str, Any],
        template_content: str,
        fields: list[TemplateField],
        _maybe_show_result: Callable[[], None],
    ) -> None:
        """Edit an existing city_note entry."""
        self._resolve_field_link_options(fields, template_config)

        path_target = Path(str(template_config["path_target"]).rstrip("/"))
        if not path_target.is_dir():
            self.add_line(f"❌ Target folder not found: {path_target}")
            _maybe_show_result()
            return

        entries = self._list_city_note_entries(path_target)
        if not entries:
            self.add_line(f"❌ No notes found under {path_target}")
            _maybe_show_result()
            return

        choice_labels = [label for label, _ in entries]
        selected_label = self.dialogs.get_choice_from_list(
            "Select Entry",
            "Choose an entry to edit:",
            choice_labels,
        )
        if not selected_label:
            return

        note_md = next(path for label, path in entries if label == selected_label)
        file_content = note_md.read_text(encoding="utf-8")
        initial_field_values = TemplateParser.parse_block(template_content, file_content, fields)
        if not initial_field_values:
            self.add_line("❌ Selected note does not match the template structure.")
            _maybe_show_result()
            return

        author_to_english: dict[str, str] = {}
        if selected_template == "📖 Book":
            authors_list, author_to_english = self._get_authors_for_book_template(template_config)
            fields = self._replace_author_field_with_combobox(fields, authors_list)

        series_last_records: dict[str, dict[str, str]] = {}
        if selected_template == "📺 Movie: series":
            aggregated = self._get_movies_aggregated_file_from_template_config(template_config)
            if aggregated:
                _, series_last_records = self._parse_series_last_records_from_aggregated_file(aggregated)
                for field in fields:
                    if field.name == "Title":
                        field.field_type = "combobox"
                        field.options = sorted(series_last_records.keys(), key=str.lower)
                        break

        movie_last_records: dict[str, dict[str, str]] = {}
        if selected_template == "🎬 Movie":
            aggregated = self._get_movies_aggregated_file_from_template_config(template_config)
            if aggregated:
                _, movie_last_records = self._parse_movies_last_records_from_aggregated_file(aggregated)
                for field in fields:
                    if field.name == "Title":
                        field.field_type = "combobox"
                        field.options = sorted(movie_last_records.keys(), key=str.lower)
                        break

        dialog_links = self._parse_template_dialog_links(template_config)
        note_dir = note_md.parent
        dialog = TemplateDialog(
            fields=fields,
            title=f"Edit {selected_template}",
            links=dialog_links,
            image_save_dir=note_dir,
            app_config=self.config,
            initial_field_values=initial_field_values,
            is_edit_mode=True,
        )
        self._wire_template_dialog_autofill(
            selected_template,
            dialog,
            series_last_records=series_last_records,
            movie_last_records=movie_last_records,
            author_to_english=author_to_english,
            apply_initial_autofill=False,
        )

        if dialog.exec() != dialog.DialogCode.Accepted:
            self.add_line("❌ Dialog was canceled.")
            _maybe_show_result()
            return

        field_values = dialog.get_field_values()
        if not field_values:
            self.add_line("❌ No field values collected.")
            _maybe_show_result()
            return

        result_markdown = TemplateParser.fill_template(template_content, field_values)
        existing_image_paths = self._collect_image_paths_from_field_values(initial_field_values, fields)
        result_markdown = self._optimize_template_images(
            template_config,
            fields,
            field_values,
            note_dir,
            result_markdown,
            skip_paths=existing_image_paths,
        )

        try:
            _, new_note_md, new_note_dir, _ = self._resolve_city_note_paths(fields, template_config, field_values)
        except ValueError as exc:
            self.add_line(f"❌ {exc}")
            _maybe_show_result()
            return

        target_md = note_md
        if new_note_md.resolve() != note_md.resolve():
            if new_note_md.exists():
                self.add_line(f"❌ Target already exists: {new_note_md}")
                _maybe_show_result()
                return
            new_note_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(note_dir), str(new_note_dir))
            target_md = new_note_md

        target_md.write_text(result_markdown.rstrip() + "\n", encoding="utf-8")
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{target_md}"')
        self.add_line(f"✅ Updated note at {target_md}")
        self.add_line("\nUpdated markdown:")
        self.add_line(result_markdown)
        _maybe_show_result()

    @ActionBase.handle_exceptions("editing markdown from template")
    def _execute_edit_from_template(
        self, *, template_name: str | None = None, suppress_result_ui: bool = False
    ) -> None:
        """Edit an existing Markdown entry using a template form."""

        def _maybe_show_result() -> None:
            if not suppress_result_ui:
                self.show_result()

        templates = self.config.get("markdown_templates", {})
        if not templates:
            self.add_line("❌ No markdown templates configured in config.json")
            _maybe_show_result()
            return

        selected_template = template_name
        if not selected_template:
            template_names = list(templates.keys())
            selected_template = self.dialogs.get_choice_from_list(
                "Select Template",
                "Choose a template to edit:",
                template_names,
            )
            if not selected_template:
                return

        template_config = templates[selected_template]
        template_file = template_config.get("template_file")
        if not template_file:
            self.add_line(f"❌ Template file not specified for '{selected_template}'")
            _maybe_show_result()
            return

        template_path = Path(template_file)
        if not template_path.is_absolute():
            template_path = h.dev.get_project_root() / template_path
        if not template_path.exists():
            self.add_line(f"❌ Template file not found: {template_file}")
            _maybe_show_result()
            return

        with Path.open(template_path, encoding="utf-8") as f:
            template_content = f.read().strip()

        fields, _ = TemplateParser.parse_template(template_content)
        if not fields:
            self.add_line(f"❌ No fields found in template: {template_file}")
            _maybe_show_result()
            return

        self._resolve_field_link_options(fields, template_config)

        path_target = template_config.get("path_target")
        if not path_target:
            self.add_line(f"❌ path_target is not configured for '{selected_template}'")
            _maybe_show_result()
            return

        if self._template_path_layout(template_config) == "city_note":
            self._execute_edit_city_note(
                selected_template=selected_template,
                template_config=template_config,
                template_content=template_content,
                fields=fields,
                _maybe_show_result=_maybe_show_result,
            )
            return

        target_path = self._resolve_template_target_path(template_config)
        if target_path is None or not target_path.exists():
            self.add_line(f"❌ Target file not found: {path_target}")
            _maybe_show_result()
            return

        with Path.open(target_path, encoding="utf-8") as f:
            file_content = f.read()

        entries = TemplateParser.split_entries(file_content, template_content)
        if not entries:
            self.add_line(f"❌ No entries matching template heading level found in {target_path}")
            _maybe_show_result()
            return

        choice_labels = [entry.display_title for entry in entries]
        selected_label = self.dialogs.get_choice_from_list(
            "Select Entry",
            "Choose an entry to edit:",
            choice_labels,
        )
        if not selected_label:
            return

        selected_entry = next(entry for entry in entries if entry.display_title == selected_label)
        initial_field_values = TemplateParser.parse_block(template_content, selected_entry.block_text, fields)
        if not initial_field_values:
            self.add_line("❌ Selected entry does not match the template structure.")
            _maybe_show_result()
            return

        author_to_english: dict[str, str] = {}
        if selected_template == "📖 Book":
            authors_list, author_to_english = self._get_authors_for_book_template(template_config)
            fields = self._replace_author_field_with_combobox(fields, authors_list)

        series_last_records: dict[str, dict[str, str]] = {}
        if selected_template == "📺 Movie: series":
            aggregated = self._get_movies_aggregated_file_from_template_config(template_config)
            if aggregated:
                _, series_last_records = self._parse_series_last_records_from_aggregated_file(aggregated)
                for field in fields:
                    if field.name == "Title":
                        field.field_type = "combobox"
                        field.options = sorted(series_last_records.keys(), key=str.lower)
                        break

        movie_last_records: dict[str, dict[str, str]] = {}
        if selected_template == "🎬 Movie":
            aggregated = self._get_movies_aggregated_file_from_template_config(template_config)
            if aggregated:
                _, movie_last_records = self._parse_movies_last_records_from_aggregated_file(aggregated)
                for field in fields:
                    if field.name == "Title":
                        field.field_type = "combobox"
                        field.options = sorted(movie_last_records.keys(), key=str.lower)
                        break

        dialog_links = self._parse_template_dialog_links(template_config)
        path_target_path = Path(str(path_target).rstrip("/"))
        image_save_dir = h.md.resolve_md_path(path_target_path).parent if path_target_path.suffix == ".md" else None

        dialog = TemplateDialog(
            fields=fields,
            title=f"Edit {selected_template}",
            links=dialog_links,
            image_save_dir=image_save_dir,
            app_config=self.config,
            initial_field_values=initial_field_values,
            is_edit_mode=True,
        )
        self._wire_template_dialog_autofill(
            selected_template,
            dialog,
            series_last_records=series_last_records,
            movie_last_records=movie_last_records,
            author_to_english=author_to_english,
            apply_initial_autofill=False,
        )

        if dialog.exec() != dialog.DialogCode.Accepted:
            self.add_line("❌ Dialog was canceled.")
            _maybe_show_result()
            return

        field_values = dialog.get_field_values()
        if not field_values:
            self.add_line("❌ No field values collected.")
            _maybe_show_result()
            return

        result_markdown = TemplateParser.fill_template(template_content, field_values)
        existing_image_paths = self._collect_image_paths_from_field_values(initial_field_values, fields)
        if image_save_dir:
            result_markdown = self._optimize_template_images(
                template_config,
                fields,
                field_values,
                image_save_dir,
                result_markdown,
                skip_paths=existing_image_paths,
            )

        new_block = result_markdown.strip()
        if selected_entry.end < len(file_content) and file_content[selected_entry.end : selected_entry.end + 1] == "\n":
            new_block += "\n"

        new_content = file_content[: selected_entry.start] + new_block + file_content[selected_entry.end :]
        with Path.open(target_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{target_path}"')
        self.add_line(f"✅ Updated entry in {target_path}")
        self.add_line("\nUpdated markdown:")
        self.add_line(result_markdown)
        _maybe_show_result()

    @ActionBase.handle_exceptions("adding markdown from template")
    def _execute_from_template(self, *, template_name: str | None = None, suppress_result_ui: bool = False) -> None:
        """Add Markdown content using template-based forms.

        Reads a template file with field placeholders, shows a form dialog,
        fills the template with user values, and inserts into target file or returns text.

        """

        def _maybe_show_result() -> None:
            if not suppress_result_ui:
                self.show_result()

        templates = self.config.get("markdown_templates", {})

        if not templates:
            self.add_line("❌ No markdown templates configured in config.json")
            _maybe_show_result()
            return

        selected_template = template_name
        if not selected_template:
            template_names = list(templates.keys())
            selected_template = self.dialogs.get_choice_from_list(
                "Select Template",
                "Choose a template to use:",
                template_names,
            )
            if not selected_template:
                return

        template_config = templates[selected_template]

        template_file = template_config.get("template_file")

        if not template_file:
            self.add_line(f"❌ Template file not specified for '{selected_template}'")
            _maybe_show_result()
            return

        template_path = Path(template_file)
        if not template_path.is_absolute():
            template_path = h.dev.get_project_root() / template_path

        if not template_path.exists():
            self.add_line(f"❌ Template file not found: {template_file}")
            _maybe_show_result()
            return

        with Path.open(template_path, encoding="utf-8") as f:
            template_content = f.read().strip()

        fields, _ = TemplateParser.parse_template(template_content)

        if not fields:
            self.add_line(f"❌ No fields found in template: {template_file}")
            _maybe_show_result()
            return

        self._resolve_field_link_options(fields, template_config)

        author_to_english: dict[str, str] = {}
        if selected_template == "📖 Book":
            authors_list, author_to_english = self._get_authors_for_book_template(template_config)
            fields = self._replace_author_field_with_combobox(fields, authors_list)

        series_titles: list[str] = []
        series_last_records: dict[str, dict[str, str]] = {}
        if selected_template == "📺 Movie: series":
            aggregated = self._get_movies_aggregated_file_from_template_config(template_config)
            if aggregated:
                series_titles, series_last_records = self._parse_series_last_records_from_aggregated_file(aggregated)

                # Replace Title field to allow fuzzy autocomplete like in quotes dialog.
                for field in fields:
                    if field.name == "Title":
                        field.field_type = "combobox"
                        field.options = series_titles
                        break

        movie_titles: list[str] = []
        movie_last_records: dict[str, dict[str, str]] = {}
        if selected_template == "🎬 Movie":
            aggregated = self._get_movies_aggregated_file_from_template_config(template_config)
            if aggregated:
                movie_titles, movie_last_records = self._parse_movies_last_records_from_aggregated_file(aggregated)

                for field in fields:
                    if field.name == "Title":
                        field.field_type = "combobox"
                        field.options = movie_titles
                        break

        dialog_links: list[tuple[str, str]] = self._parse_template_dialog_links(template_config)

        path_target = template_config.get("path_target")
        path_layout = self._template_path_layout(template_config)
        path_target_path = (
            Path(str(path_target).rstrip("/")) if path_target is not None and str(path_target).strip() else None
        )
        staging_dir: Path | None = None
        if path_layout == "city_note" and path_target_path is not None:
            path_target_path.mkdir(parents=True, exist_ok=True)
            staging_dir = self._create_template_staging_dir(path_target_path)
            image_save_dir = staging_dir
        elif path_target_path is not None and path_target_path.suffix == ".md":
            image_save_dir = h.md.resolve_md_path(path_target_path).parent
        else:
            image_save_dir = None

        allows_edit_existing = self._template_allows_edit_existing(template_config)
        entry_browser_groups = (
            self._build_entry_browser_groups(template_config, template_content) if allows_edit_existing else None
        )

        def resolve_image_save_dir(entry: TemplateExistingEntry | None) -> Path | None:
            if entry is None:
                return staging_dir if path_layout == "city_note" else image_save_dir
            if entry.kind == "city_note" and entry.note_md:
                return Path(entry.note_md).parent
            if entry.target_path:
                return h.md.resolve_md_path(Path(entry.target_path)).parent
            return image_save_dir

        def load_entry_values(entry: TemplateExistingEntry) -> dict[str, str] | None:
            return self._load_template_entry_field_values(entry, template_content, fields)

        try:
            dialog = TemplateDialog(
                fields=fields,
                title=selected_template,
                links=dialog_links,
                image_save_dir=image_save_dir,
                app_config=self.config,
                entry_browser_groups=entry_browser_groups,
                load_entry_values=load_entry_values if entry_browser_groups else None,
                resolve_image_save_dir=resolve_image_save_dir if entry_browser_groups else None,
            )

            self._wire_template_dialog_autofill(
                selected_template,
                dialog,
                series_last_records=series_last_records,
                movie_last_records=movie_last_records,
                author_to_english=author_to_english,
                apply_initial_autofill=entry_browser_groups is None,
            )

            if dialog.exec() != dialog.DialogCode.Accepted:
                self.add_line("❌ Dialog was canceled.")
                _maybe_show_result()
                return

            field_values = dialog.get_field_values()
            if not field_values:
                self.add_line("❌ No field values collected.")
                _maybe_show_result()
                return

            selected_entry = dialog.get_selected_entry()
            if selected_entry is not None:
                self._commit_template_entry_edit(
                    selected_entry=selected_entry,
                    selected_template=selected_template,
                    template_config=template_config,
                    template_content=template_content,
                    fields=fields,
                    field_values=field_values,
                    _maybe_show_result=_maybe_show_result,
                )
                return

            result_markdown = TemplateParser.fill_template(template_content, field_values)

            if path_layout == "city_note":
                self._save_new_city_note(
                    selected_template=selected_template,
                    template_config=template_config,
                    fields=fields,
                    field_values=field_values,
                    result_markdown=result_markdown,
                    staging_dir=staging_dir,
                    _maybe_show_result=_maybe_show_result,
                )
                return

            optimize_images, _ = self._resolve_image_optimize_settings(fields, template_config)
            if optimize_images and image_save_dir:
                result_markdown = self._optimize_template_images(
                    template_config,
                    fields,
                    field_values,
                    image_save_dir,
                    result_markdown,
                )

            path_target = template_config.get("path_target")
            insert_position = template_config.get("insert_position", "end")
            saved_commit_message: str | None = None
            saved_commit_paths: list[Path] = []

            if path_target:
                current_year = datetime.now(UTC).astimezone().strftime("%Y")
                path_target_clean = path_target.rstrip("/")
                path_target_path = Path(path_target_clean)
                single_file = path_target_path.suffix == ".md"
                if single_file:
                    target_path = h.md.resolve_md_path(path_target_path)
                else:
                    target_path = h.md.note_md_path(path_target_path, current_year)

                file_existed = target_path.exists()
                if file_existed:
                    with Path.open(target_path, encoding="utf-8") as f:
                        existing_content = f.read()
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    beginning_content = self.config.get("beginning_of_md", "")
                    if single_file:
                        if beginning_content:
                            existing_content = (
                                beginning_content + "\n\n## " + current_year + "\n\n" + result_markdown + "\n"
                            )
                        else:
                            existing_content = "## " + current_year + "\n\n" + result_markdown + "\n"
                    elif beginning_content:
                        existing_content = beginning_content + "\n\n# " + current_year + "\n"
                    else:
                        existing_content = "# " + current_year + "\n"

                if not file_existed and single_file:
                    new_content = existing_content
                elif insert_position == "end":
                    new_content = existing_content.rstrip() + "\n\n" + result_markdown + "\n"
                elif insert_position == "start" and single_file:
                    yaml_md, content_md = h.md.split_yaml_content(existing_content)
                    year_heading_pattern = re.compile(r"^## " + re.escape(current_year) + r"\s*$", re.MULTILINE)
                    year_match = year_heading_pattern.search(content_md)
                    if year_match:
                        year_pos = year_match.end()
                        updated_content_md = (
                            content_md[:year_pos] + "\n\n" + result_markdown + "\n\n" + content_md[year_pos:].lstrip()
                        )
                        new_content = yaml_md + "\n\n" + updated_content_md if yaml_md else updated_content_md
                    else:
                        toc_match = re.search(r"<details>[\s\S]*?<\/details>", content_md)
                        if toc_match:
                            insert_pos = toc_match.end()
                            updated_content_md = (
                                content_md[:insert_pos]
                                + "\n\n## "
                                + current_year
                                + "\n\n"
                                + result_markdown
                                + "\n\n"
                                + content_md[insert_pos:].lstrip()
                            )
                        else:
                            updated_content_md = (
                                "## " + current_year + "\n\n" + result_markdown + "\n\n" + content_md.lstrip()
                            )
                        new_content = yaml_md + "\n\n" + updated_content_md if yaml_md else updated_content_md
                elif insert_position == "start":
                    yaml_md, content_md = h.md.split_yaml_content(existing_content)
                    year_match = re.search(r"^#+ \d{4}", content_md, re.MULTILINE)

                    if year_match:
                        toc_match = re.search(r"<details>[\s\S]*?<\/details>", content_md)
                        if toc_match:
                            toc_end_pos = toc_match.end()
                            updated_content_md = (
                                content_md[:toc_end_pos]
                                + "\n\n"
                                + result_markdown
                                + "\n\n"
                                + content_md[toc_end_pos:].lstrip()
                            )
                        else:
                            year_pos = year_match.end()
                            updated_content_md = (
                                content_md[:year_pos]
                                + "\n\n"
                                + result_markdown
                                + "\n\n"
                                + content_md[year_pos:].lstrip()
                            )
                        new_content = yaml_md + "\n\n" + updated_content_md if yaml_md else updated_content_md
                    elif yaml_md:
                        new_content = yaml_md + "\n\n" + result_markdown + "\n\n" + content_md
                    else:
                        new_content = result_markdown + "\n\n" + existing_content
                else:
                    new_content = existing_content.rstrip() + "\n\n" + result_markdown + "\n"

                with Path.open(target_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                h.dev.run_command(
                    f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{target_path}"'
                )
                self.add_line(f"✅ Added markdown to {target_path}")
                self.add_line("\nGenerated markdown:")
                self.add_line(result_markdown)
                saved_commit_message = build_commit_message_for_template(
                    selected_template,
                    template_config,
                    field_values,
                )
                saved_commit_paths = [target_path]
            else:
                self.add_line("Generated markdown:")
                self.add_line(result_markdown)

            _maybe_show_result()
            if saved_commit_message and saved_commit_paths:
                self._offer_git_commit_after_markdown(
                    commit_message=saved_commit_message,
                    paths_to_add=saved_commit_paths,
                )
        finally:
            if staging_dir is not None:
                self._cleanup_template_staging_dir(staging_dir)

    @ActionBase.handle_exceptions("creating new article")
    def _execute_new_article(self) -> None:
        """Create new article with predefined template."""
        article_name = self.dialogs.get_text_input(
            "Article title", "Enter the name of the article (English, without spaces):", "name-of-article"
        )
        if not article_name:
            return

        article_name = article_name.replace(" ", "-")

        now_local = datetime.now(UTC).astimezone()
        text = self.config["beginning_of_article"].replace(
            "[YEAR]",
            now_local.strftime("%Y"),
        )
        text = text.replace("[NAME]", article_name)
        text = text.replace(
            "[DATE]",
            now_local.strftime("%Y-%m-%d"),
        )
        text += f"\n# {article_name.capitalize().replace('-', ' ')}\n\n\n"

        result, filename = h.md.add_note(Path(self.config["path_articles"]), article_name, text, is_with_images=True)
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_articles"]}" "{filename}"')
        self.add_line(result)

    @ActionBase.handle_exceptions("creating new diary entry")
    def _execute_new_diary(self, *, diary_root: Path | str | None = None) -> None:
        """Create new diary entry for current date."""
        base = Path(diary_root) if diary_root is not None else Path(self.config["path_diary"])
        result, filename = h.md.add_diary_new_dairy_in_year(base, self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)

    @ActionBase.handle_exceptions("creating new cases entry")
    def _execute_new_diary_cases(self, *, cases_root: Path | str | None = None) -> None:
        """Create new cases entry for current month."""
        if cases_root is not None:
            base = Path(cases_root)
            result, filename = h.md.add_diary_new_cases_in_year(base, self.config["beginning_of_md"])
            h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
            self.add_line(result)
            return
        path_cases = self.config.get("path_cases")
        if not path_cases:
            self.add_line("❌ path_cases is not configured in config.json.")
            self.show_result()
            return
        result, filename = h.md.add_diary_new_cases_in_year(path_cases, self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)

    @ActionBase.handle_exceptions("creating new dream entry")
    def _execute_new_diary_dream(self, *, dream_root: Path | str | None = None) -> None:
        """Create new dream journal entry for current date."""
        base = Path(dream_root) if dream_root is not None else Path(self.config["path_dream"])
        result, filename = h.md.add_diary_new_dream_in_year(base, self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)

    @ActionBase.handle_exceptions("creating new memory entry")
    def _execute_new_memory(self) -> None:
        """Create new memory entry for current date."""
        path_memories = self.config.get("path_memories")
        if not path_memories:
            self.add_line("❌ Config key 'path_memories' is not set.")
            return
        result, filename = h.md.add_diary_new_dairy_in_year(path_memories, self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)

    @ActionBase.handle_exceptions("creating new note")
    def _execute_new_note(
        self,
        *,
        is_with_images: bool = False,
        folder_path: Path | None = None,
        note_stem: str | None = None,
    ) -> None:
        """Create new general note with user-specified filename."""
        noninteractive = folder_path is not None

        if folder_path is not None:
            if note_stem is None or not str(note_stem).strip():
                self.add_line("❌ Note name is empty.")
                return
            stem_raw = str(note_stem).strip()
            if stem_raw.lower().endswith(".md"):
                stem_raw = stem_raw[:-3]
            heading_stem = stem_raw
            parent: Path = folder_path
        else:
            try:
                temp_config = h.dev.config_load(self.config_path, is_temp=True)
                default_path = temp_config.get(
                    "path_last_note_folder", self.config.get("path_last_note_folder", self.config["path_notes"])
                )
            except (FileNotFoundError, OSError):
                default_path = self.config.get("path_last_note_folder", self.config["path_notes"])

            filename_dialog = self.dialogs.get_save_filename(
                "Save Note", default_path, "Markdown (*.md);;All Files (*)"
            )
            if not filename_dialog:
                return

            heading_stem = filename_dialog.stem
            parent = filename_dialog.parent

        # Temp config should never prevent note creation.
        try:
            temp_config_path = Path(self.temp_config_path)
            temp_config_path.parent.mkdir(parents=True, exist_ok=True)
            if not temp_config_path.exists() or temp_config_path.stat().st_size == 0:
                temp_config_path.write_text("{}", encoding="utf-8")
            h.dev.config_update_value("path_last_note_folder", str(parent), self.config_path, is_temp=True)
        except (FileNotFoundError, OSError) as e:
            self.add_line(f"⚠️ Could not update temp config ({self.temp_config_path}): {e}")

        self.add_line(f"Folder path: {parent}")
        self.add_line(f"File name without extension: {heading_stem}")

        config_folder = h.dev.get_project_root() / "config"
        template_files = self.config.get("note_beginning_templates", [])

        if not template_files:
            self.add_line("❌ No note_beginning_templates configured in config.json.")
            return

        file_contents: dict[str, str] = {}
        file_choices: list[tuple[str, str]] = []
        display_to_template: dict[str, str] = {}
        for template_file in template_files:
            if template_file.startswith("snippet:"):
                file_path_str = template_file[8:]
                file_path = h.dev.get_project_root() / file_path_str
                display_name = Path(file_path_str).name
            else:
                file_path = config_folder / template_file
                display_name = template_file

            if not file_path.exists():
                self.add_line(f"⚠️ Template file not found: {template_file}")
                continue

            try:
                with Path.open(file_path, "r", encoding="utf8") as f:
                    content = f.read()
                file_contents[template_file] = content
                lines = content.split("\n")
                max_count_lines = 10
                preview = "\n".join(lines[:max_count_lines]) + "\n..." if len(lines) > max_count_lines else content
                display_to_template[display_name] = template_file
                file_choices.append((display_name, preview))
            except Exception as e:
                self.add_line(f"❌ Error reading file {template_file}: {e}")
                continue

        if not file_choices:
            self.add_line("❌ No valid beginning template files could be read.")
            return

        if noninteractive:
            selected_template_file = next(iter(file_contents))
            beginning_text = file_contents[selected_template_file]
            self.add_line(f"🔵 Using first beginning template: {selected_template_file}")
        else:
            selected_display_name = self.dialogs.get_choice_from_list_with_descriptions(
                "Select Beginning Template", "Choose a beginning template:", file_choices
            )

            if not selected_display_name:
                return

            selected_template_file = display_to_template[selected_display_name]
            beginning_text = file_contents[selected_template_file]

        text = beginning_text + f"\n# {heading_stem}\n\n\n"
        filename_final = heading_stem.replace("-", "--").replace(" ", "-")

        result, filename = h.md.add_note(parent, filename_final, text, is_with_images=is_with_images)
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)

    def _execute_new_note_with_images(self) -> None:
        """Create new note with images directory."""
        self._execute_new_note(is_with_images=True)

    @ActionBase.handle_exceptions("processing quotes")
    def _execute_new_quotes(self) -> None:
        """Add new quotes with author and book title."""
        self._execute_new_quotes_format_with_author_and_book()

    def _execute_new_quotes_format_with_author_and_book(self) -> None:
        """Format quotes with specified author and book title via dialog."""
        quotes_folder = self.config.get("path_quotes", "")
        author_books_dict = self._extract_authors_and_books_from_quotes_folder(quotes_folder)
        authors_list = sorted(author_books_dict.keys())

        fields = [
            TemplateField("Author", "combobox", "{{Author:combobox}}", "", options=authors_list),
            TemplateField("Book Title", "combobox", "{{Book Title:combobox}}", "", options=[]),
            TemplateField(
                "Quotes",
                "multiline",
                "{{Quotes:multiline}}",
                (
                    "They can get a big bang out of buying a blanket.\n\n\n"
                    "I just mean that I used to think about old Spencer quite a lot"
                ),
            ),
        ]

        dialog = TemplateDialog(
            fields=fields,
            title="Enter Book, Author and Quotes",
            app_config=self.config,
        )

        author_widget = dialog.widgets.get("Author")
        book_widget = dialog.widgets.get("Book Title")
        if isinstance(author_widget, QComboBox) and isinstance(book_widget, QComboBox):

            def update_book_list(author_text: str) -> None:
                current_book = book_widget.currentText()
                book_widget.clear()

                if hasattr(book_widget, "smart_filter_model"):
                    delattr(book_widget, "smart_filter_model")
                if hasattr(book_widget, "smart_filter_proxy"):
                    delattr(book_widget, "smart_filter_proxy")
                if hasattr(book_widget, "smart_filter_completer"):
                    delattr(book_widget, "smart_filter_completer")
                if hasattr(book_widget, "smart_filter_items"):
                    delattr(book_widget, "smart_filter_items")

                if author_text and author_text in author_books_dict:
                    books = author_books_dict[author_text]
                    book_widget.addItems(books)
                    apply_smart_filtering(book_widget)

                    if current_book:
                        index = book_widget.findText(current_book)
                        if index >= 0:
                            book_widget.setCurrentIndex(index)
                        else:
                            book_widget.setCurrentText(current_book)
                else:
                    book_widget.setCurrentText(current_book or "")

            author_widget.currentTextChanged.connect(update_book_list)

            if author_widget.currentText():
                update_book_list(author_widget.currentText())

        if dialog.exec() != dialog.DialogCode.Accepted:
            self.add_line("❌ Dialog was canceled.")
            self.show_result()
            return

        field_values = dialog.get_field_values()
        if not field_values:
            self.add_line("❌ No field values collected.")
            self.show_result()
            return

        book_title = field_values.get("Book Title", "")
        author = field_values.get("Author", "")
        quotes_content = field_values.get("Quotes", "")

        if not book_title or not author or not quotes_content:
            self.add_line("❌ Book title, author and quotes are required.")
            self.show_result()
            return

        quotes = [q.strip() for q in quotes_content.split("\n\n") if q.strip()]

        formatted_content = ""
        for quote in quotes:
            formatted_content += f"{quote}\n\n{book_title}\n{author}\n\n\n"

        formatted_content = formatted_content.rstrip()

        result = h.md.format_quotes_as_markdown_content(formatted_content)

        quotes_without_header = result
        if quotes_without_header.startswith(f"# {book_title}"):
            lines = quotes_without_header.split("\n")
            for i_original, line in enumerate(lines):
                i = i_original
                if line.strip() == f"# {book_title}":
                    while i + 1 < len(lines) and not lines[i + 1].strip():
                        i += 1
                    quotes_without_header = "\n".join(lines[i + 1 :]).lstrip()
                    break

        success = self._save_quotes_to_file(quotes_without_header, author, book_title)
        if success:
            self.add_line("✅ Quotes saved to file successfully!")
        else:
            self.add_line("❌ Failed to save quotes to file.")

        self.show_result()

    def _extract_authors_and_books_from_quotes_folder(self, quotes_folder: str) -> dict[str, list[str]]:
        """Extract authors and their books from Markdown quote files.

        If folder contains aggregated file `_<FolderName>.g.md` (e.g. `Fiction` -> `_Fiction.g.md`),
        only that file is scanned; otherwise all `*.md` in folder (and subfolders) are scanned.

        """
        author_books: dict[str, set[str]] = {}

        quotes_path = Path(quotes_folder)
        if not quotes_path.exists():
            return {}

        folder_name = quotes_path.name
        aggregated_file = quotes_path / f"_{folder_name}.g.md"
        md_files = [aggregated_file] if aggregated_file.exists() else list(quotes_path.rglob("*.md"))

        pattern = re.compile(r">\s*--\s*_([^_]+?),\s*([^_]+?)_", re.MULTILINE)

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception as e:
                print(f"Warning: Failed to read {md_file}: {e}")
                continue

            matches = pattern.findall(content)
            for author, book in matches:
                author_clean = author.strip()
                book_clean = book.strip()
                if author_clean and not author_clean.startswith("["):
                    if author_clean not in author_books:
                        author_books[author_clean] = set()
                    if book_clean:
                        author_books[author_clean].add(book_clean)

        return {author: sorted(books) for author, books in sorted(author_books.items())}

    def _extract_authors_and_english_names_from_books_folder(self, books_path: str) -> dict[str, str]:
        """Extract authors and their English names from books Markdown files."""
        result: dict[str, str] = {}
        books_dir = Path(books_path.rstrip("/"))

        if not books_dir.exists():
            return result

        heading_pattern = re.compile(r"^#{2,3}\s+.+\(([^)]+)\):\s*[\d.]+", re.MULTILINE)
        english_pattern = re.compile(r"^\s*-\s*\*\*Author's name in English:\*\*\s*(.*)$", re.MULTILINE)

        for md_file in h.md.iter_note_md_in_folder(books_dir):
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception as e:
                print(f"Warning: Failed to read {md_file}: {e}")
                continue

            blocks = re.split(r"^#{2,3}\s+", content, flags=re.MULTILINE)
            for block in blocks[1:]:
                block_for_match = "## " + block
                heading_match = heading_pattern.match(block_for_match)
                if heading_match:
                    author = heading_match.group(1).strip()
                    if not author or author.startswith("["):
                        continue
                    english_match = english_pattern.search(block_for_match)
                    english_name = english_match.group(1).strip() if english_match else ""
                    if author and (author not in result or english_name):
                        result[author] = english_name

        return result

    @staticmethod
    def _format_new_note_content(body: str, beginning_of_md: str | None) -> str:
        """Prepend YAML front matter when creating a standalone note file."""
        beginning = (beginning_of_md or "").rstrip()
        content = body.strip()
        if not beginning:
            return f"{content}\n" if content else ""
        if not content:
            return f"{beginning}\n"
        return f"{beginning}\n\n{content}\n"

    def _get_authors_for_book_template(self, template_config: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
        """Get authors list and author-to-English-name mapping for Book template."""
        path_target = template_config.get("path_target", "")
        if not path_target:
            return [], {}

        author_to_english = self._extract_authors_and_english_names_from_books_folder(path_target)
        authors_list = sorted(author_to_english.keys())
        return authors_list, author_to_english

    def _get_movies_aggregated_file_from_template_config(self, template_config: dict[str, Any]) -> Path | None:
        path_target = (template_config.get("path_target") or "").strip()
        if not path_target:
            return None

        path_target_path = Path(path_target.rstrip("/"))
        movies_dir = path_target_path.parent if path_target_path.suffix.lower() == ".md" else path_target_path
        return movies_dir / f"_{movies_dir.name}.g.md"

    @staticmethod
    def _list_city_note_entries(path_target: Path) -> list[tuple[str, Path]]:
        """List `(display_label, note_md_path)` for all notes under city subfolders."""
        entries: list[tuple[str, Path]] = []
        if not path_target.is_dir():
            return entries
        for city_dir in sorted(path_target.iterdir(), key=lambda p: p.name.lower()):
            if not city_dir.is_dir() or city_dir.name.startswith("."):
                continue
            for note_md in h.md.iter_note_md_in_folder(city_dir):
                label = f"{city_dir.name} / {note_md.parent.name}"
                entries.append((label, note_md))
        return entries

    @staticmethod
    def _list_path_subfolders(path_target: Path) -> list[str]:
        """Return sorted names of direct subfolders under `path_target`."""
        if not path_target.is_dir():
            return []
        return sorted(
            folder.name for folder in path_target.iterdir() if folder.is_dir() and not folder.name.startswith(".")
        )

    @staticmethod
    def _list_template_year_md_files(path_target: Path) -> list[Path]:
        """Return Markdown files under a year-file template folder."""
        if not path_target.is_dir():
            return []
        files: list[Path] = []
        for path in sorted(path_target.glob("*.md"), key=lambda item: item.name.lower()):
            if path.name.startswith("_") or path.name.endswith(".g.md"):
                continue
            files.append(path)
        return files

    @staticmethod
    def _load_template_entry_field_values(
        entry: TemplateExistingEntry,
        template_content: str,
        fields: list[TemplateField],
    ) -> dict[str, str] | None:
        """Parse field values from a browser entry reference."""
        if entry.kind == "city_note":
            if not entry.note_md:
                return None
            note_md = Path(entry.note_md)
            content = note_md.read_text(encoding="utf-8")
            return TemplateParser.parse_block(template_content, content, fields)

        if not entry.target_path or entry.block_start is None or entry.block_end is None:
            return None
        target_path = Path(entry.target_path)
        content = target_path.read_text(encoding="utf-8")
        block_text = content[entry.block_start : entry.block_end]
        return TemplateParser.parse_block(template_content, block_text, fields)

    @staticmethod
    def _move_staging_images_to_note(staging_dir: Path | None, note_dir: Path) -> None:
        """Copy image files from staging `img/` into the note folder `img/`."""
        if staging_dir is None:
            return
        src = staging_dir / "img"
        if not src.is_dir():
            return
        dst = note_dir / "img"
        dst.mkdir(parents=True, exist_ok=True)
        for file_path in src.iterdir():
            if file_path.is_file():
                dest = dst / file_path.name
                if dest.exists():
                    dest.unlink()
                shutil.move(str(file_path), str(dest))

    def _offer_git_commit_after_markdown(
        self,
        *,
        commit_message: str | None,
        paths_to_add: list[Path],
    ) -> None:
        """Show Git commit dialog after Markdown content was saved."""
        if not commit_message or not commit_message.strip():
            return

        message = commit_message.strip()
        print(message)

        existing_paths = [path for path in paths_to_add if path.exists()]
        if not existing_paths:
            return

        paths_git = self.config.get("paths_git", [])
        if not isinstance(paths_git, list):
            paths_git = []
        repo = resolve_git_repo(existing_paths[0], [str(path) for path in paths_git])

        result = self.dialogs.show_git_commit_offer(message, repo_path=repo)
        if result != COMMIT_OFFER_CREATE_CODE or repo is None:
            return

        success, output = run_git_commit(repo, message, existing_paths)
        if success:
            self.add_line(f"✅ Git commit created in {repo}")
            if output:
                self.add_line(output)
        else:
            self.add_line(f"❌ Git commit failed: {output}")

    def _optimize_template_images(
        self,
        template_config: dict[str, Any],
        fields: list[TemplateField],
        field_values: dict[str, str],
        image_save_dir: Path,
        result_markdown: str,
        *,
        skip_paths: set[str] | None = None,
    ) -> str:
        """Optimize image paths in generated Markdown for template image fields."""
        optimize, max_size = self._resolve_image_optimize_settings(fields, template_config)
        if not optimize:
            return result_markdown

        skip = skip_paths or set()

        for field in fields:
            if field.field_type == "image":
                candidates = [(field_values.get(field.name) or "").strip()]
            elif field.field_type == "images":
                candidates = [part.strip() for part in (field_values.get(field.name) or "").split(",") if part.strip()]
            else:
                continue

            for image_path_value in candidates:
                if not image_path_value or image_path_value in skip:
                    continue
                try:
                    new_image_path = optimize_single_image_for_template(
                        image_path_value,
                        image_save_dir,
                        max_size,
                    )
                    if new_image_path != image_path_value:
                        result_markdown = result_markdown.replace(image_path_value, new_image_path)
                except Exception as e:
                    self.add_line(f"⚠️ Image optimization skipped: {e}")

        return result_markdown

    def _parse_movies_last_records_from_aggregated_file(
        self, aggregated_path: Path
    ) -> tuple[list[str], dict[str, dict[str, str]]]:
        """Parse movie records from aggregated Movies file.

        Rule: the first encountered record in file is treated as the latest one.

        """
        if not aggregated_path.exists():
            return [], {}

        try:
            content = aggregated_path.read_text(encoding="utf-8")
        except OSError:
            return [], {}

        # Example: ## Title: 8.5
        heading_re = re.compile(r"^(?P<h>##|###)\s+(?P<title>.+?)\s*:\s*(?P<score>[\d.,]+)\s*$")
        any_heading_re = re.compile(r"^(##|###)\s+")

        def _extract_first(pattern: str, text: str) -> str:
            # Optional capture groups (e.g. `<?([^>\s]+)?>?`) can match while leaving
            # group(1) as None when the value is missing (e.g. `- **IMDb:** <>`).
            m = re.search(pattern, text, flags=re.MULTILINE)
            if m is None:
                return ""
            value = m.group(1)
            return value.strip() if value else ""

        last_records: dict[str, dict[str, str]] = {}
        current_title: str | None = None
        current_score: str | None = None
        current_body_lines: list[str] = []

        def _flush_current() -> None:
            nonlocal current_title, current_score, current_body_lines
            if not current_title or current_title in last_records:
                current_title = None
                current_score = None
                current_body_lines = []
                return

            body = "\n".join(current_body_lines)
            last_records[current_title] = {
                "score": (current_score or "").strip(),
                "original": _extract_first(r"^- \*\*Original or English title:\*\*\s*(.+?)\s*$", body),
                "kinopoisk": _extract_first(r"^- \*\*Kinopoisk:\*\*\s*<?([^>\s]+)?>?\s*$", body),
                "imdb": _extract_first(r"^- \*\*IMDb:\*\*\s*<?([^>\s]+)?>?\s*$", body),
            }

            current_title = None
            current_score = None
            current_body_lines = []

        for line in content.splitlines():
            m = heading_re.match(line.strip())
            if m:
                _flush_current()
                current_title = m.group("title").strip()
                current_score = m.group("score").strip()
                continue

            if any_heading_re.match(line) and current_title is not None:
                _flush_current()
                continue

            if current_title is not None:
                current_body_lines.append(line)

        _flush_current()

        titles = sorted(last_records.keys(), key=str.lower)
        return titles, last_records

    def _parse_series_last_records_from_aggregated_file(
        self, aggregated_path: Path
    ) -> tuple[list[str], dict[str, dict[str, str]]]:
        """Parse series records from aggregated Movies file.

        Rule: the first encountered record in file is treated as the latest one.

        """
        if not aggregated_path.exists():
            return [], {}

        try:
            content = aggregated_path.read_text(encoding="utf-8")
        except OSError:
            return [], {}

        # Example: ## Title (сезон 2): 8.5  # ignore: HP001
        heading_re = re.compile(
            r"^(?P<h>##|###)\s+(?P<title>.+?)\s*\("
            r"сезон\s+(?P<season>\d+)\)\s*:\s*(?P<score>[\d.,]+)\s*$"  # ignore: HP001
        )
        any_heading_re = re.compile(r"^(##|###)\s+")

        def _extract_first(pattern: str, text: str) -> str:
            # Optional capture groups (e.g. `<?([^>\s]+)?>?`) can match while leaving
            # group(1) as None when the value is missing (e.g. `- **IMDb:** <>`).
            m = re.search(pattern, text, flags=re.MULTILINE)
            if m is None:
                return ""
            value = m.group(1)
            return value.strip() if value else ""

        last_records: dict[str, dict[str, str]] = {}
        current_title: str | None = None
        current_season: str | None = None
        current_score: str | None = None
        current_body_lines: list[str] = []

        def _flush_current() -> None:
            nonlocal current_title, current_season, current_score, current_body_lines
            if not current_title or current_title in last_records:
                current_title = None
                current_season = None
                current_score = None
                current_body_lines = []
                return

            body = "\n".join(current_body_lines)
            last_records[current_title] = {
                "season": (current_season or "").strip(),
                "score": (current_score or "").strip(),
                "original": _extract_first(r"^- \*\*Original or English title:\*\*\s*(.+?)\s*$", body),
                "date_watching": _extract_first(r"^- \*\*Date watching:\*\*\s*(\d{4}-\d{2}-\d{2})\s*$", body),
                "kinopoisk": _extract_first(r"^- \*\*Kinopoisk:\*\*\s*<?([^>\s]+)?>?\s*$", body),
                "imdb": _extract_first(r"^- \*\*IMDb:\*\*\s*<?([^>\s]+)?>?\s*$", body),
            }

            current_title = None
            current_season = None
            current_score = None
            current_body_lines = []

        for line in content.splitlines():
            m = heading_re.match(line.strip())
            if m:
                _flush_current()
                current_title = m.group("title").strip()
                current_season = m.group("season").strip()
                current_score = m.group("score").strip()
                continue

            if any_heading_re.match(line) and current_title is not None:
                # Some other record starts; flush current.
                _flush_current()
                continue

            if current_title is not None:
                current_body_lines.append(line)

        _flush_current()

        titles = sorted(last_records.keys(), key=str.lower)
        return titles, last_records

    @staticmethod
    def _parse_template_dialog_links(template_config: dict[str, Any]) -> list[tuple[str, str]]:
        dialog_links: list[tuple[str, str]] = []
        for item in template_config.get("dialog_links", []):
            if isinstance(item, dict):
                url = str(item.get("url") or "").strip()
                if not url:
                    continue
                label_raw = item.get("label")
                label = str(label_raw).strip() if label_raw is not None else ""
                if not label:
                    label = url
                dialog_links.append((label, url))
            elif isinstance(item, str):
                cleaned = item.strip()
                if cleaned:
                    dialog_links.append((cleaned, cleaned))
        return dialog_links

    def _prepend_beginning_of_md(self, body: str) -> str:
        """Prepend configured `beginning_of_md` YAML to note body."""
        return self._format_new_note_content(body, self.config.get("beginning_of_md"))

    def _replace_author_field_with_combobox(
        self, fields: list[TemplateField], authors_list: list[str]
    ) -> list[TemplateField]:
        """Replace Author line field with combobox in Book template fields."""
        new_fields = []
        for field in fields:
            if field.name == "Author":
                new_fields.append(TemplateField("Author", "combobox", "{{Author:combobox}}", "", options=authors_list))
            else:
                new_fields.append(field)
        return new_fields

    @staticmethod
    def _resolve_city_note_paths(
        fields: list[TemplateField],
        template_config: dict[str, Any],
        field_values: dict[str, str],
    ) -> tuple[Path, Path, Path, str]:
        """Return `(city_dir, note_md, note_dir, note_stem)` for city_note layout."""
        path_target = Path(str(template_config["path_target"]).rstrip("/"))
        city_field, name_field = OnNewMarkdown._city_note_field_names(fields, template_config)
        city_name = OnNewMarkdown._sanitize_folder_name(field_values.get(city_field, "") or "")
        note_stem = OnNewMarkdown._sanitize_note_stem(field_values.get(name_field, "") or "")
        if not city_name:
            msg = f"Field '{city_field}' is required for city_note layout."
            raise ValueError(msg)
        if not note_stem:
            msg = f"Field '{name_field}' is required for city_note layout."
            raise ValueError(msg)
        city_dir = path_target / city_name
        note_md = h.md.named_note_md_path(city_dir, note_stem)
        return city_dir, note_md, note_md.parent, note_stem

    @staticmethod
    def _resolve_field_link_options(fields: list[TemplateField], template_config: dict[str, Any]) -> None:
        """Apply template `@` links such as `@subfolders` to field widgets/options."""
        path_target = template_config.get("path_target")
        if not path_target:
            return
        path_target_path = Path(str(path_target).rstrip("/"))
        subfolders = OnNewMarkdown._list_path_subfolders(path_target_path)

        for field in fields:
            if field.field_link != TemplateParser.FIELD_LINK_SUBFOLDERS:
                continue
            if field.field_type not in {"line", "combobox"}:
                continue
            field.field_type = "combobox"
            field.options = subfolders

    @staticmethod
    def _resolve_image_optimize_settings(
        fields: list[TemplateField],
        template_config: dict[str, Any],
    ) -> tuple[bool, int | None]:
        """Return whether to optimize images and max side from template fields or config fallback."""
        template_sizes = [
            field.image_max_size
            for field in fields
            if field.field_type in ("image", "images") and field.image_optimize and field.image_max_size
        ]
        if template_sizes:
            return True, max(template_sizes)

        if any(field.image_optimize for field in fields if field.field_type in ("image", "images")):
            return True, None

        if not template_config.get("image_optimize"):
            return False, None

        max_size_raw = template_config.get("image_max_size")
        max_size: int | None = None
        if max_size_raw is not None:
            with contextlib.suppress(ValueError, TypeError):
                max_size = int(max_size_raw)
        return True, max_size

    def _resolve_template_target_path(self, template_config: dict[str, Any]) -> Path | None:
        path_target = template_config.get("path_target")
        if not path_target:
            return None
        current_year = datetime.now(UTC).astimezone().strftime("%Y")
        path_target_path = Path(str(path_target).rstrip("/"))
        if path_target_path.suffix == ".md":
            return h.md.resolve_md_path(path_target_path)
        return h.md.note_md_path(path_target_path, current_year)

    @staticmethod
    def _sanitize_folder_name(text: str) -> str:
        """Sanitize folder name from a template field value."""
        cleaned = re.sub(r'[<>:"/\\|?*]', "_", text.strip()).strip(" .")
        if not cleaned:
            return ""
        size_limit = 200
        return cleaned[:size_limit] if len(cleaned) > size_limit else cleaned

    @staticmethod
    def _sanitize_note_stem(text: str) -> str:
        """Sanitize note stem for `h.md.add_note` (spaces to dashes, preserve hyphens)."""
        cleaned = text.strip()
        if not cleaned:
            return ""
        return cleaned.replace("-", "--").replace(" ", "-")

    def _save_new_city_note(
        self,
        *,
        selected_template: str,
        template_config: dict[str, Any],
        fields: list[TemplateField],
        field_values: dict[str, str],
        result_markdown: str,
        staging_dir: Path | None,
        _maybe_show_result: Callable[[], None],
    ) -> None:
        """Create a new city_note entry from filled template values."""
        try:
            city_dir, note_md, note_dir, note_stem = self._resolve_city_note_paths(
                fields, template_config, field_values
            )
        except ValueError as exc:
            self.add_line(f"❌ {exc}")
            _maybe_show_result()
            return

        if note_md.exists():
            self.add_line(f"❌ Entry already exists: {note_md}. Use Edit existing entry.")
            _maybe_show_result()
            return

        is_with_images = bool(template_config.get("note_with_images", True))
        note_content = self._prepend_beginning_of_md(result_markdown)
        msg, created_path = h.md.add_note(city_dir, note_stem, note_content, is_with_images=is_with_images)
        self._move_staging_images_to_note(staging_dir, note_dir)

        optimize_images, _ = self._resolve_image_optimize_settings(fields, template_config)
        if optimize_images:
            optimized = self._optimize_template_images(
                template_config,
                fields,
                field_values,
                note_dir,
                result_markdown,
            )
            if optimized != result_markdown:
                note_md.write_text(self._prepend_beginning_of_md(optimized), encoding="utf-8")
                result_markdown = optimized

        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{created_path}"')
        self.add_line(msg)
        self.add_line(f"✅ Added note to {created_path}")
        self.add_line("\nGenerated markdown:")
        self.add_line(result_markdown)
        _maybe_show_result()
        self._offer_git_commit_after_markdown(
            commit_message=build_commit_message_for_template(
                selected_template,
                template_config,
                field_values,
            ),
            paths_to_add=[note_dir],
        )

    def _save_quotes_to_file(self, quotes_content: str, author: str, book_title: str) -> bool:
        """Save quotes to a Markdown file."""
        selected_folder = self.dialogs.get_folder_with_choice_option(
            self.config.get("paths_quotes", []),
            self.config.get("path_quotes", ""),
        )

        if not selected_folder:
            return False

        author_folder_name = "-".join(part.strip() for part in author.split() if part.strip())
        author_folder = selected_folder / author_folder_name
        author_folder.mkdir(exist_ok=True)

        clean_title = book_title.replace("«", "").replace("»", "").replace('"', "").replace("'", "")
        book_filename = "-".join(part.strip() for part in clean_title.split() if part.strip())
        file_path = h.md.note_md_path(author_folder, book_filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        header = f"# {book_title}"
        separator = "---"

        if file_path.exists():
            existing_content = file_path.read_text(encoding="utf-8")
            lines = existing_content.split("\n")
            new_lines = []
            header_found = False

            for i, line in enumerate(lines):
                new_lines.append(line)
                if line.strip() == header.strip():
                    header_found = True
                    new_lines.append("")
                    new_lines.append(quotes_content)
                    new_lines.append("")
                    new_lines.append(separator)
                    new_lines.extend(lines[i + 1 :])
                    break

            if not header_found:
                if not existing_content.rstrip().endswith("---"):
                    new_lines.extend(["", separator, "", quotes_content])
                else:
                    new_lines.extend(["", quotes_content])

            content = "\n".join(new_lines)
        else:
            beginning_template = self.config["beginning_of_md"]
            content = f"{beginning_template}\n{header}\n\n{quotes_content}"

        content = content.rstrip() + "\n"
        file_path.write_text(content, encoding="utf-8")
        return True

    @staticmethod
    def _template_allows_edit_existing(template_config: dict[str, Any]) -> bool:
        """Return `True` when template config enables editing existing entries on add."""
        return bool(template_config.get("edit_existing"))

    @staticmethod
    def _template_path_layout(template_config: dict[str, Any]) -> str:
        """Return path layout mode: single_file, year_file, or city_note."""
        explicit = template_config.get("path_layout")
        if explicit == "city_note":
            return "city_note"
        path_target = str(template_config.get("path_target") or "").rstrip("/")
        if path_target.endswith(".md"):
            return "single_file"
        return "year_file"

    def _wire_template_dialog_autofill(
        self,
        selected_template: str,
        dialog: TemplateDialog,
        *,
        series_last_records: dict[str, dict[str, str]] | None = None,
        movie_last_records: dict[str, dict[str, str]] | None = None,
        author_to_english: dict[str, str] | None = None,
        apply_initial_autofill: bool = True,
    ) -> None:
        if selected_template == "📺 Movie: series" and series_last_records:
            title_widget = dialog.widgets.get("Title")
            season_widget = dialog.widgets.get("Season")
            score_widget = dialog.widgets.get("Score")
            original_widget = dialog.widgets.get("Original or English title")
            date_widget = dialog.widgets.get("Date watching")
            kinopoisk_widget = dialog.widgets.get("Kinopoisk")
            imdb_widget = dialog.widgets.get("IMDb")

            if (
                isinstance(title_widget, QComboBox)
                and isinstance(season_widget, QSpinBox)
                and isinstance(score_widget, QDoubleSpinBox)
                and isinstance(original_widget, QLineEdit)
                and isinstance(date_widget, QDateEdit)
                and isinstance(kinopoisk_widget, QLineEdit)
                and isinstance(imdb_widget, QLineEdit)
            ):

                def _autofill_series_fields(series_title: str | None) -> None:
                    key = (series_title or "").strip()
                    if not key:
                        return
                    record = series_last_records.get(key)
                    if not record:
                        return

                    try:
                        last_season = int(record.get("season", "").strip() or "0")
                    except ValueError:
                        last_season = 0
                    next_season = max(1, last_season + 1)
                    season_widget.setValue(next_season)

                    score_raw = (record.get("score", "") or "").strip().replace(",", ".")
                    with contextlib.suppress(ValueError):
                        score_widget.setValue(float(score_raw))

                    original_widget.setText(record.get("original", ""))
                    kinopoisk_widget.setText(record.get("kinopoisk", ""))
                    imdb_url = record.get("imdb", "")
                    if imdb_url:
                        imdb_url = re.sub(r"([?&]season=)(\d+)", rf"\g<1>{next_season}", imdb_url)
                    imdb_widget.setText(imdb_url)

                    date_watching_str = (record.get("date_watching", "") or "").strip()
                    date_watching = QDate.fromString(date_watching_str, "yyyy-MM-dd")
                    is_valid = QDate.isValid(date_watching.year(), date_watching.month(), date_watching.day())
                    date_widget.setDate(date_watching if is_valid else QDate.currentDate())

                title_widget.currentTextChanged.connect(_autofill_series_fields)
                if apply_initial_autofill and title_widget.currentText():
                    _autofill_series_fields(title_widget.currentText())

        if selected_template == "🎬 Movie" and movie_last_records:
            title_widget = dialog.widgets.get("Title")
            score_widget = dialog.widgets.get("Score")
            original_widget = dialog.widgets.get("Original or English title")
            date_widget = dialog.widgets.get("Date watching")
            kinopoisk_widget = dialog.widgets.get("Kinopoisk")
            imdb_widget = dialog.widgets.get("IMDb")

            if (
                isinstance(title_widget, QComboBox)
                and isinstance(score_widget, QDoubleSpinBox)
                and isinstance(original_widget, QLineEdit)
                and isinstance(date_widget, QDateEdit)
                and isinstance(kinopoisk_widget, QLineEdit)
                and isinstance(imdb_widget, QLineEdit)
            ):

                def _autofill_movie_fields(movie_title: str | None) -> None:
                    key = (movie_title or "").strip()
                    if not key:
                        return
                    record = movie_last_records.get(key)
                    if not record:
                        return

                    score_raw = (record.get("score", "") or "").strip().replace(",", ".")
                    with contextlib.suppress(ValueError):
                        score_widget.setValue(float(score_raw))

                    original_widget.setText(record.get("original", ""))
                    kinopoisk_widget.setText(record.get("kinopoisk", ""))
                    imdb_widget.setText(record.get("imdb", ""))
                    date_widget.setDate(QDate.currentDate())

                title_widget.currentTextChanged.connect(_autofill_movie_fields)
                if apply_initial_autofill and title_widget.currentText():
                    _autofill_movie_fields(title_widget.currentText())

        if selected_template == "📖 Book" and author_to_english:
            author_widget = dialog.widgets.get("Author")
            author_english_widget = dialog.widgets.get("Author's name in English")
            if isinstance(author_widget, QComboBox) and isinstance(author_english_widget, QLineEdit):

                def _update_author_english(author_text: str) -> None:
                    english_name = author_to_english.get(author_text, "")
                    author_english_widget.setText(english_name)

                author_widget.currentTextChanged.connect(_update_author_english)
                if apply_initial_autofill and author_widget.currentText():
                    _update_author_english(author_widget.currentText())


def _markdown_choice_sort_key(title: str) -> str:
    """Return casefolded title for sorting, ignoring leading emoji/symbols."""
    stripped = title.lstrip()
    for index, char in enumerate(stripped):
        if char.isalnum():
            return stripped[index:].lstrip().casefold()
    return stripped.casefold()
