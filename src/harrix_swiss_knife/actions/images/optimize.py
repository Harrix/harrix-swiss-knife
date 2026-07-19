"""Image optimization and management actions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.images.image_optimize import optimize_images_in_folder as _optimize_images_in_folder


class OnOptimize(ActionBase):
    """Run standard image optimization on all images in the temp folder.

    Processes all images in the temporary `images` directory and writes
    optimized versions to the `optimized_images` directory.

    """

    icon = "🚀"
    title = "Optimize images"
    bold_title = True

    @ActionBase.handle_exceptions("image optimization")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Run standard image optimization on all images in the temp folder."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("optimization thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        project_root = h.dev.get_project_root()
        return self.run_optimize_images(
            project_root / "temp/images",
            project_root / "temp/optimized_images",
        )

    def run_optimize_images(
        self,
        images_folder: Path | str,
        output_folder: Path | str,
        *,
        quality: bool = False,
        max_size: int | None = None,
        compare_png_avif: bool = True,
        convert_png_to_avif: bool = False,
        clear_output: bool = True,
        open_output: bool = True,
    ) -> str:
        """Optimize images in a folder and optionally open the output directory."""
        project_root = h.dev.get_project_root()
        result = _optimize_images_in_folder(
            Path(images_folder),
            Path(output_folder),
            project_root,
            quality=quality,
            max_size=max_size,
            compare_png_avif=compare_png_avif,
            convert_png_to_avif=convert_png_to_avif,
            clear_output=clear_output,
        )
        if open_output:
            h.file.open_file_or_folder(output_folder)
        return result

    @ActionBase.handle_exceptions("optimization thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
