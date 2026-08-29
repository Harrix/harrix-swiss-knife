const vscode = require('vscode');
const path = require('node:path');
const fs = require('node:fs');
const http = require('node:http');
const crypto = require('node:crypto');
const { execFile } = require('node:child_process');
const util = require('node:util');

const execFileAsync = util.promisify(execFile);

/** hsk integration — see harrix-cli.js and HARRIX_CLI.md */
const harrixCli = require('./harrix-cli');
/** @hsk-sync:new-note — in-extension New note (no CLI) */
const { activateNewNote } = require('./new-note');
/** @hsk-sync:note-meta — title/date resolution (keep synced with pyssg + Android) */
const noteMeta = require('./note-meta');
const { activateIconsBrowse, refreshIconsBrowseIfOpen } = require('./icons-browse');
const { activateVisualEditor } = require('./visual-editor');
const { isMarpMarkdown, renderMarpPreviewHtml, renderMarpPresentWebview } = require('./marp-deck');

function normalizeFsPath(p) {
  const resolved = path.resolve(String(p));
  return process.platform === 'win32' ? resolved.toLowerCase() : resolved;
}

function getRememberFolderExpansion() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
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
    this._key = 'harrixNotesExplorerHsk.folderExpansion.v1';
    const stored = context.workspaceState.get(this._key);
    this.expanded = new Set(
      Array.isArray(stored?.expanded) ? stored.expanded.map((x) => normalizeFsPath(String(x))) : [],
    );
    this.collapsed = new Set(
      Array.isArray(stored?.collapsed) ? stored.collapsed.map((x) => normalizeFsPath(String(x))) : [],
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

  /**
   * Workspace root folder: expanded by default unless explicitly collapsed.
   * @param {string} folderPath
   */
  isWorkspaceRootExpanded(folderPath) {
    if (!getRememberFolderExpansion()) {
      return true;
    }
    const key = normalizeFsPath(folderPath);
    return !this.collapsed.has(key);
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
      collapsed: Array.from(this.collapsed),
    });
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
      stderr: (r.stderr || '').toString(),
    };
  } catch (err) {
    const stdout = err.stdout ? err.stdout.toString() : '';
    const stderr = err.stderr ? err.stderr.toString() : '';
    return {
      ok: false,
      stdout,
      stderr,
      code: typeof err.code === 'number' ? err.code : undefined,
      message: (err.message || '').trim() || 'git command failed',
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
    const { stdout } = await execFileAsync('git', ['rev-parse', '--show-toplevel'], {
      ...GIT_EXEC_OPTS_BASE,
      cwd: resolved,
    });
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
  const rel = path.relative(gitRoot, resolved);
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
 * @param {string} filePath absolute path to a note `.md` file
 * @returns {Promise<{ gitRoot: string, pathspec: string, cleanRecursive: boolean }>}
 */
async function resolveGitNotePathspec(filePath) {
  const resolved = path.resolve(filePath);
  if (isNoteInNamedFolder(resolved)) {
    const { gitRoot, pathspec } = await resolveGitFolderPathspec(path.dirname(resolved));
    return { gitRoot, pathspec, cleanRecursive: true };
  }
  const { gitRoot } = await resolveGitFolderPathspec(path.dirname(resolved));
  const rel = path.relative(gitRoot, resolved);
  if (rel.startsWith('..') || path.isAbsolute(rel)) {
    throw new Error('Note is outside the Git repository.');
  }
  const pathspec = rel.split(path.sep).join('/');
  return { gitRoot, pathspec, cleanRecursive: false };
}

/**
 * Pathspec for `git restore` / `git ls-files` (directory trailing `/` is not always accepted).
 * @param {string} pathspec
 * @returns {string}
 */
function gitRestorePathspec(pathspec) {
  if (pathspec === '.' || pathspec === './') {
    return '.';
  }
  return pathspec.endsWith('/') ? pathspec.slice(0, -1) : pathspec;
}

/**
 * @param {string} gitRoot
 * @param {string} pathspec
 * @returns {Promise<boolean>}
 */
async function gitPathspecHasTrackedFiles(gitRoot, pathspec) {
  const restoreSpec = gitRestorePathspec(pathspec);
  const ls = await gitExecInRepo(gitRoot, ['ls-files', '--', restoreSpec]);
  if (!ls.ok) {
    return false;
  }
  return Boolean(ls.stdout.trim());
}

/** @param {string} stOut */
function gitStatusLines(stOut) {
  return stOut
    ? stOut
        .split(/\r?\n/)
        .map((l) => l.trimEnd())
        .filter(Boolean)
    : [];
}

/**
 * @param {{ gitRoot: string, pathspec: string, targetLabel: string, cleanRecursive: boolean, confirmTitle: string, successMessage: string, notTrackedMessage: string, logChannel: vscode.OutputChannel, onSuccess?: () => void }} opts
 */
async function runGitDiscardWorkflow(opts) {
  const { gitRoot, pathspec, targetLabel, cleanRecursive, confirmTitle, successMessage, logChannel, onSuccess } = opts;
  const cleanDryArgs = cleanRecursive ? ['clean', '-nd', '--', pathspec] : ['clean', '-nf', '--', pathspec];
  const cleanArgs = cleanRecursive ? ['clean', '-fd', '--', pathspec] : ['clean', '-f', '--', pathspec];
  const restoreSpec = gitRestorePathspec(pathspec);

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
  const statusLines = gitStatusLines(stOut);
  if (stOut) {
    logChannel.appendLine(stOut);
  } else {
    logChannel.appendLine('(no staged/unstaged changes under pathspec)');
  }
  logChannel.appendLine('');

  logChannel.appendLine(`> git ls-files -- ${restoreSpec}`);
  const hasTracked = await gitPathspecHasTrackedFiles(gitRoot, pathspec);
  if (hasTracked) {
    logChannel.appendLine('(tracked files present under pathspec)');
  } else {
    logChannel.appendLine('(no tracked files under pathspec)');
  }
  logChannel.appendLine('');

  if (!hasTracked) {
    if (statusLines.length === 0) {
      logChannel.appendLine('Nothing to discard.');
      logChannel.show(true);
      vscode.window.showInformationMessage('Nothing to discard.');
      return;
    }

    // If nothing under this pathspec is tracked, porcelain output can only contain untracked files.
    // We never run `git clean` in this case to avoid deleting user files in a non-tracked area.
    logChannel.appendLine('Nothing to discard: this path is not tracked by Git.');
    logChannel.show(true);
    vscode.window.showInformationMessage(
      String(opts.notTrackedMessage || 'This path is not tracked by Git. Nothing to discard.'),
    );
    return;
  }

  if (statusLines.length === 0) {
    logChannel.appendLine('Nothing to discard.');
    logChannel.show(true);
    vscode.window.showInformationMessage('Nothing to discard.');
    return;
  }

  if (hasTracked) {
    logChannel.appendLine(`> git ${cleanDryArgs.join(' ')}`);
    const dry = await gitExecInRepo(gitRoot, cleanDryArgs);
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
    logChannel.appendLine('');
  }

  logChannel.show(true);

  /** @type {string[]} */
  const confirmLines = [confirmTitle, '', '• Tracked files: reset to HEAD (staged + working tree).'];
  if (hasTracked) {
    confirmLines.push(
      cleanRecursive
        ? '• Untracked files and empty dirs inside this path: permanently deleted.'
        : '• Untracked copy of this file: permanently deleted.',
    );
  }
  confirmLines.push('• Ignored files: not touched.', '', targetLabel);

  const confirm = await vscode.window.showWarningMessage(
    confirmLines.join('\n'),
    { modal: true, detail: 'Requires Git 2.23+ (git restore).' },
    'Discard',
  );
  if (confirm !== 'Discard') {
    logChannel.appendLine('');
    logChannel.appendLine('Cancelled.');
    logChannel.show(true);
    return;
  }

  logChannel.appendLine('');
  if (hasTracked) {
    logChannel.appendLine(`> git restore --source=HEAD --staged --worktree -- ${restoreSpec}`);
    const restore = await gitExecInRepo(gitRoot, [
      'restore',
      '--source=HEAD',
      '--staged',
      '--worktree',
      '--',
      restoreSpec,
    ]);
    if (!restore.ok) {
      const errText = (restore.stderr || restore.message || '').trim();
      logChannel.appendLine(restore.stderr.trimEnd() || restore.stdout.trimEnd() || restore.message);
      if (/did not match any file\(s\) known to git/i.test(errText)) {
        logChannel.appendLine('(skipping git restore — no tracked files matched pathspec)');
      } else {
        logChannel.show(true);
        vscode.window.showErrorMessage(`git restore failed: ${restore.stderr.trim() || restore.message}`);
        return;
      }
    } else {
      if (restore.stderr.trim()) logChannel.appendLine(restore.stderr.trimEnd());
      logChannel.appendLine('OK');
    }

    logChannel.appendLine('');
    logChannel.appendLine(`> git ${cleanArgs.join(' ')}`);
    const clean = await gitExecInRepo(gitRoot, cleanArgs);
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
  }

  logChannel.show(true);
  vscode.window.showInformationMessage(successMessage);
  onSuccess?.();
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
    return await fn();
  } finally {
    provider.setFolderBusy(key, false);
  }
}

// --- Helper functions ---

function safeReaddir(dir) {
  try {
    return fs.readdirSync(dir, { withFileTypes: true });
  } catch (_e) {
    return [];
  }
}

function isMd(name) {
  return name.toLowerCase().endsWith('.md');
}
function isGMd(name) {
  return name.toLowerCase().endsWith('.g.md');
}

const NOTE_TITLE_READ_BYTES = 16 * 1024;

function getShowNoteTitleFromContent() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  return config.get('showNoteTitleFromContent', true) !== false;
}

function getShowNoteFileNameBesideTitle() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  return config.get('showNoteFileNameBesideTitle', true) !== false;
}

function getSortDateNamesNewestFirst() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  return config.get('sortDateNamesNewestFirst', true) !== false;
}

/**
 * @param {string} filePath
 */
function noteStemFromPath(filePath) {
  return noteMeta.noteStemFromName(filePath);
}

/**
 * Whether `value` is a short emoji/symbol suitable as a note tree icon (not a path/URL).
 * @param {string} value
 */
function isNoteTreeEmojiIcon(value) {
  return noteMeta.isNoteTreeEmojiIcon(value);
}

/**
 * Folder/note icon set — aligned with Android `NotesIconStyle`.
 * @returns {'harrix' | 'material'}
 */
function getNotesIconStyle() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  const raw = String(config.get('iconStyle') || 'harrix')
    .trim()
    .toLowerCase();
  return raw === 'material' ? 'material' : 'harrix';
}

/**
 * Bundled Harrix Vector Icons (same assets as Harrix Notes Android).
 * @param {'folder' | 'note'} kind
 * @param {boolean} [muted]
 * @returns {vscode.Uri}
 */
function harrixIconUri(kind, muted = false) {
  const fileName = kind === 'folder' ? 'it__folder_01.svg' : 'it__file-text_01.svg';
  const iconPath = path.join(__dirname, 'media', 'icons', fileName);
  if (!muted) {
    return vscode.Uri.file(iconPath);
  }
  try {
    const svg = fs.readFileSync(iconPath, 'utf8').replace('<svg ', '<svg opacity="0.45" ');
    return vscode.Uri.parse(`data:image/svg+xml;base64,${Buffer.from(svg, 'utf8').toString('base64')}`);
  } catch {
    return vscode.Uri.file(iconPath);
  }
}

/**
 * Build a TreeItem icon from an emoji / short symbol (data-URI SVG).
 * @param {string} emoji
 * @returns {vscode.Uri | undefined}
 */
function noteIconPathFromEmoji(emoji, muted = false) {
  const text = String(emoji ?? '').trim();
  if (!text || !isNoteTreeEmojiIcon(text)) {
    return undefined;
  }
  const escaped = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const opacity = muted ? ' opacity="0.45"' : '';
  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"${opacity}>` +
    `<text x="8" y="12.5" text-anchor="middle" font-size="13">${escaped}</text></svg>`;
  return vscode.Uri.parse(`data:image/svg+xml;base64,${Buffer.from(svg, 'utf8').toString('base64')}`);
}

/**
 * @param {string} text
 * @returns {{ title: string, icon: string }}
 */
function extractNoteMetaFromMarkdown(text) {
  return noteMeta.extractNoteMetaFromMarkdown(text);
}

/** Caches note tree labels/icons by file path and mtime. Content is read off the tree UI thread. */
class NoteTitleCache {
  constructor() {
    /** @type {Map<string, { mtimeMs: number, label: string, icon: string, resolved: boolean }>} */
    this._entries = new Map();
    /** @type {Set<string>} */
    this._inflight = new Set();
  }

  clear() {
    this._entries.clear();
    this._inflight.clear();
  }

  /**
   * Fast path for the tree: cached content title when fresh, otherwise file stem.
   * Never opens the note file.
   * @param {string} filePath
   */
  getLabelFast(filePath) {
    const key = normalizeFsPath(filePath);
    const stem = noteStemFromPath(filePath);
    let mtimeMs = 0;
    try {
      mtimeMs = fs.statSync(filePath).mtimeMs;
    } catch {
      return stem;
    }
    const cached = this._entries.get(key);
    if (cached && cached.mtimeMs === mtimeMs && cached.resolved) {
      return cached.label;
    }
    return stem;
  }

  /**
   * Fast path for YAML `icon:` when already resolved; otherwise `''` (default markdown icon).
   * @param {string} filePath
   */
  getIconFast(filePath) {
    const key = normalizeFsPath(filePath);
    let mtimeMs = 0;
    try {
      mtimeMs = fs.statSync(filePath).mtimeMs;
    } catch {
      return '';
    }
    const cached = this._entries.get(key);
    if (cached && cached.mtimeMs === mtimeMs && cached.resolved) {
      return cached.icon || '';
    }
    return '';
  }

  /**
   * @param {string} filePath
   */
  needsResolve(filePath) {
    const key = normalizeFsPath(filePath);
    if (this._inflight.has(key)) {
      return false;
    }
    let mtimeMs = 0;
    try {
      mtimeMs = fs.statSync(filePath).mtimeMs;
    } catch {
      return false;
    }
    const cached = this._entries.get(key);
    return !(cached && cached.mtimeMs === mtimeMs && cached.resolved);
  }

  /**
   * Reads a note prefix and stores label + icon. Call from a background turn.
   * @param {string} filePath
   * @returns {{ label: string, icon: string, changed: boolean }}
   */
  resolveFromDisk(filePath) {
    const key = normalizeFsPath(filePath);
    const stem = noteStemFromPath(filePath);
    const beforeLabel = this.getLabelFast(filePath);
    const beforeIcon = this.getIconFast(filePath);
    let mtimeMs = 0;
    try {
      mtimeMs = fs.statSync(filePath).mtimeMs;
    } catch {
      this._entries.set(key, { mtimeMs: 0, label: stem, icon: '', resolved: true });
      return {
        label: stem,
        icon: '',
        changed: beforeLabel !== stem || beforeIcon !== '',
      };
    }

    let label = stem;
    let icon = '';
    try {
      const fd = fs.openSync(filePath, 'r');
      const buf = Buffer.alloc(NOTE_TITLE_READ_BYTES);
      const read = fs.readSync(fd, buf, 0, NOTE_TITLE_READ_BYTES, 0);
      fs.closeSync(fd);
      const text = buf.slice(0, read).toString('utf8');
      const meta = extractNoteMetaFromMarkdown(text);
      label = noteMeta.resolveNoteTitle(text, { fileStem: stem });
      if (meta.icon) {
        icon = meta.icon;
      }
    } catch {
      // keep stem / empty icon
    }

    this._entries.set(key, { mtimeMs, label, icon, resolved: true });
    const titlesOn = getShowNoteTitleFromContent();
    const displayBefore = titlesOn ? beforeLabel : stem;
    const displayAfter = titlesOn ? label : stem;
    return {
      label,
      icon,
      changed: displayBefore !== displayAfter || icon !== beforeIcon,
    };
  }

  /**
   * @param {string} filePath
   */
  markInflight(filePath) {
    this._inflight.add(normalizeFsPath(filePath));
  }

  /**
   * @param {string} filePath
   */
  clearInflight(filePath) {
    this._inflight.delete(normalizeFsPath(filePath));
  }
}

const noteTitleCache = new NoteTitleCache();

/**
 * @param {string} filePath
 */
function getNoteDisplayLabel(filePath) {
  if (!getShowNoteTitleFromContent()) {
    return noteStemFromPath(filePath);
  }
  return noteTitleCache.getLabelFast(filePath);
}

/** Merged-folder template only: exactly `_<parentFolderName>.g.md` (case-insensitive). Other `*.g.md` stay visible. */
function isMergedTemplateGmd(fileName, parentFolderBasename) {
  if (!isGMd(fileName)) return false;
  const expected = `_${parentFolderBasename}.g.md`.toLowerCase();
  return fileName.toLowerCase() === expected;
}

const DEFAULT_ASSET_FOLDER_NAMES = ['images', 'files', 'img', 'assets', 'attachments', 'media'];

function getAssetFolderNames() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  const raw = config.get('assetFolderNames', DEFAULT_ASSET_FOLDER_NAMES);
  if (!Array.isArray(raw) || raw.length === 0) {
    return new Set(DEFAULT_ASSET_FOLDER_NAMES.map((x) => x.toLowerCase()));
  }
  return new Set(raw.map((x) => String(x).trim().toLowerCase()).filter(Boolean));
}

function isAssetFolderName(name) {
  return getAssetFolderNames().has(String(name).toLowerCase());
}

/** `featured-image.png`, `featured_image.jpg`, etc. */
function isFeaturedImageFileName(name) {
  const ext = path.extname(name);
  const base = name.slice(0, name.length - ext.length).toLowerCase();
  return base === 'featured-image' || base === 'featured_image';
}

/**
 * Folder shown as a single note item (`Folder/Folder.md` with no visible subfolders).
 * @param {string} filePath absolute path to the .md file
 */
function isCollapsedFolderNote(filePath) {
  const noteDir = path.dirname(filePath);
  const folderName = path.basename(noteDir);
  const sameNameMdPath = path.join(noteDir, `${folderName}.md`);
  if (normalizeFsPath(sameNameMdPath) !== normalizeFsPath(filePath)) {
    return false;
  }
  const sub = safeReaddir(noteDir);
  const subVisibleMd = sub.filter((e) => e.isFile() && isMd(e.name) && !isMergedTemplateGmd(e.name, folderName));
  const subFolders = sub.filter(
    (e) =>
      e.isDirectory() &&
      (hasMarkdownRecursive(path.join(noteDir, e.name)) || harrixCli.isSpecialNotesFolderName(e.name)),
  );
  return subVisibleMd.length === 1 && subFolders.length === 0;
}

/**
 * Parent folder that actually contains this note in the Harrix Notes (HSK) tree.
 * @param {string} filePath
 */
function getNoteTreeParentDir(filePath) {
  if (isCollapsedFolderNote(filePath)) {
    return path.dirname(path.dirname(filePath));
  }
  return path.dirname(filePath);
}

/** @param {string} noteDir */
function noteDirHasAttachments(noteDir) {
  const drop = getNoteDropSettings();
  for (const entry of safeReaddir(noteDir)) {
    if (entry.isFile() && isFeaturedImageFileName(entry.name)) {
      return true;
    }
    if (entry.isDirectory()) {
      const lower = entry.name.toLowerCase();
      if (
        isAssetFolderName(entry.name) ||
        lower === drop.imagesFolderName.toLowerCase() ||
        lower === drop.filesFolderName.toLowerCase()
      ) {
        return true;
      }
    }
  }
  return false;
}

/**
 * @param {vscode.DataTransfer} dataTransfer
 * @returns {Promise<vscode.Uri[]>}
 */
async function readDroppedFileUris(dataTransfer) {
  /** @type {vscode.Uri[]} */
  const uris = [];
  const seen = new Set();

  const addUri = (uri) => {
    if (uri.scheme !== 'file') {
      return;
    }
    const key = normalizeFsPath(uri.fsPath);
    if (seen.has(key)) {
      return;
    }
    seen.add(key);
    uris.push(uri);
  };

  const uriList = dataTransfer.get('text/uri-list') ?? dataTransfer.get('application/vnd.code.uri-list');
  if (uriList) {
    const raw = await uriList.asString();
    for (const line of raw.split(/\r?\n/)) {
      const trimmed = line.trim();
      if (!trimmed) {
        continue;
      }
      try {
        addUri(vscode.Uri.parse(trimmed));
      } catch {
        // skip invalid URI
      }
    }
  }

  for (const [mime, item] of dataTransfer) {
    if (mime === 'files' && typeof item.asFile === 'function') {
      const file = await item.asFile();
      if (file?.uri) {
        addUri(file.uri);
      }
      continue;
    }
    if (mime === 'text/uri-list' || mime === 'application/vnd.code.uri-list') {
      continue;
    }
    if (item.uri) {
      addUri(item.uri);
    }
  }

  return uris;
}

/**
 * Path of `toFile` relative to `fromDir`, always with `/` separators (Markdown-friendly).
 * @param {string} fromDir
 * @param {string} toFile
 */
function toMarkdownRelativePath(fromDir, toFile) {
  let rel = path.relative(fromDir, toFile);
  if (!rel) {
    rel = path.basename(toFile);
  }
  return rel.split(path.sep).join('/');
}

/** @param {string} mdPath */
function escapeMarkdownLinkPath(mdPath) {
  // biome-ignore lint/suspicious/noControlCharactersInRegex: sanitize paths that contain ASCII control chars
  if (mdPath.startsWith('<') || /\s|[\u007F\u0000-\u001f]/.test(mdPath) || /[()]/.test(mdPath)) {
    return `<${mdPath.replace(/[<>]/g, '')}>`;
  }
  return mdPath;
}

/**
 * Drop into a Markdown editor: copy into note folders when needed, then insert
 * `![](img/…)` / `` [`file`](files/…) `` relative to the target `.md`.
 * @param {NotesProvider | null | undefined} notesProvider
 */
function createMarkdownRelativeLinkDropProvider(notesProvider) {
  return {
    /**
     * @param {vscode.TextDocument} document
     * @param {vscode.Position} _position
     * @param {vscode.DataTransfer} dataTransfer
     * @param {vscode.CancellationToken} token
     */
    async provideDocumentDropEdits(document, _position, dataTransfer, token) {
      if (document.uri.scheme !== 'file' || document.languageId !== 'markdown') {
        return undefined;
      }

      const uris = await readDroppedFileUris(dataTransfer);
      if (token.isCancellationRequested || uris.length === 0) {
        return undefined;
      }

      const settings = getNoteDropSettings();
      const noteMdPath = document.uri.fsPath;
      const noteDir = path.dirname(noteMdPath);
      const { destPaths, copiedCount } = await materializeDroppedFilesForNote(noteMdPath, uris, settings);
      if (token.isCancellationRequested || destPaths.length === 0) {
        return undefined;
      }

      if (copiedCount > 0 && notesProvider) {
        if (!notesProvider.isNoteAssetsVisible(noteDir)) {
          notesProvider.setNoteAssetsVisible(noteDir, true);
        }
        notesProvider.refresh();
      }

      const insert = buildDropMarkdownInsert(destPaths, noteDir, settings);
      let imageCount = 0;
      for (const destPath of destPaths) {
        const ext = path.extname(destPath).toLowerCase();
        if (settings.imageExtensions.has(ext)) {
          imageCount += 1;
        }
      }

      const edit = new vscode.DocumentDropEdit(insert);
      edit.title =
        imageCount > 0
          ? imageCount > 1
            ? 'Insert Relative Markdown Images'
            : 'Insert Relative Markdown Image'
          : destPaths.length > 1
            ? 'Insert Relative Markdown Links'
            : 'Insert Relative Markdown Link';

      // Built-in Markdown drop yields to `markdown.link.image.attachment`, so this
      // kind wins over plain URI text and copy-into-workspace media inserts.
      if (vscode.DocumentDropOrPasteEditKind) {
        edit.kind =
          imageCount > 0
            ? vscode.DocumentDropOrPasteEditKind.Empty.append('markdown', 'link', 'image', 'attachment')
            : vscode.DocumentDropOrPasteEditKind.Empty.append('markdown', 'link', 'uri');
      }

      return edit;
    },
  };
}

/**
 * @param {import('vscode').ExtensionContext} context
 * @param {NotesProvider | null | undefined} [notesProvider]
 */
function registerMarkdownRelativeLinkDropProvider(context, notesProvider) {
  if (typeof vscode.languages.registerDocumentDropEditProvider !== 'function') {
    return;
  }
  const dropProvider = createMarkdownRelativeLinkDropProvider(notesProvider);
  const selector = { language: 'markdown', scheme: 'file' };
  const dropMimeTypes = ['text/uri-list', 'application/vnd.code.uri-list', 'files'];
  try {
    const kinds = vscode.DocumentDropOrPasteEditKind
      ? [
          vscode.DocumentDropOrPasteEditKind.Empty.append('markdown', 'link', 'image', 'attachment'),
          vscode.DocumentDropOrPasteEditKind.Empty.append('markdown', 'link', 'uri'),
        ]
      : undefined;
    context.subscriptions.push(
      vscode.languages.registerDocumentDropEditProvider(selector, dropProvider, {
        dropMimeTypes,
        providedDropEditKinds: kinds,
      }),
    );
  } catch {
    context.subscriptions.push(vscode.languages.registerDocumentDropEditProvider(selector, dropProvider));
  }
}

const DEFAULT_NOTE_DROP_IMAGE_EXTENSIONS = [
  '.jpg',
  '.jpeg',
  '.png',
  '.gif',
  '.webp',
  '.avif',
  '.bmp',
  '.svg',
  '.ico',
  '.mp4',
  '.mov',
  '.webm',
  '.mkv',
  '.m4v',
  '.ogv',
  '.mp3',
  '.wav',
  '.ogg',
  '.oga',
  '.m4a',
  '.flac',
  '.aac',
  '.opus',
];

const PREVIEW_VIDEO_EXTENSIONS = new Set(['.mp4', '.webm', '.mov', '.m4v', '.ogv', '.mkv']);
const PREVIEW_AUDIO_EXTENSIONS = new Set(['.mp3', '.wav', '.ogg', '.oga', '.m4a', '.flac', '.aac', '.opus']);

const OPEN_MEDIA_EXTERNALLY_COMMAND = 'harrixNotesExplorerHsk.openMediaExternally';

/** @type {import('node:http').Server | null} */
let openMediaHttpServer = null;
/** @type {number} */
let openMediaHttpPort = 0;
/** @type {Map<string, string>} token -> absolute fs path (avoids Unicode paths in URLs) */
const openMediaPathByToken = new Map();

/**
 * @param {string} src
 * @returns {string}
 */
function mediaExtFromSrc(src) {
  const pathOnly = String(src).split('?')[0].split('#')[0];
  const match = pathOnly.match(/(\.[a-z0-9]+)$/i);
  return match ? match[1].toLowerCase() : '';
}

/**
 * @param {string} value
 * @returns {string}
 */
function escapeHtmlAttr(value) {
  return String(value).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
}

/**
 * Try to recover an absolute path from a Markdown preview webview resource URI.
 * @param {string} src
 * @returns {string | null}
 */
function fsPathFromWebviewMediaSrc(src) {
  const raw = String(src || '').trim();
  if (!raw || /^(https?:\/\/127\.0\.0\.1|https?:\/\/localhost|data:)/i.test(raw)) {
    return null;
  }
  try {
    const uri = vscode.Uri.parse(raw);
    if (uri.scheme === 'file' && uri.fsPath) {
      return uri.fsPath;
    }
    // vscode-file://vscode-app/d:/... or similar
    if (uri.fsPath && (/^[a-zA-Z]:[\\/]/.test(uri.fsPath) || path.isAbsolute(uri.fsPath))) {
      return path.normalize(uri.fsPath);
    }
  } catch {
    // continue
  }
  try {
    const u = new URL(raw);
    let p = decodeURIComponent(u.pathname || '');
    if (process.platform === 'win32' && /^\/[a-zA-Z]:/.test(p)) {
      p = p.slice(1);
    }
    if (/^[a-zA-Z]:[\\/]/.test(p) || path.isAbsolute(p)) {
      return path.normalize(p);
    }
  } catch {
    // ignore
  }
  return null;
}

/**
 * Resolve markdown media src to an absolute local filesystem path, or null if remote/unknown.
 * @param {string} dataSrc original markdown path (`data-src`) or src
 * @param {string} webviewSrc converted preview `src`
 * @param {{ currentDocument?: vscode.Uri }} [env]
 * @returns {string | null}
 */
function resolveLocalMediaFsPath(dataSrc, webviewSrc, env) {
  let raw = String(dataSrc || '').trim();
  if (raw && !/^(https?:|data:)/i.test(raw)) {
    raw = raw.replace(/^<|>$/g, '');
    try {
      raw = decodeURIComponent(raw);
    } catch {
      // keep raw
    }
    if (!/^(https?:|data:)/i.test(raw)) {
      if (raw.startsWith('file:')) {
        try {
          return vscode.Uri.parse(raw).fsPath;
        } catch {
          // fall through
        }
      } else if (path.isAbsolute(raw) || /^[a-zA-Z]:[\\/]/.test(raw)) {
        return path.normalize(raw);
      } else {
        const doc = env?.currentDocument;
        if (doc?.scheme === 'file') {
          return path.resolve(path.dirname(doc.fsPath), raw);
        }
      }
    }
  }
  return fsPathFromWebviewMediaSrc(webviewSrc || dataSrc);
}

/**
 * Link under local media. Uses http://127.0.0.1 + opaque token (not the file path)
 * so Unicode paths are not corrupted in the URL.
 * @param {string} absFsPath
 * @returns {string}
 */
function renderOpenInSystemPlayerLink(absFsPath) {
  if (!openMediaHttpPort) {
    return '';
  }
  const token = crypto.randomBytes(16).toString('hex');
  openMediaPathByToken.set(token, absFsPath);
  while (openMediaPathByToken.size > 200) {
    const oldest = openMediaPathByToken.keys().next().value;
    openMediaPathByToken.delete(oldest);
  }
  const href = `http://127.0.0.1:${openMediaHttpPort}/open-media?t=${token}`;
  return (
    `<p class="hne-md-media-actions">` +
    `<a class="hne-md-open-external" href="${escapeHtmlAttr(href)}">Open in system player</a>` +
    `</p>\n`
  );
}

/**
 * @param {string | undefined} fsPath
 */
async function openMediaInSystemPlayer(fsPath) {
  if (!fsPath || typeof fsPath !== 'string') {
    vscode.window.showErrorMessage('Open in system player: missing file path.');
    return;
  }
  if (!pathExists(fsPath) || !isFilePath(fsPath)) {
    vscode.window.showErrorMessage(`Open in system player: file not found:\n${fsPath}`);
    return;
  }
  try {
    if (process.platform === 'win32') {
      await new Promise((resolve, reject) => {
        execFile('cmd', ['/c', 'start', '', fsPath], { windowsHide: true }, (err) => {
          if (err) {
            reject(err);
          } else {
            resolve(undefined);
          }
        });
      });
      return;
    }
    const ok = await vscode.env.openExternal(vscode.Uri.file(fsPath));
    if (!ok) {
      vscode.window.showErrorMessage(`Could not open file in system player:\n${fsPath}`);
    }
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    vscode.window.showErrorMessage(`Could not open file in system player:\n${fsPath}\n${msg}`);
  }
}

/**
 * Rewrite relative Marp image URLs to webview URIs.
 * @param {string} markdown
 * @param {import('vscode').Webview} webview
 * @param {string} noteDir
 * @returns {string}
 */
function rewriteMarpRelativeImages(markdown, webview, noteDir) {
  return String(markdown || '').replace(/!\[([^\]]*)]\(([^)]+)\)/g, (all, alt, src) => {
    const trimmed = String(src || '').trim();
    if (!trimmed || /^(https?:|data:|vscode-webview:)/i.test(trimmed)) {
      return all;
    }
    const abs = path.resolve(noteDir, trimmed);
    if (!fs.existsSync(abs)) {
      return all;
    }
    const uri = webview.asWebviewUri(vscode.Uri.file(abs)).toString();
    return `![${alt}](${uri})`;
  });
}

/**
 * Local-only helper so Markdown preview `http:` links can trigger openExternal.
 * @returns {Promise<void>}
 */
function startOpenMediaHttpServer() {
  return new Promise((resolve, reject) => {
    if (openMediaHttpServer) {
      resolve();
      return;
    }
    const server = http.createServer((req, res) => {
      try {
        const url = new URL(req.url || '/', 'http://127.0.0.1');
        if (url.pathname !== '/open-media') {
          res.writeHead(404);
          res.end();
          return;
        }
        const token = url.searchParams.get('t') || '';
        const fsPath = openMediaPathByToken.get(token) || '';
        void openMediaInSystemPlayer(fsPath);
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        res.end(
          '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Opening…</title></head>' +
            '<body><p>Opening in system player…</p>' +
            '<script>window.close();</script></body></html>',
        );
      } catch {
        res.writeHead(500);
        res.end();
      }
    });
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const addr = server.address();
      openMediaHttpPort = typeof addr === 'object' && addr ? addr.port : 0;
      openMediaHttpServer = server;
      resolve();
    });
  });
}

function stopOpenMediaHttpServer() {
  if (openMediaHttpServer) {
    openMediaHttpServer.close();
    openMediaHttpServer = null;
    openMediaHttpPort = 0;
  }
  openMediaPathByToken.clear();
}

/**
 * @param {vscode.ExtensionContext} context
 */
function registerOpenMediaExternallyCommand(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand(OPEN_MEDIA_EXTERNALLY_COMMAND, async (fsPath) => {
      await openMediaInSystemPlayer(typeof fsPath === 'string' ? fsPath : '');
    }),
  );
  context.subscriptions.push({ dispose: () => stopOpenMediaHttpServer() });
}

function getNoteDropSettings() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  const rawExt = config.get('noteDrop.imageExtensions', DEFAULT_NOTE_DROP_IMAGE_EXTENSIONS);
  const imageExtensions = new Set();
  if (Array.isArray(rawExt)) {
    for (const entry of rawExt) {
      const raw = String(entry).trim().toLowerCase();
      if (!raw) {
        continue;
      }
      imageExtensions.add(raw.startsWith('.') ? raw : `.${raw}`);
    }
  }
  if (imageExtensions.size === 0) {
    for (const ext of DEFAULT_NOTE_DROP_IMAGE_EXTENSIONS) {
      imageExtensions.add(ext);
    }
  }
  const imagesFolder = String(config.get('noteDrop.imagesFolderName', 'img') || 'img').trim() || 'img';
  const filesFolder = String(config.get('noteDrop.filesFolderName', 'files') || 'files').trim() || 'files';
  return {
    moveIntoNamedFolder: config.get('noteDrop.moveIntoNamedFolder', true) !== false,
    copyAllToNoteRoot: config.get('noteDrop.copyAllToNoteRoot', false) === true,
    imagesFolderName: sanitizeEntryName(imagesFolder) || 'img',
    filesFolderName: sanitizeEntryName(filesFolder) || 'files',
    imageExtensions,
  };
}

/**
 * @param {string} noteMdPath
 */
function isNoteInNamedFolder(noteMdPath) {
  const noteDir = path.dirname(noteMdPath);
  const stem = path.basename(noteMdPath, path.extname(noteMdPath));
  if (path.basename(noteDir).toLowerCase() !== stem.toLowerCase()) {
    return false;
  }
  const expectedMd = path.join(noteDir, `${path.basename(noteDir)}.md`);
  return normalizeFsPath(expectedMd) === normalizeFsPath(noteMdPath);
}

/**
 * @param {string} noteMdPath
 * @param {boolean} moveEnabled
 * @returns {Promise<string>} absolute path to the note .md after move
 */
async function ensureNoteInNamedFolder(noteMdPath, moveEnabled) {
  if (!moveEnabled || isNoteInNamedFolder(noteMdPath)) {
    return noteMdPath;
  }
  const stem = path.basename(noteMdPath, path.extname(noteMdPath));
  const parentDir = path.dirname(noteMdPath);
  const targetDir = path.join(parentDir, stem);
  const targetMd = path.join(targetDir, `${stem}.md`);
  if (pathExists(targetMd) && normalizeFsPath(targetMd) !== normalizeFsPath(noteMdPath)) {
    throw new Error(`Note folder already exists: ${stem}`);
  }
  fs.mkdirSync(targetDir, { recursive: true });
  await vscode.workspace.fs.rename(vscode.Uri.file(noteMdPath), vscode.Uri.file(targetMd), {
    overwrite: false,
  });
  return targetMd;
}

/**
 * Rename a note in ``Note/Note.md`` layout: folder and inner ``.md`` file together.
 * @param {string} mdPath absolute path to the note markdown file
 * @param {string} newStem new folder / file stem (no extension)
 * @returns {Promise<string>} absolute path to the renamed markdown file
 */
async function renameNamedFolderNote(mdPath, newStem) {
  const noteDir = path.dirname(mdPath);
  const grandParent = path.dirname(noteDir);
  const oldStem = path.basename(noteDir);

  if (oldStem === newStem) {
    return mdPath;
  }

  const targetFolder = path.join(grandParent, newStem);
  const targetMd = path.join(targetFolder, `${newStem}.md`);

  if (pathExists(targetFolder) && normalizeFsPath(targetFolder) !== normalizeFsPath(noteDir)) {
    throw new Error(`Target folder already exists: ${newStem}`);
  }
  if (pathExists(targetMd) && normalizeFsPath(targetMd) !== normalizeFsPath(mdPath)) {
    throw new Error(`Target note already exists: ${newStem}.md`);
  }

  await vscode.workspace.fs.rename(vscode.Uri.file(noteDir), vscode.Uri.file(targetFolder), {
    overwrite: false,
  });

  const mdAfterFolderRename = path.join(targetFolder, `${oldStem}.md`);
  if (normalizeFsPath(mdAfterFolderRename) !== normalizeFsPath(targetMd) && pathExists(mdAfterFolderRename)) {
    await vscode.workspace.fs.rename(vscode.Uri.file(mdAfterFolderRename), vscode.Uri.file(targetMd), {
      overwrite: false,
    });
  }

  return targetMd;
}

/**
 * @param {string} baseName
 * @param {ReturnType<typeof getNoteDropSettings>} settings
 * @returns {'root' | 'images' | 'files'}
 */
function classifyDroppedFile(baseName, settings) {
  if (settings.copyAllToNoteRoot) {
    return 'root';
  }
  if (isFeaturedImageFileName(baseName)) {
    return 'root';
  }
  const ext = path.extname(baseName).toLowerCase();
  if (settings.imageExtensions.has(ext)) {
    return 'images';
  }
  return 'files';
}

/**
 * @param {string} noteDir
 * @param {'root' | 'images' | 'files'} category
 * @param {ReturnType<typeof getNoteDropSettings>} settings
 */
function resolveNoteDropDestDir(noteDir, category, settings) {
  if (category === 'root') {
    return noteDir;
  }
  const folderName = category === 'images' ? settings.imagesFolderName : settings.filesFolderName;
  const destDir = path.join(noteDir, folderName);
  fs.mkdirSync(destDir, { recursive: true });
  return destDir;
}

/**
 * @param {vscode.Uri} source
 * @param {string} destPath
 */
async function copyDroppedPathOverwrite(source, destPath) {
  const srcPath = source.fsPath;
  if (isFilePath(srcPath)) {
    await vscode.workspace.fs.copy(source, vscode.Uri.file(destPath), { overwrite: true });
    return;
  }
  if (isDirectoryPath(srcPath)) {
    await vscode.workspace.fs.copy(source, vscode.Uri.file(destPath), { overwrite: true });
  }
}

/**
 * @param {string} filePath
 * @param {string} dirPath
 */
function isPathInsideDir(filePath, dirPath) {
  const fileNorm = normalizeFsPath(filePath);
  const dirNorm = normalizeFsPath(dirPath);
  if (fileNorm === dirNorm) {
    return true;
  }
  const prefix = dirNorm.endsWith(path.sep) ? dirNorm : dirNorm + path.sep;
  return fileNorm.startsWith(prefix);
}

/**
 * Destination directory path for a drop category (does not create folders).
 * @param {string} noteDir
 * @param {'root' | 'images' | 'files'} category
 * @param {ReturnType<typeof getNoteDropSettings>} settings
 */
function noteDropDestDirPath(noteDir, category, settings) {
  if (category === 'root') {
    return noteDir;
  }
  const folderName = category === 'images' ? settings.imagesFolderName : settings.filesFolderName;
  return path.join(noteDir, folderName);
}

/**
 * One Markdown image or link line (no trailing newlines).
 * @param {string} destPath absolute path of the linked file
 * @param {string} noteDir absolute note directory (parent of the `.md`)
 * @param {ReturnType<typeof getNoteDropSettings>} settings
 */
function formatDroppedMarkdownSnippet(destPath, noteDir, settings) {
  const rel = escapeMarkdownLinkPath(toMarkdownRelativePath(noteDir, destPath));
  const ext = path.extname(destPath).toLowerCase();
  if (settings.imageExtensions.has(ext)) {
    return `![](${rel})`;
  }
  return `[\`${path.basename(destPath)}\`](${rel})`;
}

/**
 * Copy dropped files into the note's img/files/root when needed.
 * @param {string} noteMdPath
 * @param {vscode.Uri[]} sourceUris
 * @param {ReturnType<typeof getNoteDropSettings>} settings
 * @returns {Promise<{ destPaths: string[], copiedCount: number }>}
 */
async function materializeDroppedFilesForNote(noteMdPath, sourceUris, settings) {
  const noteDir = path.dirname(noteMdPath);
  /** @type {string[]} */
  const destPaths = [];
  let copiedCount = 0;

  for (const source of sourceUris) {
    const srcPath = source.fsPath;
    if (!isFilePath(srcPath)) {
      continue;
    }
    const baseName = path.basename(srcPath);
    if (!baseName) {
      continue;
    }
    const category = classifyDroppedFile(baseName, settings);
    const destDir = noteDropDestDirPath(noteDir, category, settings);
    if (isPathInsideDir(srcPath, destDir)) {
      destPaths.push(srcPath);
      continue;
    }
    try {
      const resolvedDestDir = resolveNoteDropDestDir(noteDir, category, settings);
      const destPath = path.join(resolvedDestDir, baseName);
      if (normalizeFsPath(srcPath) !== normalizeFsPath(destPath)) {
        await copyDroppedPathOverwrite(source, destPath);
        copiedCount += 1;
      }
      destPaths.push(destPath);
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      void vscode.window.showErrorMessage(`Could not copy "${baseName}": ${msg}`);
    }
  }

  return { destPaths, copiedCount };
}

/**
 * @param {string[]} destPaths
 * @param {string} noteDir
 * @param {ReturnType<typeof getNoteDropSettings>} settings
 */
function buildDropMarkdownInsert(destPaths, noteDir, settings) {
  if (destPaths.length === 0) {
    return '';
  }
  const snippets = destPaths.map((p) => formatDroppedMarkdownSnippet(p, noteDir, settings));
  return snippets.join('\n');
}

/**
 * Persists note folders whose attachments are shown in the tree.
 */
class NoteAssetsVisibility {
  /**
   * @param {vscode.ExtensionContext} context
   */
  constructor(context) {
    this._context = context;
    this._key = 'harrixNotesExplorerHsk.noteAssetsVisible.v1';
    const stored = context.workspaceState.get(this._key);
    this.visible = new Set(Array.isArray(stored) ? stored.map((x) => normalizeFsPath(String(x))) : []);
  }

  /** @param {string} noteDir */
  isVisible(noteDir) {
    return this.visible.has(normalizeFsPath(noteDir));
  }

  /**
   * @param {string} noteDir
   * @param {boolean} visible
   */
  setVisible(noteDir, visible) {
    const key = normalizeFsPath(noteDir);
    if (visible) {
      this.visible.add(key);
    } else {
      this.visible.delete(key);
    }
    void this._context.workspaceState.update(this._key, Array.from(this.visible));
  }

  /** Hide attachments for every note and persist the empty set. */
  clearAll() {
    if (this.visible.size === 0) {
      return false;
    }
    this.visible.clear();
    void this._context.workspaceState.update(this._key, []);
    return true;
  }
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
  try {
    fs.accessSync(fsPath);
    return true;
  } catch {
    return false;
  }
}

function isDirectoryPath(fsPath) {
  try {
    return fs.statSync(fsPath).isDirectory();
  } catch {
    return false;
  }
}

function isFilePath(fsPath) {
  try {
    return fs.statSync(fsPath).isFile();
  } catch {
    return false;
  }
}

/**
 * Folder path for folder-level commands: directory as-is, or parent of Note/Note.md.
 * @param {unknown} uri
 * @returns {string | undefined}
 */
function resolveNotesFolderFsPath(uri) {
  const fsPath = uriToFsPath(uri);
  if (!fsPath) {
    return undefined;
  }
  if (isDirectoryPath(fsPath)) {
    return fsPath;
  }
  if (isFilePath(fsPath) && isMd(path.basename(fsPath)) && isNoteInNamedFolder(fsPath)) {
    return path.dirname(fsPath);
  }
  return undefined;
}

/** @param {unknown} treeItemOrUri */
function uriFromTreeArgOrActiveEditor(treeItemOrUri) {
  const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
  if (itemUri instanceof vscode.Uri) {
    return itemUri;
  }
  return vscode.window.activeTextEditor?.document?.uri;
}

/** @param {unknown} treeItemOrUri */
function noteUriFromTreeArg(treeItemOrUri) {
  const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
  if (itemUri instanceof vscode.Uri) {
    return itemUri;
  }
  const activeUri = vscode.window.activeTextEditor?.document?.uri;
  if (activeUri?.scheme === 'file' && isMd(path.basename(activeUri.fsPath))) {
    return activeUri;
  }
  return undefined;
}

/** @param {unknown} treeItemOrUri */
function noteDirFromTreeArg(treeItemOrUri) {
  const uri = noteUriFromTreeArg(treeItemOrUri);
  if (!uri || !isFilePath(uri.fsPath)) {
    return undefined;
  }
  return path.dirname(uri.fsPath);
}

/**
 * Folder URI for tree commands that operate on a note's directory or a folder item.
 * @param {unknown} treeItemOrUri
 * @returns {vscode.Uri | undefined}
 */
function folderUriFromTreeArg(treeItemOrUri) {
  const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
  if (itemUri instanceof vscode.Uri && itemUri.scheme === 'file') {
    const fsPath = itemUri.fsPath;
    if (isDirectoryPath(fsPath)) {
      return itemUri;
    }
    if (isFilePath(fsPath)) {
      return vscode.Uri.file(path.dirname(fsPath));
    }
  }
  const activeUri = vscode.window.activeTextEditor?.document?.uri;
  if (activeUri?.scheme === 'file' && isFilePath(activeUri.fsPath)) {
    return vscode.Uri.file(path.dirname(activeUri.fsPath));
  }
  return undefined;
}

/**
 * Opens VS Code integrated terminal at the given folder (not an external terminal app).
 * @param {vscode.Uri} folderUri
 */
function openFolderInIntegratedTerminal(folderUri) {
  const terminal = vscode.window.createTerminal({
    cwd: folderUri,
    name: path.basename(folderUri.fsPath) || undefined,
  });
  terminal.show();
}

/**
 * @param {string} raw
 */
function sanitizeEntryName(raw) {
  const name = String(raw ?? '')
    .trim()
    // biome-ignore lint/suspicious/noControlCharactersInRegex: strip Windows-illegal and control chars from names
    .replace(/[<>:"/\\|?*\u0000-\u001f]/g, '_')
    .trim();
  if (!name || name === '.' || name === '..') {
    return '';
  }
  return name;
}

/**
 * @param {number} viewColumn
 */
async function focusEditorGroupByViewColumn(viewColumn) {
  if (viewColumn === vscode.ViewColumn.One || viewColumn === 1) {
    await vscode.commands.executeCommand('workbench.action.focusFirstEditorGroup');
    return;
  }
  if (viewColumn === vscode.ViewColumn.Two || viewColumn === 2) {
    await vscode.commands.executeCommand('workbench.action.focusSecondEditorGroup');
    return;
  }
  if (viewColumn === vscode.ViewColumn.Three || viewColumn === 3) {
    await vscode.commands.executeCommand('workbench.action.focusThirdEditorGroup');
  }
}

/**
 * Closes every tab in editor groups to the right of the leftmost group.
 * Used when leaving split (editor left, preview right) on a simple note click.
 */
async function closeTabsInRightSplitGroups() {
  const closeRightGroupsWithCommands = async () => {
    let groups = vscode.window.tabGroups.all;
    let guard = 0;
    while (groups.length > 1 && guard < 10) {
      guard += 1;
      const minColumn = Math.min(...groups.map((g) => g.viewColumn ?? vscode.ViewColumn.One));
      const rightGroup = groups.find((g) => (g.viewColumn ?? vscode.ViewColumn.One) > minColumn);
      if (!rightGroup) {
        break;
      }
      await focusEditorGroupByViewColumn(rightGroup.viewColumn ?? vscode.ViewColumn.Two);
      await vscode.commands.executeCommand('workbench.action.closeEditorsInGroup');
      groups = vscode.window.tabGroups.all;
    }
  };

  const groups = vscode.window.tabGroups.all;
  if (groups.length <= 1) {
    return;
  }

  const columns = groups.map((g) => g.viewColumn ?? vscode.ViewColumn.One);
  const minColumn = Math.min(...columns);

  if (vscode.window.tabGroups?.close) {
    for (const group of groups) {
      const col = group.viewColumn ?? vscode.ViewColumn.One;
      if (col <= minColumn) {
        continue;
      }
      for (const tab of [...group.tabs]) {
        try {
          await vscode.window.tabGroups.close(tab);
        } catch {
          // ignore
        }
      }
    }
    if (vscode.window.tabGroups.all.length > 1) {
      await closeRightGroupsWithCommands();
    }
    return;
  }

  await closeRightGroupsWithCommands();
}

/**
 * @param {number} maxColumnToKeep
 */
async function closeEditorGroupsRightOfColumn(maxColumnToKeep) {
  const groups = vscode.window.tabGroups.all;
  for (const group of groups) {
    const col = group.viewColumn ?? vscode.ViewColumn.One;
    if (col <= maxColumnToKeep) {
      continue;
    }
    if (vscode.window.tabGroups?.close) {
      for (const tab of [...group.tabs]) {
        try {
          await vscode.window.tabGroups.close(tab);
        } catch {
          // ignore
        }
      }
    }
  }

  let remaining = vscode.window.tabGroups.all;
  let guard = 0;
  while (remaining.some((g) => (g.viewColumn ?? vscode.ViewColumn.One) > maxColumnToKeep) && guard < 10) {
    guard += 1;
    const overflow = remaining.find((g) => (g.viewColumn ?? vscode.ViewColumn.One) > maxColumnToKeep);
    if (!overflow) {
      break;
    }
    await focusEditorGroupByViewColumn(overflow.viewColumn ?? vscode.ViewColumn.Three);
    await vscode.commands.executeCommand('workbench.action.closeEditorsInGroup');
    remaining = vscode.window.tabGroups.all;
  }
}

/**
 * Closes all non-text editor tabs in the given column (preview, webview, custom editors).
 * @param {number} viewColumn
 */
async function closeNonTextTabsInColumn(viewColumn) {
  if (!vscode.window.tabGroups?.close) {
    return;
  }
  const group = vscode.window.tabGroups.all.find((g) => (g.viewColumn ?? vscode.ViewColumn.One) === viewColumn);
  if (!group) {
    return;
  }
  for (const tab of [...group.tabs]) {
    const input = tab.input;
    if (input instanceof vscode.TabInputText) {
      continue;
    }
    try {
      await vscode.window.tabGroups.close(tab);
    } catch {
      // ignore
    }
  }
}

/** @param {number} ms */
function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * After opening preview on the right, VS Code may add/sync a preview tab in the left group.
 * Keep only the text editor active in column 1.
 * @param {vscode.Uri} uri
 */
async function focusSourceEditorInLeftColumn(uri) {
  const leftColumn = vscode.ViewColumn.One;

  // VS Code spawns the duplicate preview tab asynchronously, so retry several times.
  for (let i = 0; i < 8; i++) {
    await closeNonTextTabsInColumn(leftColumn);
    await delay(100);
  }

  await focusEditorGroupByViewColumn(leftColumn);
  try {
    await vscode.window.showTextDocument(uri, {
      viewColumn: leftColumn,
      preview: false,
      preserveFocus: false,
    });
  } catch {
    // ignore
  }
}

/**
 * @param {vscode.Uri} uri
 * @param {'editorLeft' | 'previewLeft'} layout
 */
async function openHarrixNoteSplit(uri, layout) {
  const leftColumn = vscode.ViewColumn.One;
  const rightColumn = vscode.ViewColumn.Two;

  const openSourceInColumn = async (viewColumn) => {
    try {
      await vscode.window.showTextDocument(uri, {
        viewColumn,
        preview: false,
        preserveFocus: false,
      });
    } catch {
      await vscode.commands.executeCommand('vscode.open', uri);
    }
  };

  const openPreviewLockedInActiveColumn = async () => {
    try {
      await vscode.commands.executeCommand('markdown.showPreview', uri, undefined, { locked: true });
      return true;
    } catch {
      return false;
    }
  };

  const openPreviewToSide = async () => {
    try {
      await vscode.commands.executeCommand('markdown.showPreviewToSide', uri);
      return true;
    } catch {
      try {
        await vscode.commands.executeCommand('markdown.showPreview', uri, undefined, { locked: true });
        return true;
      } catch {
        return false;
      }
    }
  };

  // Never accumulate a third+ editor column when opening split repeatedly.
  await closeEditorGroupsRightOfColumn(2);

  if (layout === 'editorLeft') {
    await closeNonTextTabsInColumn(rightColumn);
    await focusEditorGroupByViewColumn(leftColumn);
    await openSourceInColumn(leftColumn);
    await openPreviewToSide();
    await focusSourceEditorInLeftColumn(uri);
    return;
  }

  // previewLeft: preview in column 1, source in column 2
  await closeNonTextTabsInColumn(leftColumn);
  await focusEditorGroupByViewColumn(leftColumn);
  await openPreviewLockedInActiveColumn();
  await openSourceInColumn(vscode.ViewColumn.Beside);
}

function getOpenInSplit() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');

  const unified = config.get('openInSplit');
  if (typeof unified === 'boolean') {
    return unified;
  }

  // Backward compatibility for older settings.
  const legacyEditor = config.get('openInEditorSplit');
  if (typeof legacyEditor === 'boolean') {
    return legacyEditor;
  }
  const legacyPreview = config.get('openInPreviewSplit');
  if (typeof legacyPreview === 'boolean') {
    return legacyPreview;
  }

  return true;
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
    const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
    usePreview = config.get('openNotesInPreview') !== false;
  }

  const openSource = async (viewColumn = vscode.ViewColumn.Active) => {
    try {
      await vscode.window.showTextDocument(uri, {
        viewColumn,
        preview: false,
        preserveFocus: false,
      });
    } catch {
      await vscode.commands.executeCommand('vscode.open', uri);
    }
  };

  const openPreviewOnly = async () => {
    try {
      await vscode.commands.executeCommand('markdown.showPreview', uri, undefined, { locked: true });
    } catch {
      await openSource(vscode.ViewColumn.Active);
    }
  };

  if (mode === 'editor') {
    if (getOpenInSplit()) {
      await openHarrixNoteSplit(uri, 'editorLeft');
    } else {
      await openSource(vscode.ViewColumn.Active);
    }
    return;
  }

  if (mode === 'preview') {
    if (getOpenInSplit()) {
      await openHarrixNoteSplit(uri, 'previewLeft');
    } else {
      await openPreviewOnly();
    }
    return;
  }

  // Simple tree click: close the right split pane (preview), keep left editor tabs.
  await closeTabsInRightSplitGroups();
  try {
    await vscode.commands.executeCommand('workbench.action.focusFirstEditorGroup');
  } catch {
    // ignore
  }

  if (usePreview) {
    try {
      await vscode.commands.executeCommand('markdown.showPreview', uri, vscode.ViewColumn.One, {
        locked: true,
      });
    } catch {
      await openSource(vscode.ViewColumn.One);
    }
  } else {
    await openSource(vscode.ViewColumn.Active);
  }
}

/** Directories skipped while scanning for .md (nested repos / tool caches). */
const SKIP_MARKDOWN_SCAN_DIR_NAMES = new Set([
  '.git',
  '.hg',
  '.svn',
  '.ruff_cache',
  '.venv',
  'venv',
  'node_modules',
  '__pycache__',
]);

/**
 * True if `dir` has a `.git` file or directory (work tree or linked worktree).
 * @param {string} dir
 */
function pathHasGitMeta(dir) {
  try {
    const st = fs.statSync(path.join(dir, '.git'));
    return st.isDirectory() || st.isFile();
  } catch {
    return false;
  }
}

/**
 * Walk parents for a `.git` meta entry (no `git` subprocess — fast under large folders).
 * @param {string} folderPath
 */
function isInsideGitWorkTreeFs(folderPath) {
  let cur = path.resolve(folderPath);
  for (;;) {
    if (pathHasGitMeta(cur)) {
      return true;
    }
    const parent = path.dirname(cur);
    if (parent === cur) {
      return false;
    }
    cur = parent;
  }
}

// Folder is listable when it has a `.md` note or a descendant folder that does
// (`@hsk-sync:notes-browse`, same idea as Android `directoryHasMarkdownNotes`).
function hasMarkdownRecursive(dir, depth = 0) {
  if (depth > 16) {
    return false;
  }
  const entries = safeReaddir(dir);
  for (const entry of entries) {
    if (entry.isFile() && isMd(entry.name)) {
      return true;
    }
  }
  for (const entry of entries) {
    if (entry.isDirectory() && !SKIP_MARKDOWN_SCAN_DIR_NAMES.has(entry.name.toLowerCase())) {
      if (hasMarkdownRecursive(path.join(dir, entry.name), depth + 1)) {
        return true;
      }
    }
  }
  return false;
}

/**
 * Shared listing rules for the notes tree and Icons Browse panel.
 * Folders + `.md` only (attachments omitted); collapses `Folder/Folder.md` when alone.
 *
 * @param {string} dir
 * @param {{ templateCountFor?: (folderPath: string) => number }} [opts]
 * @returns {Array<{ kind: 'folder' | 'note', path: string, name: string }>}
 */
function collectNotesDirChildSpecs(dir, opts) {
  const templateCountFor = opts?.templateCountFor || (() => 0);
  if (!dir || !fs.existsSync(dir)) {
    return [];
  }

  const entries = safeReaddir(dir);
  const folders = entries
    .filter((e) => e.isDirectory())
    .filter(
      (e) =>
        hasMarkdownRecursive(path.join(dir, e.name)) ||
        harrixCli.folderListedWithoutMarkdown(e.name, templateCountFor(path.join(dir, e.name))),
    );

  const hereName = path.basename(dir);
  const mdFiles = entries.filter((e) => e.isFile() && isMd(e.name) && !isMergedTemplateGmd(e.name, hereName));

  /** @type {Array<{ kind: 'folder' | 'note', path: string, name: string }>} */
  const specs = [];

  for (const folder of folders) {
    const folderPath = path.join(dir, folder.name);
    const sub = safeReaddir(folderPath);
    const subVisibleMd = sub.filter((e) => e.isFile() && isMd(e.name) && !isMergedTemplateGmd(e.name, folder.name));
    const subFolders = sub
      .filter((e) => e.isDirectory())
      .filter(
        (e) =>
          (!SKIP_MARKDOWN_SCAN_DIR_NAMES.has(e.name.toLowerCase()) &&
            hasMarkdownRecursive(path.join(folderPath, e.name))) ||
          harrixCli.isSpecialNotesFolderName(e.name),
      );

    const sameNameMdPath = path.join(folderPath, `${folder.name}.md`);
    const hasSameNameMd = fs.existsSync(sameNameMdPath);

    if (hasSameNameMd && subVisibleMd.length === 1 && subFolders.length === 0) {
      specs.push({ kind: 'note', path: sameNameMdPath, name: folder.name });
    } else {
      specs.push({ kind: 'folder', path: folderPath, name: folder.name });
    }
  }

  for (const file of mdFiles) {
    specs.push({ kind: 'note', path: path.join(dir, file.name), name: noteStemFromPath(file.name) });
  }

  return specs;
}

// --- TreeDataProvider ---

/**
 * @typedef {{ path: string, name: string }} WorkspaceRootEntry
 */

class NotesProvider {
  /**
   * @param {WorkspaceRootEntry[]} rootEntries
   * @param {FolderExpansionMemory | null} expansionMemory
   * @param {NoteAssetsVisibility | null} assetsVisibility
   */
  constructor(rootEntries, expansionMemory, assetsVisibility) {
    /** @type {WorkspaceRootEntry[]} */
    this.rootEntries = Array.isArray(rootEntries) ? rootEntries.slice() : [];
    /** @type {FolderExpansionMemory | null} */
    this._expansion = expansionMemory;
    /** @type {NoteAssetsVisibility | null} */
    this._assetsVisibility = assetsVisibility;
    this._emitter = new vscode.EventEmitter();
    this.onDidChangeTreeData = this._emitter.event;
    /** @type {Set<string>} resolved fs paths */
    this._busyFolderPaths = new Set();
    /** @type {Map<string, Array<{id: string, title: string}>>} CLI template targets — see harrix-cli.js */
    this._templateTargets = new Map();
    /** @type {Map<string, boolean>} normalized folder path -> inside git work tree */
    this._gitWorkTreeCache = new Map();
    /** @type {Set<string>} note paths waiting for background title resolve */
    this._titleResolveQueued = new Set();
    /** @type {Set<string>} parent dirs that need a delayed re-sort after title updates */
    this._titleResolveParentsPendingSort = new Set();
    /** @type {ReturnType<typeof setTimeout> | null} */
    this._titleResolveTimer = null;
    /** @type {ReturnType<typeof setTimeout> | null} */
    this._titleResolveParentSortTimer = null;
    /** True when a resolved title differs from the label already shown */
    this._titleResolveDirty = false;
  }

  /** First workspace folder path (fallback for commands with no selection). */
  get rootPath() {
    return this.rootEntries[0]?.path;
  }

  /**
   * @param {WorkspaceRootEntry[]} rootEntries
   */
  setRootEntries(rootEntries) {
    this.rootEntries = Array.isArray(rootEntries) ? rootEntries.slice() : [];
    this.refresh();
  }

  /**
   * Longest matching workspace root that contains `fsPath`, or `undefined`.
   * @param {string} fsPath
   * @returns {WorkspaceRootEntry | undefined}
   */
  findRootForPath(fsPath) {
    const norm = normalizeFsPath(fsPath);
    /** @type {WorkspaceRootEntry | undefined} */
    let best;
    let bestLen = -1;
    for (const entry of this.rootEntries) {
      const rootNorm = normalizeFsPath(entry.path);
      if (norm === rootNorm || norm.startsWith(rootNorm + path.sep)) {
        if (rootNorm.length > bestLen) {
          best = entry;
          bestLen = rootNorm.length;
        }
      }
    }
    return best;
  }

  /**
   * @param {string} fsPath
   * @returns {boolean}
   */
  isWorkspaceRootPath(fsPath) {
    const norm = normalizeFsPath(fsPath);
    return this.rootEntries.some((entry) => normalizeFsPath(entry.path) === norm);
  }

  refresh() {
    this._gitWorkTreeCache.clear();
    noteTitleCache.clear();
    this._titleResolveQueued.clear();
    this._titleResolveParentsPendingSort.clear();
    this._titleResolveDirty = false;
    if (this._titleResolveTimer != null) {
      clearTimeout(this._titleResolveTimer);
      this._titleResolveTimer = null;
    }
    if (this._titleResolveParentSortTimer != null) {
      clearTimeout(this._titleResolveParentSortTimer);
      this._titleResolveParentSortTimer = null;
    }
    this._emitter.fire();
  }

  /**
   * Queue content reads (YAML title + icon) after the tree has already painted.
   * Titles apply only when the setting is on; icons always apply once resolved.
   * @param {string[]} filePaths
   * @param {string | undefined} parentDir
   */
  scheduleNoteTitleResolve(filePaths, parentDir) {
    if (!Array.isArray(filePaths) || filePaths.length === 0) {
      return;
    }
    let queuedAny = false;
    for (const filePath of filePaths) {
      if (noteTitleCache.needsResolve(filePath)) {
        this._titleResolveQueued.add(normalizeFsPath(filePath));
        queuedAny = true;
      }
    }
    // Only remember the parent when something will actually resolve — otherwise
    // stale parents accumulate and refresh the wrong root mid-expand.
    if (queuedAny && typeof parentDir === 'string' && parentDir) {
      this._titleResolveParentsPendingSort.add(normalizeFsPath(parentDir));
    }
    this._kickTitleResolve();
  }

  _kickTitleResolve() {
    if (this._titleResolveTimer != null || this._titleResolveQueued.size === 0) {
      return;
    }
    this._titleResolveTimer = setTimeout(() => {
      this._titleResolveTimer = null;
      this._runTitleResolveBatch();
    }, 0);
  }

  _runTitleResolveBatch() {
    const batch = [...this._titleResolveQueued].slice(0, 12);
    for (const filePath of batch) {
      this._titleResolveQueued.delete(filePath);
    }
    /** @type {string[]} */
    const changedNotes = [];
    for (const filePath of batch) {
      noteTitleCache.markInflight(filePath);
      try {
        const { changed } = noteTitleCache.resolveFromDisk(filePath);
        if (changed) {
          this._titleResolveDirty = true;
          changedNotes.push(filePath);
        }
      } finally {
        noteTitleCache.clearInflight(filePath);
      }
    }

    // Update leaf labels immediately without re-listing parent folders (avoids
    // VS Code AsyncDataTree races when another workspace root is expanding).
    for (const filePath of changedNotes) {
      this._emitter.fire(this.createFileItem(filePath));
      this._titleResolveParentsPendingSort.add(normalizeFsPath(getNoteTreeParentDir(filePath)));
    }

    if (this._titleResolveQueued.size > 0) {
      this._kickTitleResolve();
      return;
    }

    if (!this._titleResolveDirty) {
      this._titleResolveParentsPendingSort.clear();
      return;
    }
    this._titleResolveDirty = false;
    this._scheduleParentSortRefresh();
  }

  /**
   * Debounce parent re-list so label-based sort can update after expand settles.
   * Firing parents immediately races concurrent getChildren for other roots.
   */
  _scheduleParentSortRefresh() {
    if (this._titleResolveParentSortTimer != null) {
      clearTimeout(this._titleResolveParentSortTimer);
    }
    this._titleResolveParentSortTimer = setTimeout(() => {
      this._titleResolveParentSortTimer = null;
      const parents = [...this._titleResolveParentsPendingSort];
      this._titleResolveParentsPendingSort.clear();
      for (const parentDir of parents) {
        this._fireFolderForTitleRefresh(parentDir);
      }
    }, 300);
  }

  /**
   * @param {string} parentDir
   */
  _fireFolderForTitleRefresh(parentDir) {
    if (this.isWorkspaceRootPath(parentDir)) {
      const entry = this.findRootForPath(parentDir);
      this._emitter.fire(this.createWorkspaceRootFolderItem(parentDir, entry?.name));
      return;
    }
    this._emitter.fire(this.createFolderItem(parentDir, path.basename(parentDir), this.folderDepthForPath(parentDir)));
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
    const inside = isInsideGitWorkTreeFs(folderPath);
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

  /** @param {string} noteDir */
  isNoteAssetsVisible(noteDir) {
    return this._assetsVisibility?.isVisible(noteDir);
  }

  /**
   * @param {string} noteDir
   * @param {boolean} visible
   */
  setNoteAssetsVisible(noteDir, visible) {
    if (this._assetsVisibility == null) {
      return;
    }
    this._assetsVisibility.setVisible(noteDir, visible);
    this._emitter.fire();
  }

  /** Hide attachments under every note. @returns {boolean} whether anything changed */
  hideAllNoteAssets() {
    if (this._assetsVisibility == null) {
      return false;
    }
    const changed = this._assetsVisibility.clearAll();
    if (changed) {
      this._emitter.fire();
    }
    return changed;
  }

  /**
   * Rebuild a note row and its attachment subtree (when attachments are shown).
   * @param {string} noteMdPath
   */
  refreshNoteAssets(noteMdPath) {
    const noteItem = this.createFileItem(noteMdPath);
    const parent = this.getParent(noteItem);
    // Refresh parent so the note TreeItem itself is rebuilt; children reload on expand.
    this._emitter.fire(parent);
    this._emitter.fire(noteItem);
  }

  getTreeItem(el) {
    // Rebuild notes so title/icon fires apply without re-listing the parent folder.
    if (el?.isNoteItem && el.resourceUri?.fsPath) {
      return this.createFileItem(el.resourceUri.fsPath);
    }
    return el;
  }

  /**
   * @param {vscode.TreeItem} a
   * @param {vscode.TreeItem} b
   */
  sortTreeItems(a, b) {
    const labelToString = (label) => {
      if (!label) return '';
      if (typeof label === 'string') return label;
      if (typeof label === 'object' && typeof label.label === 'string') return label.label;
      return String(label);
    };
    const nameOf = (item) => {
      if (item?.isNoteItem && item.resourceUri?.fsPath) {
        return noteStemFromPath(item.resourceUri.fsPath);
      }
      const fsPath = item?.resourceUri?.fsPath || item?.dirPath;
      if (fsPath) {
        return path.basename(fsPath);
      }
      return labelToString(item?.label);
    };
    const aLabel = labelToString(a.label);
    const bLabel = labelToString(b.label);
    if (getSortDateNamesNewestFirst()) {
      return noteMeta.compareNamesNewestDatesFirst(nameOf(a), nameOf(b), aLabel, bLabel);
    }
    return aLabel.localeCompare(bLabel, undefined, {
      numeric: true,
      sensitivity: 'base',
    });
  }

  /**
   * @param {string} dir
   * @param {string | undefined} noteDirPath
   * @param {string | undefined} parentNoteMdPath
   */
  getAssetFolderChildren(dir, noteDirPath, parentNoteMdPath) {
    const entries = safeReaddir(dir);
    const items = [];
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        items.push(this.createAssetFolderItem(fullPath, entry.name, noteDirPath, parentNoteMdPath));
      } else if (entry.isFile()) {
        items.push(this.createAssetFileItem(fullPath, entry.name, noteDirPath, parentNoteMdPath));
      }
    }
    return items.sort((a, b) => this.sortTreeItems(a, b));
  }

  /**
   * @param {string} noteDir
   * @param {string | undefined} parentNoteMdPath
   */
  getNoteAssetChildren(noteDir, parentNoteMdPath) {
    const entries = safeReaddir(noteDir);
    const items = [];
    for (const entry of entries) {
      const fullPath = path.join(noteDir, entry.name);
      if (entry.isFile() && isFeaturedImageFileName(entry.name)) {
        items.push(this.createAssetFileItem(fullPath, entry.name, noteDir, parentNoteMdPath));
      } else if (entry.isDirectory() && isAssetFolderName(entry.name)) {
        items.push(this.createAssetFolderItem(fullPath, entry.name, noteDir, parentNoteMdPath));
      }
    }
    return items.sort((a, b) => this.sortTreeItems(a, b));
  }

  /**
   * @param {string} folderPath
   */
  folderDepthForPath(folderPath) {
    const root = this.findRootForPath(folderPath);
    if (!root) {
      return 1;
    }
    const rel = path.relative(root.path, folderPath);
    if (!rel || rel.startsWith('..')) {
      return 1;
    }
    const parts = rel.split(path.sep).filter(Boolean);
    return Math.max(1, parts.length);
  }

  /**
   * @param {vscode.TreeItem} element
   * @returns {vscode.TreeItem | undefined}
   */
  getParent(element) {
    if (!element) {
      return undefined;
    }

    if (element.isNoteItem && element.resourceUri?.fsPath) {
      const parentDir = getNoteTreeParentDir(element.resourceUri.fsPath);
      if (this.isWorkspaceRootPath(parentDir)) {
        return this.createWorkspaceRootFolderItem(parentDir);
      }
      return this.createFolderItem(parentDir, path.basename(parentDir), this.folderDepthForPath(parentDir));
    }

    if (
      (element.isAssetFolder || element.contextValue === 'noteAssetFile') &&
      element.resourceUri?.fsPath &&
      element.parentNoteMdPath
    ) {
      const itemPath = element.resourceUri.fsPath;
      const parentPath = path.dirname(itemPath);
      const noteDir = element.noteDirPath;
      if (noteDir && normalizeFsPath(parentPath) === normalizeFsPath(noteDir)) {
        return this.createFileItem(element.parentNoteMdPath);
      }
      if (isDirectoryPath(parentPath)) {
        return this.createAssetFolderItem(
          parentPath,
          path.basename(parentPath),
          element.noteDirPath,
          element.parentNoteMdPath,
        );
      }
    }

    if (element.dirPath && element.folderDepth != null && !element.isAssetFolder) {
      const parentDir = path.dirname(element.dirPath);
      if (this.isWorkspaceRootPath(element.dirPath)) {
        return undefined;
      }
      if (this.isWorkspaceRootPath(parentDir)) {
        return this.createWorkspaceRootFolderItem(parentDir);
      }
      if (normalizeFsPath(parentDir) === normalizeFsPath(element.dirPath)) {
        return undefined;
      }
      const depth = typeof element.folderDepth === 'number' ? Math.max(1, element.folderDepth - 1) : 1;
      return this.createFolderItem(parentDir, path.basename(parentDir), depth);
    }

    return undefined;
  }

  getChildren(element) {
    try {
      return this._getChildrenUnguarded(element);
    } catch (err) {
      const dir = element?.dirPath || '(root)';
      console.error(`[Harrix Notes HSK] getChildren failed for ${dir}:`, err);
      return [];
    }
  }

  /**
   * @param {vscode.TreeItem | undefined} element
   */
  _getChildrenUnguarded(element) {
    if (element?.isNoteItem && element.noteDirPath && this.isNoteAssetsVisible(element.noteDirPath)) {
      const noteMdPath = element.resourceUri?.fsPath;
      return this.getNoteAssetChildren(element.noteDirPath, noteMdPath);
    }
    if (element?.isAssetFolder && element.dirPath) {
      return this.getAssetFolderChildren(element.dirPath, element.noteDirPath, element.parentNoteMdPath);
    }

    if (!element) {
      return this.rootEntries.map((entry) => this.createWorkspaceRootFolderItem(entry.path, entry.name));
    }

    const dir = element.dirPath;
    if (!dir || !fs.existsSync(dir)) return [];

    const parentFolderDepth =
      element && typeof element.folderDepth === 'number' && Number.isFinite(element.folderDepth)
        ? element.folderDepth
        : 0;

    const specs = collectNotesDirChildSpecs(dir, {
      templateCountFor: (folderPath) => this.getTemplatesForFolder(folderPath).length,
    });
    const items = specs.map((spec) =>
      spec.kind === 'folder'
        ? this.createFolderItem(spec.path, spec.name, parentFolderDepth + 1)
        : this.createFileItem(spec.path),
    );

    const sorted = items.sort((a, b) => this.sortTreeItems(a, b));
    const notePaths = sorted
      .filter((item) => item.isNoteItem && item.resourceUri?.fsPath)
      .map((item) => item.resourceUri.fsPath);
    this.scheduleNoteTitleResolve(notePaths, dir);
    return sorted;
  }

  /**
   * Plain entries for the Icons Browse webview (same rules as the tree folder children).
   * Pass `null` / `undefined` for the multi-root workspace picker.
   *
   * @param {string | null | undefined} dirPath
   * @returns {Array<{ kind: 'folder' | 'note', path: string, name: string, label: string, iconEmoji: string, description: string }>}
   */
  listIconsBrowseEntries(dirPath) {
    if (dirPath == null || dirPath === '') {
      return this.rootEntries
        .map((entry) => {
          const item = this.createWorkspaceRootFolderItem(entry.path, entry.name);
          return {
            kind: /** @type {'folder'} */ ('folder'),
            path: entry.path,
            name: entry.name,
            label: typeof item.label === 'string' ? item.label : entry.name,
            iconEmoji: '',
            description: '',
            contextValue: String(item.contextValue || 'notesFolder'),
            isWorkspaceRoot: true,
          };
        })
        .sort((a, b) => a.label.localeCompare(b.label, undefined, { numeric: true, sensitivity: 'base' }));
    }

    const specs = collectNotesDirChildSpecs(dirPath, {
      templateCountFor: (folderPath) => this.getTemplatesForFolder(folderPath).length,
    });

    /** @type {Array<{ kind: 'folder' | 'note', path: string, name: string, label: string, iconEmoji: string, description: string, contextValue: string, isWorkspaceRoot?: boolean }>} */
    const entries = [];
    /** @type {string[]} */
    const notePaths = [];

    for (const spec of specs) {
      if (spec.kind === 'folder') {
        const item = this.createFolderItem(spec.path, spec.name, 1);
        entries.push({
          kind: 'folder',
          path: spec.path,
          name: spec.name,
          label: spec.name,
          iconEmoji: '',
          description: '',
          contextValue: String(item.contextValue || 'notesFolder'),
        });
        continue;
      }

      notePaths.push(spec.path);
      if (noteTitleCache.needsResolve(spec.path)) {
        noteTitleCache.resolveFromDisk(spec.path);
      }
      const item = this.createFileItem(spec.path);
      const label = getNoteDisplayLabel(spec.path);
      const stem = noteStemFromPath(spec.path);
      entries.push({
        kind: 'note',
        path: spec.path,
        name: stem,
        label,
        iconEmoji: noteTitleCache.getIconFast(spec.path) || '',
        description: label !== stem && getShowNoteFileNameBesideTitle() ? stem : '',
        contextValue: String(item.contextValue || 'note'),
      });
    }

    this.scheduleNoteTitleResolve(notePaths, dirPath);
    return entries.sort((a, b) => a.label.localeCompare(b.label, undefined, { numeric: true, sensitivity: 'base' }));
  }

  /**
   * Folder metadata for the Icons Browse current-directory (empty-area) menu.
   *
   * @param {string | null | undefined} dirPath
   * @returns {{ kind: 'folder', path: string, name: string, label: string, contextValue: string, isWorkspaceRoot: boolean } | null}
   */
  getIconsBrowseFolderEntry(dirPath) {
    if (dirPath == null || dirPath === '') {
      return null;
    }
    if (this.isWorkspaceRootPath(dirPath)) {
      const root = this.findRootForPath(dirPath);
      const name = root?.name || path.basename(dirPath);
      const item = this.createWorkspaceRootFolderItem(dirPath, name);
      return {
        kind: 'folder',
        path: dirPath,
        name,
        label: typeof item.label === 'string' ? item.label : name,
        contextValue: String(item.contextValue || 'notesFolder'),
        isWorkspaceRoot: true,
      };
    }
    const name = path.basename(dirPath);
    const item = this.createFolderItem(dirPath, name, 1);
    return {
      kind: 'folder',
      path: dirPath,
      name,
      label: name,
      contextValue: String(item.contextValue || 'notesFolder'),
      isWorkspaceRoot: false,
    };
  }

  /**
   * @param {string} folderPath
   * @param {string} [displayName] workspace folder name (may differ from basename)
   */
  createWorkspaceRootFolderItem(folderPath, displayName) {
    const diskName = path.basename(folderPath);
    const entry = this.findRootForPath(folderPath);
    const label =
      (typeof displayName === 'string' && displayName.trim() ? displayName.trim() : '') ||
      (entry && typeof entry.name === 'string' && entry.name.trim() ? entry.name.trim() : '') ||
      diskName;
    const item = this.createFolderItem(folderPath, diskName, 1);
    item.label = label;
    item.folderDepth = 0;
    item.isWorkspaceRoot = true;
    const expanded = this._expansion == null ? true : this._expansion.isWorkspaceRootExpanded(folderPath);
    item.collapsibleState = expanded
      ? vscode.TreeItemCollapsibleState.Expanded
      : vscode.TreeItemCollapsibleState.Collapsed;
    return item;
  }

  createFolderItem(folderPath, name, folderDepth) {
    const depth =
      typeof folderDepth === 'number' && Number.isFinite(folderDepth) ? Math.max(1, Math.floor(folderDepth)) : 1;
    const expanded = this._expansion != null ? this._expansion.isExpanded(folderPath) : false;
    const collapsible = expanded ? vscode.TreeItemCollapsibleState.Expanded : vscode.TreeItemCollapsibleState.Collapsed;
    const item = new vscode.TreeItem(name, collapsible);
    item.resourceUri = vscode.Uri.file(folderPath);
    item.dirPath = folderPath;
    item.folderDepth = depth;
    item.id = `folder:${normalizeFsPath(folderPath)}`;
    item.templateItems = this.getTemplatesForFolder(folderPath);
    item.contextValue = harrixCli.resolveNotesFolderContextValue({
      name,
      folderPath,
      hasMerged: hasMergedNoteFs(folderPath, name),
      templateItems: item.templateItems,
    });
    if (this.isFolderInsideGitWorkTree(folderPath)) {
      const base = item.contextValue;
      item.contextValue = `git${base.charAt(0).toUpperCase()}${base.slice(1)}`;
    }
    const isCut = treeClipboard.isCutPath(folderPath);
    if (this.isFolderBusy(folderPath)) {
      item.iconPath = new vscode.ThemeIcon('loading~spin');
      item.description = '…';
    } else if (getNotesIconStyle() === 'harrix') {
      item.iconPath = harrixIconUri('folder', isCut);
    } else {
      item.iconPath = isCut
        ? new vscode.ThemeIcon('folder', new vscode.ThemeColor('disabledForeground'))
        : vscode.ThemeIcon.Folder;
    }
    return item;
  }

  createFileItem(filePath) {
    const noteDir = path.dirname(filePath);
    const stem = noteStemFromPath(filePath);
    const displayName = getNoteDisplayLabel(filePath);
    const assetsVisible = this.isNoteAssetsVisible(noteDir);
    const item = new vscode.TreeItem(
      displayName,
      assetsVisible ? vscode.TreeItemCollapsibleState.Expanded : vscode.TreeItemCollapsibleState.None,
    );
    item.id = `note:${normalizeFsPath(filePath)}`;
    item.resourceUri = vscode.Uri.file(filePath);
    item.noteDirPath = noteDir;
    item.isNoteItem = true;
    if (displayName !== stem && getShowNoteFileNameBesideTitle()) {
      item.description = stem;
    }
    item.command = {
      command: 'harrixNotesExplorerHsk.openNote',
      title: 'Open',
      arguments: [vscode.Uri.file(filePath)],
    };
    const tooltipLines = [filePath];
    if (displayName !== stem && getShowNoteFileNameBesideTitle()) {
      tooltipLines.push(`File: ${stem}`);
    }
    tooltipLines.push('', 'Drop files to copy into this note (featured-image → root, images → img, others → files).');
    item.tooltip = tooltipLines.join('\n');

    const movablePath = isNoteInNamedFolder(filePath) ? path.dirname(filePath) : filePath;
    const isCut = treeClipboard.isCutPath(movablePath);
    const emojiIcon = noteIconPathFromEmoji(noteTitleCache.getIconFast(filePath), isCut);
    if (emojiIcon) {
      item.iconPath = emojiIcon;
    } else if (getNotesIconStyle() === 'harrix') {
      item.iconPath = harrixIconUri('note', isCut);
    } else {
      item.iconPath = new vscode.ThemeIcon('markdown', isCut ? new vscode.ThemeColor('disabledForeground') : undefined);
    }
    if (assetsVisible) {
      item.contextValue = 'noteWithAssets';
    } else if (noteDirHasAttachments(noteDir)) {
      item.contextValue = 'noteHasAttachments';
    } else {
      item.contextValue = 'note';
    }
    // Note/Note.md (same-name folder): enable folder-level context commands
    if (isNoteInNamedFolder(filePath)) {
      item.contextValue += 'NamedFolder';
    }
    if (this.isFolderInsideGitWorkTree(noteDir)) {
      const base = item.contextValue;
      item.contextValue = `git${base.charAt(0).toUpperCase()}${base.slice(1)}`;
    }
    return item;
  }

  /**
   * @param {string} filePath
   * @param {string} displayName
   * @param {string | undefined} noteDirPath
   * @param {string | undefined} parentNoteMdPath
   */
  createAssetFileItem(filePath, displayName, noteDirPath, parentNoteMdPath) {
    const item = new vscode.TreeItem(displayName, vscode.TreeItemCollapsibleState.None);
    item.id = `asset-file:${normalizeFsPath(filePath)}`;
    item.resourceUri = vscode.Uri.file(filePath);
    item.tooltip = filePath;
    item.noteDirPath = noteDirPath;
    item.parentNoteMdPath = parentNoteMdPath;
    item.command = {
      command: 'vscode.open',
      title: 'Open',
      arguments: [item.resourceUri],
    };
    const ext = path.extname(displayName).toLowerCase();
    const imageExts = new Set(['.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif', '.svg', '.bmp', '.ico']);
    item.iconPath = imageExts.has(ext) ? vscode.Uri.file(filePath) : new vscode.ThemeIcon('file');
    item.contextValue = 'noteAssetFile';
    return item;
  }

  /**
   * @param {string} folderPath
   * @param {string} name
   * @param {string | undefined} noteDirPath
   * @param {string | undefined} parentNoteMdPath
   */
  createAssetFolderItem(folderPath, name, noteDirPath, parentNoteMdPath) {
    // Expanded so Show attachments / note-with-assets trees open nested folders fully.
    const item = new vscode.TreeItem(name, vscode.TreeItemCollapsibleState.Expanded);
    item.id = `asset-folder:${normalizeFsPath(folderPath)}`;
    item.resourceUri = vscode.Uri.file(folderPath);
    item.dirPath = folderPath;
    item.noteDirPath = noteDirPath;
    item.parentNoteMdPath = parentNoteMdPath;
    item.isAssetFolder = true;
    item.tooltip = `${folderPath}\n\nDrop files here to copy into this folder.`;
    item.iconPath = new vscode.ThemeIcon('folder');
    item.contextValue = 'noteAssetFolder';
    return item;
  }
}

/**
 * @param {NotesProvider} provider
 * @returns {Promise<void>}
 */
function waitForTreeRefresh(provider) {
  return new Promise((resolve) => {
    const disposable = provider.onDidChangeTreeData(() => {
      disposable.dispose();
      resolve();
    });
    setTimeout(() => {
      disposable.dispose();
      resolve();
    }, 300);
  });
}

/**
 * @param {vscode.TreeView<vscode.TreeItem>} view
 * @param {NotesProvider} provider
 * @param {string} filePath
 * @param {boolean | number} [expandLevels=true] `true` expands one level; a number expands that many levels
 */
async function revealNoteWithAttachments(view, provider, filePath, expandLevels = true) {
  const revealItem = provider.createFileItem(filePath);
  /** @type {vscode.TreeItem[]} */
  const chain = [];
  let cur = /** @type {vscode.TreeItem | undefined} */ (revealItem);
  while (cur) {
    chain.unshift(cur);
    cur = provider.getParent(cur);
  }
  for (const node of chain) {
    try {
      await view.reveal(node, { expand: true, focus: false });
    } catch {
      // ancestor may be off-screen; continue
    }
  }
  try {
    await view.reveal(revealItem, { expand: expandLevels, select: true, focus: false });
  } catch {
    // ignore
  }
}

/**
 * Expand a note's attachment subtree after Show/Reload Attachments.
 * Reveals the first attachment (not the note): that expands the note and keeps
 * attachment rows in view. Revealing the note alone pins it to the viewport bottom.
 * @param {vscode.TreeView<vscode.TreeItem>} view
 * @param {NotesProvider} provider
 * @param {string} filePath
 */
async function expandNoteAttachmentsInTree(view, provider, filePath) {
  const noteItem = provider.createFileItem(filePath);
  const noteDir = path.dirname(filePath);
  const assets = provider.getNoteAssetChildren(noteDir, filePath);

  /** @type {vscode.TreeItem[]} */
  const ancestors = [];
  let cur = provider.getParent(noteItem);
  while (cur) {
    ancestors.unshift(cur);
    cur = provider.getParent(cur);
  }
  for (const node of ancestors) {
    try {
      await view.reveal(node, { expand: true, select: false, focus: false });
    } catch {
      // ignore
    }
  }

  if (assets.length > 0) {
    try {
      // expand: 3 is the API max; asset folders are Expanded by default when loaded.
      await view.reveal(assets[0], { expand: 3, select: false, focus: false });
      return;
    } catch {
      // fall through — note may not be expandable in the view yet
    }
  }

  try {
    await view.reveal(noteItem, { expand: 3, select: true, focus: false });
  } catch {
    // ignore
  }
}

function getAutoRevealNotes() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  return config.get('autoReveal') !== false;
}

/**
 * Active markdown file from the text editor or the active tab (incl. Markdown preview).
 * @returns {string | undefined}
 */
function getActiveMarkdownFsPath() {
  const ed = vscode.window.activeTextEditor;
  if (ed?.document?.uri?.scheme === 'file') {
    const fsPath = ed.document.uri.fsPath;
    if (isMd(path.basename(fsPath))) {
      return fsPath;
    }
  }

  const tab = vscode.window.tabGroups.activeTabGroup?.activeTab;
  const input = tab?.input;
  if (input && typeof input === 'object' && 'uri' in input) {
    const uri = /** @type {{ uri?: vscode.Uri }} */ (input).uri;
    if (uri?.scheme === 'file' && isMd(path.basename(uri.fsPath))) {
      return uri.fsPath;
    }
  }
  return undefined;
}

/**
 * Select the active note in the Harrix Notes tree when auto-reveal is on.
 * @param {vscode.TreeView<vscode.TreeItem>} view
 * @param {NotesProvider} provider
 * @param {{ generation: number }} state
 */
async function syncNotesTreeToActiveEditor(view, provider, state) {
  if (!getAutoRevealNotes()) {
    return;
  }
  const generation = ++state.generation;
  const filePath = getActiveMarkdownFsPath();
  if (!filePath || !provider.findRootForPath(filePath)) {
    return;
  }

  const selected = view.selection?.[0];
  if (selected?.resourceUri?.fsPath && normalizeFsPath(selected.resourceUri.fsPath) === normalizeFsPath(filePath)) {
    return;
  }

  await revealNoteWithAttachments(view, provider, filePath);
  if (generation !== state.generation) {
    return;
  }
}

/**
 * @param {NotesProvider} provider
 * @param {string} targetDir
 * @param {vscode.Uri[]} sources
 */
async function dropFilesIntoDirectory(provider, targetDir, sources) {
  let copied = 0;
  for (const source of sources) {
    const baseName = path.basename(source.fsPath);
    if (!baseName || !isFilePath(source.fsPath)) {
      continue;
    }
    try {
      const destPath = path.join(targetDir, baseName);
      await copyDroppedPathOverwrite(source, destPath);
      copied += 1;
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      void vscode.window.showErrorMessage(`Could not copy "${baseName}": ${msg}`);
    }
  }
  if (copied > 0) {
    provider.refresh();
  }
}

/**
 * @param {NotesProvider} provider
 * @param {string} noteMdPath
 * @param {vscode.Uri[]} sources
 */
async function dropFilesOntoNote(provider, noteMdPath, sources) {
  const settings = getNoteDropSettings();
  let notePath = noteMdPath;
  try {
    notePath = await ensureNoteInNamedFolder(noteMdPath, settings.moveIntoNamedFolder);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    void vscode.window.showErrorMessage(`Could not prepare note folder: ${msg}`);
    return;
  }

  const noteDir = path.dirname(notePath);
  let copied = 0;
  for (const source of sources) {
    const baseName = path.basename(source.fsPath);
    if (!baseName || !isFilePath(source.fsPath)) {
      continue;
    }
    try {
      const category = classifyDroppedFile(baseName, settings);
      const destDir = resolveNoteDropDestDir(noteDir, category, settings);
      const destPath = path.join(destDir, baseName);
      await copyDroppedPathOverwrite(source, destPath);
      copied += 1;
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      void vscode.window.showErrorMessage(`Could not copy "${baseName}": ${msg}`);
    }
  }

  if (copied === 0) {
    return;
  }

  if (!provider.isNoteAssetsVisible(noteDir)) {
    provider.setNoteAssetsVisible(noteDir, true);
  }
  provider.refresh();
  vscode.window.setStatusBarMessage(
    copied === 1 ? 'Copied 1 file into note' : `Copied ${copied} files into note`,
    2500,
  );
}

/** MIME type carrying tree items dragged inside the Harrix Notes (HSK) view. */
const HNE_TREE_MOVE_MIME = 'application/vnd.harrix.notes.hsk.move';

/** Context key: tree clipboard has a cut/copied note or folder. */
const HNE_CAN_PASTE_CONTEXT = 'harrixNotesExplorerHsk.canPaste';

/** In-memory clipboard for Cut / Copy / Paste in the notes tree. */
class TreeClipboard {
  constructor() {
    /** @type {string[]} */
    this.paths = [];
    /** @type {'copy' | 'cut' | null} */
    this.operation = null;
    /** @type {(() => void) | null} */
    this.onDidChange = null;
  }

  clear() {
    this.paths = [];
    this.operation = null;
    this._updateContext();
  }

  /**
   * @param {'copy' | 'cut'} operation
   * @param {string[]} paths
   */
  set(operation, paths) {
    this.operation = operation;
    this.paths = paths.filter(Boolean);
    this._updateContext();
  }

  get canPaste() {
    return this.paths.length > 0 && this.operation != null;
  }

  /** @param {string} fsPath */
  isCutPath(fsPath) {
    if (this.operation !== 'cut') {
      return false;
    }
    const key = normalizeFsPath(fsPath);
    return this.paths.some((cutPath) => normalizeFsPath(cutPath) === key);
  }

  _updateContext() {
    void vscode.commands.executeCommand('setContext', HNE_CAN_PASTE_CONTEXT, this.canPaste);
    this.onDidChange?.();
  }
}

const treeClipboard = new TreeClipboard();

/**
 * @param {unknown} treeItemOrUri
 * @param {vscode.TreeView<vscode.TreeItem> | undefined} view
 * @returns {string[]}
 */
function getMovableSourcePathsFromArg(treeItemOrUri, view) {
  /** @type {Array<vscode.TreeItem & Record<string, unknown>>} */
  const items = [];
  if (Array.isArray(treeItemOrUri)) {
    items.push(...treeItemOrUri);
  } else if (treeItemOrUri && typeof treeItemOrUri === 'object') {
    items.push(/** @type {vscode.TreeItem & Record<string, unknown>} */ (treeItemOrUri));
  }
  if (items.length === 0 && view?.selection?.length) {
    items.push(.../** @type {Array<vscode.TreeItem & Record<string, unknown>>} */ (view.selection));
  }
  /** @type {string[]} */
  const paths = [];
  const seen = new Set();
  for (const el of items) {
    const srcPath = getMovableSourcePath(el);
    if (!srcPath) {
      continue;
    }
    const key = normalizeFsPath(srcPath);
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    paths.push(srcPath);
  }
  return paths;
}

/**
 * Absolute path of the movable unit for a dragged tree item, or `null` if the
 * item cannot be moved (workspace root, note assets).
 * @param {vscode.TreeItem & Record<string, unknown>} el
 * @returns {string | null}
 */
function getMovableSourcePath(el) {
  if (!el || el.isWorkspaceRoot || el.isAssetFolder || el.contextValue === 'noteAssetFile') {
    return null;
  }
  if (el.isNoteItem && el.resourceUri?.fsPath) {
    const mdPath = el.resourceUri.fsPath;
    return isCollapsedFolderNote(mdPath) ? path.dirname(mdPath) : mdPath;
  }
  if (typeof el.dirPath === 'string' && el.dirPath) {
    return el.dirPath;
  }
  return null;
}

/**
 * Destination directory for an internal move, or `null` if the target cannot
 * accept moved items. Dropping onto a note targets the note's containing tree
 * folder (notes never become containers).
 * @param {NotesProvider} provider
 * @param {(vscode.TreeItem & Record<string, unknown>) | undefined} target
 * @returns {string | null}
 */
function getMoveTargetDir(provider, target) {
  if (!target) {
    // Empty drop area: only safe when a single workspace folder is open.
    return provider.rootEntries.length === 1 ? provider.rootEntries[0].path : null;
  }
  if (target.isWorkspaceRoot && typeof target.dirPath === 'string') {
    return target.dirPath;
  }
  if (target.isNoteItem && target.resourceUri?.fsPath) {
    return getNoteTreeParentDir(target.resourceUri.fsPath);
  }
  if (target.isAssetFolder) {
    return null;
  }
  if (typeof target.dirPath === 'string' && isDirectoryPath(target.dirPath)) {
    return target.dirPath;
  }
  return null;
}

/**
 * @param {NotesProvider} provider
 * @param {string} targetDir
 * @param {string[]} srcPaths
 * @param {'copy' | 'cut'} operation
 * @returns {Promise<number>} number of transferred items
 */
async function transferEntriesIntoDir(provider, targetDir, srcPaths, operation) {
  const targetNorm = normalizeFsPath(targetDir);
  let transferred = 0;
  for (const srcPath of srcPaths) {
    if (!srcPath || !pathExists(srcPath)) {
      continue;
    }
    const srcNorm = normalizeFsPath(srcPath);
    const parentNorm = normalizeFsPath(path.dirname(srcPath));
    if (parentNorm === targetNorm) {
      continue;
    }
    if (targetNorm === srcNorm || targetNorm.startsWith(srcNorm + path.sep)) {
      void vscode.window.showErrorMessage(`Cannot move "${path.basename(srcPath)}" into itself.`);
      continue;
    }
    const destPath = path.join(targetDir, path.basename(srcPath));
    if (pathExists(destPath)) {
      void vscode.window.showErrorMessage(`Target already exists: ${path.basename(destPath)}`);
      continue;
    }
    try {
      const sourceUri = vscode.Uri.file(srcPath);
      const destUri = vscode.Uri.file(destPath);
      if (operation === 'cut') {
        await vscode.workspace.fs.rename(sourceUri, destUri, { overwrite: false });
      } else {
        await vscode.workspace.fs.copy(sourceUri, destUri, { overwrite: false });
      }
      transferred += 1;
    } catch (e) {
      const verb = operation === 'cut' ? 'Move' : 'Copy';
      const msg = e instanceof Error ? e.message : String(e);
      void vscode.window.showErrorMessage(`${verb} failed for "${path.basename(srcPath)}": ${msg}`);
    }
  }
  if (transferred > 0) {
    provider.refresh();
    const verb = operation === 'cut' ? 'Moved' : 'Copied';
    vscode.window.setStatusBarMessage(transferred === 1 ? `${verb} 1 item` : `${verb} ${transferred} items`, 2500);
  }
  return transferred;
}

/**
 * @param {NotesProvider} provider
 * @param {string} targetDir
 * @param {string[]} srcPaths
 */
async function moveEntriesIntoDir(provider, targetDir, srcPaths) {
  await transferEntriesIntoDir(provider, targetDir, srcPaths, 'cut');
}

/** @param {NotesProvider} provider */
function createNoteAssetsDragAndDrop(provider) {
  return {
    dropMimeTypes: ['text/uri-list', 'application/vnd.code.uri-list', 'files', HNE_TREE_MOVE_MIME],
    dragMimeTypes: [HNE_TREE_MOVE_MIME, 'text/uri-list', 'text/plain'],

    /** @param {ReadonlyArray<vscode.TreeItem & Record<string, unknown>>} source */
    handleDrag(source, dataTransfer, _token) {
      /** @type {string[]} */
      const movePaths = [];
      const seenMove = new Set();
      /** @type {string[]} */
      const uriLines = [];
      const seenUri = new Set();
      /** @type {string[]} */
      const markdownSnippets = [];
      const settings = getNoteDropSettings();

      for (const el of source) {
        // Expose file URIs so Shift+drop into a Markdown editor can insert a relative link
        // (including attachments / noteAssetFile, which are not tree-movable).
        if (el.resourceUri instanceof vscode.Uri && el.resourceUri.scheme === 'file') {
          const fsPath = el.resourceUri.fsPath;
          const uriKey = normalizeFsPath(fsPath);
          if (!seenUri.has(uriKey)) {
            seenUri.add(uriKey);
            uriLines.push(el.resourceUri.toString(true));
          }

          // Prefer plain-text Markdown for same-note attachment drops (beats workspace-relative URI text).
          const parentMd =
            typeof el.parentNoteMdPath === 'string' && el.parentNoteMdPath
              ? el.parentNoteMdPath
              : typeof el.noteDirPath === 'string' && el.noteDirPath
                ? path.join(el.noteDirPath, `${path.basename(el.noteDirPath)}.md`)
                : '';
          if (parentMd && isFilePath(fsPath)) {
            markdownSnippets.push(formatDroppedMarkdownSnippet(fsPath, path.dirname(parentMd), settings));
          }
        }

        const srcPath = getMovableSourcePath(el);
        if (!srcPath) {
          continue;
        }
        const key = normalizeFsPath(srcPath);
        if (seenMove.has(key)) {
          continue;
        }
        seenMove.add(key);
        movePaths.push(srcPath);
      }

      if (uriLines.length > 0) {
        dataTransfer.set('text/uri-list', new vscode.DataTransferItem(uriLines.join('\r\n')));
      }
      if (markdownSnippets.length > 0) {
        dataTransfer.set('text/plain', new vscode.DataTransferItem(markdownSnippets.join('\n')));
      }
      if (movePaths.length > 0) {
        dataTransfer.set(HNE_TREE_MOVE_MIME, new vscode.DataTransferItem(movePaths));
      }
    },

    /** @param {vscode.TreeItem & Record<string, unknown>} target */
    async handleDrop(target, dataTransfer, _token) {
      const moveItem = dataTransfer.get(HNE_TREE_MOVE_MIME);
      if (moveItem) {
        const srcPaths = Array.isArray(moveItem.value) ? moveItem.value : [];
        const targetDir = getMoveTargetDir(provider, target);
        if (targetDir && srcPaths.length > 0) {
          await moveEntriesIntoDir(provider, targetDir, srcPaths);
        }
        return;
      }

      const sources = await readDroppedFileUris(dataTransfer);
      if (sources.length === 0) {
        return;
      }

      if (target?.isNoteItem && target.resourceUri?.fsPath && isFilePath(target.resourceUri.fsPath)) {
        await dropFilesOntoNote(provider, target.resourceUri.fsPath, sources);
        return;
      }

      if (target?.isAssetFolder && typeof target.dirPath === 'string' && isDirectoryPath(target.dirPath)) {
        await dropFilesIntoDirectory(provider, target.dirPath, sources);
      }
    },
  };
}

/** @returns {Record<string, unknown>} */
function getPreviewCopyConfig() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  const zone = Number(config.get('previewCopy.bottomHoverZonePx', 80));
  return {
    enabled: config.get('previewCopy.enabled', true) !== false,
    showTop: config.get('previewCopy.showTopButton', true) !== false,
    showBottom: config.get('previewCopy.showBottomButton', true) !== false,
    topAlwaysVisible: config.get('previewCopy.topAlwaysVisible', true) !== false,
    bottomHoverZonePx: Number.isFinite(zone) && zone >= 0 ? zone : 80,
    backgroundColor: normalizePreviewCopyColor(config.get('previewCopy.backgroundColor', '#fefefe'), '#fefefe'),
    borderColor: normalizePreviewCopyColor(config.get('previewCopy.borderColor', '#7f7f7f'), '#7f7f7f'),
    copiedColor: normalizePreviewCopyColor(config.get('previewCopy.copiedColor', '#388a34'), '#388a34'),
    collapseFrontmatter: config.get('previewFrontmatter.collapse', true) !== false,
    frontmatterSummary: normalizePreviewFrontmatterSummary(config.get('previewFrontmatter.summary', '📋 YAML')),
    colorizeHex: config.get('previewColorize.enabled', true) !== false,
  };
}

/** @param {unknown} value */
function normalizePreviewFrontmatterSummary(value) {
  const raw = String(value ?? '').trim();
  return raw || '📋 YAML';
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
  return json.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
}

/**
 * Format an indented YAML block under a top-level key (lists / nested maps).
 * @param {string[]} blockLines
 */
function formatYamlBlockValue(blockLines) {
  /** @type {string[]} */
  const simpleListItems = [];
  let isSimpleScalarList = true;
  for (const line of blockLines) {
    if (!line.trim() || line.trimStart().startsWith('#')) {
      continue;
    }
    const listItem = line.match(/^\s+-\s+(.*)$/);
    if (!listItem) {
      isSimpleScalarList = false;
      break;
    }
    const item = listItem[1].trim();
    // Nested map entry in a list: `- author: …` / continuation lines → not a simple list.
    if (/^[A-Za-z0-9_.-]+\s*:/.test(item) || /^\s+\S/.test(line.replace(/^\s+-\s+/, ' '))) {
      // `- author: X` is a map item, not a plain scalar list.
      if (/^[A-Za-z0-9_.-]+\s*:/.test(item)) {
        isSimpleScalarList = false;
        break;
      }
    }
    simpleListItems.push(unquoteYamlScalar(item));
  }
  if (isSimpleScalarList && simpleListItems.length > 0) {
    return simpleListItems.join(', ');
  }
  return blockLines
    .map((line) => line.replace(/\s+$/, ''))
    .filter((line, idx, arr) => line.trim() || (idx > 0 && idx < arr.length - 1))
    .join('\n')
    .replace(/^\n+|\n+$/g, '');
}

/**
 * Parse YAML frontmatter into table rows. Handles `key: value` and indented lists
 * (`tags:\n  - a\n  - b` → `tags` / `a, b`). Nested maps keep a compact multi-line value.
 * @param {string} fmText
 * @returns {Array<[string, string]>}
 */
function parseFrontmatterRows(fmText) {
  const lines = String(fmText || '').split(/\r?\n/);
  /** @type {Array<[string, string]>} */
  const rows = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim() || line.trimStart().startsWith('#')) {
      i += 1;
      continue;
    }
    // Top-level keys only (no leading indent).
    const kv = line.match(/^([A-Za-z0-9_.-]+)\s*:\s*(.*)$/);
    if (!kv) {
      i += 1;
      continue;
    }
    const key = kv[1];
    const value = kv[2].trim();
    i += 1;
    if (value) {
      rows.push([key, unquoteYamlScalar(value)]);
      continue;
    }
    /** @type {string[]} */
    const blockLines = [];
    while (i < lines.length) {
      const next = lines[i];
      if (!next.trim()) {
        // Blank line inside a block: keep only if more indented content follows.
        let look = i + 1;
        while (look < lines.length && !lines[look].trim()) {
          look += 1;
        }
        if (look < lines.length && /^\s+\S/.test(lines[look])) {
          blockLines.push(next);
          i += 1;
          continue;
        }
        break;
      }
      if (next.trimStart().startsWith('#') && /^\s+#/.test(next)) {
        i += 1;
        continue;
      }
      if (!/^\s+\S/.test(next)) {
        break;
      }
      blockLines.push(next);
      i += 1;
    }
    rows.push([key, formatYamlBlockValue(blockLines)]);
  }
  return rows;
}

/**
 * Escape text for an HTML table cell; preserve line breaks for nested YAML blocks.
 * @param {string} value
 */
function formatFrontmatterCellHtml(value) {
  return escapeHtmlAttr(value).replace(/\r\n|\n|\r/g, '<br>');
}

/**
 * @param {string} text
 * @returns {string} raw YAML body between `---` markers, or `''`
 */
function rawYamlFrontmatterFromText(text) {
  let src = typeof text === 'string' ? text : String(text ?? '');
  if (src.charCodeAt(0) === 0xfeff) {
    src = src.slice(1);
  }
  const match = src.match(/^---[ \t]*\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)/);
  return match ? match[1] : '';
}

/**
 * Split leading YAML frontmatter from Markdown source (fallback when engine has no front_matter rule).
 * @param {string} src
 * @returns {{ body: string, rows: Array<[string, string]>, raw: string } | null}
 */
function extractYamlFrontmatter(src) {
  let text = typeof src === 'string' ? src : String(src ?? '');
  if (text.charCodeAt(0) === 0xfeff) {
    text = text.slice(1);
  }
  if (!text.startsWith('---')) {
    return null;
  }
  const match = text.match(/^---[ \t]*\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)/);
  if (!match) {
    return null;
  }
  const raw = match[1];
  const rows = parseFrontmatterRows(raw);
  if (rows.length === 0 && !raw.trim()) {
    return null;
  }
  return { body: text.slice(match[0].length), rows, raw };
}

/**
 * Build frontmatter HTML (table when possible; otherwise a raw YAML `<pre>`).
 * @param {Array<[string, string]>} rows
 * @param {{ collapseFrontmatter?: boolean, frontmatterSummary?: string }} cfg
 * @param {string} [rawYaml]
 */
function buildFrontmatterPreviewHtml(rows, cfg, rawYaml = '') {
  let inner = '';
  if (rows.length > 0) {
    const tableRows = rows
      .map(([key, value]) => `<tr><td>${escapeHtmlAttr(key)}</td><td>${formatFrontmatterCellHtml(value)}</td></tr>`)
      .join('');
    inner = `<table class="frontmatter hne-frontmatter-table"><tbody>${tableRows}</tbody></table>\n`;
  } else if (String(rawYaml || '').trim()) {
    inner = `<pre class="hne-frontmatter-raw"><code>${escapeHtmlAttr(String(rawYaml).replace(/\n$/, ''))}</code></pre>\n`;
  } else {
    return '';
  }
  if (cfg.collapseFrontmatter === false) {
    return inner;
  }
  const summary = escapeHtmlAttr(normalizePreviewFrontmatterSummary(cfg.frontmatterSummary || '📋 YAML'));
  return (
    `<details class="hne-frontmatter-details">` +
    `<summary class="hne-frontmatter-summary">${summary}</summary>\n` +
    `${inner}` +
    `</details>\n`
  );
}

/**
 * Raw YAML content from a markdown-it front_matter token (VS Code yamlPreamble / markdown-it-front-matter).
 * @param {import('markdown-it/lib/token') | undefined} token
 */
function frontMatterContentFromToken(token) {
  if (!token) {
    return '';
  }
  if (typeof token.meta === 'string' && token.meta.trim()) {
    return token.meta;
  }
  if (token.meta && typeof token.meta === 'object') {
    if (typeof token.meta.content === 'string' && token.meta.content) {
      return token.meta.content;
    }
    // Some hosts put parsed key/value pairs directly on meta (no `.content`).
    if (!('content' in token.meta)) {
      try {
        const entries = Object.entries(token.meta);
        if (entries.length > 0) {
          return entries
            .map(([k, v]) => `${k}: ${v == null ? '' : typeof v === 'string' ? v : JSON.stringify(v)}`)
            .join('\n');
        }
      } catch {
        // ignore
      }
    }
  }
  if (typeof token.content === 'string' && token.content) {
    return token.content;
  }
  if (typeof token.info === 'string' && token.info.trim()) {
    return token.info;
  }
  return '';
}

/**
 * Resolve document URI from markdown-it render `env` (VS Code / Cursor shapes).
 * @param {unknown} env
 * @returns {vscode.Uri | undefined}
 */
function uriFromMarkdownRenderEnv(env) {
  if (!env || typeof env !== 'object') {
    return undefined;
  }
  const record = /** @type {Record<string, unknown>} */ (env);
  const candidates = [record.currentDocument, record.resource, record.uri, record.document];
  for (const c of candidates) {
    if (c instanceof vscode.Uri) {
      return c;
    }
    if (c && typeof c === 'object' && /** @type {{ uri?: unknown }} */ (c).uri instanceof vscode.Uri) {
      return /** @type {{ uri: vscode.Uri }} */ (c).uri;
    }
    if (typeof c === 'string' && c) {
      try {
        return c.includes(':') ? vscode.Uri.parse(c) : vscode.Uri.file(c);
      } catch {
        // ignore
      }
    }
  }
  return undefined;
}

/**
 * Read YAML frontmatter body from the note file when the front_matter token has no content
 * (seen in Cursor classic preview).
 * @param {unknown} env
 */
function resolveFrontmatterRawFromEnv(env) {
  const uri = uriFromMarkdownRenderEnv(env);
  if (uri?.scheme !== 'file') {
    return '';
  }
  const target = normalizeFsPath(uri.fsPath);
  for (const doc of vscode.workspace.textDocuments) {
    if (doc.uri.scheme === 'file' && normalizeFsPath(doc.uri.fsPath) === target) {
      return rawYamlFrontmatterFromText(doc.getText());
    }
  }
  try {
    return rawYamlFrontmatterFromText(fs.readFileSync(uri.fsPath, 'utf8'));
  } catch {
    return '';
  }
}

/**
 * @param {import('markdown-it/lib/token') | undefined} token
 * @param {unknown} env
 */
function resolveFrontmatterRaw(token, env) {
  let raw = frontMatterContentFromToken(token);
  if (!String(raw).trim()) {
    raw = resolveFrontmatterRawFromEnv(env);
  }
  return raw;
}

/**
 * markdown-it block rule for `---` YAML frontmatter (used when the host has no built-in rule).
 * @type {import('markdown-it/lib/parser_block').RuleBlock}
 */
function hneFrontMatterBlockRule(state, startLine, endLine, silent) {
  if (startLine !== 0 || state.tShift[startLine] !== 0) {
    return false;
  }
  const firstLine = state.src.slice(state.bMarks[startLine], state.eMarks[startLine]).replace(/\s+$/, '');
  if (firstLine !== '---' && firstLine !== '\uFEFF---') {
    return false;
  }
  let nextLine = startLine + 1;
  let foundEnd = false;
  for (; nextLine < endLine; nextLine += 1) {
    if (state.tShift[nextLine] !== 0) {
      continue;
    }
    const line = state.src.slice(state.bMarks[nextLine], state.eMarks[nextLine]).replace(/\s+$/, '');
    if (line === '---') {
      foundEnd = true;
      break;
    }
  }
  if (!foundEnd) {
    return false;
  }
  if (silent) {
    return true;
  }
  const rawContent = state.src.slice(state.bMarks[startLine + 1], state.bMarks[nextLine]).replace(/\n$/, '');
  const token = state.push('front_matter', '', 0);
  token.block = true;
  token.hidden = false;
  token.markup = '---';
  token.map = [startLine, nextLine + 1];
  token.meta = { content: rawContent };
  token.content = rawContent;
  state.line = nextLine + 1;
  return true;
}

function registerPreviewCopyMarkdownPlugin() {
  return {
    extendMarkdownIt(/** @type {import('markdown-it')} */ md) {
      const defaultImageRender =
        md.renderer.rules.image || ((tokens, idx, options, _env, self) => self.renderToken(tokens, idx, options));

      md.renderer.rules.image = (tokens, idx, options, env, self) => {
        const token = tokens[idx];
        const src = token.attrGet('src') || '';
        const dataSrc = token.attrGet('data-src') || '';
        const ext = mediaExtFromSrc(dataSrc || src);
        const title = token.attrGet('title');
        const titleAttr = title ? ` title="${escapeHtmlAttr(title)}"` : '';

        const localFsPath = resolveLocalMediaFsPath(dataSrc, src, env);
        const openLink = localFsPath ? renderOpenInSystemPlayerLink(localFsPath) : '';

        if (PREVIEW_VIDEO_EXTENSIONS.has(ext)) {
          return (
            `<div class="hne-md-media">` +
            `<video class="hne-md-video" controls playsinline src="${escapeHtmlAttr(src)}"${titleAttr}></video>\n` +
            `${openLink}</div>`
          );
        }
        if (PREVIEW_AUDIO_EXTENSIONS.has(ext)) {
          return (
            `<div class="hne-md-media">` +
            `<audio class="hne-md-audio" controls src="${escapeHtmlAttr(src)}"${titleAttr}></audio>\n` +
            `${openLink}</div>`
          );
        }
        return defaultImageRender(tokens, idx, options, env, self);
      };

      // Modern VS Code / Cursor call `renderer.render(tokens)`, not `md.render(src)`.
      // Override the front_matter token renderer (yamlPreamble) and inject config there.
      const renderFrontMatterToken = (tokens, idx, _options, env) => {
        const cfg = getPreviewCopyConfig();
        const raw = resolveFrontmatterRaw(tokens[idx], env);
        const rows = parseFrontmatterRows(raw);
        return buildFrontmatterPreviewHtml(rows, cfg, raw);
      };
      md.renderer.rules.front_matter = renderFrontMatterToken;

      // If the host has no front_matter block rule, add one (older / stripped engines).
      let hasFrontMatterRule = true;
      try {
        md.block.ruler.enable(['front_matter'], true);
      } catch {
        hasFrontMatterRule = false;
      }
      if (!hasFrontMatterRule) {
        try {
          md.block.ruler.before('fence', 'front_matter', hneFrontMatterBlockRule, {
            alt: ['paragraph', 'reference', 'blockquote', 'list'],
          });
        } catch {
          try {
            md.block.ruler.push('front_matter', hneFrontMatterBlockRule, {
              alt: ['paragraph', 'reference', 'blockquote', 'list'],
            });
          } catch {
            // ignore
          }
        }
      }

      const originalParse = md.parse.bind(md);
      md.parse = (src, env) => {
        const nextEnv = env && typeof env === 'object' ? env : {};
        const text = typeof src === 'string' ? src : String(src ?? '');
        nextEnv.hneMarpSource = text;
        nextEnv.hneIsMarp = isMarpMarkdown(text);
        return originalParse(src, nextEnv);
      };

      const originalRendererRender = md.renderer.render.bind(md.renderer);
      md.renderer.render = (tokens, options, env) => {
        if (env?.hneIsMarp && env.hneMarpSource) {
          const cfg = getPreviewCopyConfig();
          const json = escapePreviewCopyConfigAttr(JSON.stringify(cfg));
          const configHtml = `<div id="hne-preview-copy-config" style="display:none" data-config="${json}"></div>`;
          const deckHtml = renderMarpPreviewHtml(env.hneMarpSource, (slideMd) => {
            const slideTokens = originalParse(slideMd || ' ', {});
            return originalRendererRender(slideTokens, options, {});
          });
          return configHtml + deckHtml;
        }
        // Cursor may emit an empty front_matter token — refill from the note file.
        if (Array.isArray(tokens)) {
          for (const token of tokens) {
            if (token?.type !== 'front_matter') {
              continue;
            }
            if (frontMatterContentFromToken(token).trim()) {
              continue;
            }
            const raw = resolveFrontmatterRawFromEnv(env);
            if (!raw.trim()) {
              continue;
            }
            token.meta = { ...(token.meta && typeof token.meta === 'object' ? token.meta : {}), content: raw };
            token.content = raw;
          }
        }
        const cfg = getPreviewCopyConfig();
        const json = escapePreviewCopyConfigAttr(JSON.stringify(cfg));
        const configHtml = `<div id="hne-preview-copy-config" style="display:none" data-config="${json}"></div>`;
        return configHtml + originalRendererRender(tokens, options, env);
      };

      // Fallback for hosts that still call `md.render(src)` (and may lack front_matter tokens).
      const render = md.render.bind(md);
      md.render = (src, env) => {
        const cfg = getPreviewCopyConfig();
        const text = typeof src === 'string' ? src : String(src ?? '');
        const extracted = extractYamlFrontmatter(text);
        if (!extracted) {
          return render(src, env);
        }
        const withTokens = render(src, env);
        if (
          withTokens.includes('hne-frontmatter-table') ||
          withTokens.includes('hne-frontmatter-details') ||
          withTokens.includes('hne-frontmatter-raw')
        ) {
          return withTokens;
        }
        // No front_matter token emitted — strip YAML and inject our block after the config div.
        const bodyHtml = render(extracted.body, env);
        const fmHtml = buildFrontmatterPreviewHtml(extracted.rows, cfg, extracted.raw);
        const configClose = '</div>';
        const configMark = 'id="hne-preview-copy-config"';
        const markAt = bodyHtml.indexOf(configMark);
        if (markAt !== -1) {
          const closeAt = bodyHtml.indexOf(configClose, markAt);
          if (closeAt !== -1) {
            const insertAt = closeAt + configClose.length;
            return bodyHtml.slice(0, insertAt) + fmHtml + bodyHtml.slice(insertAt);
          }
        }
        return fmHtml + bodyHtml;
      };

      return md;
    },
  };
}

/**
 * @param {vscode.ExtensionContext} context
 */
function registerPreviewCopyConfigRefresh(context) {
  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (
        !e.affectsConfiguration('harrixNotesExplorerHsk.previewCopy') &&
        !e.affectsConfiguration('harrixNotesExplorerHsk.previewFrontmatter') &&
        !e.affectsConfiguration('harrixNotesExplorerHsk.previewColorize')
      ) {
        return;
      }
      void vscode.commands.executeCommand('markdown.preview.refresh');
    }),
  );
}

/**
 * @returns {WorkspaceRootEntry[]}
 */
function getWorkspaceRootEntries() {
  const folders = vscode.workspace.workspaceFolders;
  if (!folders || folders.length === 0) {
    return [];
  }
  return folders.map((folder) => ({
    path: folder.uri.fsPath,
    name: folder.name,
  }));
}

async function activate(context) {
  registerOpenMediaExternallyCommand(context);
  try {
    await startOpenMediaHttpServer();
  } catch (err) {
    console.error('[Harrix Notes HSK] open-media HTTP server failed:', err);
  }
  registerPreviewCopyConfigRefresh(context);
  activateVisualEditor(context, {
    noteUriFromTreeArg,
    materializeDroppedFilesForNote,
    getNoteDropSettings,
    formatDroppedMarkdownSnippet,
    toMarkdownRelativePath,
  });

  const rootEntries = getWorkspaceRootEntries();
  if (rootEntries.length === 0) {
    registerMarkdownRelativeLinkDropProvider(context);
    return registerPreviewCopyMarkdownPlugin();
  }
  const rootPath = rootEntries[0].path;

  const expansionMemory = new FolderExpansionMemory(context);
  context.subscriptions.push({
    dispose: () => {
      void expansionMemory.flush();
    },
  });

  const assetsVisibility = new NoteAssetsVisibility(context);

  const provider = new NotesProvider(rootEntries, expansionMemory, assetsVisibility);
  registerMarkdownRelativeLinkDropProvider(context, provider);
  const view = vscode.window.createTreeView('harrixNotesExplorerHsk', {
    treeDataProvider: provider,
    showCollapseAll: true,
    dragAndDropController: createNoteAssetsDragAndDrop(provider),
  });
  context.subscriptions.push(view);

  context.subscriptions.push(
    vscode.workspace.onDidChangeWorkspaceFolders(() => {
      provider.setRootEntries(getWorkspaceRootEntries());
    }),
  );

  /** @type {{ generation: number }} */
  const autoRevealState = { generation: 0 };
  /** @type {ReturnType<typeof setTimeout> | null} */
  let autoRevealTimer = null;
  const queueAutoReveal = () => {
    if (autoRevealTimer) {
      clearTimeout(autoRevealTimer);
    }
    autoRevealTimer = setTimeout(() => {
      autoRevealTimer = null;
      void syncNotesTreeToActiveEditor(view, provider, autoRevealState);
    }, 50);
  };
  context.subscriptions.push({
    dispose: () => {
      if (autoRevealTimer) {
        clearTimeout(autoRevealTimer);
        autoRevealTimer = null;
      }
    },
  });

  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor(() => {
      queueAutoReveal();
    }),
  );
  context.subscriptions.push(
    vscode.window.tabGroups.onDidChangeTabs(() => {
      queueAutoReveal();
    }),
  );
  context.subscriptions.push(
    view.onDidChangeVisibility((e) => {
      if (e.visible) {
        queueAutoReveal();
      }
    }),
  );
  queueAutoReveal();

  treeClipboard.clear();
  treeClipboard.onDidChange = () => provider.refresh();
  context.subscriptions.push({
    dispose: () => {
      treeClipboard.onDidChange = null;
      treeClipboard.clear();
    },
  });

  context.subscriptions.push(
    view.onDidExpandElement((e) => {
      const el = /** @type {vscode.TreeItem & { dirPath?: string }} */ (e.element);
      if (el && typeof el.dirPath === 'string') {
        expansionMemory.recordExpand(el.dirPath);
      }
    }),
  );
  context.subscriptions.push(
    view.onDidCollapseElement((e) => {
      const el = /** @type {vscode.TreeItem & { dirPath?: string }} */ (e.element);
      if (el && typeof el.dirPath === 'string') {
        expansionMemory.recordCollapse(el.dirPath);
      }
    }),
  );

  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (
        e.affectsConfiguration('harrixNotesExplorerHsk.rememberFolderExpansion') ||
        e.affectsConfiguration('harrixNotesExplorerHsk.showNoteTitleFromContent') ||
        e.affectsConfiguration('harrixNotesExplorerHsk.showNoteFileNameBesideTitle') ||
        e.affectsConfiguration('harrixNotesExplorerHsk.iconStyle') ||
        e.affectsConfiguration('harrixNotesExplorerHsk.sortDateNamesNewestFirst') ||
        e.affectsConfiguration('harrixNotesExplorerHsk.iconsBrowse') ||
        e.affectsConfiguration('harrixNotesExplorerHsk.openNotesInPreview')
      ) {
        provider.refresh();
        refreshIconsBrowseIfOpen();
      }
      if (e.affectsConfiguration('harrixNotesExplorerHsk.autoReveal')) {
        queueAutoReveal();
      }
    }),
  );

  const logChannel = vscode.window.createOutputChannel('Harrix Notes Explorer (HSK)');
  context.subscriptions.push(logChannel);

  activateIconsBrowse({
    context,
    provider,
    getCanPaste: () => treeClipboard.canPaste,
    getCutPaths: () => (treeClipboard.operation === 'cut' ? [...treeClipboard.paths] : []),
    openNote: async (uri) => {
      await openHarrixNote(uri, 'primary');
    },
  });

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.openNote', async (treeItemOrUri) => {
      const uri = noteUriFromTreeArg(treeItemOrUri);
      if (!uri) {
        return;
      }
      await openHarrixNote(uri, 'primary');
    }),
  );
  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.openNoteInEditor', async (treeItemOrUri) => {
      const uri = noteUriFromTreeArg(treeItemOrUri);
      if (!uri) {
        return;
      }
      await openHarrixNote(uri, 'editor');
    }),
  );
  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.openNoteInPreview', async (treeItemOrUri) => {
      const uri = noteUriFromTreeArg(treeItemOrUri);
      if (!uri) {
        return;
      }
      await openHarrixNote(uri, 'preview');
    }),
  );
  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.showNoteAssets', async (treeItemOrUri) => {
      const uri = noteUriFromTreeArg(treeItemOrUri);
      if (!uri || !isFilePath(uri.fsPath)) {
        vscode.window.showErrorMessage('Open a markdown note or select one in Harrix Notes (HSK).');
        return;
      }
      const noteDir = path.dirname(uri.fsPath);
      if (!noteDirHasAttachments(noteDir)) {
        void vscode.window.showInformationMessage(
          'No attachments in this note folder (no featured image and no asset folders such as images or files).',
        );
        return;
      }
      const refreshDone = waitForTreeRefresh(provider);
      provider.setNoteAssetsVisible(noteDir, true);
      await refreshDone;
      // Let the tree apply the refreshed note row before expand/reveal.
      await new Promise((resolve) => setTimeout(resolve, 50));
      await expandNoteAttachmentsInTree(view, provider, uri.fsPath);
    }),
  );
  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.hideNoteAssets', (treeItemOrUri) => {
      const uri = noteUriFromTreeArg(treeItemOrUri);
      if (!uri || !isFilePath(uri.fsPath)) {
        vscode.window.showErrorMessage('Open a markdown note or select one in Harrix Notes (HSK).');
        return;
      }
      provider.setNoteAssetsVisible(path.dirname(uri.fsPath), false);
    }),
  );
  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.reloadNoteAssets', async (treeItemOrUri) => {
      const uri = noteUriFromTreeArg(treeItemOrUri);
      if (!uri || !isFilePath(uri.fsPath)) {
        vscode.window.showErrorMessage('Open a markdown note or select one in Harrix Notes (HSK).');
        return;
      }
      const noteDir = path.dirname(uri.fsPath);
      if (!provider.isNoteAssetsVisible(noteDir)) {
        void vscode.window.showInformationMessage(
          'Attachments are not shown for this note. Use Show Attachments first.',
        );
        return;
      }
      const refreshDone = waitForTreeRefresh(provider);
      provider.refreshNoteAssets(uri.fsPath);
      await refreshDone;
      await new Promise((resolve) => setTimeout(resolve, 50));
      await expandNoteAttachmentsInTree(view, provider, uri.fsPath);
    }),
  );
  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.hideAllNoteAssets', () => {
      if (!provider.hideAllNoteAssets()) {
        void vscode.window.showInformationMessage('No notes have attachments shown.');
      }
    }),
  );
  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.openMarkdownPreviewTabInEditor', async () => {
      try {
        await vscode.commands.executeCommand('markdown.showSource');
      } catch {
        // Built-in Markdown extension unavailable or no active preview resource.
      }
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.refresh', () => provider.refresh()),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.openMergedNote', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isDirectoryPath(fsPath)) return;

      const folderName = path.basename(fsPath);
      const gPath = mergedNotePath(fsPath, folderName);
      if (!pathExists(gPath)) {
        vscode.window.showWarningMessage(`No merged note for this folder (_${folderName}.g.md).`);
        return;
      }
      const gUri = vscode.Uri.file(gPath);
      try {
        // Prefer preview: merged notes are meant to be viewed, not edited.
        await vscode.commands.executeCommand('markdown.showPreview', gUri, undefined, { locked: true });
      } catch {
        await vscode.commands.executeCommand('vscode.open', gUri);
      }
    }),
  );

  activateNewNote({
    context,
    provider,
    rootPath,
    uriToFsPath,
    isDirectoryPath,
    isFilePath,
  });

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.presentMarp', async () => {
      const editor = vscode.window.activeTextEditor;
      const doc = editor?.document;
      if (doc?.languageId !== 'markdown') {
        vscode.window.showErrorMessage('Open a Markdown Marp note to present.');
        return;
      }
      let markdown = doc.getText();
      if (!isMarpMarkdown(markdown)) {
        vscode.window.showErrorMessage('This note is not a Marp presentation (`type: marp` or `marp: true`).');
        return;
      }
      const noteDir = path.dirname(doc.uri.fsPath);
      const panel = vscode.window.createWebviewPanel(
        'harrixNotesExplorerHsk.marpPresent',
        path.basename(doc.fileName),
        vscode.ViewColumn.Beside,
        {
          enableScripts: true,
          retainContextWhenHidden: true,
          localResourceRoots: [vscode.Uri.file(noteDir), vscode.Uri.joinPath(context.extensionUri, 'media')],
        },
      );
      markdown = rewriteMarpRelativeImages(markdown, panel.webview, noteDir);
      const markedSrc = panel.webview
        .asWebviewUri(vscode.Uri.joinPath(context.extensionUri, 'media', 'vendor', 'marked.min.js'))
        .toString();
      panel.webview.html = renderMarpPresentWebview(markdown, {
        markedSrc,
        cspSource: panel.webview.cspSource,
      });
    }),
  );

  harrixCli.activateHarrixCliIntegration({
    context,
    provider,
    rootPath,
    uriToFsPath,
    isDirectoryPath,
    isFilePath,
    normalizeFsPath,
    resolveNotesFolderFsPath,
  });

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.discardGitChangesInFolder', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const folderPath = resolveNotesFolderFsPath(itemUri);
      if (!folderPath) {
        vscode.window.showErrorMessage('Select a folder or a Note/Note.md note in Harrix Notes (HSK).');
        return;
      }

      try {
        await withFolderBusy(provider, folderPath, async () => {
          const { gitRoot, pathspec } = await resolveGitFolderPathspec(folderPath);
          await runGitDiscardWorkflow({
            gitRoot,
            pathspec,
            targetLabel: folderPath,
            cleanRecursive: true,
            confirmTitle: 'Discard all local changes under this folder?',
            successMessage: 'Git discard completed for folder.',
            notTrackedMessage: 'This folder is not tracked by Git. Nothing to discard.',
            logChannel,
            onSuccess: () => provider.refresh(),
          });
        });
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        logChannel.clear();
        logChannel.appendLine('Discard Git changes in folder (failed)');
        logChannel.appendLine(msg);
        logChannel.show(true);
        vscode.window.showErrorMessage(`Discard Git changes failed: ${msg}`);
      }
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.discardGitChangesInNote', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isFilePath(fsPath) || !isMd(path.basename(fsPath))) {
        vscode.window.showErrorMessage('Select a note in Harrix Notes (HSK).');
        return;
      }

      try {
        await withFolderBusy(provider, path.dirname(fsPath), async () => {
          const { gitRoot, pathspec, cleanRecursive } = await resolveGitNotePathspec(fsPath);
          const targetLabel = cleanRecursive ? path.dirname(fsPath) : fsPath;
          await runGitDiscardWorkflow({
            gitRoot,
            pathspec,
            targetLabel,
            cleanRecursive,
            confirmTitle: cleanRecursive
              ? 'Discard all local changes for this note folder?'
              : 'Discard all local changes for this note?',
            successMessage: 'Git discard completed for note.',
            notTrackedMessage: 'This note is not tracked by Git. Nothing to discard.',
            logChannel,
            onSuccess: () => provider.refresh(),
          });
        });
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        logChannel.clear();
        logChannel.appendLine('Discard Git changes in note (failed)');
        logChannel.appendLine(msg);
        logChannel.show(true);
        vscode.window.showErrorMessage(`Discard Git changes failed: ${msg}`);
      }
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.revealInOS', async (treeItemOrUri) => {
      const targetUri = uriFromTreeArgOrActiveEditor(treeItemOrUri);
      if (!targetUri) {
        vscode.window.showErrorMessage('Open a file or select an item in Harrix Notes (HSK).');
        return;
      }

      await vscode.commands.executeCommand('revealFileInOS', targetUri);
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.copyPath', async (treeItemOrUri) => {
      const fsPath = uriToFsPath(uriFromTreeArgOrActiveEditor(treeItemOrUri));
      if (!fsPath) {
        vscode.window.showErrorMessage('Open a file or select an item in Harrix Notes (HSK).');
        return;
      }
      await vscode.env.clipboard.writeText(fsPath);
      vscode.window.setStatusBarMessage('Copied path to clipboard', 1500);
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.copyFilename', async (treeItemOrUri) => {
      const fsPath = uriToFsPath(uriFromTreeArgOrActiveEditor(treeItemOrUri));
      if (!fsPath) {
        vscode.window.showErrorMessage('Open a file or select an item in Harrix Notes (HSK).');
        return;
      }
      const filename = path.basename(fsPath);
      await vscode.env.clipboard.writeText(filename);
      vscode.window.setStatusBarMessage('Copied filename to clipboard', 1500);
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.openInTerminal', async (treeItemOrUri) => {
      const folderUri = folderUriFromTreeArg(treeItemOrUri);
      if (!folderUri) {
        vscode.window.showErrorMessage('Select a note or folder in Harrix Notes (HSK).');
        return;
      }
      openFolderInIntegratedTerminal(folderUri);
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.findInFolder', async (treeItemOrUri) => {
      const folderUri = folderUriFromTreeArg(treeItemOrUri);
      if (!folderUri) {
        vscode.window.showErrorMessage('Select a note or folder in Harrix Notes (HSK).');
        return;
      }
      await vscode.commands.executeCommand('filesExplorer.findInFolder', folderUri);
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.cut', (treeItemOrUri) => {
      const paths = getMovableSourcePathsFromArg(treeItemOrUri, view);
      if (paths.length === 0) {
        vscode.window.showErrorMessage('Select a note or folder in Harrix Notes (HSK).');
        return;
      }
      treeClipboard.set('cut', paths);
      vscode.window.setStatusBarMessage(
        paths.length === 1 ? 'Cut 1 item to clipboard' : `Cut ${paths.length} items to clipboard`,
        1500,
      );
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.copy', (treeItemOrUri) => {
      const paths = getMovableSourcePathsFromArg(treeItemOrUri, view);
      if (paths.length === 0) {
        vscode.window.showErrorMessage('Select a note or folder in Harrix Notes (HSK).');
        return;
      }
      treeClipboard.set('copy', paths);
      vscode.window.setStatusBarMessage(
        paths.length === 1 ? 'Copied 1 item to clipboard' : `Copied ${paths.length} items to clipboard`,
        1500,
      );
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.paste', async (treeItemOrUri) => {
      if (!treeClipboard.canPaste) {
        return;
      }
      const targetDir = getMoveTargetDir(
        provider,
        /** @type {vscode.TreeItem & Record<string, unknown>} */ (treeItemOrUri),
      );
      if (!targetDir) {
        vscode.window.showErrorMessage('Select a folder or note to paste into.');
        return;
      }
      const operation = treeClipboard.operation;
      const paths = [...treeClipboard.paths];
      const transferred = await transferEntriesIntoDir(provider, targetDir, paths, operation || 'copy');
      if (operation === 'cut' && transferred > 0) {
        treeClipboard.clear();
      }
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.createFolder', async (treeItemOrUri) => {
      const folderUri = folderUriFromTreeArg(treeItemOrUri);
      const baseDir =
        treeItemOrUri && typeof treeItemOrUri.dirPath === 'string' && treeItemOrUri.dirPath
          ? treeItemOrUri.dirPath
          : folderUri?.fsPath;
      if (!baseDir || !isDirectoryPath(baseDir)) {
        vscode.window.showErrorMessage('Select a folder in Harrix Notes (HSK).');
        return;
      }

      const name = await vscode.window.showInputBox({
        title: 'New Folder',
        prompt: 'Folder name',
        placeHolder: 'Folder',
      });
      if (!name) {
        return;
      }

      const safeName = sanitizeEntryName(name);
      if (!safeName) {
        vscode.window.showErrorMessage('Invalid folder name.');
        return;
      }

      const dest = path.join(baseDir, safeName);
      if (pathExists(dest)) {
        vscode.window.showErrorMessage(`Already exists: ${safeName}`);
        return;
      }

      try {
        fs.mkdirSync(dest);
        provider.refresh();
        vscode.window.setStatusBarMessage(`Created folder ${safeName}`, 2000);
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`New Folder failed: ${msg}`);
      }
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.addFolderInNote', async (treeItemOrUri) => {
      const noteDir = noteDirFromTreeArg(treeItemOrUri);
      if (!noteDir || !isDirectoryPath(noteDir)) {
        vscode.window.showErrorMessage('Open a markdown note or select one in Harrix Notes (HSK).');
        return;
      }

      const name = await vscode.window.showInputBox({
        title: 'Add Folder',
        prompt: 'Folder name inside the note directory',
        placeHolder: 'img',
      });
      if (!name) {
        return;
      }

      const safeName = sanitizeEntryName(name);
      if (!safeName) {
        vscode.window.showErrorMessage('Invalid folder name.');
        return;
      }

      const dest = path.join(noteDir, safeName);
      if (pathExists(dest)) {
        vscode.window.showErrorMessage(`Already exists: ${safeName}`);
        return;
      }

      try {
        fs.mkdirSync(dest);
        provider.refresh();
        vscode.window.setStatusBarMessage(`Created folder ${safeName}`, 2000);
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Add Folder failed: ${msg}`);
      }
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.addFileInNote', async (treeItemOrUri) => {
      const noteDir = noteDirFromTreeArg(treeItemOrUri);
      if (!noteDir || !isDirectoryPath(noteDir)) {
        vscode.window.showErrorMessage('Open a markdown note or select one in Harrix Notes (HSK).');
        return;
      }

      const name = await vscode.window.showInputBox({
        title: 'Add File',
        prompt: 'File name inside the note directory (with extension if needed)',
        placeHolder: 'readme.txt',
      });
      if (!name) {
        return;
      }

      const safeName = sanitizeEntryName(name);
      if (!safeName) {
        vscode.window.showErrorMessage('Invalid file name.');
        return;
      }

      const dest = path.join(noteDir, safeName);
      if (pathExists(dest)) {
        vscode.window.showErrorMessage(`Already exists: ${safeName}`);
        return;
      }

      try {
        await vscode.workspace.fs.writeFile(vscode.Uri.file(dest), new Uint8Array());
        provider.refresh();
        vscode.window.setStatusBarMessage(`Created file ${safeName}`, 2000);
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Add File failed: ${msg}`);
      }
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.renameItem', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath) return;

      const isDir = isDirectoryPath(fsPath);
      const isFile = isFilePath(fsPath);
      if (!isDir && !isFile) return;

      const parentDir = path.dirname(fsPath);
      const oldBaseName = path.basename(fsPath);
      const isMarkdownFile = isFile && isMd(oldBaseName);

      const fileExt = isFile
        ? isMarkdownFile
          ? isGMd(oldBaseName)
            ? '.g.md'
            : '.md'
          : path.extname(oldBaseName)
        : '';

      const defaultValue = isFile
        ? isMarkdownFile
          ? isGMd(oldBaseName)
            ? oldBaseName.replace(/\.g\.md$/i, '')
            : oldBaseName.replace(/\.md$/i, '')
          : fileExt
            ? oldBaseName.slice(0, oldBaseName.length - fileExt.length)
            : oldBaseName
        : oldBaseName;

      const newName = await vscode.window.showInputBox({
        title: 'Rename',
        prompt: isDir
          ? 'Enter new folder name'
          : isMarkdownFile
            ? 'Enter new note name (without extension)'
            : 'Enter new file name (without extension)',
        value: defaultValue,
      });
      if (!newName) return;

      const safeNew = newName.trim();
      if (!safeNew) return;

      let namedFolderMdPath = null;
      if (isMarkdownFile && isNoteInNamedFolder(fsPath)) {
        namedFolderMdPath = fsPath;
      } else if (isDir) {
        const folderName = path.basename(fsPath);
        const candidateMd = path.join(fsPath, `${folderName}.md`);
        if (pathExists(candidateMd) && isNoteInNamedFolder(candidateMd)) {
          namedFolderMdPath = candidateMd;
        }
      }

      if (namedFolderMdPath) {
        let newStem = safeNew;
        if (newStem.toLowerCase().endsWith('.g.md')) {
          newStem = newStem.slice(0, -5);
        } else if (newStem.toLowerCase().endsWith('.md')) {
          newStem = newStem.slice(0, -3);
        }
        newStem = sanitizeEntryName(newStem);
        if (!newStem) {
          vscode.window.showErrorMessage('Invalid note name.');
          return;
        }
        try {
          const newPath = await renameNamedFolderNote(namedFolderMdPath, newStem);
          provider.refresh();
          await vscode.commands.executeCommand('vscode.open', vscode.Uri.file(newPath));
        } catch (e) {
          const msg = e instanceof Error ? e.message : String(e);
          vscode.window.showErrorMessage(`Rename failed: ${msg}`);
        }
        return;
      }

      let newBaseName = safeNew;
      if (isFile) {
        if (isMarkdownFile) {
          newBaseName = safeNew.toLowerCase().endsWith('.md') ? safeNew : `${safeNew}${fileExt}`;
        } else {
          newBaseName = path.extname(safeNew) ? safeNew : `${safeNew}${fileExt}`;
        }
      }

      const newPath = path.join(parentDir, newBaseName);

      if (newPath === fsPath) return;
      if (pathExists(newPath)) {
        vscode.window.showErrorMessage('Target name already exists.');
        return;
      }

      try {
        await vscode.workspace.fs.rename(vscode.Uri.file(fsPath), vscode.Uri.file(newPath), { overwrite: false });
        provider.refresh();

        if (isFile) {
          await vscode.commands.executeCommand('vscode.open', vscode.Uri.file(newPath));
        }
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Rename failed: ${msg}`);
      }
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.deleteItem', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath) return;

      const isDir = isDirectoryPath(fsPath);
      const isFile = isFilePath(fsPath);
      if (!isDir && !isFile) return;

      const choice = await vscode.window.showWarningMessage(
        `Delete ${isDir ? 'folder' : 'note'} "${path.basename(fsPath)}"?`,
        { modal: true },
        'Delete',
      );
      if (choice !== 'Delete') return;

      await vscode.workspace.fs.delete(vscode.Uri.file(fsPath), { recursive: isDir, useTrash: true });
      provider.refresh();
    }),
  );

  // Auto-refresh when .md files change
  const watcher = vscode.workspace.createFileSystemWatcher('**/*.md');
  const refreshTreeAndIconsBrowse = () => {
    provider.refresh();
    refreshIconsBrowseIfOpen();
  };
  watcher.onDidCreate(refreshTreeAndIconsBrowse);
  watcher.onDidDelete(refreshTreeAndIconsBrowse);
  watcher.onDidChange(refreshTreeAndIconsBrowse);
  context.subscriptions.push(watcher);

  return registerPreviewCopyMarkdownPlugin();
}

function deactivate() {
  stopOpenMediaHttpServer();
}

module.exports = { activate, deactivate };
