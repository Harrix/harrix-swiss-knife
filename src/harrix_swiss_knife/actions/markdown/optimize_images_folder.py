"""Actions for Python development and Markdown file management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.common.md_image_optimize import optimize_images_in_md_file


class OnOptimizeImagesFolder(ActionBase):
    """Optimize images in Markdown files with PNG/AVIF size comparison."""

    icon = "🖼️"
    title = "Optimize images in MD in …"

    @ActionBase.handle_exceptions("optimizing images with size comparison")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Optimize images in Markdown files with PNG/AVIF size comparison."""
        self.folder_path = self.dialogs.get_existing_directory(
            "Select folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after_show_result, self.title)

    @ActionBase.handle_exceptions("optimizing images with size comparison thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        results = []
        for md_file in sorted(Path(self.folder_path).rglob("*.md")):
            if md_file.name.endswith(".g.md"):
                continue
            results.append(
                optimize_images_in_md_file(md_file, is_convert_png_to_avif=False, is_compare_png_avif_sizes=True)
            )
        self.add_line("\n".join(results))
