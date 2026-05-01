# Notes Explorer (VS Code extension)

Custom panel in **Explorer** for browsing markdown notes with a few rules tailored for a “notes folder” workflow.

## Features

- **Tree view in Explorer**: adds **Notes** view (`notesExplorer`).
- **Show only meaningful folders**: folders that (recursively) contain at least one `*.md` are shown; folders without markdown inside (e.g. `img/`) are hidden.
- **Folder-to-file collapsing**: if a folder contains **exactly one** markdown file with the **same name** and has **no subfolders that contain markdown**, it is displayed as a single note item.
  - Example: `Python/Python.md` is shown as `Python` (no extra nesting).
- **Display without `.md` extension**.
- **Special styling for `*.g.md`**: treated as “combined/generated” notes and decorated with a custom color (`notesExplorer.gFile`).
- **Auto refresh** on markdown changes (`**/*.md`) + manual refresh command.

## How it works (rules)

### What is shown

- A **folder** is shown only if it contains at least one `*.md` file anywhere inside (recursive).
- A **note file** is any file that ends with `.md` (including `.g.md`).

### When a folder is collapsed into one note

A folder `X/` is displayed as a single note item `X` when:

- `X/X.md` exists, and
- inside `X/` there is **exactly one** `*.md` file (that is `X.md`), and
- inside `X/` there are **no subfolders** that contain markdown (recursive).

## Installation (local, via symlink)

You can install this extension locally by creating a symlink from your VS Code extensions folder to this directory.

### VS Code Insiders

Run in PowerShell from the repo root:

```powershell
New-Item -ItemType SymbolicLink `
  -Path "$env:USERPROFILE\.vscode-insiders\extensions\notes-explorer" `
  -Target (Resolve-Path ".\vscode\harrix-notes-explorer").Path
```

Restart VS Code Insiders.

### VS Code Stable

```powershell
New-Item -ItemType SymbolicLink `
  -Path "$env:USERPROFILE\.vscode\extensions\notes-explorer" `
  -Target (Resolve-Path ".\vscode\harrix-notes-explorer").Path
```

Restart VS Code.

## Usage

- Open your notes folder as a workspace in VS Code.
- In **Explorer**, open the **Notes** view.
- Click an item to open the corresponding markdown file.

### Commands

- **Refresh Notes**: `notesExplorer.refresh`
- **Reveal in File Explorer**: `notesExplorer.revealInOS`
  - If called without an argument, reveals the currently opened file.

## Customization

### Color for `*.g.md`

The extension contributes the color id `notesExplorer.gFile`.

Example user settings:

```json
{
  "workbench.colorCustomizations": {
    "notesExplorer.gFile": "#C586C0"
  }
}
```

## Development

- Entry point: `extension.js`
- Manifest: `package.json`

