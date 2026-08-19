"""Pack api-keys secrets, fitness images, and exercise catalog into a personal ZIP."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.private_data import (
    default_private_data_zip_path,
    pack_private_data,
)
from harrix_swiss_knife.paths import get_project_root


class OnPackPrivateData(ActionBase):
    """Pack personal private data for transfer to another machine.

    Includes `api-keys` secrets (not `*.example.txt`), `fitness_img`, and the
    exercise/type catalog from `sqlite_fitness`. Workout tables (`process`,
    `weight`) are not packed. Output ZIP is gitignored under `install/`.

    """

    icon = "📦"
    title = "Pack private data"
    cli_available = True
    cli_hint = "dev pack-private-data"

    @ActionBase.handle_exceptions("pack private data")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Pack private data to a ZIP path (dialog or CLI `--zip` / default)."""
        noninteractive = bool(kwargs.get("noninteractive"))
        project_root = get_project_root()
        default_zip = default_private_data_zip_path(project_root)

        zip_arg = kwargs.get("zip_path")
        if zip_arg is not None and str(zip_arg).strip():
            output_zip = Path(zip_arg).expanduser()
        elif noninteractive:
            output_zip = default_zip
        else:
            chosen = self.get_save_filename(
                "Pack private data",
                str(default_zip),
                "ZIP files (*.zip)",
            )
            if chosen is None:
                self.add_line("Cancelled.")
                self.show_result()
                return
            output_zip = chosen
            if output_zip.suffix.lower() != ".zip":
                output_zip = output_zip.with_suffix(".zip")

        sqlite_fitness = str(self.config.get("sqlite_fitness") or "")
        result = pack_private_data(
            project_root=project_root,
            sqlite_fitness=sqlite_fitness,
            output_zip=output_zip,
        )
        size_mb = result.zip_path.stat().st_size / (1024 * 1024)
        self.add_line(f"Packed {result.api_keys_count} api-key file(s).")
        self.add_line(f"Packed {result.fitness_img_count} fitness_img file(s).")
        self.add_line(f"Packed catalog: {result.exercises_count} exercise(s), {result.types_count} type(s).")
        self.add_line(f"ZIP: `{result.zip_path}` ({size_mb:.1f} MB)")
        self.add_line("Workout history (process/weight) is not included.")
        self.show_toast(f"{self.title} completed")
        self.show_result()
