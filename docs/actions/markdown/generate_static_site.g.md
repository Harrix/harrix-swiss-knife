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
    title = "Generate static site"

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

        if choice_type == "site":
            # Use configured site
            site = paths_sites[choice_data]
            self.md_folder = Path(site["input"])
            self.html_folder = Path(site["output"])
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

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("generating static site thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.md_folder is None or self.html_folder is None:
            return None

        self.add_line("🔵 Starting site generation")
        self.add_line(f"📁 Markdown folder: {self.md_folder}")
        self.add_line(f"📁 HTML output folder: {self.html_folder}")
        self.add_line("")

        try:
            sg = hsg.StaticSiteGenerator(self.md_folder)
            sg.generate_site(self.html_folder)
            self.add_line("✅ Site generation completed successfully")
            self.add_line(f"📊 Generated {len(sg.articles)} articles")
        except Exception as e:
            self.add_line(f"❌ Error during site generation: {e}")
            raise

        return None

    @ActionBase.handle_exceptions("generating static site thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
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

        if choice_type == "site":
            # Use configured site
            site = paths_sites[choice_data]
            self.md_folder = Path(site["input"])
            self.html_folder = Path(site["output"])
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
        self.add_line("")

        try:
            sg = hsg.StaticSiteGenerator(self.md_folder)
            sg.generate_site(self.html_folder)
            self.add_line("✅ Site generation completed successfully")
            self.add_line(f"📊 Generated {len(sg.articles)} articles")
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
