"""Actions for Python development and Markdown file management."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.markdown.md_image_optimize import transform_markdown_content


class OnOptimizeSelectedImages(ActionBase):
    """Optimize specific selected images in their corresponding Markdown file.

    This action allows users to select specific image files and optimizes only those
    images within their corresponding Markdown file. The action:

    1. Opens a file dialog to select multiple image files
    2. Finds the Markdown file one level up from the selected images
    3. Optimizes only the selected images within that Markdown file
    4. Updates the Markdown file with references to the optimized images

    This is useful when you want to optimize specific images without processing
    all images in a folder or when working with images in a specific location.

    """

    icon = "🖼️"
    title = "Optimize selected images in …"
    bold_title = True

    @ActionBase.handle_exceptions("optimizing selected images")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Optimize specific selected images in their corresponding Markdown file."""
        result = self.get_open_filenames_with_resize(
            "Select images to optimize",
            self.config["path_articles"],
            "Image files (*.png *.jpg *.jpeg *.gif *.webp *.mp4 *.svg *.avif);;All Files (*)",
        )
        if result[0] is None:
            return
        self.selected_images = result[0]
        resize_enabled = result[1]
        max_size_str = result[2]
        self.max_size: int | None = None
        if resize_enabled and max_size_str:
            try:
                self.max_size = int(max_size_str)
            except ValueError:
                self.max_size = 1024
        elif resize_enabled:
            self.max_size = 1024

        self.start_thread(self.in_thread, self.thread_after_show_result, self.title)

    def find_markdown_file_one_level_up(self, image_dir: Path) -> Path | None:
        """Find a Markdown file one level up from the given directory.

        Args:

        - `image_dir` (`Path`): Directory containing the images.

        Returns:

        - `Path | None`: Path to the Markdown file if found, `None` otherwise.

        """
        parent_dir = image_dir.parent
        md_files = list(parent_dir.glob("*.md"))

        if md_files:
            return md_files[0]
        return None

    @ActionBase.handle_exceptions("optimizing selected images thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if not self.selected_images:
            return

        images_by_dir: dict[Path, list[Path]] = {}
        for image_path in self.selected_images:
            parent_dir = image_path.parent
            images_by_dir.setdefault(parent_dir, []).append(image_path)

        processed_files = []
        for parent_dir, images in images_by_dir.items():
            md_file = self.find_markdown_file_one_level_up(parent_dir)
            if md_file:
                self.add_line(f"🔵 Found MD file: {md_file}")
                self.add_line(f"🔵 Processing {len(images)} images in {parent_dir}")
                result = self.optimize_selected_images_in_md(md_file, images, self.max_size)
                processed_files.append((md_file, result))
            else:
                self.add_line(f"❌ No Markdown file found one level up from {parent_dir}")

        if processed_files:
            self.add_line(f"✅ Processed {len(processed_files)} Markdown file(s)")
        else:
            self.add_line("❌ No Markdown files were processed")

    def optimize_selected_images_in_md(
        self, md_file: Path, selected_images: list[Path], max_size: int | None = None
    ) -> str:
        """Optimize only the selected images in a Markdown file."""
        try:
            document = md_file.read_text(encoding="utf-8")
            selected_image_names = {img.name for img in selected_images}
            document_new = transform_markdown_content(
                document,
                md_file.parent,
                filter_names=selected_image_names,
                is_compare_png_avif_sizes=True,
                max_size=max_size,
            )
            if document != document_new:
                md_file.write_text(document_new, encoding="utf-8")
                return f"✅ File {md_file} updated with optimized images."
        except Exception as e:
            return f"❌ Error processing {md_file}: {e}"
        return f"ℹ️ File {md_file} was not changed (no selected images found)."  # noqa: RUF001
