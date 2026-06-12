# Harrix Swiss Knife

![Featured image](https://raw.githubusercontent.com/Harrix/harrix-swiss-knife/refs/heads/main/img/featured-image.svg)

🤖 Python + Node.js application for automating personal tasks in Windows.

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [✨ Features](#-features)
- [📋 List of commands](#-list-of-commands)
- [🛠️ Deploy on an empty machine (Windows)](#%EF%B8%8F-deploy-on-an-empty-machine-windows)
  - [Prerequisites](#prerequisites)
  - [Quick install (PowerShell script)](#quick-install-powershell-script)
  - [Offline install (local bundle)](#offline-install-local-bundle)
  - [Installation steps (manual)](#installation-steps-manual)
  - [Running from command line](#running-from-command-line)
- [💻 CLI commands](#-cli-commands)
- [⚙️ Development](#%EF%B8%8F-development)
- [🔗 Create a shortcut](#-create-a-shortcut)
- [📄 License](#-license)
- [👤 Author](#-author)

</details>

This is a **personal** project tailored to **specific personal** tasks.

![GitHub](https://img.shields.io/badge/GitHub-harrix--swiss--knife-blue?logo=github) ![GitHub](https://img.shields.io/github/license/Harrix/harrix-swiss-knife)

GitHub: <https://github.com/Harrix/harrix-swiss-knife>

Documentation: [docs](https://github.com/Harrix/harrix-swiss-knife/blob/main/docs/index.g.md)

This project provides a Windows application with a system tray context menu, featuring mini-programs designed to automate specific personal tasks.

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
  - ⬇️ Download ffmpeg, avifenc, avifdec
  - ⚙️ Open config.json
  - ⬆️ Update Harrix Swiss Knife from GitHub
  - 📥 Update Node.js
  - 📥 Update uv
  - 📦 Update/Install Harrix Notes Explorer extensions for VSCode
  - 📦 Update/Install global NPM packages
  - 📋 View recent action logs
- **Images**
  - 📸 Open photos in image viewer
  - 🚀 ★ Optimize images
  - 🔝 Optimize images (high quality)
  - ⬆️ Optimize images in … and replace
  - 🖼️ Optimize one image
  - ↔️ ★ Resize and optimize images
  - 🧹 Clear folders images
  - 📂 Open the folder images
  - 📂 Open the folder optimized_images
- **File operations**
  - 🔒 Block disks
  - ✅ Check featured_image
  - ✅ Check featured_image in …
  - 🤖 ★ Combine files for AI
  - 📦 Extract ZIP archives in …
  - 🎯 Git commit message (emoji / rename)
  - 📄 List files current folder
  - 📄 List files simple
  - 📄 List files simple (ignore hidden folders)
  - 🗂️ Moves and flattens files from nested folders
  - 🗑️ Remove empty folders in …
  - 📚 Rename FB2, Epub, PDF files in …
  - 📝 Rename files by mapping in …
  - 🖲️ Rename largest images to featured_image in …
  - ├ Tree view of a folder
  - ├ Tree view of a folder (ignore hidden folders)
- **Markdown**
  - 📝 ★ New Markdown ꟲᴸᴵ
  - 🎬 Get a list of movies, books for web
  - 👈 Heading level: Decrease
  - 👉 Heading level: Increase
  - 🏷️ Append YAML tag in …
  - 💎 ★ Beautify MD and regenerate .g.md in … ꟲᴸᴵ
  - 💎 Beautify MD in …
  - 🚧 Check MD in … ꟲᴸᴵ
  - 📥 Download images in …
  - ❞ Fix MD with quotes
  - 📑 Generate a short version with only TOC
  - 🌐 Generate static site
  - 📋 Get set variables from YAML in …
  - 🖼️ Optimize images in MD in …
  - 🖼️ ★ Optimize selected images in MD
  - 📶 Sort sections in one MD
- **Python**
  - 🚧 Check PY in … ꟲᴸᴵ
  - 🐍 New uv library
  - 🐍 New uv project
  - ⚡ Publish Python library to PyPI
  - 🌟 ruff sort, ruff format, sort in PY files ꟲᴸᴵ
  - 🌟 ★ ruff sort, ruff format, sort, make docs in PY files ꟲᴸᴵ
- 💰 Finance tracker
- 🏃🏻 Fitness tracker
- 🍔 Food tracker
- ✅ Habit tracker
- 🚀 Optimize image from clipboard
- 🚀 Optimize image from clipboard as …
- × Exit

## 🛠️ Deploy on an empty machine (Windows)

### Prerequisites

Install the following software:

- Git
- Python
- Cursor or VSCode (with Python extensions)
- Node.js

### Quick install (PowerShell script)

### Offline install (local bundle)

If you need a more reliable install (slow/blocked internet, npm registry timeouts), you can prepare an offline bundle once on a machine with internet:

```powershell
.\install\download-bundle.ps1
```

This will populate `install\dependencies\` (ignored by git) with installers and binaries. Then copy the whole `install\` folder to the target machine and run:

```powershell
.\install\install.bat
```

Run in PowerShell. The script can detect the parent folder when you run it from an already-cloned `harrix-swiss-knife` repo (`install\harrix-swiss-knife.ps1`) or pick a default automatically.

**Standalone bootstrap** (no clone yet; downloads the script then runs it):

```powershell
irm https://raw.githubusercontent.com/Harrix/harrix-swiss-knife/main/install/harrix-swiss-knife.ps1 -OutFile "$env:TEMP\harrix-swiss-knife.ps1"
& "$env:TEMP\harrix-swiss-knife.ps1"
```

**From an already-cloned repo**:

```powershell
.\install\harrix-swiss-knife.ps1
```

**How to run the `.ps1` file**

- From PowerShell in repo root (recommended if execution policy blocks scripts):

  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File .\install\harrix-swiss-knife.ps1
  ```

- From **cmd.exe**: same `-File` line, or `cd` into `install` and run the command with `harrix-swiss-knife.ps1`.

- **As Administrator**: run `install\install.bat` (double-click or from a terminal) if you need an elevated shell for your environment (for example restricted policies). That shows a UAC prompt and starts the same script elevated. The `.bat` does not forward parameters; for `-InstallRoot` and other switches, open an elevated PowerShell yourself and run `-File` as above.

Optional parameters: `-InstallRoot "D:\GitHub"`, `-SkipPrerequisites`, `-SkipBinaries`, `-Force` (re-download ffmpeg/avif binaries), `-NoPauseOnError` (exit immediately after failure; default is to wait for Enter so the console does not flash closed).

On a **very fresh** Windows image, **winget** may be missing until you install **Microsoft App Installer** from the Microsoft Store (or otherwise install WinGet). If the deploy window closes too quickly, run `install.bat` again: the elevated PowerShell window waits for Enter after an error, and the `.bat` ends with `pause` so you can read the launcher output.

The script installs Git, Python, Node.js, and uv via **winget** when missing, clones **harrix-pylib**, **harrix-pyssg**, and **harrix-swiss-knife** as siblings, runs `uv sync` in each, runs `npm i` and global Prettier in `harrix-swiss-knife`, downloads **ffmpeg** / **libavif** executables into the project root, and runs `uv tool install -e`. Install the bundled **Harrix Notes Explorer (HSK)** VS Code extension from the tray app (**Dev** → **Install or update Harrix Notes Explorer (HSK) extension**) when you want it in a specific editor.

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

3. Open the folder `D:/GitHub/harrix-pylib` in Cursor (or VSCode) and open a terminal `Ctrl` + `` ` ``.

4. Install dependencies:

   ```shell
   uv sync
   ```

5. Open the folder `D:/GitHub/harrix-pyssg` in Cursor (or VSCode), open a terminal, and run:

   ```shell
   uv sync
   ```

6. Open the folder `D:/GitHub/harrix-swiss-knife` in Cursor (or VSCode) and open a terminal `Ctrl` + `` ` ``.

7. Install dependencies:

   ```shell
   uv sync
   npm i
   npm i -g prettier
   ```

8. Download required executables:
   - **ffmpeg.exe**: Download from [FFmpeg Builds](https://github.com/BtbN/FFmpeg-Builds/releases) (e.g., `ffmpeg-master-latest-win64-gpl.zip`)
   - **libavif executables** (`avifdec.exe`, `avifenc.exe`): Download from [libavif releases](https://github.com/AOMediaCodec/libavif/releases) (e.g., `libavif-v1.3.0-windows-x64-dynamic.zip`)

   Licensing / attribution for downloaded binaries: see [`THIRD_PARTY_NOTICES.md`](https://github.com/Harrix/harrix-swiss-knife/blob/main/THIRD_PARTY_NOTICES.md).

   Copy all executables to the project folder `D:/GitHub/harrix-swiss-knife`. Alternatively, use the Dev menu action **Download Optimize dependencies (ffmpeg, avifenc, avifdec)** to fetch and extract them automatically.

9. Install the CLI command so it can be called from any folder, use `uv tool`:

   ```shell
   uv tool install -e "D:/GitHub/harrix-swiss-knife"
   ```

10. Install VS Code extension Harrix Notes Explorer (HSK) (local copy of the `vscode\harrix-notes-explorer-hsk` folder). Prefer the tray app (**Dev** → **Install or update Harrix Notes Explorer (HSK) extension**) so **`extensions.json`** is updated; a plain **`Copy-Item`** alone may not register the extension in current VS Code builds. If the UI still hides it, use **Developer: Install Extension from Location** once, then **Developer: Reload Window**. Check **`argv.json`** for **`--extensions-dir`** if files are not where you expect.

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

Restart VS Code or Cursor, or run **Developer: Reload Window**. If you used **`Copy-Item`** only, confirm `%USERPROFILE%\.vscode-insiders\extensions\extensions.json` (or the matching path for stable VS Code / Cursor) contains **`local.harrix-notes-explorer-hsk`**.

Usage:

- Open your notes folder as a workspace in VS Code.
- In **Explorer**, open the **Harrix Notes (HSK)** view.

Commands:

- **Refresh Harrix Notes (HSK)**: `harrixNotesExplorerHsk.refresh`
- **Reveal in File Explorer**: `harrixNotesExplorerHsk.revealInOS`

11. Run the application:
    Open `src\harrix_swiss_knife\main.py` and run (or run `D:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe D:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py` in a terminal).

### Running from command line

After installation, you can run the script from terminal:

```shell
D:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe D:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py
```

## 💻 CLI commands

Folder arguments are optional (default: current directory) for commands that take a positional `FOLDER`.

- `harrix-swiss-knife-cli markdown beautify-regenerate-g-md "D:/path/to/project"`
- `harrix-swiss-knife-cli markdown check "D:/path/to/project"`
- `harrix-swiss-knife-cli python check "D:/path/to/project"`
- `harrix-swiss-knife-cli python check-all`
- `harrix-swiss-knife-cli python ruff-sort-docs "D:/path/to/project"`
- `harrix-swiss-knife-cli python ruff-sort "D:/path/to/project"`
- `harrix-swiss-knife-cli text fix-text-with-ai` (opens a dialog for multi-line input; copies result to clipboard)
- `harrix-swiss-knife-cli markdown new-note`
- `harrix-swiss-knife-cli markdown new-note --folder "D:/path/to/notes" --name "My note"`
- `harrix-swiss-knife-cli markdown new-note-with-images`
- `harrix-swiss-knife-cli markdown new-note-with-images --folder "D:/path/to/notes" --name "My note"`
- `harrix-swiss-knife-cli markdown new-diary-note`
- `harrix-swiss-knife-cli markdown new-diary-note --folder "D:/path/to/diary"`
- `harrix-swiss-knife-cli markdown new-dream-note`
- `harrix-swiss-knife-cli markdown new-dream-note --folder "D:/path/to/dream"`
- `harrix-swiss-knife-cli markdown new-cases-note`
- `harrix-swiss-knife-cli markdown new-cases-note --folder "D:/path/to/cases"`
- `harrix-swiss-knife-cli markdown list-templates`
- `harrix-swiss-knife-cli markdown add-from-template --template "Movie"`
- `harrix-swiss-knife-cli markdown add-from-template --template "Book"`
- `harrix-swiss-knife-cli markdown add-from-template --template "Travel"`
- `harrix-swiss-knife-cli dev install-harrix-notes-explorer-hsk vscode` (Windows only; syncs public repo when `path_harrix_notes_explorer` is set; reload the editor window after install)
- `harrix-swiss-knife-cli dev install-harrix-notes-explorer-hsk insiders`
- `harrix-swiss-knife-cli dev install-harrix-notes-explorer-hsk insiders --with-public` (also install public `harrix-notes-explorer` into the editor profile)
- `harrix-swiss-knife-cli dev install-harrix-notes-explorer-hsk cursor`
- `harrix-swiss-knife-cli dev install-harrix-notes-explorer-hsk vscodium`
- `harrix-swiss-knife-cli dev install-harrix-notes-explorer-hsk windsurf`
- `harrix-swiss-knife-cli dev install-harrix-notes-explorer-hsk antigravity`

## ⚙️ Development

[DEVELOPMENT.md](https://github.com/Harrix/harrix-swiss-knife/blob/main/DEVELOPMENT.md)

## 🔗 Create a shortcut

To create a desktop shortcut, use the following path:

```shell
D:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe D:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py
```

## 📄 License

This project is licensed under the [MIT License](https://github.com/Harrix/harrix-swiss-knife/blob/main/LICENSE.md).

## 👤 Author

Author: [Anton Sergienko](https://github.com/Harrix).
