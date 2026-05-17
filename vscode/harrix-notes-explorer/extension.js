const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const { execFile, execFileSync } = require('child_process');
const util = require('util');

const execFileAsync = util.promisify(execFile);

function normalizeFsPath(p) {
  const resolved = path.resolve(String(p));
  return process.platform === 'win32' ? resolved.toLowerCase() : resolved;
}

function getCliExecOptions() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
  const cwdRaw = String(config.get('cliWorkingDirectory', '') || '').trim();
  const cwd = cwdRaw ? path.resolve(cwdRaw) : undefined;
  return {
    windowsHide: true,
    maxBuffer: 10 * 1024 * 1024,
    ...(cwd ? { cwd } : {})
  };
}

function getRememberFolderExpansion() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
  return config.get('rememberFolderExpansion') !== false;
}

/**
 * Persists expanded/collapsed folder paths (normalized) in workspace state so the tree
 * restores after reload. Folders not in either set start collapsed when remembering is on.
 */
class FolderExpansionMemory {
  /**
   * @param {vscode.ExtensionContext} context
   */
  constructor(context) {
    this._context = context;
    this._key = 'harrixNotesExplorer.folderExpansion.v1';
    const stored = context.workspaceState.get(this._key);
    this.expanded = new Set(
      Array.isArray(stored?.expanded) ? stored.expanded.map(x => normalizeFsPath(String(x))) : []
    );
    this.collapsed = new Set(
      Array.isArray(stored?.collapsed) ? stored.collapsed.map(x => normalizeFsPath(String(x))) : []
    );
    /** @type {ReturnType<typeof setTimeout> | null} */
    this._saveTimer = null;
  }

  /**
   * @param {string} folderPath
   */
  isExpanded(folderPath) {
    if (!getRememberFolderExpansion()) {
      return false;
    }
    const key = normalizeFsPath(folderPath);
    if (this.collapsed.has(key)) {
      return false;
    }
    if (this.expanded.has(key)) {
      return true;
    }
    return false;
  }

  /** @param {string} folderPath */
  recordExpand(folderPath) {
    if (!getRememberFolderExpansion()) {
      return;
    }
    const key = normalizeFsPath(folderPath);
    this.collapsed.delete(key);
    this.expanded.add(key);
    this._scheduleSave();
  }

  /** @param {string} folderPath */
  recordCollapse(folderPath) {
    if (!getRememberFolderExpansion()) {
      return;
    }
    const key = normalizeFsPath(folderPath);
    this.expanded.delete(key);
    this.collapsed.add(key);
    this._scheduleSave();
  }

  _scheduleSave() {
    if (this._saveTimer) {
      clearTimeout(this._saveTimer);
    }
    this._saveTimer = setTimeout(() => this.flush(), 250);
  }

  flush() {
    if (this._saveTimer) {
      clearTimeout(this._saveTimer);
      this._saveTimer = null;
    }
    return this._context.workspaceState.update(this._key, {
      expanded: Array.from(this.expanded),
      collapsed: Array.from(this.collapsed)
    });
  }
}

/**
 * Uses absolute folder path and stem without `.md` — matches Click options `--folder` / `--name`.
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

  const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
  const executable = config.get('cliExecutable', 'harrix-swiss-knife-cli');

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
 * Runs `harrix-swiss-knife-cli markdown new-diary-note --folder <folder>`.
 * @param {string} diaryRootPath
 */
async function runHarrixMarkdownNewDiaryNote(diaryRootPath) {
  const folderArg = path.resolve(diaryRootPath);
  const args = ['markdown', 'new-diary-note', '--folder', folderArg];

  const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
  const executable = config.get('cliExecutable', 'harrix-swiss-knife-cli');

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
 * Runs `harrix-swiss-knife-cli markdown new-dream-note --folder <folder>`.
 * @param {string} dreamRootPath
 */
async function runHarrixMarkdownNewDreamNote(dreamRootPath) {
  const folderArg = path.resolve(dreamRootPath);
  const args = ['markdown', 'new-dream-note', '--folder', folderArg];

  const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
  const executable = config.get('cliExecutable', 'harrix-swiss-knife-cli');

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
 * Runs `harrix-swiss-knife-cli markdown new-cases-note --folder <folder>`.
 * @param {string} casesRootPath
 */
async function runHarrixMarkdownNewCasesNote(casesRootPath) {
  const folderArg = path.resolve(casesRootPath);
  const args = ['markdown', 'new-cases-note', '--folder', folderArg];

  const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
  const executable = config.get('cliExecutable', 'harrix-swiss-knife-cli');

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
 * Runs `harrix-swiss-knife-cli markdown add-from-template --template "<id>"`.
 * @param {string} templateId
 */
async function runHarrixMarkdownAddFromTemplate(templateId) {
  const args = ['markdown', 'add-from-template', '--template', String(templateId)];

  const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
  const executable = config.get('cliExecutable', 'harrix-swiss-knife-cli');

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
 * Runs `harrix-swiss-knife-cli markdown list-templates`.
 * @returns {Promise<Array<{id: string, title: string, path_target?: string}>>}
 */
async function runHarrixMarkdownListTemplates() {
  const args = ['markdown', 'list-templates'];

  const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
  const executable = config.get('cliExecutable', 'harrix-swiss-knife-cli');

  try {
    const { stdout } = await execFileAsync(executable, args, getCliExecOptions());
    const text = (stdout || '').toString().trim();
    if (!text) return [];
    const parsed = JSON.parse(text);
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter(x => x && typeof x === 'object')
      .map(x => ({
        id: String(x.id || ''),
        title: String(x.title || ''),
        path_target: x.path_target ? String(x.path_target) : undefined
      }))
      .filter(x => x.id && x.title);
  } catch (err) {
    // Best-effort. Extension should still work without template commands.
    return [];
  }
}

/**
 * Runs `harrix-swiss-knife-cli markdown beautify-regenerate-g-md <folder>`.
 * @param {string} folderPath
 */
async function runHarrixBeautifyRegenerateGMd(folderPath) {
  const folderArg = path.resolve(folderPath);
  const args = ['markdown', 'beautify-regenerate-g-md', folderArg];

  const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
  const executable = config.get('cliExecutable', 'harrix-swiss-knife-cli');

  try {
    await execFileAsync(executable, args, getCliExecOptions());
  } catch (err) {
    const stderr = err.stderr ? err.stderr.toString() : '';
    const stdout = err.stdout ? err.stdout.toString() : '';
    const msg = (stderr || stdout || err.message || '').trim();
    throw new Error(msg || `CLI exited with code ${err.code}`);
  }
}

const GIT_EXEC_OPTS_BASE = { windowsHide: true, maxBuffer: 10 * 1024 * 1024 };

/**
 * @param {string} gitRoot
 * @param {string[]} args
 * @returns {Promise<{ ok: true, stdout: string, stderr: string } | { ok: false, stdout: string, stderr: string, code?: number, message: string }>}
 */
async function gitExecInRepo(gitRoot, args) {
  try {
    const r = await execFileAsync('git', args, { ...GIT_EXEC_OPTS_BASE, cwd: gitRoot });
    return {
      ok: true,
      stdout: (r.stdout || '').toString(),
      stderr: (r.stderr || '').toString()
    };
  } catch (err) {
    const stdout = err.stdout ? err.stdout.toString() : '';
    const stderr = err.stderr ? err.stderr.toString() : '';
    return {
      ok: false,
      stdout,
      stderr,
      code: typeof err.code === 'number' ? err.code : undefined,
      message: (err.message || '').trim() || 'git command failed'
    };
  }
}

/**
 * Resolve repository root and a pathspec (POSIX, trailing `/` for subfolders) for Git commands.
 * @param {string} folderPath
 * @returns {Promise<{ gitRoot: string, pathspec: string }>}
 */
async function resolveGitFolderPathspec(folderPath) {
  const resolved = path.resolve(folderPath);
  let gitRootRaw;
  try {
    const { stdout } = await execFileAsync(
      'git',
      ['rev-parse', '--show-toplevel'],
      { ...GIT_EXEC_OPTS_BASE, cwd: resolved }
    );
    gitRootRaw = (stdout || '').toString().trim();
  } catch (err) {
    const stderr = err.stderr ? err.stderr.toString().trim() : '';
    const out = err.stdout ? err.stdout.toString().trim() : '';
    const msg = (stderr || out || err.message || '').trim();
    throw new Error(msg || 'Not a Git repository.');
  }
  if (!gitRootRaw) {
    throw new Error('Could not determine Git repository root.');
  }
  const gitRoot = path.resolve(gitRootRaw);
  let rel = path.relative(gitRoot, resolved);
  if (rel.startsWith('..') || path.isAbsolute(rel)) {
    throw new Error('Folder is outside the Git repository.');
  }
  if (!rel || rel === '.') {
    return { gitRoot, pathspec: '.' };
  }
  const posix = rel.split(path.sep).join('/');
  const pathspec = posix.endsWith('/') ? posix : `${posix}/`;
  return { gitRoot, pathspec };
}

/**
 * Shows a busy state on the folder row while `fn` runs (spinner icon).
 * @param {NotesProvider} provider
 * @param {string} folderPath
 * @param {() => Promise<void>} fn
 */
async function withFolderBusy(provider, folderPath, fn) {
  const key = normalizeFsPath(folderPath);
  provider.setFolderBusy(key, true);
  try {
    await fn();
  } finally {
    provider.setFolderBusy(key, false);
  }
}

// --- Helper functions ---

function safeReaddir(dir) {
  try { return fs.readdirSync(dir, { withFileTypes: true }); }
  catch (e) { return []; }
}

function isMd(name) { return name.toLowerCase().endsWith('.md'); }
function isGMd(name) { return name.toLowerCase().endsWith('.g.md'); }

/** Merged-folder template only: exactly `_<parentFolderName>.g.md` (case-insensitive). Other `*.g.md` stay visible. */
function isMergedTemplateGmd(fileName, parentFolderBasename) {
  if (!isGMd(fileName)) return false;
  const expected = `_${parentFolderBasename}.g.md`.toLowerCase();
  return fileName.toLowerCase() === expected;
}

/** Folder named `Diary` (case-insensitive) — shown in tree even without .md; gets diary CLI menu */
function isDiaryFolderName(name) {
  return String(name).toLowerCase() === 'diary';
}

/** Folder named `Dreams` (case-insensitive) — shown in tree even without .md; gets dream CLI menu */
function isDreamsFolderName(name) {
  return String(name).toLowerCase() === 'dreams';
}

/** Folder named `Cases` (case-insensitive) — shown in tree even without .md; gets cases CLI menu */
function isCasesFolderName(name) {
  return String(name).toLowerCase() === 'cases';
}

function isSpecialNotesFolderName(name) {
  return (
    isDiaryFolderName(name) ||
    isDreamsFolderName(name) ||
    isCasesFolderName(name)
  );
}

/** Combined folder note: _<FolderName>.g.md next to sibling .md files */
function mergedNotePath(folderPath, folderName) {
  return path.join(folderPath, `_${folderName}.g.md`);
}

function hasMergedNoteFs(folderPath, folderName) {
  return pathExists(mergedNotePath(folderPath, folderName));
}

function uriToFsPath(uri) {
  return uri instanceof vscode.Uri ? uri.fsPath : undefined;
}

function pathExists(fsPath) {
  try { fs.accessSync(fsPath); return true; } catch { return false; }
}

function isDirectoryPath(fsPath) {
  try { return fs.statSync(fsPath).isDirectory(); } catch { return false; }
}

function isFilePath(fsPath) {
  try { return fs.statSync(fsPath).isFile(); } catch { return false; }
}

/** @param {unknown} treeItemOrUri */
function noteUriFromTreeArg(treeItemOrUri) {
  const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
  return itemUri instanceof vscode.Uri ? itemUri : undefined;
}

/**
 * @param {vscode.Uri} uri
 * @param {'primary' | 'editor' | 'preview'} mode
 */
async function openHarrixNote(uri, mode) {
  if (!(uri instanceof vscode.Uri) || !isFilePath(uri.fsPath)) {
    return;
  }
  let usePreview;
  if (mode === 'editor') {
    usePreview = false;
  } else if (mode === 'preview') {
    usePreview = true;
  } else {
    const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
    usePreview = config.get('openNotesInPreview') !== false;
  }
  if (usePreview) {
    try {
      await vscode.commands.executeCommand('markdown.showPreview', uri, undefined, { locked: true });
    } catch {
      await vscode.commands.executeCommand('vscode.open', uri);
    }
  } else {
    await vscode.commands.executeCommand('vscode.open', uri);
  }
}

// Check whether a folder contains at least one .md file (recursively)
function hasMarkdownRecursive(dir) {
  for (const entry of safeReaddir(dir)) {
    if (entry.isFile() && isMd(entry.name)) return true;
    if (entry.isDirectory()) {
      if (hasMarkdownRecursive(path.join(dir, entry.name))) return true;
    }
  }
  return false;
}

// --- TreeDataProvider ---

class NotesProvider {
  /**
   * @param {string} rootPath
   * @param {FolderExpansionMemory | null} expansionMemory
   */
  constructor(rootPath, expansionMemory) {
    this.rootPath = rootPath;
    /** @type {FolderExpansionMemory | null} */
    this._expansion = expansionMemory;
    this._emitter = new vscode.EventEmitter();
    this.onDidChangeTreeData = this._emitter.event;
    /** @type {Set<string>} resolved fs paths */
    this._busyFolderPaths = new Set();
    /** @type {Map<string, Array<{id: string, title: string}>>} resolved folder path -> templates */
    this._templateTargets = new Map();
    /** @type {Map<string, boolean>} normalized folder path -> inside git work tree */
    this._gitWorkTreeCache = new Map();
  }

  refresh() {
    this._gitWorkTreeCache.clear();
    this._emitter.fire();
  }

  /**
   * @param {string} folderPath
   * @returns {boolean}
   */
  isFolderInsideGitWorkTree(folderPath) {
    const key = normalizeFsPath(folderPath);
    if (this._gitWorkTreeCache.has(key)) {
      return /** @type {boolean} */ (this._gitWorkTreeCache.get(key));
    }
    let inside = false;
    try {
      const out = execFileSync('git', ['rev-parse', '--is-inside-work-tree'], {
        ...GIT_EXEC_OPTS_BASE,
        cwd: folderPath,
        encoding: 'utf8'
      });
      inside = String(out || '').trim() === 'true';
    } catch {
      inside = false;
    }
    this._gitWorkTreeCache.set(key, inside);
    return inside;
  }

  /** @param {Map<string, Array<{id: string, title: string}>>} map */
  setTemplateTargets(map) {
    this._templateTargets = map;
    this._emitter.fire();
  }

  /**
   * @param {string} folderPath
   * @returns {Array<{id: string, title: string}>}
   */
  getTemplatesForFolder(folderPath) {
    return this._templateTargets.get(normalizeFsPath(folderPath)) || [];
  }

  /**
   * @param {string} folderPath absolute or relative folder path
   * @param {boolean} busy
   */
  setFolderBusy(folderPath, busy) {
    const key = normalizeFsPath(folderPath);
    if (busy) {
      this._busyFolderPaths.add(key);
    } else {
      this._busyFolderPaths.delete(key);
    }
    this._emitter.fire();
  }

  isFolderBusy(folderPath) {
    return this._busyFolderPaths.has(normalizeFsPath(folderPath));
  }

  getTreeItem(el) { return el; }

  getChildren(element) {
    const dir = element ? element.dirPath : this.rootPath;
    if (!dir || !fs.existsSync(dir)) return [];

    const parentFolderDepth =
      element && typeof element.folderDepth === 'number' && Number.isFinite(element.folderDepth)
        ? element.folderDepth
        : 0;

    const entries = safeReaddir(dir);

    // Folders that contain at least one .md file (recursively)
    const folders = entries
      .filter(e => e.isDirectory())
      .filter(e =>
        hasMarkdownRecursive(path.join(dir, e.name)) ||
        isSpecialNotesFolderName(e.name) ||
        this.getTemplatesForFolder(path.join(dir, e.name)).length > 0
      );

    const hereName = path.basename(dir);
    // .md in this folder; hide only merged template `_<folder>.g.md`, not other *.g.md
    const mdFiles = entries.filter(
      e => e.isFile() && isMd(e.name) && !isMergedTemplateGmd(e.name, hereName)
    );

    const items = [];

    // --- folders ---
    for (const folder of folders) {
      const folderPath = path.join(dir, folder.name);
      const sub = safeReaddir(folderPath);
      const subVisibleMd = sub.filter(
        e => e.isFile() && isMd(e.name) && !isMergedTemplateGmd(e.name, folder.name)
      );
      const subFolders = sub
        .filter(e => e.isDirectory())
        .filter(e =>
          hasMarkdownRecursive(path.join(folderPath, e.name)) ||
          isSpecialNotesFolderName(e.name)
        );

      const sameNameMdPath = path.join(folderPath, folder.name + '.md');
      const hasSameNameMd = fs.existsSync(sameNameMdPath);

      // Rule: folder + exactly one .md with the same name + no "visible" subfolders
      // => collapse into a single file
      if (hasSameNameMd && subVisibleMd.length === 1 && subFolders.length === 0) {
        items.push(this.createFileItem(sameNameMdPath, folder.name));
      } else {
        items.push(this.createFolderItem(folderPath, folder.name, parentFolderDepth + 1));
      }
    }

    // --- .md files ---
    for (const file of mdFiles) {
      const filePath = path.join(dir, file.name);
      const displayName = file.name.replace(/\.md$/i, '');
      items.push(this.createFileItem(filePath, displayName));
    }

    const labelToString = (label) => {
      if (!label) return '';
      if (typeof label === 'string') return label;
      if (typeof label === 'object' && typeof label.label === 'string') return label.label;
      return String(label);
    };

    return items.sort((a, b) =>
      labelToString(a.label).localeCompare(labelToString(b.label), undefined, { numeric: true, sensitivity: 'base' })
    );
  }

  createFolderItem(folderPath, name, folderDepth) {
    const depth =
      typeof folderDepth === 'number' && Number.isFinite(folderDepth) ? Math.max(1, Math.floor(folderDepth)) : 1;
    const expanded = this._expansion != null ? this._expansion.isExpanded(folderPath) : false;
    const collapsible = expanded
      ? vscode.TreeItemCollapsibleState.Expanded
      : vscode.TreeItemCollapsibleState.Collapsed;
    const item = new vscode.TreeItem(name, collapsible);
    item.resourceUri = vscode.Uri.file(folderPath);
    item.dirPath = folderPath;
    item.folderDepth = depth;
    item.templateItems = this.getTemplatesForFolder(folderPath);
    if (isDiaryFolderName(name)) {
      item.contextValue = hasMergedNoteFs(folderPath, name)
        ? 'notesFolderWithMergedDiary'
        : 'notesFolderDiary';
    } else if (isDreamsFolderName(name)) {
      item.contextValue = hasMergedNoteFs(folderPath, name)
        ? 'notesFolderWithMergedDreams'
        : 'notesFolderDreams';
    } else if (isCasesFolderName(name)) {
      item.contextValue = hasMergedNoteFs(folderPath, name)
        ? 'notesFolderWithMergedCases'
        : 'notesFolderCases';
    } else if ((item.templateItems || []).length > 0) {
      item.contextValue = hasMergedNoteFs(folderPath, name)
        ? 'notesFolderTemplateTargetWithMerged'
        : 'notesFolderTemplateTarget';
    } else {
      item.contextValue = hasMergedNoteFs(folderPath, name)
        ? 'notesFolderWithMerged'
        : 'notesFolder';
    }
    if (this.isFolderInsideGitWorkTree(folderPath)) {
      const base = item.contextValue;
      item.contextValue = `git${base.charAt(0).toUpperCase()}${base.slice(1)}`;
    }
    if (this.isFolderBusy(folderPath)) {
      item.iconPath = new vscode.ThemeIcon('loading~spin');
      item.description = '…';
    } else {
      item.iconPath = vscode.ThemeIcon.Folder;
    }
    return item;
  }

  createFileItem(filePath, displayName) {
    const item = new vscode.TreeItem(displayName, vscode.TreeItemCollapsibleState.None);
    item.resourceUri = vscode.Uri.file(filePath);
    item.tooltip = filePath;
    item.command = {
      command: 'harrixNotesExplorer.openNote',
      title: 'Open',
      arguments: [vscode.Uri.file(filePath)]
    };

    item.iconPath = new vscode.ThemeIcon('markdown');
    item.contextValue = 'note';
    return item;
  }
}

/** @returns {Record<string, unknown>} */
function getPreviewCopyConfig() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
  const zone = Number(config.get('previewCopy.bottomHoverZonePx', 80));
  return {
    enabled: config.get('previewCopy.enabled', true) !== false,
    showTop: config.get('previewCopy.showTopButton', true) !== false,
    showBottom: config.get('previewCopy.showBottomButton', true) !== false,
    topAlwaysVisible: config.get('previewCopy.topAlwaysVisible', true) !== false,
    bottomHoverZonePx: Number.isFinite(zone) && zone >= 0 ? zone : 80,
    backgroundColor: normalizePreviewCopyColor(config.get('previewCopy.backgroundColor', '#fefefe'), '#fefefe'),
    borderColor: normalizePreviewCopyColor(config.get('previewCopy.borderColor', '#7f7f7f'), '#7f7f7f'),
    copiedColor: normalizePreviewCopyColor(config.get('previewCopy.copiedColor', '#388a34'), '#388a34')
  };
}

/**
 * @param {unknown} value
 * @param {string} fallback
 */
function normalizePreviewCopyColor(value, fallback) {
  const raw = String(value ?? '').trim();
  if (!raw) {
    return fallback;
  }
  return raw.startsWith('#') ? raw : `#${raw}`;
}

/**
 * @param {string} json
 */
function escapePreviewCopyConfigAttr(json) {
  return json
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;');
}

function registerPreviewCopyMarkdownPlugin() {
  return {
    extendMarkdownIt(/** @type {import('markdown-it')} */ md) {
      const render = md.render.bind(md);
      md.render = function (src, env) {
        const cfg = getPreviewCopyConfig();
        const json = escapePreviewCopyConfigAttr(JSON.stringify(cfg));
        const configHtml =
          '<' +
          'div id="hne-preview-copy-config" style="display:none" data-config="' +
          json +
          '"></' +
          'div>';
        return configHtml + render(src, env);
      };
      return md;
    }
  };
}

/**
 * @param {vscode.ExtensionContext} context
 */
function registerPreviewCopyConfigRefresh(context) {
  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (!e.affectsConfiguration('harrixNotesExplorer.previewCopy')) {
        return;
      }
      void vscode.commands.executeCommand('markdown.preview.refresh');
    })
  );
}

function activate(context) {
  registerPreviewCopyConfigRefresh(context);

  const folders = vscode.workspace.workspaceFolders;
  if (!folders || folders.length === 0) {
    return registerPreviewCopyMarkdownPlugin();
  }
  const rootPath = folders[0].uri.fsPath;

  const expansionMemory = new FolderExpansionMemory(context);
  context.subscriptions.push({
    dispose: () => {
      void expansionMemory.flush();
    }
  });

  const provider = new NotesProvider(rootPath, expansionMemory);
  const view = vscode.window.createTreeView('harrixNotesExplorer', {
    treeDataProvider: provider,
    showCollapseAll: true
  });
  context.subscriptions.push(view);

  context.subscriptions.push(
    view.onDidExpandElement(e => {
      const el = /** @type {vscode.TreeItem & { dirPath?: string }} */ (e.element);
      if (el && typeof el.dirPath === 'string') {
        expansionMemory.recordExpand(el.dirPath);
      }
    })
  );
  context.subscriptions.push(
    view.onDidCollapseElement(e => {
      const el = /** @type {vscode.TreeItem & { dirPath?: string }} */ (e.element);
      if (el && typeof el.dirPath === 'string') {
        expansionMemory.recordCollapse(el.dirPath);
      }
    })
  );

  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration(e => {
      if (e.affectsConfiguration('harrixNotesExplorer.rememberFolderExpansion')) {
        provider.refresh();
      }
    })
  );

  const logChannel = vscode.window.createOutputChannel('Harrix Notes Explorer');
  context.subscriptions.push(logChannel);

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.openNote', async treeItemOrUri => {
      const uri = noteUriFromTreeArg(treeItemOrUri);
      if (!uri) {
        return;
      }
      await openHarrixNote(uri, 'primary');
    })
  );
  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.openNoteInEditor', async treeItemOrUri => {
      const uri = noteUriFromTreeArg(treeItemOrUri);
      if (!uri) {
        return;
      }
      await openHarrixNote(uri, 'editor');
    })
  );
  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.openNoteInPreview', async treeItemOrUri => {
      const uri = noteUriFromTreeArg(treeItemOrUri);
      if (!uri) {
        return;
      }
      await openHarrixNote(uri, 'preview');
    })
  );
  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.openMarkdownPreviewTabInEditor', async () => {
      try {
        await vscode.commands.executeCommand('markdown.showSource');
      } catch {
        // Built-in Markdown extension unavailable or no active preview resource.
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.refresh', () => provider.refresh())
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.openMergedNote', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isDirectoryPath(fsPath)) return;

      const folderName = path.basename(fsPath);
      const gPath = mergedNotePath(fsPath, folderName);
      if (!pathExists(gPath)) {
        vscode.window.showWarningMessage('No merged note for this folder (_' + folderName + '.g.md).');
        return;
      }
      await vscode.commands.executeCommand('vscode.open', vscode.Uri.file(gPath));
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.newDiaryNote', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isDirectoryPath(fsPath)) {
        vscode.window.showErrorMessage('Select the Diary folder in Harrix Notes.');
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
    vscode.commands.registerCommand('harrixNotesExplorer.newDreamNote', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isDirectoryPath(fsPath)) {
        vscode.window.showErrorMessage('Select the Dreams folder in Harrix Notes.');
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
    vscode.commands.registerCommand('harrixNotesExplorer.newCasesNote', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isDirectoryPath(fsPath)) {
        vscode.window.showErrorMessage('Select the Cases folder in Harrix Notes.');
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
    vscode.commands.registerCommand('harrixNotesExplorer.addFromTemplate', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isDirectoryPath(fsPath)) {
        vscode.window.showErrorMessage('Select a target folder in Harrix Notes.');
        return;
      }

      const templateItems =
        Array.isArray(treeItemOrUri?.templateItems) ? treeItemOrUri.templateItems : provider.getTemplatesForFolder(fsPath);

      if (!templateItems || templateItems.length === 0) {
        vscode.window.showErrorMessage('No templates configured for this folder.');
        return;
      }

      let templateId = '';
      if (templateItems.length === 1) {
        const only = templateItems[0];
        templateId =
          only && typeof only.id === 'string' && only.id.trim() ? only.id.trim() : '';
      } else {
        const chosenItem = await vscode.window.showQuickPick(
          templateItems.map(t => ({ label: t.title, description: t.id })),
          {
            title: 'Add from template',
            placeHolder: 'Choose a template'
          }
        );
        // Use `description` for template id — VS Code may set its own `id` on pick items.
        templateId =
          chosenItem &&
          typeof chosenItem.description === 'string' &&
          chosenItem.description.trim()
            ? chosenItem.description.trim()
            : '';
      }

      if (!templateId) return;

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
    vscode.commands.registerCommand('harrixNotesExplorer.beautifyRegenerateGMd', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isDirectoryPath(fsPath)) {
        vscode.window.showErrorMessage('Select a folder in Harrix Notes.');
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
    vscode.commands.registerCommand('harrixNotesExplorer.discardGitChangesInFolder', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isDirectoryPath(fsPath)) {
        vscode.window.showErrorMessage('Select a folder in Harrix Notes.');
        return;
      }

      try {
        await withFolderBusy(provider, fsPath, async () => {
          const { gitRoot, pathspec } = await resolveGitFolderPathspec(fsPath);
          logChannel.clear();
          logChannel.appendLine(`Git root: ${gitRoot}`);
          logChannel.appendLine(`Pathspec: ${pathspec}`);
          logChannel.appendLine('');

          logChannel.appendLine(`> git status --porcelain -- ${pathspec}`);
          const st = await gitExecInRepo(gitRoot, ['status', '--porcelain', '--', pathspec]);
          if (!st.ok) {
            logChannel.appendLine(st.stderr.trimEnd() || st.stdout.trimEnd() || st.message);
            logChannel.show(true);
            vscode.window.showErrorMessage(`git status failed: ${st.stderr.trim() || st.message}`);
            return;
          }
          const stOut = st.stdout.trimEnd();
          if (stOut) {
            logChannel.appendLine(stOut);
          } else {
            logChannel.appendLine('(no staged/unstaged changes under pathspec)');
          }
          logChannel.appendLine('');

          logChannel.appendLine(`> git clean -nd -- ${pathspec}`);
          const dry = await gitExecInRepo(gitRoot, ['clean', '-nd', '--', pathspec]);
          if (!dry.ok) {
            logChannel.appendLine(dry.stderr.trimEnd() || dry.stdout.trimEnd() || dry.message);
            logChannel.show(true);
            vscode.window.showErrorMessage(`git clean dry-run failed: ${dry.stderr.trim() || dry.message}`);
            return;
          }
          const dryOut = dry.stdout.trimEnd();
          const dryErr = dry.stderr.trimEnd();
          if (dryErr) logChannel.appendLine(dryErr);
          if (dryOut) {
            logChannel.appendLine(dryOut);
          } else if (!dryErr) {
            logChannel.appendLine('(nothing untracked would be removed)');
          }

          logChannel.show(true);

          const confirm = await vscode.window.showWarningMessage(
            [
              'Discard all local changes under this folder?',
              '',
              '• Tracked files: reset to HEAD (staged + working tree).',
              '• Untracked files and empty dirs: permanently deleted.',
              '• Ignored files: not touched.',
              '',
              fsPath
            ].join('\n'),
            { modal: true, detail: 'Requires Git 2.23+ (git restore).' },
            'Discard'
          );
          if (confirm !== 'Discard') {
            logChannel.appendLine('');
            logChannel.appendLine('Cancelled.');
            logChannel.show(true);
            return;
          }

          logChannel.appendLine('');
          logChannel.appendLine(`> git restore --source=HEAD --staged --worktree -- ${pathspec}`);
          const restore = await gitExecInRepo(gitRoot, [
            'restore',
            '--source=HEAD',
            '--staged',
            '--worktree',
            '--',
            pathspec
          ]);
          if (!restore.ok) {
            logChannel.appendLine(restore.stderr.trimEnd() || restore.stdout.trimEnd() || restore.message);
            logChannel.show(true);
            vscode.window.showErrorMessage(`git restore failed: ${restore.stderr.trim() || restore.message}`);
            return;
          }
          if (restore.stderr.trim()) logChannel.appendLine(restore.stderr.trimEnd());
          logChannel.appendLine('OK');

          logChannel.appendLine('');
          logChannel.appendLine(`> git clean -fd -- ${pathspec}`);
          const clean = await gitExecInRepo(gitRoot, ['clean', '-fd', '--', pathspec]);
          if (!clean.ok) {
            logChannel.appendLine(clean.stderr.trimEnd() || clean.stdout.trimEnd() || clean.message);
            logChannel.show(true);
            vscode.window.showErrorMessage(`git clean failed: ${clean.stderr.trim() || clean.message}`);
            return;
          }
          if (clean.stdout.trim()) logChannel.appendLine(clean.stdout.trimEnd());
          if (clean.stderr.trim()) logChannel.appendLine(clean.stderr.trimEnd());
          if (!clean.stdout.trim() && !clean.stderr.trim()) {
            logChannel.appendLine('(done)');
          }

          logChannel.show(true);
          vscode.window.showInformationMessage('Git discard completed for folder.');
          provider.refresh();
        });
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        logChannel.clear();
        logChannel.appendLine('Discard Git changes in folder (failed)');
        logChannel.appendLine(msg);
        logChannel.show(true);
        vscode.window.showErrorMessage(`Discard Git changes failed: ${msg}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.revealInOS', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const targetUri =
        itemUri instanceof vscode.Uri
          ? itemUri
          : vscode.window.activeTextEditor?.document?.uri;

      if (!targetUri) return;

      await vscode.commands.executeCommand('revealFileInOS', targetUri);
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.copyPath', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath) return;
      await vscode.env.clipboard.writeText(fsPath);
      vscode.window.setStatusBarMessage('Copied path to clipboard', 1500);
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.createNote', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);

      const baseDir =
        fsPath && isDirectoryPath(fsPath)
          ? fsPath
          : fsPath && isFilePath(fsPath)
            ? path.dirname(fsPath)
            : rootPath;

      const name = await vscode.window.showInputBox({
        title: 'Create Note',
        prompt: 'Enter note name (without extension)',
        placeHolder: 'My-note'
      });
      if (!name) return;

      const safeName = name.trim();
      if (!safeName) return;

      try {
        await withFolderBusy(provider, baseDir, () =>
          runHarrixMarkdownNewNote(baseDir, safeName, false)
        );
        provider.refresh();
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Create note failed: ${msg}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.createNoteWithImages', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);

      const baseDir =
        fsPath && isDirectoryPath(fsPath)
          ? fsPath
          : rootPath;

      if (!baseDir || !isDirectoryPath(baseDir)) {
        vscode.window.showErrorMessage('Choose a folder in Harrix Notes.');
        return;
      }

      const name = await vscode.window.showInputBox({
        title: 'Create Note with Images',
        prompt: 'Enter note name (without extension)',
        placeHolder: 'My-note'
      });
      if (!name) return;

      const safeName = name.trim();
      if (!safeName) return;

      try {
        await withFolderBusy(provider, baseDir, () =>
          runHarrixMarkdownNewNote(baseDir, safeName, true)
        );
        provider.refresh();
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Create note with images failed: ${msg}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.renameItem', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath) return;

      const isDir = isDirectoryPath(fsPath);
      const isFile = isFilePath(fsPath);
      if (!isDir && !isFile) return;

      const parentDir = path.dirname(fsPath);
      const oldBaseName = path.basename(fsPath);

      const fileExt = isFile
        ? (isGMd(oldBaseName) ? '.g.md' : '.md')
        : '';

      const defaultValue = isFile
        ? (isGMd(oldBaseName)
          ? oldBaseName.replace(/\.g\.md$/i, '')
          : oldBaseName.replace(/\.md$/i, ''))
        : oldBaseName;

      const newName = await vscode.window.showInputBox({
        title: 'Rename',
        prompt: isDir ? 'Enter new folder name' : 'Enter new note name (without extension)',
        value: defaultValue
      });
      if (!newName) return;

      const safeNew = newName.trim();
      if (!safeNew) return;

      const newBaseName = isFile
        ? (safeNew.toLowerCase().endsWith('.md') ? safeNew : `${safeNew}${fileExt}`)
        : safeNew;

      const newPath = path.join(parentDir, newBaseName);

      if (newPath === fsPath) return;
      if (pathExists(newPath)) {
        vscode.window.showErrorMessage('Target name already exists.');
        return;
      }

      await vscode.workspace.fs.rename(vscode.Uri.file(fsPath), vscode.Uri.file(newPath), { overwrite: false });
      provider.refresh();

      if (isFile) {
        await vscode.commands.executeCommand('vscode.open', vscode.Uri.file(newPath));
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.deleteItem', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath) return;

      const isDir = isDirectoryPath(fsPath);
      const isFile = isFilePath(fsPath);
      if (!isDir && !isFile) return;

      const choice = await vscode.window.showWarningMessage(
        `Delete ${isDir ? 'folder' : 'note'} "${path.basename(fsPath)}"?`,
        { modal: true },
        'Delete'
      );
      if (choice !== 'Delete') return;

      await vscode.workspace.fs.delete(vscode.Uri.file(fsPath), { recursive: isDir, useTrash: true });
      provider.refresh();
    })
  );

  // Auto-refresh when .md files change
  const watcher = vscode.workspace.createFileSystemWatcher('**/*.md');
  watcher.onDidCreate(() => provider.refresh());
  watcher.onDidDelete(() => provider.refresh());
  watcher.onDidChange(() => provider.refresh());
  context.subscriptions.push(watcher);

  // Load templates -> folder targets (best-effort) and refresh the tree.
  (async () => {
    const templates = await runHarrixMarkdownListTemplates();
    const map = new Map();
    for (const t of templates) {
      if (!t.path_target) continue;
      const key = normalizeFsPath(t.path_target);
      const arr = map.get(key) || [];
      arr.push({ id: t.id, title: t.title });
      map.set(key, arr);
    }
    provider.setTemplateTargets(map);
  })();

  return registerPreviewCopyMarkdownPlugin();
}

function deactivate() { }

module.exports = { activate, deactivate };


