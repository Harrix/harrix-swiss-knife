/**
 * In-extension New note (no hsk CLI).
 *
 * @hsk-sync:new-note — keep aligned with OnNewMarkdown and harrix-notes-android.
 */

const vscode = require('vscode');
const path = require('node:path');
const fs = require('node:fs');

const PERSONAL_FRONTMATTER_KEYS = new Set(['author', 'author-email']);

const DEFAULT_BEGINNING_TEMPLATES = [
  {
    id: 'beginning-of-md',
    label: 'beginning-of-md.md',
    content: '---\nlang: ru\n---\n',
  },
  {
    id: 'beginning-of-article',
    label: 'beginning-of-article.md',
    content:
      '---\ndate: [DATE]\ncategories: [it]\ntags: []\nlicense: CC BY 4.0\nlicense-url: <YOUR_LICENSE_URL>\npermalink-source: <YOUR_PERMALINK_SOURCE>/[YEAR]/blob/main/[NAME]/[NAME].md\npermalink: <YOUR_SITE>/articles/[YEAR]/[NAME]/\nlang: ru\n---\n',
  },
  {
    id: 'beginning-of-md-en',
    label: 'beginning-of-md-en.md',
    content: '---\nlang: en\n---\n',
  },
];

/**
 * @returns {{ enabled: boolean, author: string, authorEmail: string }}
 */
function getPersonalDataSettings() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  return {
    enabled: config.get('personalData.enabled') === true,
    author: String(config.get('personalData.author') ?? 'noname'),
    authorEmail: String(config.get('personalData.authorEmail') ?? ''),
  };
}

/**
 * @returns {Array<{ id: string, label: string, content: string }>}
 */
function getBeginningTemplates() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  const raw = config.get('newNote.beginningTemplates');
  if (!Array.isArray(raw) || raw.length === 0) {
    return DEFAULT_BEGINNING_TEMPLATES.map((t) => ({ ...t }));
  }
  const templates = [];
  for (const item of raw) {
    if (!item || typeof item !== 'object') {
      continue;
    }
    const id = String(item.id || '').trim();
    const label = String(item.label || id || 'template').trim() || 'template';
    const content = String(item.content ?? '');
    if (!id && !content) {
      continue;
    }
    templates.push({ id: id || label, label, content });
  }
  return templates.length > 0 ? templates : DEFAULT_BEGINNING_TEMPLATES.map((t) => ({ ...t }));
}

/**
 * @param {Array<{ id: string, label: string, content: string }>} templates
 * @returns {{ id: string, label: string, content: string } | undefined}
 */
function resolveDefaultTemplate(templates) {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  const defaultId = String(config.get('newNote.defaultBeginningTemplateId') || '').trim();
  if (defaultId) {
    const found = templates.find((t) => t.id === defaultId || t.label === defaultId);
    if (found) {
      return found;
    }
  }
  return templates[0];
}

/**
 * Merge or strip author / author-email in YAML frontmatter.
 * @hsk-sync:new-note
 *
 * @param {string} beginning
 * @param {{ enabled: boolean, author: string, authorEmail: string }} personal
 * @returns {string}
 */
function applyPersonalDataToBeginning(beginning, personal) {
  const text = beginning || '';
  if (!text.trim()) {
    return text;
  }

  const enabled = personal.enabled === true;
  const author = personal.author != null ? String(personal.author) : 'noname';
  const authorEmail = personal.authorEmail != null ? String(personal.authorEmail) : '';

  const stripped = text.replace(/^\uFEFF/, '');
  if (!stripped.startsWith('---')) {
    if (!enabled) {
      return text;
    }
    const lines = ['---', `author: ${author}`];
    if (authorEmail) {
      lines.push(`author-email: ${authorEmail}`);
    }
    lines.push('---');
    return `${lines.join('\n')}\n${stripped.replace(/^\n+/, '')}`;
  }

  const lines = stripped.split(/\r?\n/);
  let endIdx = -1;
  for (let i = 1; i < lines.length; i += 1) {
    if (lines[i].trim() === '---') {
      endIdx = i;
      break;
    }
  }
  if (endIdx < 0) {
    return text;
  }

  /** @type {string[]} */
  const bodyLines = [];
  for (const line of lines.slice(1, endIdx)) {
    const key = line.includes(':') ? line.split(':', 1)[0].trim().toLowerCase() : '';
    if (PERSONAL_FRONTMATTER_KEYS.has(key)) {
      continue;
    }
    bodyLines.push(line);
  }

  if (enabled) {
    let insertAt = 0;
    for (let i = 0; i < bodyLines.length; i += 1) {
      if (bodyLines[i].split(':', 1)[0].trim().toLowerCase() === 'lang') {
        insertAt = i;
        break;
      }
      insertAt = i + 1;
    }
    const personalLines = [`author: ${author}`];
    if (authorEmail) {
      personalLines.push(`author-email: ${authorEmail}`);
    }
    bodyLines.splice(insertAt, 0, ...personalLines);
  }

  const rebuilt = ['---', ...bodyLines, '---', ...lines.slice(endIdx + 1)];
  let result = rebuilt.join('\n');
  if (text.endsWith('\n')) {
    result += '\n';
  }
  return result;
}

/**
 * @param {string} stem
 * @returns {string}
 */
function sanitizeNoteStem(stem) {
  return String(stem).replace(/-/g, '--').replace(/ /g, '-');
}

/**
 * @param {string} beginning
 * @param {string} headingStem
 * @returns {string}
 */
function buildNewNoteContent(beginning, headingStem) {
  const withPersonal = applyPersonalDataToBeginning(beginning, getPersonalDataSettings());
  return `${withPersonal.replace(/\s+$/, '')}\n# ${headingStem}\n\n\n`;
}

/**
 * Create `{folder}/{stem}/{stem}.md` like h.md.add_note.
 *
 * @param {string} baseDir
 * @param {string} rawName
 * @param {string} content
 * @returns {string} absolute path to the new .md file
 */
function writeNewNoteFiles(baseDir, rawName, content) {
  let stemRaw = rawName.trim();
  if (!stemRaw) {
    throw new Error('Empty note name');
  }
  if (stemRaw.toLowerCase().endsWith('.md')) {
    stemRaw = stemRaw.slice(0, -3);
  }
  const folderStem = sanitizeNoteStem(stemRaw);
  const noteDir = path.join(path.resolve(baseDir), folderStem);
  const noteMd = path.join(noteDir, `${folderStem}.md`);
  fs.mkdirSync(noteDir, { recursive: true });
  fs.writeFileSync(noteMd, content, 'utf8');
  return noteMd;
}

/**
 * @param {Array<{ id: string, label: string, content: string }>} templates
 * @returns {Promise<{ id: string, label: string, content: string } | undefined>}
 */
async function pickBeginningTemplate(templates) {
  if (templates.length === 1) {
    return templates[0];
  }
  const defaultTemplate = resolveDefaultTemplate(templates);
  const items = templates.map((t) => ({
    label: t.label,
    description: t.id === defaultTemplate?.id ? 'default' : undefined,
    template: t,
  }));
  const picked = await vscode.window.showQuickPick(items, {
    title: 'Select Beginning Template',
    placeHolder: 'Choose a beginning template',
  });
  return picked?.template;
}

/**
 * @typedef {object} NewNoteDeps
 * @property {import('vscode').ExtensionContext} context
 * @property {{ refresh: () => void }} provider
 * @property {string} [rootPath]
 * @property {(uri: unknown) => string | undefined} uriToFsPath
 * @property {(fsPath: string) => boolean} isDirectoryPath
 * @property {(fsPath: string) => boolean} isFilePath
 */

/**
 * Register in-extension New note command.
 * @hsk-sync:new-note
 *
 * @param {NewNoteDeps} deps
 */
function activateNewNote(deps) {
  const { context, provider, rootPath, uriToFsPath, isDirectoryPath, isFilePath } = deps;

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.createNote', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);

      const baseDir =
        fsPath && isDirectoryPath(fsPath)
          ? fsPath
          : fsPath && isFilePath(fsPath)
            ? path.dirname(fsPath)
            : typeof rootPath === 'string' && rootPath
              ? rootPath
              : '';

      if (!baseDir) {
        vscode.window.showErrorMessage('Select a folder in Harrix Notes (HSK).');
        return;
      }

      const name = await vscode.window.showInputBox({
        title: 'New Note',
        prompt: 'Enter note name (without extension)',
        placeHolder: 'My-note',
      });
      if (!name) {
        return;
      }

      const safeName = name.trim();
      if (!safeName) {
        return;
      }

      const templates = getBeginningTemplates();
      const selected = await pickBeginningTemplate(templates);
      if (!selected) {
        return;
      }

      let headingStem = safeName;
      if (headingStem.toLowerCase().endsWith('.md')) {
        headingStem = headingStem.slice(0, -3);
      }

      try {
        const content = buildNewNoteContent(selected.content, headingStem);
        const noteMd = writeNewNoteFiles(baseDir, safeName, content);
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(noteMd));
        await vscode.window.showTextDocument(doc);
        provider.refresh();
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`New Note failed: ${msg}`);
      }
    }),
  );
}

module.exports = {
  activateNewNote,
  applyPersonalDataToBeginning,
  buildNewNoteContent,
  sanitizeNoteStem,
  DEFAULT_BEGINNING_TEMPLATES,
};
