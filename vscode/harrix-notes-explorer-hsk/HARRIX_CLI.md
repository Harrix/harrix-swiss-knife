---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# hsk boundary

This extension can be built **with** or **without** integration to `hsk`. All CLI-specific code lives behind a single boundary.

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [Files (CLI layer)](#files-cli-layer)
- [Not part of the CLI layer](#not-part-of-the-cli-layer)
- [Public build checklist](#public-build-checklist)
- [Core (not CLI) — New note](#core-not-cli--new-note)
- [CLI commands (registered in `harrix-cli.js`)](#cli-commands-registered-in-harrix-clijs)
- [Settings (CLI only)](#settings-cli-only)

</details>

## Files (CLI layer)

| File                                                                         | Role                                                                                    |
| ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| [`harrix-cli.js`](harrix-cli.js)                                             | CLI runners, command registration, template loading, Diary/Dreams/Cases tree helpers    |
| [`package.harrix-cli.contributes.json`](package.harrix-cli.contributes.json) | Manifest keys and command IDs to remove from `package.json` for a public build          |
| [`extension.js`](extension.js)                                               | Core tree/UI; imports `harrix-cli` only via `require('./harrix-cli')` and `harrixCli.*` |
| [`icons-browse-menu.js`](icons-browse-menu.js)                               | Icons Browse context menu; CLI items (`beautifyMd`, …) are stripped in the public build |

## Not part of the CLI layer

These stay in `extension.js` for a public build:

- Git discard commands (`discardGitChangesInFolder`, `discardGitChangesInNote`) — use `git` directly
- `addFolderInNote`, `addFileInNote`, `createFolder` — local filesystem only
- `openIconsBrowse` / Icons Browse webview panel — local filesystem only (`icons-browse.js`, `icons-browse-menu.js`)
- `iconStyle` (`harrix` / `material`) + bundled `media/icons/*.svg` (same as Harrix Notes Android)
- `openMergedNote`, merged `*.g.md` tree rules — file open only (beautify/regenerate is CLI)
- Note titles, preview copy, drag-and-drop, folder expansion, etc.

`NotesProvider._templateTargets` / `setTemplateTargets` remain in `extension.js` but are only filled from `harrix-cli.js`. After removing CLI, clear template usage in `getChildren` / `createFolderItem` or leave an empty map.

## Public build checklist

1. Delete [`harrix-cli.js`](harrix-cli.js).
2. In [`extension.js`](extension.js):
   - Remove `const harrixCli = require('./harrix-cli');`
   - Remove `harrixCli.activateHarrixCliIntegration({ ... });`
   - Replace `harrixCli.folderListedWithoutMarkdown(...)` with `false` or remove the extra folder filter branch.
   - Replace `harrixCli.isSpecialNotesFolderName(...)` with `false` where used.
   - In `createFolderItem`, set `contextValue` without `harrixCli.resolveNotesFolderContextValue` (use only `notesFolder` / `notesFolderWithMerged`).
   - Optionally remove `templateItems`, `getTemplatesForFolder`, `setTemplateTargets` from `NotesProvider`.
3. In [`package.json`](package.json): remove entries listed in [`package.harrix-cli.contributes.json`](package.harrix-cli.contributes.json) (settings, commands, menu items, `viewItem` values for Diary/Dreams/Cases/templates).
4. In [`icons-browse-menu.js`](icons-browse-menu.js): remove the same CLI command IDs and `out.push(item(CMD.…))` rows (Beautify / Regenerate / Check MD / Optimize images / Diary / Dreams / Cases / template). Keep Git discard.
5. Remove `_harrixCli` from `package.json` if present.
6. Delete this file and `package.harrix-cli.contributes.json` if you no longer need the checklist.
7. Reload VS Code / reinstall the extension.

## Core (not CLI) — New note

- `harrixNotesExplorerHsk.createNote` — implemented in `new-note.js` (`@hsk-sync:new-note`); keep in public builds.
- `harrixNotesExplorerHsk.createMarpNote` — same New note path with `type: marp` / `marp: true`.
- `harrixNotesExplorerHsk.createJupyterNote` — same New note path with `type: jupyter`, `files/*.ipynb`, and a Markdown link to the notebook.
- `harrixNotesExplorerHsk.presentMarp` — fullscreen slideshow webview for Marp notes.
- Jupyter preview — `jupyter-notebook.js` + Markdown preview (`@hsk-sync:jupyter-notebook`).

## CLI commands (registered in `harrix-cli.js`)

- `harrixNotesExplorerHsk.newDiaryNote`
- `harrixNotesExplorerHsk.newDreamNote`
- `harrixNotesExplorerHsk.newCasesNote`
- `harrixNotesExplorerHsk.addFromTemplate`
- `harrixNotesExplorerHsk.beautifyMd`
- `harrixNotesExplorerHsk.regenerateGMd`
- `harrixNotesExplorerHsk.beautifyRegenerateGMd`
- `harrixNotesExplorerHsk.checkMarkdownInFolder`
- `harrixNotesExplorerHsk.optimizeImagesFolder`
- `harrixNotesExplorerHsk.optimizeImagesFolderNoSizeLimit`
- `harrixNotesExplorerHsk.convertToSiteArticleLink` (local convert; does not run `hsk` in Terminal)

## Settings (CLI only)

- `harrixNotesExplorerHsk.cliExecutable`
- `harrixNotesExplorerHsk.optimizeImagesFolderMaxSize` (default `1024`)
- `harrixNotesExplorerHsk.siteLink.defaultLanguage` (default `ru`)
- `harrixNotesExplorerHsk.siteLink.siteName` (default `harrix.dev`)
- `harrixNotesExplorerHsk.siteLink.githubUser` (default `Harrix`)
