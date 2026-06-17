"""Image optimization using Python and external tools."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import harrix_pylib as h

from harrix_swiss_knife.actions.images.optimize import OnOptimize
from harrix_swiss_knife.actions.images.raster_optimize import RASTER_EXTENSIONS, optimize_raster_file

if TYPE_CHECKING:
    from pathlib import Path

TOOL_EXTENSIONS = h.img.EXE_RASTER_EXTENSIONS


class OnOptimizePython(OnOptimize):
    """Optimize images in the temp folder using Python and external tools.

    SVG files are optimized with the Python SVG optimizer from harrix-pylib.
    GIF, MP4, and AVIF files are processed via ffmpeg, avifenc, and avifdec.
    PNG, JPG, and WEBP files are processed via Pillow and ffmpeg.
    """

    icon = "🐍"
    title = "Optimize images (Python)"

    @OnOptimize.handle_exceptions("optimization thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        project_root = h.dev.get_project_root()
        images_folder = project_root / "temp/images"
        output_folder = project_root / "temp/optimized_images"
        return self.optimize_images_python(images_folder, output_folder, project_root)

    def optimize_images_python(self, images_folder: Path, output_folder: Path, project_root: Path) -> str:
        """Optimize images with Python, Pillow, and external tools.

        Args:

        - `images_folder` (`Path`): Source folder with images.
        - `output_folder` (`Path`): Destination folder for optimized images.
        - `project_root` (`Path`): Project root with ffmpeg.exe, avifenc.exe, avifdec.exe.

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

        for file in sorted(images_folder.iterdir()):
            if not file.is_file():
                continue
            ext = file.suffix.lower()
            if ext == ".svg":
                lines.append(h.img.optimize_svg(file, output_folder / file.name))
            elif ext in TOOL_EXTENSIONS:
                try:
                    output_name = file.with_suffix(".avif").name if ext in {".gif", ".mp4"} else file.name
                    lines.append(
                        h.img.optimize_image_with_tools(
                            file,
                            output_folder / output_name,
                            project_root=project_root,
                        )
                    )
                except RuntimeError as error:
                    lines.append(f"❌ Error while processing file {file.name}: {error}")
            elif ext in RASTER_EXTENSIONS:
                try:
                    lines.append(
                        optimize_raster_file(
                            file,
                            output_folder,
                            project_root,
                        )
                    )
                except (RuntimeError, ValueError) as error:
                    lines.append(f"❌ Error while processing file {file.name}: {error}")

        if not lines:
            lines.append("🔵 No supported image files found.")

        h.file.open_file_or_folder(output_folder)
        return "\n".join(lines)
