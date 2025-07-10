---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# harrix-swiss-knife

![Featured image](https://raw.githubusercontent.com/Harrix/harrix-swiss-knife/refs/heads/main/img/featured-image.svg)

A multifunctional tool for developers with a rich set of utilities for working with files, images, Python code, and more.

<details>
<summary>📖 Contents</summary>

## Contents

- [List of commands](#list-of-commands)
- [Deploy on an empty machine (Windows)](#deploy-on-an-empty-machine-windows)
  - [Prerequisites](#prerequisites)
  - [Installation steps](#installation-steps)
  - [Running from command line](#running-from-command-line)
- [Development](#development)
  - [CLI commands](#cli-commands)
  - [Add a new action](#add-a-new-action)
  - [Add file to a resource file](#add-file-to-a-resource-file)
- [Create a shortcut](#create-a-shortcut)
- [License](#license)

</details>

This is a **personal** project tailored to **specific personal** tasks.

![GitHub](https://img.shields.io/badge/GitHub-harrix--swiss--knife-blue?logo=github) ![GitHub](https://img.shields.io/github/license/Harrix/harrix-swiss-knife)

GitHub: <https://github.com/Harrix/harrix-swiss-knife>

Documentation: [docs](https://github.com/Harrix/harrix-swiss-knife/blob/main/docs/index.g.md)

This project provides a Windows application with a system tray context menu, featuring mini-programs designed to automate specific personal tasks.

![Screenshot](https://raw.githubusercontent.com/Harrix/harrix-swiss-knife/refs/heads/main/img/screenshot.png)

_Figure 1: Screenshot_

## List of commands

- **Dev**
  - ℹ️ About
  - 📦 Install/Update global NPM packages
  - ⚙️ Open config.json
  - 📥 Update uv
- **Images**
  - 📸 Open Camera Uploads
  - 🚀 Optimize images
  - 🔝 Optimize images (high quality)
  - ⬆️ Optimize images in … and replace
  - 🖼️ Optimize one image
  - ↔️ Resize and optimize images (with PNG to AVIF)
  - 🧹 Clear folders images
  - 📂 Open the folder images
  - 📂 Open the folder optimized_images
- **File operations**
  - 🔒 Block disks
  - ✅ Check featured_image
  - ✅ Check featured_image in …
  - 🗂️ Moves and flattens files from nested folders
  - 📚 Rename FB2 files in …
  - 📚 Rename PDF files in …
  - 🖲️ Rename largest images to featured_image in …
  - ├ Tree view of a folder
  - ├ Tree view of a folder (ignore hidden folders)
- **Markdown**
  - 🎬 Get a list of movies, books for web
  - 👉 Increase heading level
  - ❞ Quotes. Format quotes as Markdown content
  - 😎 Beautify MD and regenerate .g.md in …
  - 😎 Beautify MD in …
  - 🚧 Check in …
  - 📥 Download images in …
  - 🧏 Generate a short version with only TOC
  - ⚖️ Optimize images in MD in …
  - ❞ Quotes. Add author and title
  - 📶 Sort sections in one MD
- **New Markdown**
  - ✍️ New article
  - 📖 New diary note
  - 💤 New dream note
  - 📓 New note
  - 📓 New note with images
- **Python**
  - 🚧 Check PY in …
  - 🐍 New uv project
  - 👷‍♂️ Publish Python library to PyPI
  - 🌟 isort, ruff format, sort in PY files
  - ⭐ isort, ruff format, sort, make docs in PY files
- 🏃🏻 Fitness tracker
- 🚀 Optimize image from clipboard
- 🚀 Optimize image from clipboard as …
- × Exit

## Deploy on an empty machine (Windows)

### Prerequisites

Install the following software:

- Git
- Cursor or VSCode (with Python extensions)
- Node.js
- [uv](https://docs.astral.sh/uv/) ([Installing and Working with uv (Python) in VSCode](https://github.com/Harrix/harrix.dev-articles-2025-en/blob/main/uv-vscode-python/uv-vscode-python.md))

### Installation steps

1. Clone project:

   ```shell
   mkdir C:/GitHub
   cd C:/GitHub
   git clone https://github.com/Harrix/harrix-pylib.git
   git clone https://github.com/Harrix/harrix-swiss-knife.git
   ```

2. Open the folder `C:/GitHub/harrix-swiss-knife` in Cursor (or VSCode).

3. Open a terminal `Ctrl` + `` ` ``.

4. Install dependencies (`uv sync --upgrade` is optional):

   ```shell
   uv sync
   uv add --editable ../harrix-pylib
   uv sync --upgrade
   npm i
   npm i -g npm-check-updates prettier
   ```

   Alternatively, instead of the two previous commands, run `Dev` → `Install/Update global NPM packages`.

5. Download required executables:
   - **ffmpeg.exe**: Download from [FFmpeg Builds](https://github.com/BtbN/FFmpeg-Builds/releases) (e.g., `ffmpeg-master-latest-win64-gpl.zip`)
   - **libavif executables** (`avifdec.exe`, `avifenc.exe`): Download from [libavif releases](https://github.com/AOMediaCodec/libavif/releases) (e.g., `libavif-v1.3.0-windows-x64-dynamic.zip`)

   Copy all executables to the project folder `C:/GitHub/harrix-swiss-knife`.

6. Run the application:
   Open `src\harrix_swiss_knife\main.py` and run (or run `C:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe C:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py` in a terminal).

### Running from command line

After installation, you can run the script from terminal:

```shell
c:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe c:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py
```

## Development

<details>
<summary>Development ⬇️</summary>

### CLI commands

CLI commands after installation:

- `uv self update` — update uv itself.
- `uv sync --upgrade` — update all project libraries (sometimes you need to call twice).
- `ruff check` — lint the project's Python files.
- `ruff check --fix` — lint and fix the project's Python files.
- `pyside6-rcc src/harrix_swiss_knife/resources.qrc -o src/harrix_swiss_knife/resources_rc.py` — convert UI file to PY class.
- `isort .` — sort imports.
- `ruff format` — format the project's Python files.
- `uv python install 3.13` + `uv python pin 3.13` + `uv sync` — switch to a different Python version.
- `vermin src` — determine the minimum Python version using [vermin](https://github.com/netromdk/vermin). However, if the version is below 3.10, we stick with 3.10 because Python 3.10 annotations are used.

### Add a new action

- Add a new action `class On<action>(action_base.ActionBase)` in `src/harrix_swiss_knife/action_<section>.py`.
- Site for searching emojis: <https://emojidb.org/>.
- In `main.py` add action `self.add_items(...)`.
- From `harrix-swiss-knife`, call the command `Python` → `isort, ruff format, sort, make docs in PY files` and select the folder `harrix_swiss_knife`.

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

### Add file to a resource file

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

</details>

## Create a shortcut

To create a desktop shortcut, use the following path:

```shell
C:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe C:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py
```

## License

License: [MIT](https://github.com/Harrix/harrix-swiss-knife/blob/main/LICENSE.md).
