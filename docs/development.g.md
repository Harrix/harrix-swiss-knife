---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# ⚙️ Development

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [💻 CLI commands](#-cli-commands)
- [➕ Add a new action](#-add-a-new-action)
- [📁 Add file to a resource file](#-add-file-to-a-resource-file)
- [📝 Add a new Markdown template (for 📝 Add markdown from template)](#-add-a-new-markdown-template-for--add-markdown-from-template)
  - [🚀 Quick start](#-quick-start)
  - [📋 Supported Field Types](#-supported-field-types)

</details>

## 💻 CLI commands

CLI commands after installation:

- `.venv\Scripts\Activate.ps1` — activate virtual environment
- `isort .` — sort imports.
- `npm update`: update packages according to `package.json`.
- `pyside6-designer` — Qt Widgets Designer.
- `pyside6-uic src/harrix_swiss_knife/apps/finance/window.ui -o src/harrix_swiss_knife/apps/finance/window.py` — convert Finance UI file to PY class.
- `pyside6-uic src/harrix_swiss_knife/apps/fitness/window.ui -o src/harrix_swiss_knife/apps/fitness/window.py` — convert Fitness UI file to PY class.
- `pyside6-uic src/harrix_swiss_knife/apps/food/window.ui -o src/harrix_swiss_knife/apps/food/window.py` — convert Food UI file to PY class.
- `ruff check --fix` — lint and fix the project's Python files.
- `ruff check` — lint the project's Python files.
- `ruff format` — format the project's Python files.
- `ty check` — check Python types in the project's Python files.
- `uv python install 3.13` + `uv python pin 3.13` + `uv sync` — switch to a different Python version.
- `uv self update` — update uv itself.
- `uv sync --upgrade` — update all project libraries (sometimes you need to call twice).
- `vermin src` — determine the minimum Python version using [vermin](https://github.com/netromdk/vermin). However, if the version is below 3.10, we stick with 3.10 because Python 3.10 annotations are used.

## ➕ Add a new action

- Add a new action `class On<action>(action_base.ActionBase)` in `src/harrix_swiss_knife/action_<section>.py`.
- Site for searching emojis: <https://emojidb.org/>.
- In `main.py` add action `self.add_items(...)`.
- Run or restart `harrix-swiss-knife`.
- Run `ty check`.
- Run `ruff check`.
- Check error messages in Cursor.
- From `harrix-swiss-knife`, call the command `Python` → `isort, ruff format, sort, make docs in PY files` and select the folder `harrix-swiss-knife`.
- From `harrix-swiss-knife`, call the command `Python` → `Check PY in ...` and select folder `harrix-swiss-knife`.

Example action:

```python
class OnCheckFeaturedImageInFolders(ActionBase):
    """Check for featured image files in all configured folders.

    This action automatically checks all directories specified in the
    paths_with_featured_image configuration setting for the presence of
    files named `featured_image` with any extension, providing a status
    report for each directory.
    """

    icon = "✅"
    title = "Check featured_image"

    @ActionBase.handle_exceptions("checking featured image in folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        for path in self.config["paths_with_featured_image"]:
            result = h.file.check_featured_image(path)[1]
            self.add_line(result)
        self.show_result()
```

Example action with QThread:

```python
class OnNpmManagePackages(ActionBase):
    """Install or update configured NPM packages globally.

    This action manages NPM packages specified in the `config["npm_packages"]` list:
    1. Updates NPM itself to the latest version
    2. Installs/updates all configured packages (npm install will update if already exists)
    3. Runs global update to ensure all packages are at latest versions

    This ensures all configured packages are present and up-to-date in the system.
    """

    icon = "📦"
    title = "Install/Update global NPM packages"

    @ActionBase.handle_exceptions("NPM package management")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("NPM operations thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Update NPM itself first
        self.add_line("Updating NPM...")
        result = h.dev.run_command("npm update npm -g")
        self.add_line(result)

        # Install/update all configured packages
        self.add_line("Installing/updating configured packages...")
        install_commands = "\n".join([f"npm i -g {package}" for package in self.config["npm_packages"]])
        result = h.dev.run_command(install_commands)
        self.add_line(result)

        # Run global update to ensure everything is up-to-date
        self.add_line("Running global update...")
        result = h.dev.run_command("npm update -g")
        self.add_line(result)

        return "NPM packages management completed"

    @ActionBase.handle_exceptions("NPM thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("NPM packages management completed")
        self.add_line(result)
        self.show_result()
```

Example action with sequence of QThread:

```python
class OnHarrixActionWithSequenceOfThread(ActionBase):
    """Docstring."""

    icon = "👷‍♂️"
    title = "Sequence of thread"

    @ActionBase.handle_exceptions("action")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread_01, self.thread_after_01, self.title)
        return "Started the process chain"

    @ActionBase.handle_exceptions("action thread 01")
    def in_thread_01(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # First operation
        self.add_line("Starting first operation")
        time.sleep(5)  # Simulating work
        return "First operation completed"

    @ActionBase.handle_exceptions("action thread 02")
    def in_thread_02(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Second operation
        self.add_line("Starting second operation")
        time.sleep(self.time_waiting_seconds)  # Simulating work
        return "Second operation completed"

    @ActionBase.handle_exceptions("action thread 03")
    def in_thread_03(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Third operation
        self.add_line("Starting third operation")
        time.sleep(5)  # Simulating work
        return "Third operation completed"

    @ActionBase.handle_exceptions("action thread 01 completion")
    def thread_after_01(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread_01(). For handling the results of thread execution."""
        self.add_line(result)  # Log the result from the first thread

        # Start the second operation
        self.time_waiting_seconds = 20
        message = f"Wait {self.time_waiting_seconds} seconds for the package to be published."
        self.start_thread(self.in_thread_02, self.thread_after_02, message)

    @ActionBase.handle_exceptions("action thread 02 completion")
    def thread_after_02(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread_02(). For handling the results of thread execution."""
        self.add_line(result)  # Log the result from the second thread

        # Start the third operation
        self.start_thread(self.in_thread_03, self.thread_after_03, self.title)

    @ActionBase.handle_exceptions("action thread 03 completion")
    def thread_after_03(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread_03(). For handling the results of thread execution."""
        self.add_line(result)  # Log the result from the third thread
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

## 📁 Add file to a resource file

Add files (pictures, etc.) to the `src\harrix_swiss_knife\assets` folder.

In the file `resources.qrc` add line for example `<file>assets/logo.svg</file>`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<RCC>
    <qresource prefix="/">
        <file>assets/logo.svg</file>
    </qresource>
</RCC>
```

Generate `resources_rc.py`:

```shell
pyside6-rcc src/harrix_swiss_knife/resources.qrc -o src/harrix_swiss_knife/resources_rc.py
```

## 📝 Add a new Markdown template (for 📝 Add markdown from template)

### 🚀 Quick start

Template system allows adding structured markdown content (movies, books, etc.) through dynamic forms.

Create a new `.md` file in `config/` folder with field placeholders:

```markdown
## {{Title:line}}: {{Score:float:10}}

![Featured Image]({{Featured Image:image}})

- **Date:** {{Date:date}}
- **URL:** <{{URL:line}}>
- **Source:** {{Source:line}}
- **Published:** {{Published:bool:true}}
- **Comments:** {{Comments:multiline}}

## Gallery

{{Gallery Images:images}}

## Documents

[Download]({{Main Document:file}})

## Attachments

{{Attachments:files}}
```

Add template configuration to `config/config.json`:

```json
"markdown_templates": {
  "your-template-name": {
    "template_file": "config/template-your-name.md",
    "target_file": "D:/path/to/target-file.md",
    "insert_position": "start",
    "dialog_links": [
      {"label": "IMDb", "url": "https://www.imdb.com"},
      {"label": "Metacritic", "url": "https://www.metacritic.com"}
    ]
  }
}
```

Options:

- `template_file` — Path to template file
- `target_file` — Target markdown file (optional, if omitted - just returns text)
- `insert_position` — `"start"` (after TOC) or `"end"` (default)
- `dialog_links` — Optional list of helper links shown only in the form dialog

### 📋 Supported Field Types

Syntax:

```text
{{FieldName:FieldType}}
{{FieldName:FieldType:DefaultValue}}
```

Available types:

| Type        | Widget                 | Example                  | Default Value Example                      |
| ----------- | ---------------------- | ------------------------ | ------------------------------------------ |
| `line`      | Single-line text input | `{{Title:line}}`         | `{{Title:line:Untitled}}`                  |
| `int`       | Integer spinner        | `{{Season:int}}`         | `{{Season:int:1}}`                         |
| `float`     | Decimal spinner        | `{{Score:float}}`        | `{{Score:float:10}}`                       |
| `date`      | Date picker            | `{{Date:date}}`          | `{{Date:date:2025-01-01}}`                 |
| `bool`      | Checkbox               | `{{Published:bool}}`     | `{{Published:bool:true}}`                  |
| `multiline` | Text area              | `{{Comments:multiline}}` | `{{Comments:multiline:No comments}}`       |
| `image`     | Single image picker    | `{{Featured:image}}`     | `{{Featured:image:path/to/img.png}}`       |
| `images`    | Multiple image picker  | `{{Gallery:images}}`     | `{{Gallery:images:img1.png,img2.jpg}}`     |
| `file`      | Single file picker     | `{{Document:file}}`      | `{{Document:file:path/to/doc.pdf}}`        |
| `files`     | Multiple file picker   | `{{Attachments:files}}`  | `{{Attachments:files:doc1.pdf,doc2.docx}}` |

Notes:

- Float values that are whole numbers are formatted without decimals (`11.0` → `11`)
- Date format: `yyyy-MM-dd`
- Default values are optional
- **Dialog Links**: `dialog_links` items open in your default browser; they do not affect generated markdown
- **Image/File Types**: Support drag & drop, file dialogs, and preview functionality
- **Multiple Types**: `images` and `files` return comma-separated paths
- **Supported Image Formats**: PNG, JPG, JPEG, GIF, BMP, SVG, WEBP, AVIF
- **File Types**: Accept any file type for `file` and `files` fields
