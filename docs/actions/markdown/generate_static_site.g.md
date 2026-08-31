---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `generate_static_site.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnGenerateStaticSite`](#%EF%B8%8F-class-ongeneratestaticsite)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnGenerateStaticSite`

```python
class OnGenerateStaticSite(ActionBase)
```

Generate a static HTML site from Markdown files using harrix-pyssg.

This action prompts the user to select:

1. A folder containing Markdown files (md_folder)
2. An output folder for generated HTML files (html_folder)

It then uses the StaticSiteGenerator class from harrix-pyssg to convert
all Markdown files in the selected folder (and subfolders) into HTML files,
preserving the folder structure and copying associated images and assets.

<details>
<summary>Code:</summary>

```python
class OnGenerateStaticSite(ActionBase):

    icon = "🌐"
    title = "Generate static site…"
    icons_dir: Path | None = None
    theme_dir: Path | None = None

    @ActionBase.handle_exceptions("generating static site")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Generate a static HTML site from Markdown files using harrix-pyssg."""
        # Get sites from config
        paths_sites = self.config.get("paths_sites", [])

        # Build list of choices with site descriptions
        choices = []
        site_map = {}

        for idx, site in enumerate(paths_sites):
            if isinstance(site, dict) and "input" in site and "output" in site:
                display_text = f"🌐 {site['input']} → {site['output']}"
                choices.append(display_text)
                site_map[display_text] = ("site", idx)

        # Add manual selection option
        manual_choice_text = "📁 Select folders manually..."
        choices.append(manual_choice_text)
        site_map[manual_choice_text] = ("manual", None)

        # Show selection dialog (always show, even if only manual option is available)
        selected_choice = self.dialogs.get_choice_from_list(
            "Select site configuration",
            "Choose a site from the list or select folders manually:",
            choices,
        )

        if not selected_choice:
            return

        choice_type, choice_data = site_map[selected_choice]

        self.theme_dir: Path | None = None
        self.icons_dir: Path | None = None

        if choice_type == "site":
            # Use configured site
            site = paths_sites[choice_data]
            self.md_folder = Path(site["input"])
            self.html_folder = Path(site["output"])
            self.theme_dir = self._resolve_theme_dir(site.get("theme"))
            self.icons_dir = self._resolve_icons_dir(site.get("icons"))
        elif choice_type == "manual":
            # Request folders manually
            self.md_folder = self.dialogs.get_existing_directory(
                "Select folder with Markdown files",
                self.config.get("path_articles", self.config.get("path_notes", ".")),
            )
            if not self.md_folder:
                return

            self.html_folder = self.dialogs.get_existing_directory(
                "Select output folder for HTML files",
                str(self.md_folder.parent / "build_site"),
            )
            if not self.html_folder:
                return

            self.theme_dir = self._resolve_theme_dir(None)
            self.icons_dir = self._resolve_icons_dir(None)

        if self.theme_dir is None:
            continue_without_theme = self.dialogs.get_yes_no_question(
                "No HTML theme",
                "Theme folder is not set or missing.\n\n"
                "Without a sliced theme, pages will be body HTML fragments "
                "(no header/footer/CSS).\n\n"
                "Slice a template with `hsk site slice-html-template`, set "
                "`paths_sites[].theme` or `path_html_theme` in config.json, "
                "then retry.\n\n"
                "Continue with fragments only?",
                default_yes=False,
            )
            if not continue_without_theme:
                return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("generating static site thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.md_folder is None or self.html_folder is None:
            return None

        self.add_line("🔵 Starting site generation")
        self.add_line(f"📁 Markdown folder: {self.md_folder}")
        self.add_line(f"📁 HTML output folder: {self.html_folder}")
        if self.theme_dir is not None:
            self.add_line(f"🎨 Theme folder: {self.theme_dir}")
        if self.icons_dir is not None:
            self.add_line(f"🧩 Icons folder: {self.icons_dir}")
        self.add_line("")

        try:
            sg = hsg.StaticSiteGenerator(
                self.md_folder,
                theme_dir=self.theme_dir,
                site_name=str(self.config.get("site_name", "harrix.dev")),
                default_language=str(self.config.get("site_default_language", "ru")),
                site_title=str(self.config.get("site_title", "Harrix")),
                per_page=int(self.config.get("site_per_page", 20)),
                icons_dir=self.icons_dir,
                icons_per_page=int(self.config.get("site_icons_per_page", 96)),
                icons_language=str(self.config.get("site_icons_language", "en")),
            )
            sg.generate_site(self.html_folder)
            self.add_line("✅ Site generation completed successfully")
            self.add_line(f"📊 Generated {len(sg.articles)} articles")
            self.add_line(f"📄 Generated {len(sg.listing_pages)} listing pages")
            if sg.icon_families:
                self.add_line(f"🧩 Generated {len(sg.icon_families)} icon families")
                self.add_line(f"🔲 Generated {len(sg.icon_grid_pages)} icon grid pages")
        except Exception as e:
            self.add_line(f"❌ Error during site generation: {e}")
            raise

        return None

    @ActionBase.handle_exceptions("generating static site thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()

    def _resolve_icons_dir(self, icons_value: Any) -> Path | None:
        """Resolve a Harrix-Vector-Icons repo from site config or `path_vector_icons`."""
        candidates: list[Path] = []
        if icons_value:
            candidates.append(Path(str(icons_value)))
        default_icons = self.config.get("path_vector_icons")
        if default_icons:
            candidates.append(Path(str(default_icons)))
        for candidate in candidates:
            icons_dir = candidate.expanduser().resolve()
            if (icons_dir / "catalog.json").is_file() or (icons_dir / "icons").is_dir():
                return icons_dir
            if icons_dir.name == "icons" and icons_dir.is_dir():
                return icons_dir
        return None

    def _resolve_theme_dir(self, theme_value: Any) -> Path | None:
        """Resolve sliced theme directory from site config or global config."""
        candidates: list[Path] = []
        if theme_value:
            candidates.append(Path(str(theme_value)))
        default_theme = self.config.get("path_html_theme")
        if default_theme:
            candidates.append(Path(str(default_theme)))

        for candidate in candidates:
            theme_dir = candidate.expanduser().resolve()
            if (theme_dir / "parts" / "main.html").is_file():
                return theme_dir
        return None
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Generate a static HTML site from Markdown files using harrix-pyssg.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        # Get sites from config
        paths_sites = self.config.get("paths_sites", [])

        # Build list of choices with site descriptions
        choices = []
        site_map = {}

        for idx, site in enumerate(paths_sites):
            if isinstance(site, dict) and "input" in site and "output" in site:
                display_text = f"🌐 {site['input']} → {site['output']}"
                choices.append(display_text)
                site_map[display_text] = ("site", idx)

        # Add manual selection option
        manual_choice_text = "📁 Select folders manually..."
        choices.append(manual_choice_text)
        site_map[manual_choice_text] = ("manual", None)

        # Show selection dialog (always show, even if only manual option is available)
        selected_choice = self.dialogs.get_choice_from_list(
            "Select site configuration",
            "Choose a site from the list or select folders manually:",
            choices,
        )

        if not selected_choice:
            return

        choice_type, choice_data = site_map[selected_choice]

        self.theme_dir: Path | None = None
        self.icons_dir: Path | None = None

        if choice_type == "site":
            # Use configured site
            site = paths_sites[choice_data]
            self.md_folder = Path(site["input"])
            self.html_folder = Path(site["output"])
            self.theme_dir = self._resolve_theme_dir(site.get("theme"))
            self.icons_dir = self._resolve_icons_dir(site.get("icons"))
        elif choice_type == "manual":
            # Request folders manually
            self.md_folder = self.dialogs.get_existing_directory(
                "Select folder with Markdown files",
                self.config.get("path_articles", self.config.get("path_notes", ".")),
            )
            if not self.md_folder:
                return

            self.html_folder = self.dialogs.get_existing_directory(
                "Select output folder for HTML files",
                str(self.md_folder.parent / "build_site"),
            )
            if not self.html_folder:
                return

            self.theme_dir = self._resolve_theme_dir(None)
            self.icons_dir = self._resolve_icons_dir(None)

        if self.theme_dir is None:
            continue_without_theme = self.dialogs.get_yes_no_question(
                "No HTML theme",
                "Theme folder is not set or missing.\n\n"
                "Without a sliced theme, pages will be body HTML fragments "
                "(no header/footer/CSS).\n\n"
                "Slice a template with `hsk site slice-html-template`, set "
                "`paths_sites[].theme` or `path_html_theme` in config.json, "
                "then retry.\n\n"
                "Continue with fragments only?",
                default_yes=False,
            )
            if not continue_without_theme:
                return

        self.start_thread(self.in_thread, self.thread_after, self.title)
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
        if self.md_folder is None or self.html_folder is None:
            return None

        self.add_line("🔵 Starting site generation")
        self.add_line(f"📁 Markdown folder: {self.md_folder}")
        self.add_line(f"📁 HTML output folder: {self.html_folder}")
        if self.theme_dir is not None:
            self.add_line(f"🎨 Theme folder: {self.theme_dir}")
        if self.icons_dir is not None:
            self.add_line(f"🧩 Icons folder: {self.icons_dir}")
        self.add_line("")

        try:
            sg = hsg.StaticSiteGenerator(
                self.md_folder,
                theme_dir=self.theme_dir,
                site_name=str(self.config.get("site_name", "harrix.dev")),
                default_language=str(self.config.get("site_default_language", "ru")),
                site_title=str(self.config.get("site_title", "Harrix")),
                per_page=int(self.config.get("site_per_page", 20)),
                icons_dir=self.icons_dir,
                icons_per_page=int(self.config.get("site_icons_per_page", 96)),
                icons_language=str(self.config.get("site_icons_language", "en")),
            )
            sg.generate_site(self.html_folder)
            self.add_line("✅ Site generation completed successfully")
            self.add_line(f"📊 Generated {len(sg.articles)} articles")
            self.add_line(f"📄 Generated {len(sg.listing_pages)} listing pages")
            if sg.icon_families:
                self.add_line(f"🧩 Generated {len(sg.icon_families)} icon families")
                self.add_line(f"🔲 Generated {len(sg.icon_grid_pages)} icon grid pages")
        except Exception as e:
            self.add_line(f"❌ Error during site generation: {e}")
            raise

        return None
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>
