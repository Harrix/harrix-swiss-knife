---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `optimize_images_in_md.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnOptimizeImagesInMd`](#%EF%B8%8F-class-onoptimizeimagesinmd)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)

</details>

## 🏛️ Class `OnOptimizeImagesInMd`

```python
class OnOptimizeImagesInMd(ActionBase)
```

Optimize images in Markdown files with PNG/AVIF size comparison.

<details>
<summary>Code:</summary>

```python
class OnOptimizeImagesInMd(ActionBase):

    icon = "🖼️"
    title = "Optimize images in MD in …"
    cli_available = True
    cli_hint = "md optimize-images-folder [FOLDER] [--max-size N]"

    CONFIG_KEY: ClassVar[str] = "optimize_images_folder_max_size"
    DEFAULT_MAX_SIZE: ClassVar[int] = 1024

    @ActionBase.handle_exceptions("optimizing images with size comparison")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        max_size: int | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Optimize images in Markdown files with PNG/AVIF size comparison."""
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                "optimizing images with size comparison",
            )
            return

        if folder_path is not None:
            self.folder_path = Path(folder_path).resolve()
        else:
            self.folder_path = self.dialogs.get_existing_directory(
                "Select folder with Markdown files", self.config["path_articles"]
            )
        if not self.folder_path:
            return

        if noninteractive:
            self.max_size = max_size
        else:
            choice = self.get_max_image_size_option(
                "Optimize images — size limit",
                default_enabled=True,
                default_max_size=self._load_max_size_from_config(),
            )
            if choice is None:
                return
            enabled, value = choice
            self._save_config_value(self.CONFIG_KEY, value)
            self.max_size = value if enabled else None

        if self.max_size is not None:
            self.add_line(f"🔵 Max image size: {self.max_size}px")
        else:
            self.add_line("🔵 Max image size: not limited")

        if noninteractive:
            self.in_thread()
            return

        self.start_thread(self.in_thread, self.thread_after_show_result, self.title)

    @ActionBase.handle_exceptions("optimizing images with size comparison thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        size_stats = OptimizeSizeStats()
        md_files = [
            md_file for md_file in sorted(Path(self.folder_path).rglob("*.md")) if not md_file.name.endswith(".g.md")
        ]
        results = [
            optimize_images_in_md_file(
                md_file,
                is_convert_png_to_avif=False,
                is_compare_png_avif_sizes=True,
                max_size=self.max_size,
                size_stats=size_stats,
            )
            for md_file in h.file.iter_with_progress(md_files)
        ]
        summary = summarize_md_optimize_messages(results)
        if summary:
            self.add_line(summary)
        if size_stats.count > 0:
            self.add_line(size_stats.format_summary())

    def _load_max_size_from_config(self) -> int:
        """Return stored max size from config, or the default."""
        raw = self.config.get(self.CONFIG_KEY, self.DEFAULT_MAX_SIZE)
        try:
            value = int(raw)
        except (TypeError, ValueError):
            return self.DEFAULT_MAX_SIZE
        return value if value > 0 else self.DEFAULT_MAX_SIZE
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, folder_path: Path | None = None, max_size: int | None = None, noninteractive: bool = False, **_kwargs: Any) -> None
```

Optimize images in Markdown files with PNG/AVIF size comparison.

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        max_size: int | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                "optimizing images with size comparison",
            )
            return

        if folder_path is not None:
            self.folder_path = Path(folder_path).resolve()
        else:
            self.folder_path = self.dialogs.get_existing_directory(
                "Select folder with Markdown files", self.config["path_articles"]
            )
        if not self.folder_path:
            return

        if noninteractive:
            self.max_size = max_size
        else:
            choice = self.get_max_image_size_option(
                "Optimize images — size limit",
                default_enabled=True,
                default_max_size=self._load_max_size_from_config(),
            )
            if choice is None:
                return
            enabled, value = choice
            self._save_config_value(self.CONFIG_KEY, value)
            self.max_size = value if enabled else None

        if self.max_size is not None:
            self.add_line(f"🔵 Max image size: {self.max_size}px")
        else:
            self.add_line("🔵 Max image size: not limited")

        if noninteractive:
            self.in_thread()
            return

        self.start_thread(self.in_thread, self.thread_after_show_result, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        if self.folder_path is None:
            return
        size_stats = OptimizeSizeStats()
        md_files = [
            md_file for md_file in sorted(Path(self.folder_path).rglob("*.md")) if not md_file.name.endswith(".g.md")
        ]
        results = [
            optimize_images_in_md_file(
                md_file,
                is_convert_png_to_avif=False,
                is_compare_png_avif_sizes=True,
                max_size=self.max_size,
                size_stats=size_stats,
            )
            for md_file in h.file.iter_with_progress(md_files)
        ]
        summary = summarize_md_optimize_messages(results)
        if summary:
            self.add_line(summary)
        if size_stats.count > 0:
            self.add_line(size_stats.format_summary())
```

</details>
