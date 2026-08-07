/**
 * hsk integration for Harrix Notes Explorer (HSK).
 *
 * Public / standalone build: delete this file, remove `require('./harrix-cli')` from
 * extension.js, and strip entries listed in package.harrix-cli.contributes.json
 * and HARRIX_CLI.md from package.json.
 */

const vscode = require('vscode');
const path = require('node:path');
const { execFile } = require('node:child_process');
const util = require('node:util');

const execFileAsync = util.promisify(execFile);

// --- CLI process helpers ---

function getCliExecOptions() {
  return {
    windowsHide: true,
    maxBuffer: 10 * 1024 * 1024,
  };
}

function getCliExecutable() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  return config.get('cliExecutable', 'hsk');
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

/** @param {string} diaryRootPath */
function runHarrixMarkdownNewDiaryNote(diaryRootPath) {
  runHarrixCliInTerminal(['md', 'new-diary-note', '--folder', path.resolve(diaryRootPath)]);
}

/** @param {string} dreamRootPath */
function runHarrixMarkdownNewDreamNote(dreamRootPath) {
  runHarrixCliInTerminal(['md', 'new-dream-note', '--folder', path.resolve(dreamRootPath)]);
}

/** @param {string} casesRootPath */
function runHarrixMarkdownNewCasesNote(casesRootPath) {
  runHarrixCliInTerminal(['md', 'new-cases-note', '--folder', path.resolve(casesRootPath)]);
}

/** @param {string} templateId */
function runHarrixMarkdownAddFromTemplate(templateId) {
  runHarrixCliInTerminal(['md', 'add-from-template', '--template', String(templateId)]);
}

/**
 * @returns {Promise<Array<{id: string, title: string, path_target?: string}>>}
 */
async function runHarrixMarkdownListTemplates() {
  const args = ['md', 'list-templates'];
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
        path_target: x.path_target ? String(x.path_target) : undefined,
      }))
      .filter((x) => x.id && x.title);
  } catch {
    return [];
  }
}

/** @param {string} folderPath */
function runHarrixBeautifyRegenerateGMd(folderPath) {
  runHarrixCliInTerminal(['md', 'beautify-regenerate-g-md', path.resolve(folderPath)]);
}

/** @param {string} folderPath */
function runHarrixMarkdownCheck(folderPath) {
  runHarrixCliInTerminal(['md', 'check', path.resolve(folderPath)]);
}

/**
 * @param {string} folderPath
 * @param {number} maxSize
 */
function runHarrixOptimizeImagesFolder(folderPath, maxSize) {
  runHarrixCliInTerminal(['md', 'optimize-images-folder', path.resolve(folderPath), '--max-size', String(maxSize)]);
}

/** @returns {number} */
function getOptimizeImagesFolderMaxSize() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  const raw = config.get('optimizeImagesFolderMaxSize', 1024);
  const value = Number(raw);
  if (!Number.isFinite(value) || value < 1) {
    return 1024;
  }
  return Math.floor(value);
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
 * @property {(uri: unknown) => string | undefined} uriToFsPath
 * @property {(fsPath: string) => boolean} isDirectoryPath
 * @property {(fsPath: string) => boolean} isFilePath
 * @property {(fsPath: string) => boolean} normalizeFsPath
 * @property {(uri: unknown) => string | undefined} resolveNotesFolderFsPath
 */

/**
 * Folder for folder-level CLI: tree selection (folder / Note/Note.md), else parent of
 * selected or active markdown (so F1 works without a tree click).
 * @param {unknown} treeItemOrUri
 * @param {HarrixCliDeps} deps
 * @returns {string | undefined}
 */
function resolveFolderPathForCliCommand(treeItemOrUri, deps) {
  const { uriToFsPath, isFilePath, resolveNotesFolderFsPath } = deps;
  const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
  const fromTree = resolveNotesFolderFsPath(itemUri);
  if (fromTree) {
    return fromTree;
  }

  const selectedPath = uriToFsPath(itemUri);
  if (selectedPath && isFilePath(selectedPath) && selectedPath.toLowerCase().endsWith('.md')) {
    return path.dirname(selectedPath);
  }

  const activeUri = vscode.window.activeTextEditor?.document?.uri;
  if (activeUri?.scheme === 'file' && isFilePath(activeUri.fsPath) && activeUri.fsPath.toLowerCase().endsWith('.md')) {
    const fromActiveNamed = resolveNotesFolderFsPath(activeUri);
    if (fromActiveNamed) {
      return fromActiveNamed;
    }
    return path.dirname(activeUri.fsPath);
  }

  return undefined;
}

/**
 * Registers CLI commands and loads template folder targets into the tree provider.
 * @param {HarrixCliDeps} deps
 */
/** @typedef {{ defaultLanguage: string, siteName: string, githubUser: string }} SiteLinkSettings */

/** @returns {SiteLinkSettings} */
function getSiteLinkSettings() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  const defaultLanguage = String(config.get('siteLink.defaultLanguage', 'ru') || 'ru').trim() || 'ru';
  const siteName = String(config.get('siteLink.siteName', 'harrix.dev') || 'harrix.dev').trim() || 'harrix.dev';
  const githubUser = String(config.get('siteLink.githubUser', 'Harrix') || 'Harrix').trim() || 'Harrix';
  return { defaultLanguage, siteName, githubUser };
}

/**
 * @param {{ section: string, year: string | null, lang: string }} parts
 * @param {SiteLinkSettings} settings
 */
function buildContentRepoName(parts, settings) {
  let name = `${settings.siteName}-${parts.section}`;
  if (parts.year) {
    name += `-${parts.year}`;
  }
  if (parts.lang && parts.lang !== settings.defaultLanguage) {
    name += `-${parts.lang}`;
  }
  return name;
}

/**
 * @param {string} repoName
 * @param {SiteLinkSettings} settings
 * @returns {{ section: string, year: string | null, lang: string } | null}
 */
function parseContentRepoName(repoName, settings) {
  const prefix = `${settings.siteName}-`;
  if (!repoName.startsWith(prefix)) {
    return null;
  }
  const tokens = repoName.slice(prefix.length).split('-').filter(Boolean);
  if (tokens.length === 0) {
    return null;
  }
  let lang = settings.defaultLanguage;
  let year = null;
  if (tokens.length >= 2 && /^(en|ru)$/i.test(tokens[tokens.length - 1])) {
    lang = tokens.pop().toLowerCase();
  }
  if (tokens.length >= 2 && /^\d{4}$/.test(tokens[tokens.length - 1])) {
    year = tokens.pop();
  }
  const section = tokens.join('-');
  if (!section) {
    return null;
  }
  return { section, year, lang };
}

/**
 * @param {{ section: string, year: string | null, lang: string }} parts
 * @param {string} slug
 * @param {SiteLinkSettings} settings
 */
function buildSiteArticleUrl(parts, slug, settings) {
  const segments = [parts.lang || settings.defaultLanguage, parts.section];
  if (parts.year) {
    segments.push(parts.year);
  }
  segments.push(slug);
  return `https://${settings.siteName}/${segments.join('/')}/`;
}

/**
 * @param {string} repoName
 * @param {string} slug
 * @param {SiteLinkSettings} settings
 */
function buildGitHubBlobUrl(repoName, slug, settings) {
  return `https://github.com/${settings.githubUser}/${repoName}/blob/main/${slug}/${slug}.md`;
}

/**
 * @param {string} linkText
 * @param {string} githubUrl
 * @param {string} siteUrl
 */
function formatSiteArticleDualLink(linkText, githubUrl, siteUrl) {
  return `[${linkText}](${githubUrl}) | [↗️](${siteUrl})`;
}

/**
 * @param {string} raw
 * @returns {{ linkText: string, target: string } | null}
 */
function unwrapMarkdownLink(raw) {
  const text = String(raw ?? '').trim();
  const match = /^\[([^\]]*)\]\(([^)\s]+)\)$/.exec(text);
  if (!match) {
    return null;
  }
  return { linkText: match[1], target: match[2].trim() };
}

/**
 * @param {string} url
 * @param {SiteLinkSettings} settings
 * @returns {{ section: string, year: string | null, lang: string, slug: string } | null}
 */
function parseGitHubBlobUrl(url, settings) {
  const match = /^https?:\/\/github\.com\/[^/]+\/([^/]+)\/blob\/[^/]+\/([^/]+)\/\2\.md\/?(?:[?#].*)?$/i.exec(
    String(url ?? '').trim(),
  );
  if (!match) {
    return null;
  }
  const parsed = parseContentRepoName(match[1], settings);
  if (!parsed) {
    return null;
  }
  return { ...parsed, slug: match[2] };
}

/**
 * @param {string} raw
 * @param {SiteLinkSettings} settings
 * @returns {{ section: string, year: string | null, lang: string, slug: string } | null}
 */
function parseSiteUrlOrPath(raw, settings) {
  let pathText = String(raw ?? '').trim();
  if (!pathText) {
    return null;
  }
  const sitePrefix = `https://${settings.siteName}/`;
  const sitePrefixHttp = `http://${settings.siteName}/`;
  if (pathText.toLowerCase().startsWith(sitePrefix.toLowerCase())) {
    pathText = pathText.slice(sitePrefix.length);
  } else if (pathText.toLowerCase().startsWith(sitePrefixHttp.toLowerCase())) {
    pathText = pathText.slice(sitePrefixHttp.length);
  }
  pathText = pathText.replace(/^[?#].*$/, '');
  pathText = pathText.split(/[?#]/, 1)[0];
  pathText = pathText.replace(/^\/+/, '').replace(/\/+$/, '');
  const parts = pathText.split('/').filter(Boolean);
  if (parts.length < 2) {
    return null;
  }
  let lang = settings.defaultLanguage;
  if (/^(en|ru)$/i.test(parts[0])) {
    lang = parts.shift().toLowerCase();
  }
  if (parts.length < 2) {
    return null;
  }
  const slug = parts.pop();
  let year = null;
  if (parts.length >= 2 && /^\d{4}$/.test(parts[parts.length - 1])) {
    year = parts.pop();
  }
  const section = parts.join('-');
  if (!section || !slug) {
    return null;
  }
  return { section, year, lang, slug };
}

/**
 * @param {string} input
 * @param {SiteLinkSettings} settings
 * @returns {string | null}
 */
function convertInputToSiteArticleDualLink(input, settings) {
  const trimmed = String(input ?? '').trim();
  if (!trimmed) {
    return null;
  }

  let linkText = '';
  let target = trimmed;
  const wrapped = unwrapMarkdownLink(trimmed);
  if (wrapped) {
    linkText = wrapped.linkText;
    target = wrapped.target;
  }

  let parsed = parseGitHubBlobUrl(target, settings);
  if (!parsed) {
    parsed = parseSiteUrlOrPath(target, settings);
  }
  if (!parsed) {
    return null;
  }

  const repoName = buildContentRepoName(parsed, settings);
  const githubUrl = buildGitHubBlobUrl(repoName, parsed.slug, settings);
  const siteUrl = buildSiteArticleUrl(parsed, parsed.slug, settings);
  return formatSiteArticleDualLink(linkText, githubUrl, siteUrl);
}

async function convertToSiteArticleLinkCommand() {
  const settings = getSiteLinkSettings();
  const editor = vscode.window.activeTextEditor;
  let input = '';
  let useSelection = false;

  if (editor && !editor.selection.isEmpty) {
    input = editor.document.getText(editor.selection);
    useSelection = true;
  } else {
    input = await vscode.env.clipboard.readText();
  }

  const dual = convertInputToSiteArticleDualLink(input, settings);
  if (!dual) {
    vscode.window.showErrorMessage('Could not parse selection/clipboard as a GitHub blob URL or site article path.');
    return;
  }

  if (useSelection && editor) {
    const ok = await editor.edit((editBuilder) => {
      editBuilder.replace(editor.selection, dual);
    });
    if (ok) {
      vscode.window.showInformationMessage('Converted to site article dual link.');
    }
    return;
  }

  await vscode.env.clipboard.writeText(dual);
  vscode.window.showInformationMessage('Site article dual link copied to clipboard.');
}

function activateHarrixCliIntegration(deps) {
  const { context, provider, uriToFsPath, isDirectoryPath, normalizeFsPath } = deps;

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
    }),
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
    }),
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
    }),
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
            placeHolder: 'Choose a template',
          },
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
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.checkMarkdownInFolder', async (treeItemOrUri) => {
      const folderPath = resolveFolderPathForCliCommand(treeItemOrUri, deps);
      if (!folderPath) {
        vscode.window.showErrorMessage('Open a markdown note or select a folder / Note/Note.md in Harrix Notes (HSK).');
        return;
      }
      try {
        runHarrixMarkdownCheck(folderPath);
        vscode.window.showInformationMessage('Markdown check running in Terminal.');
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Markdown check failed: ${msg}`);
      }
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.beautifyRegenerateGMd', async (treeItemOrUri) => {
      const folderPath = resolveFolderPathForCliCommand(treeItemOrUri, deps);
      if (!folderPath) {
        vscode.window.showErrorMessage('Open a markdown note or select a folder / Note/Note.md in Harrix Notes (HSK).');
        return;
      }
      try {
        runHarrixBeautifyRegenerateGMd(folderPath);
        vscode.window.showInformationMessage('Beautify Markdown running in Terminal.');
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Beautify Markdown and Regenerate .g.md in Folder failed: ${msg}`);
      }
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.optimizeImagesFolder', async (treeItemOrUri) => {
      const folderPath = resolveFolderPathForCliCommand(treeItemOrUri, deps);
      if (!folderPath) {
        vscode.window.showErrorMessage('Open a markdown note or select a folder / Note/Note.md in Harrix Notes (HSK).');
        return;
      }
      try {
        const maxSize = getOptimizeImagesFolderMaxSize();
        runHarrixOptimizeImagesFolder(folderPath, maxSize);
        vscode.window.showInformationMessage(`Optimize images running in Terminal (max ${maxSize}px).`);
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Optimize images in folder failed: ${msg}`);
      }
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.convertToSiteArticleLink', async () => {
      try {
        await convertToSiteArticleLinkCommand();
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Convert to site article dual link failed: ${msg}`);
      }
    }),
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
  resolveNotesFolderContextValue,
};
