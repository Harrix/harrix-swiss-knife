"""Install personal private-data ZIP (api-keys, fitness images, exercise catalog)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.private_data import (
    default_private_data_zip_path,
    install_private_data,
)
from harrix_swiss_knife.paths import get_project_root


class OnInstallPrivateData(ActionBase):
    """Install personal private data from a transfer ZIP.

    Overwrites matching `api-keys` secrets, overlays `fitness_img` (does not
    delete extras), and upserts exercises/types by English name. Does not
    modify `process` or `weight`. Close the Fitness tracker before installing
    if the database is locked.

    """

    icon = "📥"
    title = "Install private data"
    cli_available = True
    cli_hint = "dev install-private-data"

    @ActionBase.handle_exceptions("install private data")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Install private data from a ZIP path (dialog or CLI `--zip` / default)."""
        noninteractive = bool(kwargs.get("noninteractive"))
        project_root = get_project_root()
        default_zip = default_private_data_zip_path(project_root)

        zip_arg = kwargs.get("zip_path")
        if zip_arg is not None and str(zip_arg).strip():
            zip_path = Path(zip_arg).expanduser()
        elif noninteractive:
            zip_path = default_zip
        else:
            chosen = self.get_open_filename(
                "Install private data",
                str(default_zip),
                "ZIP files (*.zip)",
            )
            if chosen is None:
                self.add_line("Cancelled.")
                self.show_result()
                return
            zip_path = chosen

        sqlite_fitness = str(self.config.get("sqlite_fitness") or "")
        recover_sql = project_root / "src" / "harrix_swiss_knife" / "apps" / "fitness" / "recover.sql"
        result = install_private_data(
            project_root=project_root,
            sqlite_fitness=sqlite_fitness,
            zip_path=zip_path,
            recover_sql_path=recover_sql,
        )
        if result.created_database:
            self.add_line(f"Created fitness database from recover.sql: `{result.fitness_db_path}`")
        self.add_line(f"Installed {result.api_keys_count} api-key file(s).")
        self.add_line(f"Installed {result.fitness_img_count} fitness_img file(s) -> `{result.fitness_img_dir}`")
        stats = result.catalog_stats
        self.add_line(
            "Catalog upsert: "
            f"{stats.exercises_inserted} exercise(s) inserted, "
            f"{stats.exercises_updated} updated; "
            f"{stats.types_inserted} type(s) inserted, "
            f"{stats.types_updated} updated."
        )
        self.add_line(f"Fitness DB: `{result.fitness_db_path}`")
        self.add_line("Workout history (process/weight) was not modified.")
        self.add_line("If Fitness is open, restart that window to see catalog changes.")
        self.show_toast(f"{self.title} completed")
        self.show_result()
