"""Image optimization and management actions."""

from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.images.optimize import OnOptimize


class OnOptimizeSingleImage(OnOptimize):
    """Optimize a single image file and replace the original in place.

    This action prompts the user to select a single image file, processes it
    using the npm optimize script, and replaces the original file with the
    optimized version in the same folder.
    """

    icon = "🖼️"
    title = "Optimize one image in …"
    bold_title = False

    @ActionBase.handle_exceptions("single file optimization")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Optimize a single image file and replace the original in place."""
        filename = self.dialogs.get_open_filename(
            "Select an Image File",
            self.config["path_articles"],
            "Image Files (*.jpg *.jpeg *.webp *.png *.svg *.avif *.mp4);;All Files (*)",
        )
        if not filename:
            return

        filename = Path(filename)
        target_dir = filename.parent
        stem = filename.stem

        with TemporaryDirectory() as temp_folder:
            temp_filename = Path(temp_folder) / filename.name
            shutil.copy(filename, temp_filename)

            # E501 fix: split long line for readability and line length
            npm_command = (
                f'npm run optimize imagesFolder="{temp_folder}" '
                'outputFolder="optimized_images" convertPngToAvif=compare'
            )
            result = self.optimize_images_common(
                npm_command,
                None,
            )

            if result is not None:
                self.add_line(result)

            optimized_dir = h.dev.get_project_root() / "temp/optimized_images"
            for ext in (".avif", ".png", ".svg"):
                output_file = optimized_dir / (stem + ext)
                if output_file.exists():
                    target_path = target_dir / (stem + ext)
                    shutil.copy2(output_file, target_path)
                    if target_path != filename and filename.exists():
                        filename.unlink()
                    h.file.open_file_or_folder(target_dir)
                    break

        self.show_result()
