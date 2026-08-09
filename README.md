# Harrix Swiss Knife

![Featured image](https://raw.githubusercontent.com/Harrix/harrix-swiss-knife/refs/heads/main/img/featured-image.svg)

🤖 Python application for automating personal tasks in Windows.

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [✨ Features](#-features)
- [📋 List of commands](#-list-of-commands)
- [🛠️ Deploy on an empty machine (Windows)](#️-deploy-on-an-empty-machine-windows)
  - [Prerequisites](#prerequisites)
  - [Quick install (PowerShell script)](#quick-install-powershell-script)
  - [Offline install (local bundle)](#offline-install-local-bundle)
  - [Installation steps (manual)](#installation-steps-manual)
  - [Running from command line](#running-from-command-line)
- [💻 CLI commands](#-cli-commands)
- [⚙️ Development](#️-development)
- [🔗 Create a shortcut](#-create-a-shortcut)
- [📄 License](#-license)
- [👤 Author](#-author)

</details>

This is a **personal** project tailored to **specific personal** tasks.

![GitHub](https://img.shields.io/badge/GitHub-harrix--swiss--knife-blue?logo=github) ![GitHub](https://img.shields.io/github/license/Harrix/harrix-swiss-knife)

GitHub: <https://github.com/Harrix/harrix-swiss-knife>

Documentation: [docs](https://github.com/Harrix/harrix-swiss-knife/blob/main/docs/index.g.md)

This project provides a Windows application with a system tray context menu, featuring mini-programs designed to automate specific personal tasks:

![Screenshot](https://raw.githubusercontent.com/Harrix/harrix-swiss-knife/refs/heads/main/img/screenshot.png)

_Figure 1: Screenshot_

## ✨ Features

- 🖼️ **Image Processing** - Optimize, resize, convert images with advanced compression
- 📁 **File Operations** - Batch file management, archive extraction, folder organization
- 📝 **Markdown Tools** - Document processing, TOC generation, content formatting
- 🐍 **Python Development** - Project setup, code formatting, PyPI publishing
- 🖥️ **System Tray Integration** - Quick access through Windows system tray menu
- ⚡ **Personal Automation** - Custom workflows tailored for specific tasks

## 📋 List of commands

- **Dev**
  - ℹ️ About
  - 🚀 Add to Windows autostart
  - 🧹 Clear temp folder
  - 🔗 Create desktop shortcut
  - ⬇️ Download ffmpeg, avifenc, avifdec
  - ⌨️ Install CLI (hsk on PATH) ꟲᴸᴵ
  - ⚙️ Open `config.json`
  - 📊 Show action usage stats ꟲᴸᴵ
  - 📌 Sync Quick Access folders to Total Commander
  - ⬆️ Update Harrix Swiss Knife from GitHub…
  - 📥 Update Node.js
  - 📥 Update uv
  - 📦 Update/Install global NPM packages
  - 📋 View recent action logs
- **Android**
  - 📱 Build Android APK in … ꟲᴸᴵ
  - 🔬 Check Android code in … ꟲᴸᴵ
  - ✨ Format Android code in … ꟲᴸᴵ
- **VS Code**
  - 🔬 Check VS Code extension ꟲᴸᴵ
  - ✨ Format VS Code extension ꟲᴸᴵ
  - 🔄 Sync Harrix Notes Explorer public repo ꟲᴸᴵ
  - 📦 Update/install Harrix Notes Explorer extension for VS Code… ꟲᴸᴵ
- **Images**
  - 📸 Open photos in image viewer
  - 🤖 Recognize text (AI)…
  - 🔤 Recognize text (OCR, local)…
  - 🚀 ★ Optimize images
  - 🔝 Optimize images (high quality)
  - ⬆️ Optimize images in … and replace
  - 🖼️ Optimize one image in …
  - ↔️ ★ Resize and optimize images…
  - 🧹 Clear folders `images` and `optimized_images`
  - 📂 Open folder `images`
  - 📂 Open folder `optimized_images`
  - 🚀 Optimize image from clipboard
  - 🚀 Optimize image from clipboard as …
  - 📷 Screenshot region
- **File operations**
  - ✅ Check featured_image in all folders
  - ✅ Check featured_image in …
  - 🤖 ★ Combine files for AI…
  - 🪟 Convert path to Windows from clipboard
  - ↩️ Discard uncommitted Git changes in … ꟲᴸᴵ
  - 📦 Extract ZIP archives in …
  - 🎯 Git commit message…
  - 📄 List files in …
  - 📄 List files in … (ignore hidden folders)
  - 📄 List files in … (only current folder)
  - 🔒 Lock disks (BitLocker)
  - 🗂️ Move and flatten files in …
  - 🗑️ Remove empty folders in …
  - 📚 Rename FB2, Epub, PDF files in …
  - 📅 Rename date in filenames DD.MM.YYYY → YYYY.MM.DD in …
  - 📝 Rename files by mapping in …
  - 🖲️ Rename largest images to featured_image in …
  - ├ Tree view in …
  - ├ Tree view in … (ignore hidden folders)
- **Markdown**
  - 📝 ★ New Markdown… ꟲᴸᴵ
  - 🎬 Get a list of movies, books for web…
  - 👈 Heading level: Decrease…
  - 👉 Heading level: Increase…
  - 🏷️ Append YAML tag in …
  - 💎 ★ Beautify MD and regenerate `.g.md` in … ꟲᴸᴵ
  - 💎 Beautify MD in … ꟲᴸᴵ
  - 🚧 Check MD in … ꟲᴸᴵ
  - 📥 Download images in …
  - ❞ Fix MD with quotes in …
  - 📑 Generate a short version with only TOC in …
  - 🌐 Generate static site…
  - 📋 Get set variables from YAML in …
  - 📁 Move MD into named folders in …
  - 🖼️ Optimize images in MD in … ꟲᴸᴵ
  - 🖼️ ★ Optimize selected images in …
  - 📶 Sort sections in …
- **Site**
  - 📦 Add site content submodule… ꟲᴸᴵ
  - 🔗 Fix site article link titles in … ꟲᴸᴵ
  - ⬇️ Pull site submodules ꟲᴸᴵ
- **Text**
  - 🤖 Fix text with AI from clipboard
  - 🤖 Fix text with AI… ꟲᴸᴵ
  - ✍️ Rewrite text with AI…
  - 🎙️ Speech to text with AI…
- **Python**
  - 🚧 Full PY check all projects ꟲᴸᴵ
  - 🚧 Full PY check in … ꟲᴸᴵ
  - 🚧 Harrix PY check in … ꟲᴸᴵ
  - 🐍 New uv library in …
  - 📓 New uv notebook in …
  - 🐍 New uv project in …
  - ⚡ Publish Python library to PyPI in …
  - 🌟 Ruff sort, ruff format, sort PY in … ꟲᴸᴵ
  - 🌟 ★ Ruff sort, ruff format, sort, make docs PY in … ꟲᴸᴵ
- 💰 Finance tracker
- 🏃🏻 Fitness tracker
- 🍔 Food tracker
- ✅ Habit tracker
- ⚡ Quick launcher…
- × Exit

## 🛠️ Deploy on an empty machine (Windows)

### Prerequisites

Install the following software:

- Git
- [uv](https://docs.astral.sh/uv/) (manages CPython; no separate Python installer required)
- Cursor or VSCode (with Python extensions)

### Quick install (PowerShell script)

### Offline install (local bundle)

If you need a more reliable install (slow/blocked internet), you can prepare an offline bundle once on a machine with internet:

```powershell
.\install\download-bundle.ps1
```

This will populate `install\dependencies\` (ignored by Git) with installers and binaries. Then copy the whole `install\` folder to the target machine and run:

```powershell
.\install\install.bat
```

Run in PowerShell. The script can detect the parent folder when you run it from an already-cloned `harrix-swiss-knife` repo (`install\harrix-swiss-knife.ps1`) or pick a default automatically.

**Standalone bootstrap** (no clone yet; downloads the script then runs it):

```powershell
irm https://raw.githubusercontent.com/Harrix/harrix-swiss-knife/main/install/harrix-swiss-knife.ps1 -OutFile "$env:TEMP\harrix-swiss-knife.ps1"
& "$env:TEMP\harrix-swiss-knife.ps1"
```

**From an already-cloned repo:**

```powershell
.\install\harrix-swiss-knife.ps1
```

**How to run the `.ps1` file:**

- From PowerShell in repo root (recommended if execution policy blocks scripts):

  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File .\install\harrix-swiss-knife.ps1
  ```

- From `cmd.exe`: same `-File` line, or `cd` into `install` and run the command with `harrix-swiss-knife.ps1`.

- **As Administrator:** run `install\install.bat` (double-click or from a terminal) if you need an elevated shell for your environment (for example restricted policies). That shows a UAC prompt and starts the same script elevated. The `.bat` does not forward parameters; for `-InstallRoot` and other switches, open an elevated PowerShell yourself and run `-File` as above.

Optional parameters: `-InstallRoot "D:\GitHub"`, `-SkipPrerequisites`, `-SkipBinaries`, `-Force` (re-download ffmpeg/avif binaries), `-NoPauseOnError` (exit immediately after failure; default is to wait for Enter so the console does not flash closed).

On a **very fresh** Windows image, **winget** may be missing until you install **Microsoft App Installer** from the Microsoft Store (or otherwise install WinGet). If the deploy window closes too quickly, run `install.bat` again: the elevated PowerShell window waits for Enter after an error, and the `.bat` ends with `pause` so you can read the launcher output.

The script installs Git and uv via **winget** when missing (plus VS Code if no editor is found), installs managed CPython with **`uv python install`** (pin from `.python-version`), clones **harrix-pylib**, **harrix-pyssg**, and **harrix-swiss-knife** as siblings, runs `uv sync` in each, downloads **ffmpeg** / **libavif** executables into the project root, runs `uv tool install -e`, creates a desktop shortcut, and adds the app to Windows autostart (Startup folder). Install the bundled **Harrix Notes Explorer (HSK)** VS Code extension from the tray app (**Dev** → **Install or update Harrix Notes Explorer (HSK) extension**) when you want it in a specific editor.

### Installation steps (manual)

Commands for PowerShell.

1. Install [uv](https://docs.astral.sh/uv/) ([Installing and Working with uv (Python) in VSCode](https://github.com/Harrix/harrix.dev-articles-2025-en/blob/main/uv-vscode-python/uv-vscode-python.md)):
   ```shell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
2. Restart PowerShell and clone projects:

   ```shell
   mkdir D:/GitHub
   cd D:/GitHub
   git clone https://github.com/Harrix/harrix-pylib.git
   git clone https://github.com/Harrix/harrix-pyssg.git
   git clone https://github.com/Harrix/harrix-swiss-knife.git
   ```

3. Open the folder `D:/GitHub/harrix-pylib` in Cursor (or VSCode) and open a terminal `Ctrl` + ```.

4. Install dependencies:

   ```shell
   uv sync
   ```

5. Open the folder `D:/GitHub/harrix-pyssg` in Cursor (or VSCode), open a terminal, and run:

   ```shell
   uv sync
   ```

6. Open the folder `D:/GitHub/harrix-swiss-knife` in Cursor (or VSCode) and open a terminal `Ctrl` + ```.

7. Install dependencies:

   ```shell
   uv sync
   ```

8. Download required executables:

   - `ffmpeg.exe`: Download from [FFmpeg Builds](https://github.com/BtbN/FFmpeg-Builds/releases) (e.g., `ffmpeg-master-latest-win64-gpl.zip`)
   - `libavif` executables (`avifdec.exe`, `avifenc.exe`): Download from [libavif releases](https://github.com/AOMediaCodec/libavif/releases) (e.g., `libavif-v1.3.0-windows-x64-dynamic.zip`)

   Licensing / attribution for downloaded binaries: see [`THIRD_PARTY_NOTICES.md`](https://github.com/Harrix/harrix-swiss-knife/blob/main/THIRD_PARTY_NOTICES.md).

   Copy all executables to the project folder `D:/GitHub/harrix-swiss-knife`. Alternatively, use the Dev menu action **Download Optimize dependencies (ffmpeg, avifenc, avifdec)** to fetch and extract them automatically.

9. Install the global `hsk` CLI so commands work from any folder (`uv tool` adds shims to `%USERPROFILE%\.local\bin`):

   ```shell
   uv tool install -e "D:/GitHub/harrix-swiss-knife"
   ```

   The offline installer (`install\harrix-swiss-knife.ps1`) runs this automatically. To reinstall later (for example after `pyproject.toml` changes), use **Dev** → **Install CLI (hsk on PATH)** or `hsk dev install-cli`.

10. Install VS Code extension Harrix Notes Explorer (HSK) (local copy of the `vscode\harrix-notes-explorer-hsk` folder). Prefer the tray app (**Dev** → **Install or update Harrix Notes Explorer (HSK) extension**) so **`extensions.json`** is updated; a plain **`Copy-Item`** alone may not register the extension in current VS Code builds. Restart VS Code or Cursor.

11. Run the application:

Open `src\harrix_swiss_knife\main.py` and run (or run `D:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe D:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py` in a terminal).

### Running from command line

After installation, you can run the script from terminal:

```shell
D:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe D:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py
```

## 💻 CLI commands

Folder arguments are optional (default: current directory) for commands that take a positional `FOLDER`.

- `hsk md beautify-md "D:/path/to/project"` — deletes generated `*.g.md` dumps first (keeps `*.include.g.md`)
- `hsk md beautify-md "D:/path/to/project" --no-prose-fixes` — skip MdChecker typography autofixes in MdFormatter
- `hsk md beautify-md "D:/path/to/project" --no-format-code-blocks` — skip formatting fenced code bodies (e.g. `latex`)
- `hsk md beautify-md "D:/path/to/project" --prose-wrap always --print-width 80` — Prettier prose wrap (`always`/`never`/`preserve`)
- `hsk md beautify-regenerate-g-md "D:/path/to/project"`
- `hsk md beautify-regenerate-g-md "D:/path/to/project" --no-prose-fixes` — skip MdChecker typography autofixes in MdFormatter
- `hsk md beautify-regenerate-g-md "D:/path/to/project" --no-format-code-blocks` — skip formatting fenced code bodies (e.g. `latex`)
- `hsk md beautify-regenerate-g-md "D:/path/to/project" --prose-wrap always --print-width 80` — Prettier prose wrap (`always`/`never`/`preserve`)
- `hsk md check "D:/path/to/project"` — all Harrix MD rules
- `hsk md check "D:/path/to/project" --include-g-md` — all Harrix MD rules and checking `.g.md`
- `hsk md check "D:/path/to/project" --rule H001` — check only selected rule ids (repeatable)
- `hsk md optimize-images-folder "D:/path/to/folder"` — optimize images referenced by Markdown under the folder
- `hsk md optimize-images-folder "D:/path/to/folder" --max-size 1920` — resize when width or height exceeds max px
- `hsk py check "D:/path/to/project"` — ty, ruff, pytest, Harrix PY/MD for one folder
- `hsk py check-all` — ty, ruff, pytest, Harrix PY/MD for all paths_python_projects
- `hsk py harrix-check "D:/path/to/project"` — Harrix PY rules + docstring Markdown (incl. Private; locations in `.py`)
- `hsk py ruff-sort-docs "D:/path/to/project"`
- `hsk py ruff-sort-docs "D:/path/to/project" --no-prose-fixes` — skip MdChecker typography autofixes in docstrings and generated Markdown
- `hsk py ruff-sort "D:/path/to/project"`
- `hsk file discard-git-changes "D:/path/to/parent"` — `git reset --hard` + `git clean -fd` in each Git repo under the folder (the folder itself or immediate children)
- `hsk file discard-git-changes "D:/path/to/parent" --status` — only list repositories with uncommitted changes (no discard)
- `hsk text fix-text-with-ai` (opens a dialog for multi-line input; copies result to clipboard)
- `hsk md new-note`
- `hsk md new-note --folder "D:/path/to/notes" --name "My note"`
- `hsk md new-note-with-images`
- `hsk md new-note-with-images --folder "D:/path/to/notes" --name "My note"`
- `hsk md new-diary-note`
- `hsk md new-diary-note --folder "D:/path/to/diary"`
- `hsk md new-dream-note`
- `hsk md new-dream-note --folder "D:/path/to/dream"`
- `hsk md new-cases-note`
- `hsk md new-cases-note --folder "D:/path/to/cases"`
- `hsk md list-templates`
- `hsk md add-from-template --template "Movie"`
- `hsk md add-from-template --template "Book"`
- `hsk md add-from-template --template "Travel"`
- `hsk md edit-from-template --template "Movie"` — edit existing Markdown via a markdown_templates entry
- `hsk android format [FOLDER]` — Spotless (ktlint) format (tray uses `paths_android_projects`)
- `hsk android check [FOLDER]` — Spotless check + Detekt + Android Lint (`qualityCheck`)
- `hsk android build [FOLDER] [debug|release]` — build APK using `android_build_variant` in `config.json` when variant omitted (default `release`; Windows; JDK 17 + Android SDK; tray also picks Release + install device/AVD)
- `hsk android build debug` — build debug APK in `.`
- `hsk android build release` — build release APK in `.` (debug-signed for sideload)
- `hsk android build --all` — build/install all `paths_android_projects` sequentially
- `hsk android build --all release` — same with explicit variant
- `hsk vscode format` — Biome format for `vscode/harrix-notes-explorer-hsk/`
- `hsk vscode check` — Biome lint + format check for the VS Code extension
- `hsk vscode sync-notes-explorer` — sync HSK extension into public `path_harrix_notes_explorer` repo
- `hsk site add-submodule "D:/path/to/content"` — add folder as Git submodule of `path_site_repo`
- `hsk site fix-article-links "D:/path/to/article"` — fix titles in site article dual links
- `hsk site pull-submodules` — pull `origin main` in each submodule of `path_site_repo`
- `hsk site pull-submodules "D:/path/to/site-repo"` — same for an explicit site repo folder
- `hsk dev action-usage` — show sorted action invocation statistics (unused first)
- `hsk dev install-cli` (global `hsk` on PATH via `uv tool install -e`)
- `hsk dev install-harrix-notes-explorer-hsk vscode` (Windows only; syncs public repo when `path_harrix_notes_explorer` is set; reload the editor window after install)
- `hsk dev install-harrix-notes-explorer-hsk insiders`
- `hsk dev install-harrix-notes-explorer-hsk insiders --with-public` (also install public `harrix-notes-explorer` into the editor profile)
- `hsk dev install-harrix-notes-explorer-hsk cursor`
- `hsk dev install-harrix-notes-explorer-hsk vscodium`
- `hsk dev install-harrix-notes-explorer-hsk windsurf`
- `hsk dev install-harrix-notes-explorer-hsk antigravity`

## ⚙️ Development

[`DEVELOPMENT.md`](https://github.com/Harrix/harrix-swiss-knife/blob/main/DEVELOPMENT.md)

## 🔗 Create a shortcut

To create a desktop shortcut, use the following path:

```shell
D:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe D:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py
```

## 📄 License

This project is licensed under the [MIT License](https://github.com/Harrix/harrix-swiss-knife/blob/main/LICENSE.md).

## 👤 Author

Author: [Anton Sergienko](https://github.com/Harrix).
