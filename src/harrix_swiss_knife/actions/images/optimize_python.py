"""Image optimization using Python SVG optimizer."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import harrix_pylib as h

from harrix_swiss_knife.actions.images.optimize import OnOptimize

RASTER_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".avif"})


class OnOptimizePython(OnOptimize):
    """Optimize images in the temp folder using Python for SVG and npm for raster.

    SVG files are optimized with the Python SVG optimizer from harrix-pylib.
    Raster images are processed through the existing npm optimize pipeline.
    """

    icon = "🐍"
    title = "Optimize images (Python SVG)"

    @OnOptimize.handle_exceptions("optimization thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        project_root = h.dev.get_project_root()
        images_folder = project_root / "temp/images"
        output_folder = project_root / "temp/optimized_images"
        return self.optimize_images_python(images_folder, output_folder)

    def optimize_images_python(self, images_folder: Path, output_folder: Path) -> str:
        """Optimize images with Python SVG optimizer and npm for raster files.

        Args:

        - `images_folder` (`Path`): Source folder with images.
        - `output_folder` (`Path`): Destination folder for optimized images.

        Returns:

        - `str`: Newline-separated status messages.

        """
        lines: list[str] = []
        if output_folder.exists():
            for item in output_folder.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        else:
            output_folder.mkdir(parents=True, exist_ok=True)

        if not images_folder.exists():
            lines.append(f"❌ Images folder not found: {images_folder}")
            return "\n".join(lines)

        raster_files: list[Path] = []
        for file in sorted(images_folder.iterdir()):
            if not file.is_file():
                continue
            ext = file.suffix.lower()
            if ext == ".svg":
                lines.append(h.img.optimize_svg(file, output_folder / file.name))
            elif ext in RASTER_EXTENSIONS:
                raster_files.append(file)

        if raster_files:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                for file in raster_files:
                    shutil.copy(file, temp_path / file.name)
                npm_result = h.dev.run_command(
                    f'npm run optimize imagesFolder="{temp_path}" '
                    f'outputFolder="{output_folder}" convertPngToAvif=compare'
                )
                if npm_result:
                    lines.append(npm_result)

        if not lines:
            lines.append("🔵 No supported image files found.")

        h.file.open_file_or_folder(output_folder)
        return "\n".join(lines)
