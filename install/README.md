# Install staging (`install/`)

Builder output only. Target machines never need this folder.

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [Distributables](#distributables)
- [Staging (gitignored)](#staging-gitignored)

</details>

## Distributables

After **Dev** → **Build installer EXEs** (`hsk dev build-install-zips`):

| File                             | Purpose                                        |
| -------------------------------- | ---------------------------------------------- |
| `harrix-swiss-knife-online.exe`  | Double-click installer; clones from GitHub     |
| `harrix-swiss-knife-offline.exe` | Same wizard; uses bundled `repos/` + uv caches |

Both are a frozen PySide6 stub with a zip payload appended after an `HSK1` trailer. The tray app itself still runs via `uv` + `pythonw` after install.

## Staging (gitignored)

- `dependencies/` — installers, media tools, repo snapshots, uv caches
- `.installer-stub/` — reusable PyInstaller one-file stub
- `.payload-*.zip` — temporary overlays while packing

Requires **PyInstaller** on the builder (`uv sync --group dev`).
