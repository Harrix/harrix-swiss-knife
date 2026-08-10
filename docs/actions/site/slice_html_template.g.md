---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `slice_html_template.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnSliceHtmlTemplate`](#%EF%B8%8F-class-onslicehtmltemplate)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnSliceHtmlTemplate`

```python
class OnSliceHtmlTemplate(ActionBase)
```

Slice a built Harrix HTML template (`dist/`) into SSG theme parts.

Reads a built template folder (for example `Harrix-HTML-Template/dist` or
`Harrix-HTML-Template-dist-history`) and writes `parts/`, optional asset
snippets, and copied CSS/JS into the theme output folder for
`harrix_pyssg.StaticSiteGenerator`.

<details>
<summary>Code:</summary>

```python
class OnSliceHtmlTemplate(ActionBase):

    icon = "✂️"
    title = "Slice HTML template…"
    description = "Slice built Harrix HTML template into theme parts for pyssg"
    cli_available: ClassVar[bool] = True
    cli_hint: ClassVar[str] = "site slice-html-template"

    dist_dir: Path | None = None
    theme_dir: Path | None = None
    source_html: str = "article.html"

    @ActionBase.handle_exceptions("slicing HTML template")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        output_path: Path | None = None,
        source_html: str | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Slice a built template folder into a theme directory."""
        if source_html:
            self.source_html = source_html

        if noninteractive:
            if folder_path is None or output_path is None:
                self.handle_error(
                    ValueError("folder_path and output_path are required when noninteractive is True"),
                    self.title,
                )
                return
            self.dist_dir = Path(folder_path).resolve()
            self.theme_dir = Path(output_path).resolve()
            self._slice_template()
            return

        default_dist = self.config.get("path_html_template_dist", ".")
        self.dist_dir = self.dialogs.get_existing_directory(
            "Select built HTML template folder (dist)",
            default_dist,
        )
        if not self.dist_dir:
            return
        self.dist_dir = Path(self.dist_dir).resolve()

        default_theme = str(self.config.get("path_html_theme", self.dist_dir.parent / "theme"))
        theme_text = self.dialogs.get_path_input(
            "Theme output folder",
            "Path for sliced theme parts (folder will be created/replaced):",
            default_theme,
        )
        if not theme_text:
            return
        self.theme_dir = Path(theme_text).expanduser().resolve()

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("slicing HTML template thread")
    def in_thread(self) -> str | None:
        """Slice the template in a worker thread."""
        self._slice_template()
        return f"{self.title} completed"

    @ActionBase.handle_exceptions("slicing HTML template thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result dialog after the worker finishes."""
        self.show_toast(f"{self.title} completed")
        self.show_result()

    def _slice_template(self) -> None:
        """Run `ThemeSlicer` and write status lines."""
        if self.dist_dir is None or self.theme_dir is None:
            return

        self.add_line(f"📁 Template dist: {self.dist_dir}")
        self.add_line(f"📁 Theme output: {self.theme_dir}")
        self.add_line(f"📄 Source HTML: {self.source_html}")

        slicer = hsg.ThemeSlicer(
            dist_dir=self.dist_dir,
            theme_dir=self.theme_dir,
            source_html=self.source_html,
        )
        theme_path = slicer.slice()
        self.add_line(f"✅ Theme sliced to {theme_path}")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, folder_path: Path | None = None, output_path: Path | None = None, source_html: str | None = None, noninteractive: bool = False, **_kwargs: Any) -> None
```

Slice a built template folder into a theme directory.

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        output_path: Path | None = None,
        source_html: str | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if source_html:
            self.source_html = source_html

        if noninteractive:
            if folder_path is None or output_path is None:
                self.handle_error(
                    ValueError("folder_path and output_path are required when noninteractive is True"),
                    self.title,
                )
                return
            self.dist_dir = Path(folder_path).resolve()
            self.theme_dir = Path(output_path).resolve()
            self._slice_template()
            return

        default_dist = self.config.get("path_html_template_dist", ".")
        self.dist_dir = self.dialogs.get_existing_directory(
            "Select built HTML template folder (dist)",
            default_dist,
        )
        if not self.dist_dir:
            return
        self.dist_dir = Path(self.dist_dir).resolve()

        default_theme = str(self.config.get("path_html_theme", self.dist_dir.parent / "theme"))
        theme_text = self.dialogs.get_path_input(
            "Theme output folder",
            "Path for sliced theme parts (folder will be created/replaced):",
            default_theme,
        )
        if not theme_text:
            return
        self.theme_dir = Path(theme_text).expanduser().resolve()

        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Slice the template in a worker thread.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        self._slice_template()
        return f"{self.title} completed"
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and result dialog after the worker finishes.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>
