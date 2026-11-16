const fs = require('node:fs');
const path = require('node:path');
const noteMeta = require('./note-meta');

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
 * @param {string} dir
 * @returns {import('node:fs').Dirent[]}
 */
function safeReaddir(dir) {
  try {
    return fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return [];
  }
}

/** @param {string} name */
function isMd(name) {
  return name.toLowerCase().endsWith('.md');
}

/** @param {string} name */
function isGMd(name) {
  return name.toLowerCase().endsWith('.g.md');
}

/**
 * Merged-folder template only: exactly `_<parentFolderName>.g.md` (case-insensitive).
 * Other `*.g.md` stay visible.
 * @param {string} fileName
 * @param {string} parentFolderBasename
 */
function isMergedTemplateGmd(fileName, parentFolderBasename) {
  if (!isGMd(fileName)) {
    return false;
  }
  const expected = `_${parentFolderBasename}.g.md`.toLowerCase();
  return fileName.toLowerCase() === expected;
}

/** Folder named `Diary` / `Dreams` / `Cases` (case-insensitive). */
function isSpecialNotesFolderName(name) {
  const lower = String(name).toLowerCase();
  return lower === 'diary' || lower === 'dreams' || lower === 'cases';
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
 * Folder is listable when it has a `.md` note or a descendant folder that does
 * (`@hsk-sync:notes-browse`, same idea as Android `directoryHasMarkdownNotes`).
 * @param {string} dir
 * @param {number} [depth]
 */
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
 * @param {{
 *   templateCountFor?: (folderPath: string) => number,
 *   isSpecialFolderName?: (name: string) => boolean,
 *   folderListedWithoutMarkdown?: (folderName: string, templateTargetCount: number) => boolean,
 * }} [opts]
 * @returns {Array<{ kind: 'folder' | 'note', path: string, name: string }>}
 */
function collectNotesDirChildSpecs(dir, opts) {
  const templateCountFor = opts?.templateCountFor || (() => 0);
  const isSpecial = opts?.isSpecialFolderName || isSpecialNotesFolderName;
  const listedWithoutMd = opts?.folderListedWithoutMarkdown || folderListedWithoutMarkdown;
  if (!dir || !fs.existsSync(dir)) {
    return [];
  }

  const entries = safeReaddir(dir);
  const folders = entries
    .filter((e) => e.isDirectory())
    .filter(
      (e) =>
        hasMarkdownRecursive(path.join(dir, e.name)) ||
        listedWithoutMd(e.name, templateCountFor(path.join(dir, e.name))),
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
          isSpecial(e.name),
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
    specs.push({ kind: 'note', path: path.join(dir, file.name), name: noteMeta.noteStemFromName(file.name) });
  }

  return specs;
}

/**
 * Folder shown as a single note item (`Folder/Folder.md` with no visible subfolders).
 * @param {string} filePath absolute path to the .md file
 * @param {(p: string) => string} normalizeFsPath
 * @param {(name: string) => boolean} [isSpecialFolderName]
 */
function isCollapsedFolderNote(filePath, normalizeFsPath, isSpecialFolderName) {
  const isSpecial = isSpecialFolderName || isSpecialNotesFolderName;
  const noteDir = path.dirname(filePath);
  const folderName = path.basename(noteDir);
  const sameNameMdPath = path.join(noteDir, `${folderName}.md`);
  if (normalizeFsPath(sameNameMdPath) !== normalizeFsPath(filePath)) {
    return false;
  }
  const sub = safeReaddir(noteDir);
  const subVisibleMd = sub.filter((e) => e.isFile() && isMd(e.name) && !isMergedTemplateGmd(e.name, folderName));
  const subFolders = sub.filter(
    (e) => e.isDirectory() && (hasMarkdownRecursive(path.join(noteDir, e.name)) || isSpecial(e.name)),
  );
  return subVisibleMd.length === 1 && subFolders.length === 0;
}

/**
 * Parent folder that actually contains this note in the Harrix Notes (HSK) tree.
 * @param {string} filePath
 * @param {(p: string) => string} normalizeFsPath
 * @param {(name: string) => boolean} [isSpecialFolderName]
 */
function getNoteTreeParentDir(filePath, normalizeFsPath, isSpecialFolderName) {
  if (isCollapsedFolderNote(filePath, normalizeFsPath, isSpecialFolderName)) {
    return path.dirname(path.dirname(filePath));
  }
  return path.dirname(filePath);
}

module.exports = {
  SKIP_MARKDOWN_SCAN_DIR_NAMES,
  safeReaddir,
  isMd,
  isGMd,
  isMergedTemplateGmd,
  isSpecialNotesFolderName,
  folderListedWithoutMarkdown,
  hasMarkdownRecursive,
  collectNotesDirChildSpecs,
  isCollapsedFolderNote,
  getNoteTreeParentDir,
};
