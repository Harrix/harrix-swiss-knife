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

const HARIX_TERMINAL_NAME = 'Harrix Notes (HSK)';

/** @param {string} value */
function quoteForTerminal(value) {
  const text = String(value);
  if (!/[\s"]/.test(text)) {
    return text;
  }
  return `"${text.replace(/"/g, '\\"')}"`;
}

function getOrCreateHarrixTerminal() {
  const existing = vscode.window.terminals.find((t) => t.name === HARIX_TERMINAL_NAME);
  if (existing) {
    return existing;
  }
  return vscode.window.createTerminal(HARIX_TERMINAL_NAME);
}

/** @param {string[]} cliArgs */
function buildHarrixCliCommand(cliArgs) {
  const parts = [quoteForTerminal(getCliExecutable()), ...cliArgs.map(quoteForTerminal)];
  return parts.join(' ');
}

/** @param {string[]} cliArgs */
function runHarrixCliInTerminal(cliArgs) {
  const terminal = getOrCreateHarrixTerminal();
  terminal.show(true);
  terminal.sendText(buildHarrixCliCommand(cliArgs));
}

/**
 * @param {string} baseDir
 * @param {string} rawName
 */
function runHarrixMarkdownNewNote(baseDir, rawName) {
  const stem = rawName.trim();
  if (!stem) {
    throw new Error('Empty note name');
  }
  const nameArg = stem.toLowerCase().endsWith('.md') ? stem.slice(0, -3) : stem;
  runHarrixCliInTerminal(['markdown', 'new-note', '--folder', path.resolve(baseDir), '--name', nameArg]);
}

/** @param {string} diaryRootPath */
function runHarrixMarkdownNewDiaryNote(diaryRootPath) {
  runHarrixCliInTerminal(['markdown', 'new-diary-note', '--folder', path.resolve(diaryRootPath)]);
}

/** @param {string} dreamRootPath */
function runHarrixMarkdownNewDreamNote(dreamRootPath) {
  runHarrixCliInTerminal(['markdown', 'new-dream-note', '--folder', path.resolve(dreamRootPath)]);
}

/** @param {string} casesRootPath */
function runHarrixMarkdownNewCasesNote(casesRootPath) {
  runHarrixCliInTerminal(['markdown', 'new-cases-note', '--folder', path.resolve(casesRootPath)]);
}

/** @param {string} templateId */
function runHarrixMarkdownAddFromTemplate(templateId) {
  runHarrixCliInTerminal(['markdown', 'add-from-template', '--template', String(templateId)]);
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
function runHarrixBeautifyRegenerateGMd(folderPath) {
  runHarrixCliInTerminal(['markdown', 'beautify-regenerate-g-md', path.resolve(folderPath)]);
}

/** @param {string} folderPath */
function runHarrixMarkdownCheck(folderPath) {
  runHarrixCliInTerminal(['markdown', 'check', path.resolve(folderPath)]);
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
  const {
    context,
    provider,
    rootPath,
    uriToFsPath,
    isDirectoryPath,
    normalizeFsPath
  } = deps;

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
        runHarrixMarkdownNewDiaryNote(fsPath);
        vscode.window.showInformationMessage('New Diary Note running in Terminal.');
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`New Diary Note failed: ${msg}`);
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
        runHarrixMarkdownNewDreamNote(fsPath);
        vscode.window.showInformationMessage('New Dream Note running in Terminal.');
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`New Dream Note failed: ${msg}`);
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
        runHarrixMarkdownNewCasesNote(fsPath);
        vscode.window.showInformationMessage('New Cases Note running in Terminal.');
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`New Cases Note failed: ${msg}`);
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
            title: 'Add from Template',
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
        runHarrixMarkdownAddFromTemplate(templateId);
        vscode.window.showInformationMessage('Add from Template running in Terminal.');
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Add from Template failed: ${msg}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.checkMarkdownInFolder', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isDirectoryPath(fsPath)) {
        vscode.window.showErrorMessage('Select a folder in Harrix Notes (HSK).');
        return;
      }
      try {
        runHarrixMarkdownCheck(fsPath);
        vscode.window.showInformationMessage('Markdown check running in Terminal.');
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Markdown check failed: ${msg}`);
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
        runHarrixBeautifyRegenerateGMd(fsPath);
        vscode.window.showInformationMessage('Beautify Markdown running in Terminal.');
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Beautify Markdown and Regenerate .g.md in Folder failed: ${msg}`);
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
        runHarrixMarkdownNewNote(baseDir, safeName);
        vscode.window.showInformationMessage('New Note running in Terminal.');
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`New Note failed: ${msg}`);
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
