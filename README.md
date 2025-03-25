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
  - ☰ Get the list of items from this menu
  - ⚙️ Open config.json
  - 📥 Install global NPM packages
  - 📥 Update NPM and global NPM packages
- **Apps**
  - 🏃🏻 Fitness tracker
- **Images**
  - 🚀 Optimize images
  - 🔝 Optimize images (high quality)
  - ⬆️ Optimize images in … and replace
  - ⬆️ Optimize images in …/temp
  - 🖼️ Optimize one image
  - 🧹 Clear folders images
  - 📂 Open the folder images
  - 📂 Open the folder optimized_images
- **File operations**
  - 🗂️ Moves and flattens files from nested folders
  - ✅ Check featured_image.* in …
  - ✅ Check featured_image.*
  - 🔒 Block disks
  - 📸 Open Camera Uploads
  - ├ Tree view of a folder (ignore hidden folders)
  - ├ Tree view of a folder
- **Markdown**
  - 💤 New dream note
  - 📚 New diary note with images
  - 📖 New diary note
  - ✍️ New article
  - 📓 New note with images
  - 📓 New note
  - 📥 Download images in one MD
  - 📥 Download images in …
  - ✨ Format YAML
  - ❞ Quotes. Add author and title
  - 🌄 Add image captions in …
  - 🌄 Add image captions in one MD
  - 📑 Generate TOC in …
  - 📑 Generate TOC in one MD
  - 🎬 Get a list of movies, books for web
  - 👉 Increase heading level
  - ✨ Prettier in …
  - 📶 Sort sections in …
  - 📶 Sort sections in one MD
  - 🔗 Combine MD files in …
- **Python**
  - 🌟 isort, ruff format, sort in PY files
  - 🐍 New uv project in …
  - 🐍 New uv project in Projects
  - 📶 Sort classes, methods, functions in one PY file
  - 📶 Sort classes, methods, functions in PY files
  - ⬇️ Extracts list of funcs to a MD list from one PY file
  - 🏗️ Generate MD documentation in …
  - 👩🏻‍🍳 01 Prepare harrix-pylib
  - 👷‍♂️ 02 Publish and update harrix-pylib
- 🚀 Optimize image from clipboard
- 🚀 Optimize image from clipboard as …
- × Exit

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

- Copy `ffmpeg.exe` to the project folder `C:/GitHub/harrix-swiss-knife`. For example, from `ffmpeg-master-latest-win64-gpl.zip` (<https://github.com/BtbN/FFmpeg-Builds/releases>).

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

### Add a new action

- Add a new action `class on_<action>(action_base.ActionBase)` in `src/harrix_swiss_knife/action_<section>.py`.
- Site for searching emojis <https://emojidb.org/>.
- If you need to display `output.txt` add the line `is_show_output = True` after `title: str = ...`.
- In `main.py` add action `self.add_item(self.menu_<section>, hsk.md.on_<action>)` in `<section>`.
- From `harrix-swiss-knife`, call the command `Python` → `isort, ruff format, sort in PY files` and select the folder `harrix_swiss_knife`.

Example an action:

```python
class on_sort_sections(action_base.ActionBase):
    icon: str = "⬆️"
    title: str = "Sort sections in one MD"

    def execute(self, *args, **kwargs):
        filename = self.get_open_filename("Open Markdown file", config["path_notes"], "Markdown (*.md);;All Files (*)")
        if not filename:
            return

        try:
            self.add_line(h.md.sort_sections(filename))
            self.add_line(h.md.generate_image_captions(filename))
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")
```

Example an action with QThread:

```python
class on_npm_update_packages(action_base.ActionBase):
    icon: str = "📥"
    title: str = "Update NPM and global NPM packages"

    def execute(self, *args, **kwargs):
        self.toast = toast_countdown_notification.ToastCountdownNotification(on_npm_update_packages.title)
        self.toast.show()
        self.toast.start_countdown()

        class Worker(QThread):
            finished = Signal(str)

            def __init__(self, parent=None):
                super().__init__(parent)

            def run(self):
                commands = "npm update npm -g\nnpm update -g"
                result = h.dev.run_powershell_script(commands)
                self.finished.emit(result)

        self.worker = Worker()
        self.worker.finished.connect(self.on_update_finished)
        self.worker.start()

    @Slot(str)
    def on_update_finished(self, result: str):
        self.toast.close()

        self.show_toast("Update completed", duration=2000)

        self.show_text_textarea(result)
        self.add_line(result)
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
pyside6-rcc src\harrix_swiss_knife\resources.qrc -o src\harrix_swiss_knife\resources_rc.py
```

### Convert UI file to PY class

```shell
pyside6-uic src/harrix_swiss_knife/fitness_window.ui -o src/harrix_swiss_knife/fitness_window.py
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
