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
  - 📥 Update Node.js
  - 📥 Update uv
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
  - 📝 ★ New Markdown
  - 🎬 Get a list of movies, books for web
  - 👈 Heading level: Decrease
  - 👉 Heading level: Increase
  - 🏷️ Append YAML tag in …
  - 💎 ★ Beautify MD and regenerate .g.md in …
  - 💎 Beautify MD in …
  - 🚧 Check MD in …
  - 📥 Download images in …
  - ❞ Fix MD with quotes
  - 📑 Generate a short version with only TOC
  - 🌐 Generate static site
  - 📋 Get set variables from YAML in …
  - 🖼️ Optimize images in MD in …
  - 🖼️ ★ Optimize selected images in MD
  - 📶 Sort sections in one MD
- **Python**
  - 🚧 Check PY in …
  - 🐍 New uv library
  - 🐍 New uv project
  - ⚡ Publish Python library to PyPI
  - 🌟 isort, ruff format, sort in PY files
  - 🌟 ★ isort, ruff format, sort, make docs in PY files
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

Run in PowerShell. The script can prompt for the install folder (default `D:\GitHub` in the dialog) or detect the parent folder when you run it from an already-cloned `harrix-swiss-knife` repo (`scripts\harrix-swiss-knife.ps1`).

**Standalone bootstrap** (no clone yet; downloads the script then runs it):

```powershell
irm https://raw.githubusercontent.com/Harrix/harrix-swiss-knife/main/scripts/harrix-swiss-knife.ps1 -OutFile "$env:TEMP\harrix-swiss-knife.ps1"
& "$env:TEMP\harrix-swiss-knife.ps1"
```

**From an already-cloned repo**:

```powershell
.\scripts\harrix-swiss-knife.ps1
```

**How to run the `.ps1` file**

- From PowerShell in repo root (recommended if execution policy blocks scripts):

  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\harrix-swiss-knife.ps1
  ```

- From **cmd.exe**: same `-File` line, or `cd` into `scripts` and run the command with `harrix-swiss-knife.ps1`.

- **As Administrator** (for Notes Explorer symlinks if you do not use Developer Mode): run `scripts\install.bat` (double-click or from a terminal). That shows a UAC prompt and starts the same script elevated. The `.bat` does not forward parameters; for `-InstallRoot` and other switches, open an elevated PowerShell yourself and run `-File` as above.

Optional parameters: `-InstallRoot "D:\GitHub"`, `-SkipPrerequisites`, `-SkipBinaries`, `-SkipExtensionSymlinks`, `-Force` (re-download ffmpeg/avif binaries), `-NoPauseOnError` (exit immediately after failure; default is to wait for Enter so the console does not flash closed).

On a **very fresh** Windows image, **winget** may be missing until you install **Microsoft App Installer** from the Microsoft Store (or otherwise install WinGet). If the deploy window closes too quickly, run `install.bat` again: the elevated PowerShell window waits for Enter after an error, and the `.bat` ends with `pause` so you can read the launcher output.

The script installs Git, Python, Node.js, and uv via **winget** when missing, clones **harrix-pylib**, **harrix-pyssg**, and **harrix-swiss-knife** as siblings, runs `uv sync` in each, runs `npm i` and global Prettier in `harrix-swiss-knife`, downloads **ffmpeg** / **libavif** executables into the project root, runs `uv tool install -e`, and creates **Notes Explorer** symlinks for VS Code / Insiders / Cursor when the corresponding `extensions` folder exists. Symlinks need Windows Developer Mode or an elevated PowerShell if creation fails.

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

   Copy all executables to the project folder `D:/GitHub/harrix-swiss-knife`. Alternatively, use the Dev menu action **Download Optimize dependencies (ffmpeg, avifenc, avifdec)** to fetch and extract them automatically.

9. Install the CLI command so it can be called from any folder, use `uv tool`:

   ```shell
   uv tool install -e "D:/GitHub/harrix-swiss-knife"
   ```

10. Install VS Code extension Notes Explorer (local, via symlink):

VS Code Insiders:

```powershell
New-Item -ItemType SymbolicLink `
  -Path "$env:USERPROFILE\.vscode-insiders\extensions\notes-explorer" `
  -Target (Resolve-Path ".\vscode\harrix-notes-explorer").Path
```

VS Code Stable:

```powershell
New-Item -ItemType SymbolicLink `
  -Path "$env:USERPROFILE\.vscode\extensions\notes-explorer" `
  -Target (Resolve-Path ".\vscode\harrix-notes-explorer").Path
```

Restart VS Code.

Usage:

- Open your notes folder as a workspace in VS Code.
- In **Explorer**, open the **Notes** view.

Commands:

- **Refresh Notes**: `notesExplorer.refresh`
- **Reveal in File Explorer**: `notesExplorer.revealInOS`

11. Run the application:
    Open `src\harrix_swiss_knife\main.py` and run (or run `D:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe D:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py` in a terminal).

### Running from command line

After installation, you can run the script from terminal:

```shell
D:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe D:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py
```

## 💻 CLI commands

- `harrix-swiss-knife-cli markdown beautify-regenerate-g-md "D:/path/to/project"`
- `harrix-swiss-knife-cli python isort-ruff-sort-docs "D:/path/to/project"`
- `harrix-swiss-knife-cli python isort-ruff-sort "D:/path/to/project"`

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
