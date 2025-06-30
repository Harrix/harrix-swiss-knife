---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# harrix-swiss-knife

![harrix-swiss-knife](https://raw.githubusercontent.com/Harrix/harrix-swiss-knife/refs/heads/main/img/featured-image.svg)

This is a **personal** project tailored to **specific personal** tasks.

![GitHub](https://img.shields.io/github/license/Harrix/harrix-swiss-knife)

GitHub: <https://github.com/Harrix/harrix-swiss-knife>.

This project provides an application with a context menu in the system tray, featuring mini-programs designed to automate specific personal tasks. The project is intended for use on Windows.

![Screenshot](https://raw.githubusercontent.com/Harrix/harrix-swiss-knife/refs/heads/main/img/screenshoot.png)

_Figure 1: Screenshot_

## List of commands

- **Dev**
  - Get the list of items from this menu
  - Install global NPM packages
  - Open config.json
  - Update NPM and global NPM packages
  - Update uv
- **Images**
  - Optimize images
  - Optimize images (high quality)
  - Optimize images in … and replace
  - Optimize one image
  - Resize and optimize images (with PNG to AVIF)
  - Clear folders images
  - Open the folder images
  - Open the folder optimized_images
- **File operations**
  - Block disks
  - Check featured_image
  - Check featured_image in …
  - Moves and flattens files from nested folders
  - Open Camera Uploads
  - Rename largest images to featured_image in …
  - Tree view of a folder
  - Tree view of a folder (ignore hidden folders)
- **Markdown**
  - Format quotes as Markdown content
  - Get a list of movies, books for web
  - Increase heading level
  - Add image captions in one MD
  - Add image captions in …
  - Beautify MD notes in …
  - Check in …
  - Check one MD
  - Combine MD files in …
  - Download images in one MD
  - Download images in …
  - Format YAML in …
  - Generate TOC in one MD
  - Generate TOC in …
  - Generate a short version with only TOC
  - Optimize images (with PNG to AVIF) in …
  - Optimize images in one MD
  - Optimize images in …
  - Prettier in …
  - Quotes. Add author and title
  - Sort sections in one MD
- **New Markdown**
  - New article
  - New diary note
  - New dream note
  - New note
  - New note with images
- **Python**
  - Extracts list of funcs to a MD list from one PY file
  - New uv project in Projects
  - New uv project in …
  - isort, ruff format, sort in PY files
  - isort, ruff format, sort, make docs in PY files
  - 01 Prepare harrix-pylib
  - 02 Publish and update harrix-pylib
- Fitness tracker
- Optimize image from clipboard
- Optimize image from clipboard as …
- Exit

## Deploy on an empty machine (Windows)

- Install [uv](https://docs.astral.sh/uv/) ([Installing and Working with uv (Python) in VSCode](https://github.com/Harrix/harrix.dev-articles-2025-en/blob/main/uv-vscode-python/uv-vscode-python.md)), Node.js, VSCode (with python extensions), Git.

- Clone project:

  ```shell
  mkdir C:/GitHub
  cd C:/GitHub
  git clone https://github.com/Harrix/harrix-swiss-knife.git
  ```

- Open the folder `C:/GitHub/harrix-swiss-knife` in VSCode.

- Open a terminal `Ctrl` + `` ` ``.

- Run `uv sync`.

- Run `uv sync --upgrade` (optional).

- Run `npm i`.

- Run `npm i -g npm-check-updates` and `npm i -g prettier` (or run `Dev` → `Install global NPM packages`).

- Download and copy `ffmpeg.exe` to the project folder `C:/GitHub/harrix-swiss-knife`. For example, from `ffmpeg-master-latest-win64-gpl.zip` (<https://github.com/BtbN/FFmpeg-Builds/releases>).

- Download and copy libavif executables (`avifdec.exe`, `avifenc.exe`) to the project folder `C:/GitHub/harrix-swiss-knife`. Download the latest Windows release from libavif releases page: <https://github.com/AOMediaCodec/libavif/releases>. Extract the executables from the Windows archive (e.g., `libavif-v1.3.0-windows-x64-dynamic.zip`).

- Open `src\harrix-swiss-knife\main.py` and run.

After you can run the script from a terminal (or VSCode):

```shell
c:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe c:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py
```

## Development

<details>
<summary>Development ⬇️</summary>

### CLI commands

CLI commands after installation.

- `uv self update` — update uv itself.
- `uv sync --upgrade` — update all project libraries (sometimes you need to call twice).
- `isort .` — sort imports.
- `ruff format` — format the project's Python files.
- `ruff check` — lint the project's Python files.
- `ruff check --fix` — lint and fix the project's Python files.
- `uv python install 3.13` + `uv python pin 3.13` + `uv sync` — switch to a different Python version.
- `vermin src` — determines the minimum version of Python.
- `ncu -u` + `npm install` + `npm audit fix --force` — update NPM packages.

### Add a new action

- Add a new action `class on_<action>(action_base.ActionBase)` in `src/harrix_swiss_knife/action_<section>.py`.
- Site for searching emojis <https://emojidb.org/>.
- In `main.py` add action `self.add_item(self.menu_<section>, hsk.md.on_<action>)` in `<section>`.
- From `harrix-swiss-knife`, call the command `Python` → `isort, ruff format, sort in PY files` and select the folder `harrix_swiss_knife`.

Example an action:

```python
class on_check_featured_image_in_folders(action_base.ActionBase):
    """Docstring."""

    icon = "✅"
    title = "Check featured_image.*"

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

Examples an action with QThread:

```python
class on_npm_update_packages(action_base.ActionBase):
    """Docstring."""

    icon = "📥"
    title = "Update NPM and global NPM packages"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = "npm update npm -g\nnpm update -g"
        return h.dev.run_powershell_script(commands)

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Update completed")
        self.add_line(result)
        self.show_result()
```

```python
class on_sort_isort_fmt_python_code_folder(action_base.ActionBase):
    """Docstring."""

    icon = "🌟"
    title = "isort, ruff format, sort in PY files"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory("Select Project folder", config["path_github"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = f"cd {self.folder_path}\nisort .\nruff format"
        self.add_line(h.dev.run_powershell_script(commands))
        self.add_line(h.file.apply_func(self.folder_path, ".py", h.py.sort_py_code))

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

Example an action with sequence of QThread:

```python
class on_harrix_action_with_sequence_of_thread(action_base.ActionBase):
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

### Update `harrix-pylib`

- Run `uv sync --upgrade` (maybe twice).
- Change version in line `"harrix-pylib>=<version>"` in `pyproject.toml`
- Run `uv sync --upgrade`.
- Create a commit `⬆️ Update harrix-pylib`.

Or from `harrix-swiss-knife`, call the command `Python` → `02 Publish and update harrix-pylib`.

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

### Convert UI file to PY class

```shell
pyside6-uic src/harrix_swiss_knife/fitness/window.ui -o src/harrix_swiss_knife/fitness/window.py
```

### Minimum Python Version

We determine the minimum Python version using [vermin](https://github.com/netromdk/vermin):

```shell
vermin src
```

However, if the version is below 3.10, we stick with 3.10 because Python 3.10 annotations are used.

</details>

## Create a shortcut

Example path for a shortcut:

```shell
C:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe c:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py
```

## License

License: [MIT](https://github.com/Harrix/harrix-swiss-knife/blob/main/LICENSE.md).
