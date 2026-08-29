/**
 * Jupyter notebook note preview (read-only, GitHub-like).
 *
 * `@hsk-sync:jupyter-notebook` — keep aligned with harrix-notes-android
 * (`JupyterNotebook`, `JupyterHtml`).
 */

const fs = require('node:fs');
const path = require('node:path');

const FRONTMATTER_RE = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/;
const MD_LINK_RE = /(!)?\[([^\]]*)]\(([^)]+)\)/g;
const ANGLE_LINK_RE = /<([^>\s]+\.ipynb)>/gi;
const JUPYTER_TYPES = new Set(['jupyter', 'ipynb', 'notebook']);

/**
 * YAML `type: jupyter` / `ipynb` / `notebook`.
 * @param {string} source
 * @returns {boolean}
 */
function isJupyterMarkdown(source) {
  const fm = FRONTMATTER_RE.exec(String(source || '').replace(/^\uFEFF/, ''));
  if (!fm) {
    return false;
  }
  for (const line of fm[1].split(/\r?\n/)) {
    const m = /^type\s*:\s*(.*)$/i.exec(line.trim());
    if (m && JUPYTER_TYPES.has(unquote(m[1]).toLowerCase())) {
      return true;
    }
  }
  return false;
}

/**
 * First Markdown / autolink pointing at a `.ipynb` file.
 * @param {string} source
 * @returns {string}
 */
function findNotebookRelativePath(source) {
  const text = stripFrontmatter(String(source || ''));
  MD_LINK_RE.lastIndex = 0;
  let match = MD_LINK_RE.exec(text);
  while (match) {
    const isImage = match[1] === '!';
    const href = stripLinkHref(match[3]);
    if (!isImage && isIpynbHref(href)) {
      return href;
    }
    match = MD_LINK_RE.exec(text);
  }
  ANGLE_LINK_RE.lastIndex = 0;
  const angle = ANGLE_LINK_RE.exec(text);
  if (angle && isIpynbHref(angle[1])) {
    return stripLinkHref(angle[1]);
  }
  return '';
}

/**
 * Empty nbformat 4 notebook with a markdown title cell.
 * @param {string} title
 * @returns {string}
 */
function emptyNotebookJson(title) {
  const heading = String(title || '').trim() || 'Notebook';
  const notebook = {
    nbformat: 4,
    nbformat_minor: 5,
    metadata: {
      kernelspec: {
        display_name: 'Python 3',
        language: 'python',
        name: 'python3',
      },
      language_info: { name: 'python' },
    },
    cells: [
      {
        cell_type: 'markdown',
        metadata: {},
        source: [`# ${heading}\n`],
      },
    ],
  };
  return `${JSON.stringify(notebook, null, 1)}\n`;
}

/**
 * @param {string} markdown
 * @param {string | undefined} noteFsPath
 * @param {(md: string) => string} renderMarkdown
 * @returns {string}
 */
function renderJupyterPreviewHtml(markdown, noteFsPath, renderMarkdown) {
  const noteDir = noteFsPath ? path.dirname(noteFsPath) : '';
  const notebookPath = resolveNotebookPath(markdown, noteDir);
  if (!notebookPath) {
    return '';
  }
  let raw = '';
  try {
    raw = fs.readFileSync(notebookPath, 'utf8');
  } catch {
    return `<div class="hne-nb-missing">Could not read notebook: ${escapeHtml(path.basename(notebookPath))}</div>`;
  }
  let notebook;
  try {
    notebook = JSON.parse(raw);
  } catch {
    return `<div class="hne-nb-missing">Notebook JSON is invalid: ${escapeHtml(path.basename(notebookPath))}</div>`;
  }
  const language = notebookLanguage(notebook);
  const cells = Array.isArray(notebook.cells) ? notebook.cells : [];
  const inner = cells.map((cell, index) => renderCell(cell, index, language, renderMarkdown)).join('\n');
  const name = escapeHtml(path.basename(notebookPath));
  return `<div class="hne-nb"><div class="hne-nb-file">${name}</div>${inner}</div>`;
}

/**
 * @param {string} markdown
 * @param {string} noteDir
 * @returns {string}
 */
function resolveNotebookPath(markdown, noteDir) {
  if (!noteDir) {
    return '';
  }
  const rel = findNotebookRelativePath(markdown);
  if (rel) {
    const abs = path.normalize(path.join(noteDir, rel));
    if (pathExists(abs)) {
      return abs;
    }
  }
  const fromFiles = firstIpynbInDir(path.join(noteDir, 'files'));
  if (fromFiles) {
    return fromFiles;
  }
  return firstIpynbInDir(noteDir);
}

function firstIpynbInDir(dir) {
  let names = [];
  try {
    names = fs.readdirSync(dir);
  } catch {
    return '';
  }
  const found = names.find((name) => name.toLowerCase().endsWith('.ipynb'));
  if (!found) {
    return '';
  }
  const abs = path.join(dir, found);
  try {
    if (fs.statSync(abs).isFile()) {
      return abs;
    }
  } catch {
    return '';
  }
  return '';
}

function pathExists(filePath) {
  try {
    return fs.statSync(filePath).isFile();
  } catch {
    return false;
  }
}

function notebookLanguage(notebook) {
  const info = notebook?.metadata?.language_info?.name;
  if (typeof info === 'string' && info.trim()) {
    return info.trim().toLowerCase();
  }
  const kernel = notebook?.metadata?.kernelspec?.language;
  if (typeof kernel === 'string' && kernel.trim()) {
    return kernel.trim().toLowerCase();
  }
  return 'python';
}

function renderCell(cell, index, language, renderMarkdown) {
  const kind = String(cell?.cell_type || 'code').toLowerCase();
  if (kind === 'markdown') {
    const html = renderMarkdown(cellSource(cell) || ' ');
    return `<div class="hne-nb-cell hne-nb-md" data-index="${index}">${html}</div>`;
  }
  if (kind === 'raw') {
    return `<div class="hne-nb-cell hne-nb-raw" data-index="${index}"><pre>${escapeHtml(cellSource(cell))}</pre></div>`;
  }
  const count = cell?.execution_count;
  const prompt = count == null || count === '' ? ' ' : String(count);
  const codeHtml = renderMarkdown(`\`\`\`${language}\n${cellSource(cell)}\n\`\`\`\n`);
  const outputs = Array.isArray(cell?.outputs) ? cell.outputs : [];
  const outHtml = outputs.map((output) => renderOutput(output, renderMarkdown)).join('');
  return (
    `<div class="hne-nb-cell hne-nb-code" data-index="${index}">` +
    `<div class="hne-nb-input"><div class="hne-nb-prompt">In [${escapeHtml(prompt)}]:</div>` +
    `<div class="hne-nb-source">${codeHtml}</div></div>` +
    (outHtml ? `<div class="hne-nb-outputs">${outHtml}</div>` : '') +
    `</div>`
  );
}

function renderOutput(output, renderMarkdown) {
  const type = String(output?.output_type || '').toLowerCase();
  if (type === 'stream') {
    const cls = String(output.name || '').toLowerCase() === 'stderr' ? 'hne-nb-stderr' : 'hne-nb-stdout';
    return `<pre class="${cls}">${escapeHtml(joinText(output.text))}</pre>`;
  }
  if (type === 'error') {
    const ename = escapeHtml(String(output.ename || 'Error'));
    const evalue = escapeHtml(String(output.evalue || ''));
    const tb = Array.isArray(output.traceback) ? output.traceback.map(stripAnsi).join('\n') : '';
    return `<pre class="hne-nb-error">${ename}: ${evalue}\n${escapeHtml(tb)}</pre>`;
  }
  const data = output?.data && typeof output.data === 'object' ? output.data : {};
  return renderMimeBundle(data, renderMarkdown);
}

function renderMimeBundle(data, renderMarkdown) {
  if (typeof data['text/html'] !== 'undefined') {
    return `<div class="hne-nb-html">${sanitizeHtml(joinText(data['text/html']))}</div>`;
  }
  if (typeof data['image/png'] !== 'undefined') {
    return mimeImage('image/png', data['image/png']);
  }
  if (typeof data['image/jpeg'] !== 'undefined') {
    return mimeImage('image/jpeg', data['image/jpeg']);
  }
  if (typeof data['image/svg+xml'] !== 'undefined') {
    return `<div class="hne-nb-svg">${sanitizeHtml(joinText(data['image/svg+xml']))}</div>`;
  }
  if (typeof data['text/markdown'] !== 'undefined') {
    return `<div class="hne-nb-md-out">${renderMarkdown(joinText(data['text/markdown']) || ' ')}</div>`;
  }
  if (typeof data['text/plain'] !== 'undefined') {
    return `<pre class="hne-nb-plain">${escapeHtml(joinText(data['text/plain']))}</pre>`;
  }
  return '';
}

function mimeImage(mime, value) {
  const b64 = joinText(value).replace(/\s+/g, '');
  if (!b64) {
    return '';
  }
  return `<img class="hne-nb-image" src="data:${mime};base64,${escapeHtmlAttr(b64)}" alt="" />`;
}

function cellSource(cell) {
  return joinText(cell?.source);
}

function joinText(value) {
  if (Array.isArray(value)) {
    return value.map((part) => String(part ?? '')).join('');
  }
  if (value == null) {
    return '';
  }
  return String(value);
}

function stripFrontmatter(source) {
  const text = String(source || '').replace(/^\uFEFF/, '');
  const fm = FRONTMATTER_RE.exec(text);
  return fm ? text.slice(fm[0].length) : text;
}

function stripLinkHref(raw) {
  let href = String(raw || '').trim();
  const space = href.search(/\s+/);
  if (space > 0) {
    href = href.slice(0, space);
  }
  href = href.replace(/^<|>$/g, '').replace(/^['"]|['"]$/g, '');
  return href.replace(/\\/g, '/').replace(/^\.\//, '');
}

function isIpynbHref(href) {
  const cleaned = String(href || '')
    .split('?')[0]
    .split('#')[0]
    .trim()
    .toLowerCase();
  return cleaned.endsWith('.ipynb');
}

function unquote(value) {
  let v = String(value || '').trim();
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
    v = v.slice(1, -1);
  }
  return v.trim();
}

function stripAnsi(text) {
  return String(text || '').replace(new RegExp(`${String.fromCharCode(27)}\\[[0-9;]*m`, 'g'), '');
}

function sanitizeHtml(html) {
  return String(html || '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<iframe[\s\S]*?<\/iframe>/gi, '')
    .replace(/<object[\s\S]*?<\/object>/gi, '')
    .replace(/<embed\b[^>]*>/gi, '')
    .replace(/\son\w+\s*=/gi, ' ')
    .replace(/javascript:/gi, '');
}

function escapeHtml(text) {
  return String(text || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function escapeHtmlAttr(text) {
  return escapeHtml(text).replace(/'/g, '&#39;');
}

module.exports = {
  emptyNotebookJson,
  findNotebookRelativePath,
  isJupyterMarkdown,
  renderJupyterPreviewHtml,
};
