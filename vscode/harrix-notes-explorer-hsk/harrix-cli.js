/**
 * harrix-swiss-knife-cli integration for Harrix Notes Explorer (HSK).
 *
 * Public / standalone build: delete this file, remove `require('./harrix-cli')` from
 * extension.js, and strip entries listed in package.harrix-cli.contributes.json
 * and HARRIX_CLI.md from package.json.
 */

const vscode = require('vscode');
const path = require('path');
const { execFile } = require('child_process');
const util = require('util');

const execFileAsync = util.promisify(execFile);

// --- CLI process helpers ---

function getCliExecOptions() {
  return {
    windowsHide: true,
    maxBuffer: 10 * 1024 * 1024
  };
}

function getCliExecutable() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  return config.get('cliExecutable', 'harrix-swiss-knife-cli');
}

/**
 * @param {string} executable
 * @param {string[]} args
 */
async function runCli(executable, args) {
  try {
    await execFileAsync(executable, args, getCliExecOptions());
  } catch (err) {
    const stderr = err.stderr ? err.stderr.toString() : '';
    const stdout = err.stdout ? err.stdout.toString() : '';
    const msg = (stderr || stdout || err.message || '').trim();
    throw new Error(msg || `CLI exited with code ${err.code}`);
  }
}

/**
 * @param {string} baseDir
 * @param {string} rawName
 * @param {boolean} withImages
 */
async function runHarrixMarkdownNewNote(baseDir, rawName, withImages) {
  const stem = rawName.trim();
  if (!stem) {
    throw new Error('Empty note name');
  }
  const nameArg = stem.toLowerCase().endsWith('.md') ? stem.slice(0, -3) : stem;
  const subcommand = withImages ? 'new-note-with-images' : 'new-note';
  const folderArg = path.resolve(baseDir);
  const args = ['markdown', subcommand, '--folder', folderArg, '--name', nameArg];
  await runCli(getCliExecutable(), args);
}

/** @param {string} diaryRootPath */
async function runHarrixMarkdownNewDiaryNote(diaryRootPath) {
  const args = ['markdown', 'new-diary-note', '--folder', path.resolve(diaryRootPath)];
  await runCli(getCliExecutable(), args);
}

/** @param {string} dreamRootPath */
async function runHarrixMarkdownNewDreamNote(dreamRootPath) {
  const args = ['markdown', 'new-dream-note', '--folder', path.resolve(dreamRootPath)];
  await runCli(getCliExecutable(), args);
}

/** @param {string} casesRootPath */
async function runHarrixMarkdownNewCasesNote(casesRootPath) {
  const args = ['markdown', 'new-cases-note', '--folder', path.resolve(casesRootPath)];
  await runCli(getCliExecutable(), args);
}

/** @param {string} templateId */
async function runHarrixMarkdownAddFromTemplate(templateId) {
  const args = ['markdown', 'add-from-template', '--template', String(templateId)];
  await runCli(getCliExecutable(), args);
}

/**
 * @returns {Promise<Array<{id: string, title: string, path_target?: string}>>}
 */
async function runHarrixMarkdownListTemplates() {
  const args = ['markdown', 'list-templates'];
  try {
    const { stdout } = await execFileAsync(getCliExecutable(), args, getCliExecOptions());
    const text = (stdout || '').toString().trim();
    if (!text) {
      return [];
    }
    const parsed = JSON.parse(text);
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed
      .filter((x) => x && typeof x === 'object')
      .map((x) => ({
        id: String(x.id || ''),
        title: String(x.title || ''),
        path_target: x.path_target ? String(x.path_target) : undefined
      }))
      .filter((x) => x.id && x.title);
  } catch {
    return [];
  }
}

/** @param {string} folderPath */
async function runHarrixBeautifyRegenerateGMd(folderPath) {
  const args = ['markdown', 'beautify-regenerate-g-md', path.resolve(folderPath)];
  await runCli(getCliExecutable(), args);
}

// --- Tree integration (Diary / Dreams / Cases / template targets) ---

/** Folder named `Diary` (case-insensitive) — shown in tree even without .md; diary CLI menu */
function isDiaryFolderName(name) {
  return String(name).toLowerCase() === 'diary';
}

/** Folder named `Dreams` (case-insensitive) */
function isDreamsFolderName(name) {
  return String(name).toLowerCase() === 'dreams';
}

/** Folder named `Cases` (case-insensitive) */
function isCasesFolderName(name) {
  return String(name).toLowerCase() === 'cases';
}

function isSpecialNotesFolderName(name) {
  return isDiaryFolderName(name) || isDreamsFolderName(name) || isCasesFolderName(name);
}

/**
 * Show a folder in the tree when it has no .md yet (CLI-only folders / template targets).
 * @param {string} folderName
 * @param {number} templateTargetCount
 */
function folderListedWithoutMarkdown(folderName, templateTargetCount) {
  return isSpecialNotesFolderName(folderName) || templateTargetCount > 0;
}

/**
 * `viewItem` context value for a notes folder (before optional `git` prefix).
 * @param {{ name: string, hasMerged: boolean, templateItems: Array<{id: string, title: string}> }} opts
 */
function resolveNotesFolderContextValue(opts) {
  const { name, hasMerged, templateItems } = opts;
  const templates = templateItems || [];
  if (isDiaryFolderName(name)) {
    return hasMerged ? 'notesFolderWithMergedDiary' : 'notesFolderDiary';
  }
  if (isDreamsFolderName(name)) {
    return hasMerged ? 'notesFolderWithMergedDreams' : 'notesFolderDreams';
  }
  if (isCasesFolderName(name)) {
    return hasMerged ? 'notesFolderWithMergedCases' : 'notesFolderCases';
  }
  if (templates.length > 0) {
    return hasMerged ? 'notesFolderTemplateTargetWithMerged' : 'notesFolderTemplateTarget';
  }
  return hasMerged ? 'notesFolderWithMerged' : 'notesFolder';
}

/**
 * @typedef {object} HarrixCliDeps
 * @property {import('vscode').ExtensionContext} context
 * @property {{ refresh: () => void, getTemplatesForFolder: (folderPath: string) => Array<{id: string, title: string}>, setTemplateTargets: (map: Map<string, Array<{id: string, title: string}>>) => void }} provider
 * @property {string} rootPath
 * @property {(provider: unknown, folderPath: string, fn: () => Promise<void>) => Promise<void>} withFolderBusy
 * @property {(uri: unknown) => string | undefined} uriToFsPath
 * @property {(fsPath: string) => boolean} isDirectoryPath
 * @property {(fsPath: string) => boolean} isFilePath
 * @property {(fsPath: string) => boolean} normalizeFsPath
 */

/**
 * Registers CLI commands and loads template folder targets into the tree provider.
 * @param {HarrixCliDeps} deps
 */
function activateHarrixCliIntegration(deps) {
  const { context, provider, rootPath, withFolderBusy, uriToFsPath, isDirectoryPath, normalizeFsPath } =
    deps;

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.newDiaryNote', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isDirectoryPath(fsPath)) {
        vscode.window.showErrorMessage('Select the Diary folder in Harrix Notes (HSK).');
        return;
      }
      const folderName = path.basename(fsPath);
      if (!isDiaryFolderName(folderName)) {
        vscode.window.showErrorMessage('This command is only for a folder named Diary.');
        return;
      }
      try {
        await withFolderBusy(provider, fsPath, () => runHarrixMarkdownNewDiaryNote(fsPath));
        provider.refresh();
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`New diary note failed: ${msg}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.newDreamNote', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isDirectoryPath(fsPath)) {
        vscode.window.showErrorMessage('Select the Dreams folder in Harrix Notes (HSK).');
        return;
      }
      const folderName = path.basename(fsPath);
      if (!isDreamsFolderName(folderName)) {
        vscode.window.showErrorMessage('This command is only for a folder named Dreams.');
        return;
      }
      try {
        await withFolderBusy(provider, fsPath, () => runHarrixMarkdownNewDreamNote(fsPath));
        provider.refresh();
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`New dream note failed: ${msg}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.newCasesNote', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isDirectoryPath(fsPath)) {
        vscode.window.showErrorMessage('Select the Cases folder in Harrix Notes (HSK).');
        return;
      }
      const folderName = path.basename(fsPath);
      if (!isCasesFolderName(folderName)) {
        vscode.window.showErrorMessage('This command is only for a folder named Cases.');
        return;
      }
      try {
        await withFolderBusy(provider, fsPath, () => runHarrixMarkdownNewCasesNote(fsPath));
        provider.refresh();
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`New cases note failed: ${msg}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.addFromTemplate', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isDirectoryPath(fsPath)) {
        vscode.window.showErrorMessage('Select a target folder in Harrix Notes (HSK).');
        return;
      }

      const templateItems = Array.isArray(treeItemOrUri?.templateItems)
        ? treeItemOrUri.templateItems
        : provider.getTemplatesForFolder(fsPath);

      if (!templateItems || templateItems.length === 0) {
        vscode.window.showErrorMessage('No templates configured for this folder.');
        return;
      }

      let templateId = '';
      if (templateItems.length === 1) {
        const only = templateItems[0];
        templateId = only && typeof only.id === 'string' && only.id.trim() ? only.id.trim() : '';
      } else {
        const chosenItem = await vscode.window.showQuickPick(
          templateItems.map((t) => ({ label: t.title, description: t.id })),
          {
            title: 'Add from template',
            placeHolder: 'Choose a template'
          }
        );
        templateId =
          chosenItem && typeof chosenItem.description === 'string' && chosenItem.description.trim()
            ? chosenItem.description.trim()
            : '';
      }

      if (!templateId) {
        return;
      }

      try {
        await withFolderBusy(provider, fsPath, () => runHarrixMarkdownAddFromTemplate(templateId));
        provider.refresh();
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Add from template failed: ${msg}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.beautifyRegenerateGMd', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isDirectoryPath(fsPath)) {
        vscode.window.showErrorMessage('Select a folder in Harrix Notes (HSK).');
        return;
      }
      try {
        await withFolderBusy(provider, fsPath, () => runHarrixBeautifyRegenerateGMd(fsPath));
        provider.refresh();
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Beautify Markdown / regenerate .g.md failed: ${msg}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.createNote', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);

      const baseDir =
        fsPath && isDirectoryPath(fsPath)
          ? fsPath
          : fsPath && deps.isFilePath(fsPath)
            ? path.dirname(fsPath)
            : rootPath;

      const name = await vscode.window.showInputBox({
        title: 'New Note',
        prompt: 'Enter note name (without extension)',
        placeHolder: 'My-note'
      });
      if (!name) {
        return;
      }

      const safeName = name.trim();
      if (!safeName) {
        return;
      }

      try {
        await withFolderBusy(provider, baseDir, () =>
          runHarrixMarkdownNewNote(baseDir, safeName, false)
        );
        provider.refresh();
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`New note failed: ${msg}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.createNoteWithImages', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);

      const baseDir = fsPath && isDirectoryPath(fsPath) ? fsPath : rootPath;

      if (!baseDir || !isDirectoryPath(baseDir)) {
        vscode.window.showErrorMessage('Choose a folder in Harrix Notes (HSK).');
        return;
      }

      const name = await vscode.window.showInputBox({
        title: 'New Note with Images',
        prompt: 'Enter note name (without extension)',
        placeHolder: 'My-note'
      });
      if (!name) {
        return;
      }

      const safeName = name.trim();
      if (!safeName) {
        return;
      }

      try {
        await withFolderBusy(provider, baseDir, () =>
          runHarrixMarkdownNewNote(baseDir, safeName, true)
        );
        provider.refresh();
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`New note with images failed: ${msg}`);
      }
    })
  );

  void loadTemplateTargetsIntoProvider(provider, normalizeFsPath);
}

/**
 * @param {HarrixCliDeps['provider']} provider
 * @param {(fsPath: string) => boolean} normalizeFsPath
 */
async function loadTemplateTargetsIntoProvider(provider, normalizeFsPath) {
  const templates = await runHarrixMarkdownListTemplates();
  const map = new Map();
  for (const t of templates) {
    if (!t.path_target) {
      continue;
    }
    const key = normalizeFsPath(t.path_target);
    const arr = map.get(key) || [];
    arr.push({ id: t.id, title: t.title });
    map.set(key, arr);
  }
  provider.setTemplateTargets(map);
}

module.exports = {
  activateHarrixCliIntegration,
  folderListedWithoutMarkdown,
  isSpecialNotesFolderName,
  resolveNotesFolderContextValue
};
