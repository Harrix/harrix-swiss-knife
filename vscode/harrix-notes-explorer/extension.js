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
  let rel = path.relative(gitRoot, resolved);
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
  return stOut ? stOut.split(/\r?\n/).map((l) => l.trimEnd()).filter(Boolean) : [];
}

/**
 * @param {{ gitRoot: string, pathspec: string, targetLabel: string, cleanRecursive: boolean, confirmTitle: string, successMessage: string, notTrackedMessage: string, logChannel: vscode.OutputChannel, onSuccess?: () => void }} opts
 */
async function runGitDiscardWorkflow(opts) {
  const { gitRoot, pathspec, targetLabel, cleanRecursive, confirmTitle, successMessage, logChannel, onSuccess } =
    opts;
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
    vscode.window.showInformationMessage(String(opts.notTrackedMessage || 'This path is not tracked by Git. Nothing to discard.'));
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
        : '• Untracked copy of this file: permanently deleted.'
    );
  }
  confirmLines.push('• Ignored files: not touched.', '', targetLabel);

  const confirm = await vscode.window.showWarningMessage(
    confirmLines.join('\n'),
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
  if (hasTracked) {
    logChannel.appendLine(`> git restore --source=HEAD --staged --worktree -- ${restoreSpec}`);
    const restore = await gitExecInRepo(gitRoot, [
      'restore',
      '--source=HEAD',
      '--staged',
      '--worktree',
      '--',
      restoreSpec
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

const NOTE_TITLE_READ_BYTES = 16 * 1024;

function getShowNoteTitleFromContent() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
  return config.get('showNoteTitleFromContent', true) !== false;
}

/**
 * @param {string} filePath
 */
function noteStemFromPath(filePath) {
  const base = path.basename(filePath);
  if (base.toLowerCase().endsWith('.g.md')) {
    return base.slice(0, -5);
  }
  return base.replace(/\.md$/i, '');
}

/**
 * @param {string} value
 */
function unquoteYamlScalar(value) {
  let v = String(value ?? '').trim();
  if (
    (v.startsWith('"') && v.endsWith('"')) ||
    (v.startsWith("'") && v.endsWith("'"))
  ) {
    v = v.slice(1, -1);
  }
  return v.trim();
}

/**
 * @param {string} fmText
 */
function titleFromFrontmatterBlock(fmText) {
  for (const line of fmText.split(/\r?\n/)) {
    const m = /^title\s*:\s*(.*)$/i.exec(line);
    if (!m) {
      continue;
    }
    const title = unquoteYamlScalar(m[1]);
    if (title) {
      return title;
    }
  }
  return '';
}

/**
 * @param {string} body
 */
function firstH1AfterFrontmatter(body) {
  const lines = body.split(/\r?\n/);
  let inFence = false;
  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      continue;
    }
    if (line.startsWith('```')) {
      inFence = !inFence;
      continue;
    }
    if (inFence) {
      continue;
    }
    if (line.startsWith('<!--') && line.includes('-->')) {
      continue;
    }
    const h1 = /^#\s+(.+)$/.exec(line);
    if (h1 && !line.startsWith('##')) {
      return h1[1].trim();
    }
  }
  return '';
}

/**
 * @param {string} text
 */
function extractNoteTitleFromMarkdown(text) {
  let src = String(text ?? '');
  if (src.charCodeAt(0) === 0xfeff) {
    src = src.slice(1);
  }
  const fmMatch = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(src);
  if (fmMatch) {
    const fromYaml = titleFromFrontmatterBlock(fmMatch[1]);
    if (fromYaml) {
      return fromYaml;
    }
    const fromH1 = firstH1AfterFrontmatter(src.slice(fmMatch[0].length));
    if (fromH1) {
      return fromH1;
    }
    return '';
  }
  return firstH1AfterFrontmatter(src);
}

/** Caches note tree labels by file path and mtime. */
class NoteTitleCache {
  constructor() {
    /** @type {Map<string, { mtimeMs: number, label: string }>} */
    this._entries = new Map();
  }

  clear() {
    this._entries.clear();
  }

  /**
   * @param {string} filePath
   */
  getLabel(filePath) {
    const key = normalizeFsPath(filePath);
    const stem = noteStemFromPath(filePath);
    let mtimeMs = 0;
    try {
      mtimeMs = fs.statSync(filePath).mtimeMs;
    } catch {
      return stem;
    }

    const cached = this._entries.get(key);
    if (cached && cached.mtimeMs === mtimeMs) {
      return cached.label;
    }

    let label = stem;
    try {
      const fd = fs.openSync(filePath, 'r');
      const buf = Buffer.alloc(NOTE_TITLE_READ_BYTES);
      const read = fs.readSync(fd, buf, 0, NOTE_TITLE_READ_BYTES, 0);
      fs.closeSync(fd);
      const text = buf.slice(0, read).toString('utf8');
      const title = extractNoteTitleFromMarkdown(text);
      if (title) {
        label = title;
      }
    } catch {
      // keep stem
    }

    this._entries.set(key, { mtimeMs, label });
    return label;
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
  return noteTitleCache.getLabel(filePath);
}

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

const DEFAULT_ASSET_FOLDER_NAMES = ['images', 'files', 'img', 'assets', 'attachments', 'media'];

function getAssetFolderNames() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
  const raw = config.get('assetFolderNames', DEFAULT_ASSET_FOLDER_NAMES);
  if (!Array.isArray(raw) || raw.length === 0) {
    return new Set(DEFAULT_ASSET_FOLDER_NAMES.map((x) => x.toLowerCase()));
  }
  return new Set(
    raw.map((x) => String(x).trim().toLowerCase()).filter(Boolean)
  );
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
  const subVisibleMd = sub.filter(
    (e) => e.isFile() && isMd(e.name) && !isMergedTemplateGmd(e.name, folderName)
  );
  const subFolders = sub.filter(
    (e) =>
      e.isDirectory() &&
      (hasMarkdownRecursive(path.join(noteDir, e.name)) || isSpecialNotesFolderName(e.name))
  );
  return subVisibleMd.length === 1 && subFolders.length === 0;
}

/**
 * Parent folder that actually contains this note in the Harrix Notes tree.
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
  '.m4v'
];

function getNoteDropSettings() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
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
  const imagesFolder =
    String(config.get('noteDrop.imagesFolderName', 'img') || 'img').trim() || 'img';
  const filesFolder =
    String(config.get('noteDrop.filesFolderName', 'files') || 'files').trim() || 'files';
  return {
    moveIntoNamedFolder: config.get('noteDrop.moveIntoNamedFolder', true) !== false,
    copyAllToNoteRoot: config.get('noteDrop.copyAllToNoteRoot', false) === true,
    imagesFolderName: sanitizeEntryName(imagesFolder) || 'img',
    filesFolderName: sanitizeEntryName(filesFolder) || 'files',
    imageExtensions
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
    overwrite: false
  });
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
 * Persists note folders whose attachments are shown in the tree.
 */
class NoteAssetsVisibility {
  /**
   * @param {vscode.ExtensionContext} context
   */
  constructor(context) {
    this._context = context;
    this._key = 'harrixNotesExplorer.noteAssetsVisible.v1';
    const stored = context.workspaceState.get(this._key);
    this.visible = new Set(
      Array.isArray(stored) ? stored.map((x) => normalizeFsPath(String(x))) : []
    );
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

/** @param {unknown} treeItemOrUri */
function noteDirFromTreeArg(treeItemOrUri) {
  const uri = noteUriFromTreeArg(treeItemOrUri);
  if (!uri || !isFilePath(uri.fsPath)) {
    return undefined;
  }
  return path.dirname(uri.fsPath);
}

/**
 * @param {string} raw
 */
function sanitizeEntryName(raw) {
  const name = String(raw ?? '').trim().replace(/[<>:"/\\|?*\u0000-\u001f]/g, '_').trim();
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
  const group = vscode.window.tabGroups.all.find(
    (g) => (g.viewColumn ?? vscode.ViewColumn.One) === viewColumn
  );
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
      preserveFocus: false
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
        preserveFocus: false
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

function getOpenInEditorSplit() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
  return config.get('openInEditorSplit', true) !== false;
}

function getOpenInPreviewSplit() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorer');
  return config.get('openInPreviewSplit', true) !== false;
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

  const openSource = async (viewColumn = vscode.ViewColumn.Active) => {
    try {
      await vscode.window.showTextDocument(uri, {
        viewColumn,
        preview: false,
        preserveFocus: false
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
    if (getOpenInEditorSplit()) {
      await openHarrixNoteSplit(uri, 'editorLeft');
    } else {
      await openSource(vscode.ViewColumn.Active);
    }
    return;
  }

  if (mode === 'preview') {
    if (getOpenInPreviewSplit()) {
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
        locked: true
      });
    } catch {
      await openSource(vscode.ViewColumn.One);
    }
  } else {
    await openSource(vscode.ViewColumn.Active);
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
   * @param {NoteAssetsVisibility | null} assetsVisibility
   */
  constructor(rootPath, expansionMemory, assetsVisibility) {
    this.rootPath = rootPath;
    /** @type {FolderExpansionMemory | null} */
    this._expansion = expansionMemory;
    /** @type {NoteAssetsVisibility | null} */
    this._assetsVisibility = assetsVisibility;
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
    noteTitleCache.clear();
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

  /** @param {string} noteDir */
  isNoteAssetsVisible(noteDir) {
    return this._assetsVisibility != null && this._assetsVisibility.isVisible(noteDir);
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

  getTreeItem(el) { return el; }

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
    return labelToString(a.label).localeCompare(labelToString(b.label), undefined, {
      numeric: true,
      sensitivity: 'base'
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
    const rel = path.relative(this.rootPath, folderPath);
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
      if (normalizeFsPath(parentDir) === normalizeFsPath(this.rootPath)) {
        return undefined;
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
          element.parentNoteMdPath
        );
      }
    }

    if (element.dirPath && element.folderDepth && !element.isAssetFolder) {
      const parentDir = path.dirname(element.dirPath);
      if (
        normalizeFsPath(parentDir) === normalizeFsPath(element.dirPath) ||
        normalizeFsPath(parentDir) === normalizeFsPath(this.rootPath)
      ) {
        return undefined;
      }
      const depth =
        typeof element.folderDepth === 'number' ? Math.max(1, element.folderDepth - 1) : 1;
      return this.createFolderItem(parentDir, path.basename(parentDir), depth);
    }

    return undefined;
  }

  getChildren(element) {
    if (element?.isNoteItem && element.noteDirPath && this.isNoteAssetsVisible(element.noteDirPath)) {
      const noteMdPath = element.resourceUri?.fsPath;
      return this.getNoteAssetChildren(element.noteDirPath, noteMdPath);
    }
    if (element?.isAssetFolder && element.dirPath) {
      return this.getAssetFolderChildren(
        element.dirPath,
        element.noteDirPath,
        element.parentNoteMdPath
      );
    }

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
        items.push(this.createFileItem(sameNameMdPath));
      } else {
        items.push(this.createFolderItem(folderPath, folder.name, parentFolderDepth + 1));
      }
    }

    // --- .md files ---
    for (const file of mdFiles) {
      const filePath = path.join(dir, file.name);
      items.push(this.createFileItem(filePath));
    }

    return items.sort((a, b) => this.sortTreeItems(a, b));
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

  createFileItem(filePath) {
    const noteDir = path.dirname(filePath);
    const stem = noteStemFromPath(filePath);
    const displayName = getNoteDisplayLabel(filePath);
    const assetsVisible = this.isNoteAssetsVisible(noteDir);
    const item = new vscode.TreeItem(
      displayName,
      assetsVisible
        ? vscode.TreeItemCollapsibleState.Expanded
        : vscode.TreeItemCollapsibleState.None
    );
    item.id = `note:${normalizeFsPath(filePath)}`;
    item.resourceUri = vscode.Uri.file(filePath);
    item.noteDirPath = noteDir;
    item.isNoteItem = true;
    if (displayName !== stem) {
      item.description = stem;
    }
    item.command = {
      command: 'harrixNotesExplorer.openNote',
      title: 'Open',
      arguments: [vscode.Uri.file(filePath)]
    };
    const tooltipLines = [filePath];
    if (displayName !== stem) {
      tooltipLines.push(`File: ${stem}`);
    }
    tooltipLines.push(
      '',
      'Drop files to copy into this note (featured-image → root, images → img, others → files).'
    );
    item.tooltip = tooltipLines.join('\n');

    item.iconPath = new vscode.ThemeIcon('markdown');
    if (assetsVisible) {
      item.contextValue = 'noteWithAssets';
    } else if (noteDirHasAttachments(noteDir)) {
      item.contextValue = 'noteHasAttachments';
    } else {
      item.contextValue = 'note';
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
      arguments: [item.resourceUri]
    };
    const ext = path.extname(displayName).toLowerCase();
    const imageExts = new Set(['.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif', '.svg', '.bmp', '.ico']);
    item.iconPath = imageExts.has(ext)
      ? vscode.Uri.file(filePath)
      : new vscode.ThemeIcon('file');
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
    const item = new vscode.TreeItem(name, vscode.TreeItemCollapsibleState.Collapsed);
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
 */
async function revealNoteWithAttachments(view, provider, filePath) {
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
    await view.reveal(revealItem, { expand: true, select: true, focus: false });
  } catch {
    // ignore
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
    2500
  );
}

/** @param {NotesProvider} provider */
function createNoteAssetsDragAndDrop(provider) {
  return {
    dropMimeTypes: ['text/uri-list', 'application/vnd.code.uri-list', 'files'],
    dragMimeTypes: [],

    /** @param {vscode.TreeItem} target */
    async handleDrop(target, dataTransfer, _token) {
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
    }
  };
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
    copiedColor: normalizePreviewCopyColor(config.get('previewCopy.copiedColor', '#388a34'), '#388a34'),
    collapseFrontmatter: config.get('previewFrontmatter.collapse', true) !== false,
    frontmatterSummary: normalizePreviewFrontmatterSummary(config.get('previewFrontmatter.summary', '📋 YAML'))
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
      if (
        !e.affectsConfiguration('harrixNotesExplorer.previewCopy') &&
        !e.affectsConfiguration('harrixNotesExplorer.previewFrontmatter')
      ) {
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

  const assetsVisibility = new NoteAssetsVisibility(context);

  const provider = new NotesProvider(rootPath, expansionMemory, assetsVisibility);
  const view = vscode.window.createTreeView('harrixNotesExplorer', {
    treeDataProvider: provider,
    showCollapseAll: true,
    dragAndDropController: createNoteAssetsDragAndDrop(provider)
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
      if (
        e.affectsConfiguration('harrixNotesExplorer.rememberFolderExpansion') ||
        e.affectsConfiguration('harrixNotesExplorer.showNoteTitleFromContent')
      ) {
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
    vscode.commands.registerCommand('harrixNotesExplorer.showNoteAssets', async (treeItemOrUri) => {
      const uri = noteUriFromTreeArg(treeItemOrUri);
      if (!uri || !isFilePath(uri.fsPath)) {
        return;
      }
      const noteDir = path.dirname(uri.fsPath);
      if (!noteDirHasAttachments(noteDir)) {
        void vscode.window.showInformationMessage(
          'No attachments in this note folder (no featured image and no asset folders such as images or files).'
        );
        return;
      }
      const refreshDone = waitForTreeRefresh(provider);
      provider.setNoteAssetsVisible(noteDir, true);
      await refreshDone;
      await revealNoteWithAttachments(view, provider, uri.fsPath);
    })
  );
  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.hideNoteAssets', (treeItemOrUri) => {
      const uri = noteUriFromTreeArg(treeItemOrUri);
      if (!uri || !isFilePath(uri.fsPath)) {
        return;
      }
      provider.setNoteAssetsVisible(path.dirname(uri.fsPath), false);
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
          await runGitDiscardWorkflow({
            gitRoot,
            pathspec,
            targetLabel: fsPath,
            cleanRecursive: true,
            confirmTitle: 'Discard all local changes under this folder?',
            successMessage: 'Git discard completed for folder.',
            notTrackedMessage: 'This folder is not tracked by Git. Nothing to discard.',
            logChannel,
            onSuccess: () => provider.refresh()
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
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.discardGitChangesInNote', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isFilePath(fsPath) || !isMd(path.basename(fsPath))) {
        vscode.window.showErrorMessage('Select a note in Harrix Notes.');
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
            onSuccess: () => provider.refresh()
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
    vscode.commands.registerCommand('harrixNotesExplorer.addFolderInNote', async (treeItemOrUri) => {
      const noteDir = noteDirFromTreeArg(treeItemOrUri);
      if (!noteDir || !isDirectoryPath(noteDir)) {
        vscode.window.showErrorMessage('Choose a note in Harrix Notes.');
        return;
      }

      const name = await vscode.window.showInputBox({
        title: 'Add folder',
        prompt: 'Folder name inside the note directory',
        placeHolder: 'img'
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
        vscode.window.showErrorMessage(`Add folder failed: ${msg}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorer.addFileInNote', async (treeItemOrUri) => {
      const noteDir = noteDirFromTreeArg(treeItemOrUri);
      if (!noteDir || !isDirectoryPath(noteDir)) {
        vscode.window.showErrorMessage('Choose a note in Harrix Notes.');
        return;
      }

      const name = await vscode.window.showInputBox({
        title: 'Add file',
        prompt: 'File name inside the note directory (with extension if needed)',
        placeHolder: 'readme.txt'
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
        vscode.window.showErrorMessage(`Add file failed: ${msg}`);
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


