"""Export or import personal private data (API keys and fitness catalog/images)."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.private_data import (
    ZIP_API_KEYS_DIR,
    PrivateDataSelection,
    default_private_data_zip_path,
    inspect_private_data_zip,
    install_private_data,
    list_api_key_files_in_zip,
    list_api_key_secret_files,
    pack_private_data,
    selection_from_part_flags,
)
from harrix_swiss_knife.paths import get_project_root


class OnTransferPrivateData(ActionBase):
    """Export or import personal private data for another machine.

    Choose **Export** or **Import**, then one dialog: data types (API keys and/or
    exercise catalog plus `fitness_img`) and which `api-keys/*.txt` files.
    Workout tables (`process`, `weight`) are never included. Import overlays
    images next to existing files and upserts the catalog by English name.

    """

    icon = "📦"
    title = "Transfer private data"
    cli_available = True
    cli_hint = "dev private-data export|import"

    CHOICE_EXPORT = "Export"
    CHOICE_IMPORT = "Import"
    PART_API_KEYS = "API keys"
    PART_FITNESS = "Exercise catalog and images"

    @ActionBase.handle_exceptions("transfer private data")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Run export or import from tray dialogs or CLI flags."""
        noninteractive = bool(kwargs.get("noninteractive"))
        mode = str(kwargs.get("mode") or "").strip().lower()
        project_root = get_project_root()
        default_zip = default_private_data_zip_path(project_root)
        sqlite_fitness = str(self.config.get("sqlite_fitness") or "")
        recover_sql = project_root / "src" / "harrix_swiss_knife" / "apps" / "fitness" / "recover.sql"

        if not mode:
            if noninteractive:
                self.add_line("❌ CLI requires `export` or `import`.")
                return
            chosen = self.get_choice_from_list_with_descriptions(
                self.title,
                "Choose export (pack a ZIP) or import (install a ZIP).",
                [
                    (self.CHOICE_EXPORT, "Pack selected data into a personal ZIP."),
                    (self.CHOICE_IMPORT, "Install selected data from a personal ZIP."),
                ],
            )
            if chosen is None:
                self.add_line("Cancelled.")
                self.show_result()
                return
            mode = "export" if chosen == self.CHOICE_EXPORT else "import"

        if mode == "export":
            self._run_export(
                project_root=project_root,
                default_zip=default_zip,
                sqlite_fitness=sqlite_fitness,
                noninteractive=noninteractive,
                zip_arg=kwargs.get("zip_path"),
                include_api_keys=bool(kwargs.get("include_api_keys")),
                include_fitness=bool(kwargs.get("include_fitness")),
                parts_specified=bool(kwargs.get("parts_specified")),
                api_key_files=_kwargs_api_key_files(kwargs),
            )
            return
        if mode == "import":
            self._run_import(
                project_root=project_root,
                default_zip=default_zip,
                sqlite_fitness=sqlite_fitness,
                recover_sql=recover_sql,
                noninteractive=noninteractive,
                zip_arg=kwargs.get("zip_path"),
                include_api_keys=bool(kwargs.get("include_api_keys")),
                include_fitness=bool(kwargs.get("include_fitness")),
                parts_specified=bool(kwargs.get("parts_specified")),
                api_key_files=_kwargs_api_key_files(kwargs),
            )
            return

        self.add_line(f"❌ Unknown mode: {mode}")
        if not noninteractive:
            self.show_result()

    def _apply_cli_api_key_files(
        self,
        selection: PrivateDataSelection,
        *,
        available_names: list[str],
        requested_names: tuple[str, ...],
    ) -> PrivateDataSelection | None:
        """Apply `--api-key` filenames, or keep every key when the list is empty.

        Args:

        - `selection` (`PrivateDataSelection`): Parts chosen for transfer.
        - `available_names` (`list[str]`): Filenames that exist for this operation.
        - `requested_names` (`tuple[str, ...]`): Filenames from `--api-key`.

        Returns:

        - `PrivateDataSelection | None`: Selection with filenames, or `None` on error.

        """
        if not selection.api_keys or not requested_names:
            return selection
        unknown = sorted(set(requested_names) - set(available_names))
        if unknown:
            self.add_line(f"❌ Unknown API key file(s): {', '.join(unknown)}")
            self.show_result()
            return None
        return replace(selection, api_key_files=requested_names)

    def _interactive_parts_and_keys(
        self,
        *,
        parts_label: str,
        keys_label: str,
        part_defaults: list[str],
        part_disabled: list[str],
        key_names: list[str],
    ) -> PrivateDataSelection | None:
        """One dialog: data types and API key files (same layout as the VS Code installer).

        Args:

        - `parts_label` (`str`): Help text for the data-type section.
        - `keys_label` (`str`): Help text for the API key file section.
        - `part_defaults` (`list[str]`): Data types checked by default.
        - `part_disabled` (`list[str]`): Data types that cannot be selected.
        - `key_names` (`list[str]`): API key filenames to show.

        Returns:

        - `PrivateDataSelection | None`: Combined selection, or `None` on cancel.

        """
        selected = self.get_dual_checkbox_selection(
            self.title,
            section1_title="Data",
            section1_label=parts_label,
            section1_choices=[self.PART_API_KEYS, self.PART_FITNESS],
            section1_default_selected=part_defaults,
            section1_disabled_choices=part_disabled,
            section2_title="API keys",
            section2_label=keys_label,
            section2_choices=key_names,
            section2_default_selected=key_names,
            section2_disabled_choices=[],
        )
        if selected is None:
            self.add_line("Cancelled.")
            self.show_result()
            return None
        parts, keys = selected
        want_keys = self.PART_API_KEYS in parts or bool(keys)
        want_fitness = self.PART_FITNESS in parts
        if not want_keys and not want_fitness:
            self.add_line("❌ Select at least one data type or API key file.")
            self.show_result()
            return None
        if self.PART_API_KEYS in parts and key_names and not keys:
            self.add_line("❌ Select at least one API key file.")
            self.show_result()
            return None
        if want_keys and not key_names:
            self.add_line("❌ No API key files are available for this selection.")
            self.show_result()
            return None
        return PrivateDataSelection(
            api_keys=want_keys,
            fitness=want_fitness,
            api_key_files=tuple(keys),
        )

    def _local_api_key_names(self, project_root: Path) -> list[str]:
        """Return secret filenames under the project's `api-keys` folder.

        Args:

        - `project_root` (`Path`): Application project root.

        Returns:

        - `list[str]`: Filenames, or an empty list when the folder is missing.

        """
        try:
            return [path.name for path in list_api_key_secret_files(project_root / ZIP_API_KEYS_DIR)]
        except FileNotFoundError:
            return []

    def _resolve_export_selection(
        self,
        *,
        project_root: Path,
        noninteractive: bool,
        include_api_keys: bool,
        include_fitness: bool,
        parts_specified: bool,
        requested_names: tuple[str, ...],
    ) -> PrivateDataSelection | None:
        key_names = self._local_api_key_names(project_root)
        if noninteractive or parts_specified:
            selection = selection_from_part_flags(api_keys=include_api_keys, fitness=include_fitness)
            return self._apply_cli_api_key_files(
                selection,
                available_names=key_names,
                requested_names=requested_names,
            )
        part_disabled = [] if key_names else [self.PART_API_KEYS]
        part_defaults = [self.PART_FITNESS]
        if key_names:
            part_defaults.insert(0, self.PART_API_KEYS)
        return self._interactive_parts_and_keys(
            parts_label="Choose which data to export.",
            keys_label="Choose which API key files to include.",
            part_defaults=part_defaults,
            part_disabled=part_disabled,
            key_names=key_names,
        )

    def _resolve_import_selection(
        self,
        *,
        zip_path: Path,
        present: PrivateDataSelection,
        noninteractive: bool,
        include_api_keys: bool,
        include_fitness: bool,
        parts_specified: bool,
        requested_names: tuple[str, ...],
    ) -> PrivateDataSelection | None:
        key_names = list_api_key_files_in_zip(zip_path) if present.api_keys else []
        if noninteractive or parts_specified:
            wanted = selection_from_part_flags(api_keys=include_api_keys, fitness=include_fitness)
            if not parts_specified:
                wanted = PrivateDataSelection(
                    api_keys=wanted.api_keys and present.api_keys,
                    fitness=wanted.fitness and present.fitness,
                )
            return self._apply_cli_api_key_files(
                wanted,
                available_names=key_names,
                requested_names=requested_names,
            )
        part_disabled: list[str] = []
        part_defaults: list[str] = []
        if present.api_keys:
            part_defaults.append(self.PART_API_KEYS)
        else:
            part_disabled.append(self.PART_API_KEYS)
        if present.fitness:
            part_defaults.append(self.PART_FITNESS)
        else:
            part_disabled.append(self.PART_FITNESS)
        return self._interactive_parts_and_keys(
            parts_label="Choose which data to import. Missing parts in this ZIP are disabled.",
            keys_label="Choose which API key files to import from this ZIP.",
            part_defaults=part_defaults,
            part_disabled=part_disabled,
            key_names=key_names,
        )

    def _resolve_zip_path(
        self,
        *,
        zip_arg: object,
        default_zip: Path,
        noninteractive: bool,
        save: bool,
        dialog_title: str,
    ) -> Path | None:
        if zip_arg is not None and str(zip_arg).strip():
            return Path(str(zip_arg)).expanduser()
        if noninteractive:
            return default_zip
        if save:
            chosen = self.get_save_filename(dialog_title, str(default_zip), "ZIP files (*.zip)")
        else:
            chosen = self.get_open_filename(dialog_title, str(default_zip), "ZIP files (*.zip)")
        if chosen is None:
            self.add_line("Cancelled.")
            self.show_result()
            return None
        return chosen

    def _run_export(
        self,
        *,
        project_root: Path,
        default_zip: Path,
        sqlite_fitness: str,
        noninteractive: bool,
        zip_arg: object,
        include_api_keys: bool,
        include_fitness: bool,
        parts_specified: bool,
        api_key_files: tuple[str, ...],
    ) -> None:
        selection = self._resolve_export_selection(
            project_root=project_root,
            noninteractive=noninteractive,
            include_api_keys=include_api_keys,
            include_fitness=include_fitness,
            parts_specified=parts_specified,
            requested_names=api_key_files,
        )
        if selection is None:
            return
        output_zip = self._resolve_zip_path(
            zip_arg=zip_arg,
            default_zip=default_zip,
            noninteractive=noninteractive,
            save=True,
            dialog_title="Export private data",
        )
        if output_zip is None:
            return
        if output_zip.suffix.lower() != ".zip":
            output_zip = output_zip.with_suffix(".zip")

        result = pack_private_data(
            project_root=project_root,
            sqlite_fitness=sqlite_fitness,
            output_zip=output_zip,
            selection=selection,
        )
        size_mb = result.zip_path.stat().st_size / (1024 * 1024)
        if selection.api_keys:
            names = ", ".join(result.api_key_files)
            self.add_line(f"Exported {result.api_keys_count} API key file(s): {names}")
        if selection.fitness:
            self.add_line(f"Exported {result.fitness_img_count} fitness image file(s).")
            self.add_line(f"Exported catalog: {result.exercises_count} exercise(s), {result.types_count} type(s).")
            if result.missing_exercise_images:
                missing = ", ".join(result.missing_exercise_images)
                self.add_line(f"No AVIF for {len(result.missing_exercise_images)} exercise(s): {missing}")
        self.add_line(f"ZIP: `{result.zip_path}` ({size_mb:.1f} MB)")
        self.add_line("Workout history (process/weight) is not included.")
        self.show_toast(f"{self.title} completed")
        self.show_result()

    def _run_import(
        self,
        *,
        project_root: Path,
        default_zip: Path,
        sqlite_fitness: str,
        recover_sql: Path,
        noninteractive: bool,
        zip_arg: object,
        include_api_keys: bool,
        include_fitness: bool,
        parts_specified: bool,
        api_key_files: tuple[str, ...],
    ) -> None:
        zip_path = self._resolve_zip_path(
            zip_arg=zip_arg,
            default_zip=default_zip,
            noninteractive=noninteractive,
            save=False,
            dialog_title="Import private data",
        )
        if zip_path is None:
            return

        present = inspect_private_data_zip(zip_path)
        selection = self._resolve_import_selection(
            zip_path=zip_path,
            present=present,
            noninteractive=noninteractive,
            include_api_keys=include_api_keys,
            include_fitness=include_fitness,
            parts_specified=parts_specified,
            requested_names=api_key_files,
        )
        if selection is None:
            return

        result = install_private_data(
            project_root=project_root,
            sqlite_fitness=sqlite_fitness,
            zip_path=zip_path,
            recover_sql_path=recover_sql,
            selection=selection,
        )
        if result.created_database and result.fitness_db_path is not None:
            self.add_line(f"Created fitness database from recover.sql: `{result.fitness_db_path}`")
        if selection.api_keys:
            self.add_line(f"Imported {result.api_keys_count} API key file(s).")
        if selection.fitness:
            img_dir = result.fitness_img_dir
            self.add_line(f"Imported {result.fitness_img_count} fitness image file(s) -> `{img_dir}`")
            stats = result.catalog_stats
            self.add_line(
                "Catalog upsert: "
                f"{stats.exercises_inserted} exercise(s) inserted, "
                f"{stats.exercises_updated} updated; "
                f"{stats.types_inserted} type(s) inserted, "
                f"{stats.types_updated} updated."
            )
            if result.missing_exercise_images:
                missing = ", ".join(result.missing_exercise_images)
                self.add_line(f"Still no AVIF for {len(result.missing_exercise_images)} exercise(s): {missing}")
            if result.fitness_db_path is not None:
                self.add_line(f"Fitness DB: `{result.fitness_db_path}`")
            self.add_line("Workout history (process/weight) was not modified.")
            self.add_line("If Fitness is open, restart that window to see catalog and image changes.")
        self.show_toast(f"{self.title} completed")
        self.show_result()


def _kwargs_api_key_files(kwargs: dict[str, Any]) -> tuple[str, ...]:
    """Return CLI `--api-key` filenames from action kwargs.

    Args:

    - `kwargs` (`dict[str, Any]`): Action keyword arguments.

    Returns:

    - `tuple[str, ...]`: Non-empty filenames to export, or empty for every key.

    """
    raw = kwargs.get("api_key_files")
    if raw is None:
        return ()
    if isinstance(raw, str):
        name = raw.strip()
        return (name,) if name else ()
    if isinstance(raw, (list, tuple)):
        return tuple(str(name).strip() for name in raw if str(name).strip())
    return ()
