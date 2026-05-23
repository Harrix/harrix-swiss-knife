# harrix-swiss-knife-cli boundary

This extension can be built **with** or **without** integration to `harrix-swiss-knife-cli`. All CLI-specific code lives behind a single boundary.

## Files (CLI layer)

| File | Role |
|------|------|
| [`harrix-cli.js`](harrix-cli.js) | CLI runners, command registration, template loading, Diary/Dreams/Cases tree helpers |
| [`package.harrix-cli.contributes.json`](package.harrix-cli.contributes.json) | Manifest keys and command IDs to remove from `package.json` for a public build |
| [`extension.js`](extension.js) | Core tree/UI; imports `harrix-cli` only via `require('./harrix-cli')` and `harrixCli.*` |

## Not part of the CLI layer

These stay in `extension.js` for a public build:

- Git discard commands (`discardGitChangesInFolder`, `discardGitChangesInNote`) — use `git` directly
- `addFolderInNote`, `addFileInNote` — local filesystem only
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
4. Remove `_harrixCli` from `package.json` if present.
5. Delete this file and `package.harrix-cli.contributes.json` if you no longer need the checklist.
6. Reload VS Code / reinstall the extension.

## CLI commands (registered in `harrix-cli.js`)

- `harrixNotesExplorer.createNote`
- `harrixNotesExplorer.createNoteWithImages`
- `harrixNotesExplorer.newDiaryNote`
- `harrixNotesExplorer.newDreamNote`
- `harrixNotesExplorer.newCasesNote`
- `harrixNotesExplorer.addFromTemplate`
- `harrixNotesExplorer.beautifyRegenerateGMd`

## Settings (CLI only)

- `harrixNotesExplorer.cliExecutable`
- `harrixNotesExplorer.cliWorkingDirectory`
