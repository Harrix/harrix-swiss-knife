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
  - [BotHub (Food / Finance AI) on restricted networks](#bothub-food--finance-ai-on-restricted-networks)
- [📦 Building Windows install zip bundles](#-building-windows-install-zip-bundles)
  - [Before you start](#before-you-start)
  - [Steps](#steps)
- [VS Code extension: Harrix Notes Explorer (HSK)](#vs-code-extension-harrix-notes-explorer-hsk)
  - [Install (local, copy folder)](#install-local-copy-folder)
  - [Install via tray (Windows)](#install-via-tray-windows)
  - [Troubleshooting (extension missing in VS Code / Insiders)](#troubleshooting-extension-missing-in-vs-code--insiders)
  - [hsk boundary](#hsk-boundary)
  - [Usage](#usage)
  - [Customization](#customization)
- [➕ Add a new action](#-add-a-new-action)
  - [Example action with CLI command](#example-action-with-cli-command)
- [📁 Add file to a resource file](#-add-file-to-a-resource-file)
- [📝 Add a new Markdown template (for 📝 Add Markdown from template)](#-add-a-new-markdown-template-for--add-markdown-from-template)
  - [🚀 Quick start](#-quick-start)
  - [📋 Supported Field Types](#-supported-field-types)

</details>

## 💻 CLI commands

CLI commands after installation:

- `.venv\Scripts\Activate.ps1` — activate virtual environment
- `ruff check --select I --fix` — sort imports.
- `winget upgrade OpenJS.NodeJS`: upgrade Node.js (tray action **Update Node.js**).
- `pyside6-designer` — Qt Widgets Designer.
- `pyside6-uic src/harrix_swiss_knife/apps/finance/window.ui -o src/harrix_swiss_knife/apps/finance/window.py` — convert Finance UI file to PY class.
- `pyside6-uic src/harrix_swiss_knife/apps/fitness/window.ui -o src/harrix_swiss_knife/apps/fitness/window.py` — convert Fitness UI file to PY class.
- `pyside6-uic src/harrix_swiss_knife/apps/food/window.ui -o src/harrix_swiss_knife/apps/food/window.py` — convert Food UI file to PY class.
- `pyside6-uic src/harrix_swiss_knife/apps/habits/window.ui -o src/harrix_swiss_knife/apps/habits/window.py` — convert Habits UI file to PY class.
- `ruff check --fix` — lint and fix the project's Python files.
- `ruff check` — lint the project's Python files.
- `ruff format` — format the project's Python files.
- `ty check` — check Python types in the project's Python files.
- `uv python install 3.13` + `uv python pin 3.13` + `uv sync` — switch to a different Python version.
- `uv python upgrade` — upgrade python to the latest patch release.
- `uv self update` — update uv itself.
- `uv sync --upgrade` — update all project libraries (sometimes you need to call twice).
- `vermin src` — determine the minimum Python version using [vermin](https://github.com/netromdk/vermin). However, if the version is below 3.10, we stick with 3.10 because Python 3.10 annotations are used.

### BotHub (Food / Finance AI) on restricted networks

BotHub HTTPS uses `certifi` and optional `SSL_CERT_FILE` (corporate root CA). Proxy resolution order: `bothub.proxy` in `config/config.json` (empty = auto), Qt system proxy (PAC/WPAD on Windows), `HTTPS_PROXY` / `HTTP_PROXY`, then Windows/urllib proxy settings. Example: `"bothub": { "proxy": "http://proxy.school.local:3128", ... }`.

## 📦 Building Windows install zip bundles

Scripts live in `install\`. To refresh installer payloads and produce the distributable zips, run the **download/build steps** below in numeric order (`01` → `06`). Step **`06`** is optional log cleanup.

### Before you start

1. **Quit `harrix-swiss-knife` completely** (tray icon → exit, close any terminal running `main.py` from this repo’s `.venv`). While the app uses the project virtualenv, `uv sync` during cache refresh can fail with **Access is denied** when replacing DLLs under `.venv` (for example `matplotlib`).
2. Ensure sibling repos exist next to this checkout when you snapshot sources or warm the uv cache: `harrix-pylib`, `harrix-pyssg` (same parent folder as `harrix-swiss-knife`).
3. Some steps request **UAC elevation** (separate elevated PowerShell window).

### Steps

| Step | Batch file                                        | Zip pipeline | Purpose                                                                                                                                           |
| ---- | ------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | `install\01_download-bundle-force-binaries.bat`   | Core         | Media binaries + fallback zips → `install\dependencies\` (**elevated**).                                                                          |
| 2    | `install\02_download-bundle-force-installers.bat` | Core         | Installers (Git, Python, uv, VS Code) → `install\dependencies\` (**elevated**).                                                                   |
| 3    | `install\03_download-repos.bat`                   | Offline kit  | `git archive` snapshots → `install\dependencies\repos\`.                                                                                          |
| 4    | `install\04_download-uv-cache.bat`                | Offline kit  | Warm `install\dependencies\uv-cache\` (**quit `harrix-swiss-knife` first**).                                                                      |
| 5    | `install\06_build-install-zips.bat`               | Core         | Writes `install-harrix-swiss-knife.zip` and `install-offline-harrix-swiss-knife.zip` into `install\`.                                             |
| 6    | `install\07_clean-logs.bat`                       | Optional     | Logs only: `*.log` under `install\` and `install\dependencies\` (often **after** steps 1–5).                                                      |

After step 5, pick up the two zip files from `install\` for distribution.

## VS Code extension: Harrix Notes Explorer (HSK)

Local VS Code extension is bundled in this repo:

- Folder: `vscode/harrix-notes-explorer-hsk/`
- Entry point: `vscode/harrix-notes-explorer-hsk/extension.js`
- Manifest: `vscode/harrix-notes-explorer-hsk/package.json`

### Install (local, copy folder)

Current VS Code / Insiders / Cursor track unpacked extensions in **`extensions.json`** next to the extension folders (not only by scanning directories). Copying only the `harrix-notes-explorer-hsk` tree can leave the UI empty until that file lists **`local.harrix-notes-explorer-hsk`**.

The tray action (**Dev** → **Install or update Harrix Notes Explorer (HSK) extension**) copies the tree **and** upserts that ID into each target **`extensions.json`**. The repository deploy script (`install/harrix-swiss-knife.ps1`) does **not** install the extension into editors. If you copy by hand with `Copy-Item` only, either merge the same entry yourself or use **Developer: Install Extension from Location** once (see troubleshooting).

From the repo root in PowerShell: remove any existing `harrix-notes-explorer-hsk` folder under that editor’s `extensions` directory, then copy the bundled extension tree (ordinary directory; no symlinks).

VS Code Insiders:

```powershell
$src = (Resolve-Path ".\vscode\harrix-notes-explorer-hsk").Path
$dst = "$env:USERPROFILE\.vscode-insiders\extensions\harrix-notes-explorer-hsk"
if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Force -Recurse }
Copy-Item -LiteralPath $src -Destination $dst -Recurse
```

VS Code Stable:

```powershell
$src = (Resolve-Path ".\vscode\harrix-notes-explorer-hsk").Path
$dst = "$env:USERPROFILE\.vscode\extensions\harrix-notes-explorer-hsk"
if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Force -Recurse }
Copy-Item -LiteralPath $src -Destination $dst -Recurse
```

Cursor:

```powershell
$src = (Resolve-Path ".\vscode\harrix-notes-explorer-hsk").Path
$dst = "$env:USERPROFILE\.cursor\extensions\harrix-notes-explorer-hsk"
if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Force -Recurse }
Copy-Item -LiteralPath $src -Destination $dst -Recurse
```

### Install via tray (Windows)

From the tray app: **Dev** → **Update/Install Harrix Notes Explorer extensions for VSCode**. When **`path_harrix_notes_explorer`** is set, the action first rebuilds the public extension into that Git repo (everything except `.git/` is replaced), then opens a checkbox dialog for VS Code-family editors. It **copies** `vscode/harrix-notes-explorer-hsk` into `harrix-notes-explorer-hsk` under each selected editor’s extensions folder and **updates** **`extensions.json`**. Optionally installs public **`harrix-notes-explorer`** from the synced repo into the same editors. No UAC is required for a normal user profile.

Restart the editor or run **Developer: Reload Window** after installing.

### Troubleshooting (extension missing in VS Code / Insiders)

1. **Confirm `extensions.json` lists the extension**

Open `%USERPROFILE%\.vscode-insiders\extensions\extensions.json` (or `.vscode\extensions` / `.cursor\extensions` for the editor you use) and search for **`local.harrix-notes-explorer-hsk`**. If the folder exists but this ID is missing, the editor may not show the extension until you register it (tray action, or **Developer: Install Extension from Location**). 2. **Confirm the editor sees the install**

Run `code-insiders --list-extensions` (or `code --list-extensions`) and check for **`local.harrix-notes-explorer-hsk`**. 3. **Custom extensions directory**

Open `%USERPROFILE%\.vscode-insiders\argv.json` (or the matching `argv.json` for stable VS Code / Cursor) and check for **`--extensions-dir`**. If set, the extension folder and **`extensions.json`** live under that directory instead of the default `%USERPROFILE%\.vscode-insiders\extensions`. 4. **Copy failed or old files remain**

Close the corresponding editor (file locks), delete `%USERPROFILE%\…\extensions\harrix-notes-explorer-hsk` if needed, then run the tray action or `Copy-Item` again. 5. **Manual copy without tray or script**

Command Palette → **Developer: Install Extension from Location** → select the repo folder `vscode\harrix-notes-explorer-hsk` (or the copied `harrix-notes-explorer-hsk` folder). Then **Developer: Reload Window**. 6. **Logs**

**Developer: Show Logs…** → **Window** or **Extension Host** for manifest or path errors.

### hsk boundary

Commands that call `hsk` live in [`vscode/harrix-notes-explorer-hsk/harrix-cli.js`](vscode/harrix-notes-explorer-hsk/harrix-cli.js). The **HSK** extension keeps this layer; the **public** extension does not.

The public build runs as part of **Update/Install Harrix Notes Explorer extensions** (tray) or `hsk dev install-harrix-notes-explorer-hsk <editor>` when **`path_harrix_notes_explorer`** is configured:

- Reads **`path_harrix_notes_explorer`** and **`harrix_notes_explorer_publisher`** from `config/config.json` (defaults: `D:/GitHub/harrix-notes-explorer`, `harrix`).
- Builds from [`vscode/harrix-notes-explorer-hsk`](vscode/harrix-notes-explorer-hsk): renames `harrixNotesExplorerHsk.*` → `harrixNotesExplorer.*`, strips CLI files and manifest entries (see [`HARRIX_CLI.md`](vscode/harrix-notes-explorer-hsk/HARRIX_CLI.md)).
- **Deletes everything in the target repo except `.git/`**, then copies the build to the repo root (`package.json` at top level).
- Refuses to sync into the harrix-swiss-knife project root.
- CLI: add **`--with-public`** to also install `harrix-notes-explorer` from that repo into the editor profile (e.g. `dev install-harrix-notes-explorer-hsk insiders --with-public`).

Manual checklist (if not using the action): [`HARRIX_CLI.md`](vscode/harrix-notes-explorer-hsk/HARRIX_CLI.md) and [`package.harrix-cli.contributes.json`](vscode/harrix-notes-explorer-hsk/package.harrix-cli.contributes.json). Git discard, local add file/folder, and merged-note open stay in `extension.js`.

### Usage

- Open your notes folder as a workspace in VS Code.
- In **Explorer**, open the **Harrix Notes (HSK)** view.

Commands:

- **Refresh Harrix Notes (HSK):** `harrixNotesExplorerHsk.refresh`
- **Reveal in File Explorer:** `harrixNotesExplorerHsk.revealInOS`

### Customization

**Note labels in the tree** (`harrixNotesExplorerHsk.showNoteTitleFromContent`, default `true`): each note row uses YAML frontmatter `title:` if present, otherwise the first `#` heading, otherwise the file name without `.md`. Set to `false` to always show only the file name (previous behavior). When the label differs from the file name, `harrixNotesExplorerHsk.showNoteFileNameBesideTitle` (default `true`) controls whether the file name is shown as a gray description beside the title; set to `false` to show only the title.
Fenced code blocks in the built-in **Markdown preview** (including notes opened via **Harrix Notes (HSK)** with `openNotesInPreview`) can show **Copy** buttons (see `harrixNotesExplorerHsk.previewCopy.*` settings: enable buttons, top/bottom visibility, hover zone, colors). Defaults: top always visible, bottom on hover in the last 80px, background `#fefefe`, border/icon `#7f7f7f`. Preview scripts run only in a **trusted** workspace; if buttons are missing, check workspace trust and **Markdown: Preview Security Settings**. After changing colors or visibility, the preview refreshes automatically.

Example:

```json
{
  "harrixNotesExplorerHsk.previewCopy.backgroundColor": "#fefefe",
  "harrixNotesExplorerHsk.previewCopy.borderColor": "#7f7f7f",
  "harrixNotesExplorerHsk.previewCopy.topAlwaysVisible": true
}
```

If you previously used `notesExplorer.*` settings or `notesExplorer.gFile` under `workbench.colorCustomizations`, rename them to `harrixNotesExplorerHsk.*` and `local.harrix-notes-explorer-hsk.gFileHsk` (the extension contributes color ID `gFileHsk` for optional `*.g.md` theming).

Example user settings:

```json
{
  "workbench.colorCustomizations": {
    "local.harrix-notes-explorer-hsk.gFileHsk": "#C586C0"
  }
}
```

## ➕ Add a new action

Actions live under `src/harrix_swiss_knife/actions/`. Each menu section is a **subpackage** with one `On*` class per file:

| Section         | Package                | Used in `main.py` as        |
| --------------- | ---------------------- | --------------------------- |
| Apps            | `actions/apps/`        | `hsk.app_actions.OnFinance` |
| Dev             | `actions/development/` | `hsk.dev.OnAboutDialog`     |
| File operations | `actions/files/`       | `hsk.file.On…`              |
| Images          | `actions/images/`      | `hsk.images.On…`            |
| Markdown        | `actions/markdown/`    | `hsk.md.On…`                |
| Python          | `actions/python/`      | `hsk.py.On…`                |

**File name:** drop the `On` prefix and use snake*case — `OnCheckFeaturedImageInFolders` → `check_featured_image_in_folders.py`. For a reserved name like `exit`, use `exit*.py`.
**Steps:**

1. Create `src/harrix_swiss_knife/actions/<section>/<action_snake_case>.py` with `class On<Action>(ActionBase)` (import only what this action needs; see existing files in the same section).
2. Export the class from `src/harrix_swiss_knife/actions/<section>/__init__.py` (`from … import On…` and add to `__all__`).
3. Add the class to `menu_structure` in `src/harrix_swiss_knife/main.py` (`MainMenu.__init__()`, via `add_menu_structure(...)`).
4. Emoji icons: <https://emojidb.org/>.
5. If the action should be available from CLI (`hsk`):
   - Set `cli_available = True` and `cli_hint = "<section> <command-name>"` on the class.
   - Add a Click command in `src/harrix_swiss_knife/cli.py` (import from `harrix_swiss_knife.actions.<section>`).
   - Verify: `hsk <section> <command-name> --help` and a test run.
6. Run or restart `harrix-swiss-knife`.
7. Run `ty check` and `ruff check`.
8. From the tray app: `Python` → `ruff sort, ruff format, sort, make docs PY in …` on `harrix-swiss-knife`, then `Harrix PY check in …` on the same folder.

If the new action **inherits** another action or calls `OtherOnAction().execute(...)`, import that class from its module (e.g. `from harrix_swiss_knife.actions.images.optimize import OnOptimize`), not only from the section `__init__.py`.

Example action file:

```python
# src/harrix_swiss_knife/actions/files/check_featured_image_in_folders.py
"""Actions for file operations and management of directory structures."""
from __future__ import annotations
from typing import Any
import harrix_pylib as h
from harrix_swiss_knife.actions.base import ActionBase
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
        """Check for featured image files in all configured folders."""
        for path in self.config["paths_with_featured_image"]:
            result = h.file.check_featured_image(path)[1]
            self.add_line(result)
        self.show_result()
```

Register in the section package:

```python
# src/harrix_swiss_knife/actions/files/__init__.py (add import + __all__ entry)
from harrix_swiss_knife.actions.files.check_featured_image_in_folders import OnCheckFeaturedImageInFolders
```

### Example action with CLI command

- Add CLI command in `src/harrix_swiss_knife/cli.py` (import action + Click group/command).
- In the action, prefer `folder_path` + `noninteractive` so the same logic works in tray UI and CLI.
- Set `cli_available = True` and `cli_hint` (e.g. `"md check"`) so the tray menu and main window show a `ꟲᴸᴵ` suffix and CLI tooltip. The menu action also gets `cli_copy_command` for right-click **Copy CLI command** (tray menu and main window list).
- In `cli.py`, call `_exit_if_action_failed(action)` after the action runs. It exits with code `1` when `_cli_action_failed` finds any `❌` line or a `🔢 Count errors` line in `result_lines` (script-friendly checks):

```python
# src/harrix_swiss_knife/actions/<section>/<action_snake_case>.py
from __future__ import annotations
from pathlib import Path
from typing import Any
from harrix_swiss_knife.actions.base import ActionBase
class On<SomeActionName>Folder(ActionBase):
    """Do something with a folder (tray action + CLI command)."""
    icon = "🛠️"
    title = "<Human readable title>"
    cli_available = True
    cli_hint = "<section> <command-name>"
    def do_work_common(self) -> None:
        """Shared logic for tray thread and CLI (no dialogs)."""
        if self.folder_path is None:
            return
        self.add_line(f"🔵 Starting processing for path: {self.folder_path}")
        # ... do work synchronously ...
    @ActionBase.handle_exceptions("<context for errors>")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                self.title,
            )
            return
        if folder_path is not None:
            self.folder_path = Path(folder_path).resolve()
        else:
            self.folder_path = self.dialogs.get_folder_with_choice_option(
                self.config["<paths_config_key>"],
                self.config["<default_path_config_key>"],
            )
        if not self.folder_path:
            return
        if noninteractive:
            self.do_work_common()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)
    @ActionBase.handle_exceptions("<context> thread")
    def in_thread(self) -> str | None:
        self.do_work_common()
        return f"{self.title} completed"
    @ActionBase.handle_exceptions("<context> thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

```python
# src/harrix_swiss_knife/cli.py (add import + command; reuse _exit_if_action_failed at file bottom)
from __future__ import annotations
from pathlib import Path
import click
from harrix_swiss_knife.actions.<section> import On<SomeActionName>Folder
@cli.group("<section>")
def <section>_group() -> None:
    """<Section-related commands>."""
@<section>_group.command("<command-name>")
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def <command_name>(folder: Path) -> None:
    """<One-line help> (same as tray action)."""
    action = On<SomeActionName>Folder()
    action(folder_path=folder, noninteractive=True)
    _exit_if_action_failed(action)
```

CLI call examples:

- `hsk <section> <command-name> --help`
- `hsk <section> <command-name> "D:/path/to/folder"`
- `hsk <section> <command-name>` (uses current directory when `folder` defaults to `.`)

**Other CLI shapes** (see existing commands in `cli.py`):

- **Dialogs / Qt UI:** call `_ensure_qt_app()` before the action (e.g. `md new-note`, `md add-from-template`).
- **No folder argument:** pass kwargs to `execute(..., noninteractive=True)` (e.g. `dev install-harrix-notes-explorer-hsk` with `editor=` and optional `with_public=True`).
- **Extra Click options:** e.g. `md check --rule H001` (repeatable `--rule`); wire options into `execute` kwargs.

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
    title = "Update/Install global NPM packages"
    @ActionBase.handle_exceptions("NPM package management")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Install or update configured NPM packages globally."""
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

Example action with sequence of QThread (illustrative pattern only — this class is not shipped in the repo):

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

## 📝 Add a new Markdown template (for 📝 Add Markdown from template)

### 🚀 Quick start

Template system allows adding structured Markdown content (movies, books, etc.) through dynamic forms.

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
    "path_target": "D:/path/to/target-folder/",
    "insert_position": "start",
    "dialog_links": [
      {"label": "IMDb", "url": "https://www.imdb.com"},
      {"label": "Metacritic", "url": "https://www.metacritic.com"}
    ]
  },
  "Events (single file + image optimize)": {
    "template_file": "config/template-event.md",
    "path_target": "D:/Notes/Events/Events.md",
    "insert_position": "start",
    "image_optimize": true,
    "image_max_size": 1024,
    "dialog_links": [{"label": "Afisha", "url": "https://afisha.yandex.ru/"}]
  }
}
```

Options:

- `template_file` — Path to template file
- `path_target` — Target path (optional). Two modes:
  - **Folder:** path ends with `/` or has no `.md` → file is `{path_target}{current_year}.md`, e.g. `D:/Notes/Movies/` → `D:/Notes/Movies/2026.md`
  - **Single file:** path is a full path to a `.md` file, e.g. `D:/Notes/Events/Events.md` → all entries go into that file; new block is inserted under the current year section `## {year}` (or after TOC if that year section does not exist yet)
- `insert_position` — `"start"` (after year heading or TOC) or `"end"` (default)
- `edit_existing` — Optional. If `true`, choosing this template from New Markdown first asks whether to add a new entry or edit an existing one
- `path_layout` — Optional. `"city_note"` stores each entry as a separate note under `{path_target}/{City}/{Title}/{Title}.md` with optional `img/` (see `path_city_field`, `path_note_name_field`, `note_with_images`). Default: folder → `{year}.md`, or single `.md` file
- `path_city_field` — Field name for city subfolder when `path_layout` is `"city_note"` (default: `"City"`)
- `path_note_name_field` — Field name for note stem when `path_layout` is `"city_note"` (default: `"Title"`)
- `note_with_images` — Optional. If `true` with `city_note`, creates `img/` inside each note folder (default: `false`)
- `dialog_links` — Optional list of helper links shown only in the form dialog
- `image_optimize` — Optional. If `true`, the image from the template (when `path_target` is a file) is optimized after insert (same as “Optimize selected images in …”): copy to `img/`, optimize, optionally resize.
- `image_max_size` — Optional. Max width/height in pixels when `image_optimize` is used (e.g. `1024`)

**Image field when `path_target` is a file:** images are saved to `{path_target_parent}/img/`; drag & drop, paste from clipboard (Ctrl+V or Paste button) are supported; path in Markdown is relative (`img/filename.ext`). If the template also has a `Date` field, the image widget shows an internal “Filename:” row synced with the event date (default filename = date, user can change); existing files are not overwritten (`_1`, `_2` suffixes).

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
- **Dialog Links:** `dialog_links` items open in your default browser; they do not affect generated Markdown
- **Image/File Types:** Support drag & drop, file dialogs, and preview functionality
- **Image field:** When target is a single `.md` file, images are saved to that file’s `img/` folder; paste from clipboard (Ctrl+V or Paste button) is supported. If the template has a `Date` field, the image widget shows a “Filename:” row (default = date, editable); filenames are made unique (`_1`, `_2`) to avoid overwriting.
- **Images field (multiple):** Same as image; when target is a single `.md` file, images are saved to `img/` with date-based base name. If the template has a `Date` field, the widget shows a "Filename base:" row (default = date); files are named `date_01`, `date_02`, etc. The placeholder `{{Images:images}}` is replaced by one Markdown image line per file (alt text from `Title` if present).
- **Multiple Types:** `images` and `files` return comma-separated paths
- **Supported Image Formats:** PNG, JPG, JPEG, GIF, BMP, SVG, WEBP, AVIF
- **File Types:** Accept any file type for `file` and `files` fields
