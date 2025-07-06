# harrix-swiss-knife

![harrix-swiss-knife](https://raw.githubusercontent.com/Harrix/harrix-swiss-knife/refs/heads/main/img/featured-image.svg)

This is a **personal** project tailored to **specific personal** tasks.

![GitHub](https://img.shields.io/badge/GitHub-harrix--swiss--knife-blue?logo=github) ![GitHub](https://img.shields.io/github/license/Harrix/harrix-swiss-knife)

GitHub: <https://github.com/Harrix/harrix-swiss-knife>

This project provides a Windows application with a system tray context menu, featuring mini-programs designed to automate specific personal tasks.

![Screenshot](https://raw.githubusercontent.com/Harrix/harrix-swiss-knife/refs/heads/main/img/screenshot.png)

_Figure 1: Screenshot_

## List of commands

- **Dev**
  - ☰ Get the list of items from this menu
  - 📦 Install/Update global NPM packages
  - ⚙️ Open config.json
  - 📥 Update uv
- **Images**
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
  - 📸 Open Camera Uploads
  - 🖲️ Rename largest images to featured_image in …
  - ├ Tree view of a folder
  - ├ Tree view of a folder (ignore hidden folders)
- **Markdown**
  - ❞ Format quotes as Markdown content
  - 🎬 Get a list of movies, books for web
  - 👉 Increase heading level
  - 🌄 Add image captions in one MD
  - 🌄 Add image captions in …
  - 😎 Beautify MD notes in …
  - 🚧 Check in …
  - 🚧 Check one MD
  - 🔗 Combine MD files in …
  - 📥 Download images in one MD
  - 📥 Download images in …
  - ✨ Format YAML in …
  - 📑 Generate TOC in one MD
  - 📑 Generate TOC in …
  - 🤏 Generate a short version with only TOC
  - 🖼️ Optimize images (with PNG to AVIF) in …
  - 🖼️ Optimize images in one MD
  - 🖼️ Optimize images in …
  - ✨ Prettier in …
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
  - ⬇️ Extracts list of funcs to a MD list from one PY file
  - 🐍 New uv project in Projects
  - 🐍 New uv project in …
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
- VSCode (with Python extensions)
- Node.js
- [uv](https://docs.astral.sh/uv/) ([Installing and Working with uv (Python) in VSCode](https://github.com/Harrix/harrix.dev-articles-2025-en/blob/main/uv-vscode-python/uv-vscode-python.md))

### Installation steps

1. Clone project:

   ```shell
   mkdir C:/GitHub
   cd C:/GitHub
   git clone https://github.com/Harrix/harrix-swiss-knife.git
   ```

2. Open the folder `C:/GitHub/harrix-swiss-knife` in VSCode (or Cursor).

3. Open a terminal `Ctrl` + `` ` ``.

4. Install dependencies (`uv sync --upgrade` is optional):

   ```shell
   uv sync
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
class OnCheckFeaturedImageInFolders(action_base.ActionBase):
    """Check for featured image files in all configured folders.

    This action automatically checks all directories specified in the
    paths_with_featured_image configuration setting for the presence of
    files named `featured_image` with any extension, providing a status
    report for each directory.
    """

    icon = "✅"
    title = "Check featured_image"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        for path in config["paths_with_featured_image"]:
            try:
                result = h.file.check_featured_image(path)[1]
            except Exception as e:
                result = f"❌ Error: {e}"
            self.add_line(result)
        self.show_result()
```

Example action with QThread:

```python
class OnNpmUpdatePackages(action_base.ActionBase):
    """Update NPM itself and all globally installed packages.

    This action first updates the npm package manager to its latest version,
    then updates all globally installed npm packages to their latest versions,
    ensuring the development environment has the most current tools available.
    """

    icon = "📥"
    title = "Update NPM and global NPM packages"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = "npm update npm -g\nnpm update -g"
        return h.dev.run_powershell_script(commands)

    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Update completed")
        self.add_line(result)
        self.show_result()
```

Example action with sequence of QThread:

```python
class OnHarrixActionWithSequenceOfThread(action_base.ActionBase):
    """Docstring."""

    icon = "👷‍♂️"
    title = "Sequence of thread"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread_01, self.thread_after_01, self.title)
        return "Started the process chain"

    def in_thread_01(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # First operation
        self.add_line("Starting first operation")
        time.sleep(5)  # Simulating work
        return "First operation completed"

    def in_thread_02(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Second operation
        self.add_line("Starting second operation")
        time.sleep(self.time_waiting_seconds)  # Simulating work
        return "Second operation completed"

    def in_thread_03(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Third operation
        self.add_line("Starting third operation")
        time.sleep(5)  # Simulating work
        return "Third operation completed"

    def thread_after_01(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread_01(). For handling the results of thread execution."""
        self.add_line(result)  # Log the result from the first thread

        # Start the second operation
        self.time_waiting_seconds = 20
        message = f"Wait {self.time_waiting_seconds} seconds for the package to be published."
        self.start_thread(self.in_thread_02, self.thread_after_02, message)

    def thread_after_02(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread_02(). For handling the results of thread execution."""
        self.add_line(result)  # Log the result from the second thread

        # Start the third operation
        self.start_thread(self.in_thread_03, self.thread_after_03, self.title)

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
