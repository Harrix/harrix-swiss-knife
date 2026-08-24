/**
 * Resolve note title and date from Markdown metadata.
 *
 * @hsk-sync:note-meta — keep behavior aligned with:
 * - `harrix_pylib.note_meta`
 * - `harrix-notes-android` `NoteMetaResolver` / `NoteTitleExtractor`
 *
 * Title priority: YAML `title` → first `#` heading → `titleFromId(fileStem)`.
 * Date priority: date in file name → YAML `date` → file ctime → file mtime.
 */

const path = require('node:path');
const fs = require('node:fs');

const FRONTMATTER_RE = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/;
const TITLE_LINE_RE = /^title\s*:\s*(.*)$/i;
const DATE_LINE_RE = /^date\s*:\s*(.*)$/i;
const H1_RE = /^#\s+(.+)$/;
const DATE_IN_NAME_RE =
  /(?:(?<y4>\d{4})[.-](?<m4>\d{2})[.-](?<d4>\d{2})|(?<y8>\d{4})(?<m8>\d{2})(?<d8>\d{2})|(?<dEu>\d{2})\.(?<mEu>\d{2})\.(?<yEu>\d{4}))/;

/**
 * @param {string} fileName
 * @returns {string}
 */
function noteStemFromName(fileName) {
  const base = path.basename(String(fileName || ''));
  if (base.toLowerCase().endsWith('.g.md')) {
    return base.slice(0, -5);
  }
  if (base.toLowerCase().endsWith('.md')) {
    return base.replace(/\.md$/i, '');
  }
  return base.replace(/\.[^.]+$/, '');
}

/**
 * @param {string} value
 * @returns {string}
 */
function unquoteYamlScalar(value) {
  let v = String(value ?? '').trim();
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
    v = v.slice(1, -1);
  }
  return v.trim();
}

/**
 * @param {string} text
 * @returns {string}
 */
function stripHtmlComments(text) {
  return String(text ?? '')
    .replace(/<!--[\s\S]*?-->/g, '')
    .trim();
}

/**
 * @param {string} text
 * @returns {string}
 */
function stripBom(text) {
  const src = String(text ?? '');
  return src.charCodeAt(0) === 0xfeff ? src.slice(1) : src;
}

/**
 * @param {string} fmText
 * @returns {string}
 */
function titleFromFrontmatterBlock(fmText) {
  for (const line of String(fmText ?? '').split(/\r?\n/)) {
    const m = TITLE_LINE_RE.exec(line);
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
 * @returns {string}
 */
function firstH1AfterFrontmatter(body) {
  const lines = String(body ?? '').split(/\r?\n/);
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
    if (line.startsWith('##')) {
      continue;
    }
    const h1 = H1_RE.exec(line);
    if (h1) {
      return h1[1].trim();
    }
  }
  return '';
}

/**
 * @param {string} mdText
 * @returns {string}
 */
function extractTitleFromMarkdown(mdText) {
  const src = stripBom(mdText);
  const fmMatch = FRONTMATTER_RE.exec(src);
  let title = '';
  if (fmMatch) {
    title = titleFromFrontmatterBlock(fmMatch[1]) || firstH1AfterFrontmatter(src.slice(fmMatch[0].length));
  } else {
    title = firstH1AfterFrontmatter(src);
  }
  return stripHtmlComments(title);
}

/**
 * @param {string} fileStem
 * @returns {string}
 */
function titleFromId(fileStem) {
  const stem = String(fileStem ?? '').trim();
  if (!stem) {
    return '';
  }
  const sep = stem.indexOf('__');
  const slug = sep === -1 ? stem : stem.slice(sep + 2);
  return pythonTitle(slug.replace(/-/g, ' ').replace(/_/g, ' '));
}

/**
 * @param {string} text
 * @returns {string}
 */
function pythonTitle(text) {
  let out = '';
  let cap = true;
  for (const ch of text) {
    if (/\p{L}/u.test(ch)) {
      out += cap ? ch.toUpperCase() : ch.toLowerCase();
      cap = false;
    } else {
      out += ch;
      cap = true;
    }
  }
  return out;
}

/**
 * @param {string} mdText
 * @param {{ fileStem?: string }} [opts]
 * @returns {string}
 */
function resolveNoteTitle(mdText, opts = {}) {
  const fromContent = extractTitleFromMarkdown(mdText);
  if (fromContent) {
    return fromContent;
  }
  const human = titleFromId(opts.fileStem ?? '');
  return human || 'Untitled';
}

/**
 * @param {RegExpMatchArray} match
 * @returns {string | null} YYYY-MM-DD
 */
function isoDateFromMatch(match) {
  const g = match.groups || {};
  let y;
  let m;
  let d;
  if (g.y4) {
    y = g.y4;
    m = g.m4;
    d = g.d4;
  } else if (g.y8) {
    y = g.y8;
    m = g.m8;
    d = g.d8;
  } else if (g.yEu) {
    y = g.yEu;
    m = g.mEu;
    d = g.dEu;
  } else {
    return null;
  }
  const yi = Number(y);
  const mi = Number(m);
  const di = Number(d);
  if (!yi || mi < 1 || mi > 12 || di < 1 || di > 31) {
    return null;
  }
  const dt = new Date(Date.UTC(yi, mi - 1, di));
  if (dt.getUTCFullYear() !== yi || dt.getUTCMonth() !== mi - 1 || dt.getUTCDate() !== di) {
    return null;
  }
  return `${y}-${m}-${d}`;
}

/**
 * @param {string} fileName
 * @returns {string | null} YYYY-MM-DD
 */
function parseDateFromFileName(fileName) {
  const stem = noteStemFromName(fileName);
  const match = DATE_IN_NAME_RE.exec(stem);
  if (!match) {
    return null;
  }
  return isoDateFromMatch(match);
}

const YEAR_NAME_RE = /^(\d{4})$/;
const YEAR_MONTH_NAME_RE = /^(\d{4})[-.](\d{2})$/;
const DATE_NAME_YEAR_MIN = 1900;
const DATE_NAME_YEAR_MAX = 2100;

/**
 * Numeric key for year / date file or folder names (`2026`, `2026-10`, `2026-10-11`).
 * Higher values are more recent. Returns `null` when the name is not a date.
 *
 * @param {string} name
 * @returns {number | null} YYYYMMDD (missing month/day padded with `00`)
 */
function dateNameSortKey(name) {
  const stem = noteStemFromName(name);
  const iso = parseDateFromFileName(stem);
  if (iso) {
    return Number(iso.replace(/-/g, ''));
  }
  const yearMonth = YEAR_MONTH_NAME_RE.exec(stem);
  if (yearMonth) {
    const year = Number(yearMonth[1]);
    const month = Number(yearMonth[2]);
    if (year >= DATE_NAME_YEAR_MIN && year <= DATE_NAME_YEAR_MAX && month >= 1 && month <= 12) {
      return year * 10000 + month * 100;
    }
  }
  const yearOnly = YEAR_NAME_RE.exec(stem);
  if (yearOnly) {
    const year = Number(yearOnly[1]);
    if (year >= DATE_NAME_YEAR_MIN && year <= DATE_NAME_YEAR_MAX) {
      return year * 10000;
    }
  }
  return null;
}

/**
 * Compare labels; when both names are years or dates, newest comes first.
 *
 * @param {string} aName
 * @param {string} bName
 * @param {string} [aLabel]
 * @param {string} [bLabel]
 * @returns {number}
 */
function compareNamesNewestDatesFirst(aName, bName, aLabel, bLabel) {
  const aKey = dateNameSortKey(aName);
  const bKey = dateNameSortKey(bName);
  if (aKey != null && bKey != null && aKey !== bKey) {
    return bKey - aKey;
  }
  return String(aLabel || aName || '').localeCompare(String(bLabel || bName || ''), undefined, {
    numeric: true,
    sensitivity: 'base',
  });
}

/**
 * @param {unknown} value
 * @returns {string | null} YYYY-MM-DD
 */
function parseDateValue(value) {
  if (value == null) {
    return null;
  }
  if (value instanceof Date && !Number.isNaN(value.getTime())) {
    const y = value.getFullYear();
    const m = String(value.getMonth() + 1).padStart(2, '0');
    const d = String(value.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }
  const text = String(value).trim();
  if (!text) {
    return null;
  }
  const token = text.split(/\s+/)[0];
  const match = DATE_IN_NAME_RE.exec(token);
  if (match) {
    return isoDateFromMatch(match);
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(token)) {
    return token;
  }
  return null;
}

/**
 * @param {string} mdText
 * @returns {string | null} YYYY-MM-DD
 */
function parseDateFromYaml(mdText) {
  const src = stripBom(mdText);
  const fmMatch = FRONTMATTER_RE.exec(src);
  if (!fmMatch) {
    return null;
  }
  for (const line of fmMatch[1].split(/\r?\n/)) {
    const m = DATE_LINE_RE.exec(line.trim());
    if (!m) {
      continue;
    }
    const parsed = parseDateValue(unquoteYamlScalar(m[1]));
    if (parsed) {
      return parsed;
    }
  }
  return null;
}

/**
 * @param {number | Date | null | undefined} value
 * @returns {string | null} YYYY-MM-DD
 */
function isoDateFromTimestamp(value) {
  if (value == null) {
    return null;
  }
  const dt = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(dt.getTime())) {
    return null;
  }
  const y = dt.getFullYear();
  const m = String(dt.getMonth() + 1).padStart(2, '0');
  const d = String(dt.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

/**
 * @param {string} mdText
 * @param {{
 *   fileName?: string,
 *   ctimeMs?: number | null,
 *   mtimeMs?: number | null,
 * }} [opts]
 * @returns {{ value: string, source: 'filename' | 'yaml' | 'file_ctime' | 'file_mtime' } | null}
 */
function resolveNoteDate(mdText, opts = {}) {
  const fileName = String(opts.fileName ?? '');
  const fromName = parseDateFromFileName(fileName);
  if (fromName) {
    return { value: fromName, source: 'filename' };
  }
  const fromYaml = parseDateFromYaml(mdText);
  if (fromYaml) {
    return { value: fromYaml, source: 'yaml' };
  }
  const fromCtime = isoDateFromTimestamp(opts.ctimeMs);
  if (fromCtime) {
    return { value: fromCtime, source: 'file_ctime' };
  }
  const fromMtime = isoDateFromTimestamp(opts.mtimeMs);
  if (fromMtime) {
    return { value: fromMtime, source: 'file_mtime' };
  }
  return null;
}

/**
 * @param {string} filePath
 * @param {string | null} [mdText]
 * @returns {{ value: string, source: 'filename' | 'yaml' | 'file_ctime' | 'file_mtime' } | null}
 */
function resolveNoteDateForPath(filePath, mdText = null) {
  let text = mdText;
  let ctimeMs = null;
  let mtimeMs = null;
  try {
    const st = fs.statSync(filePath);
    ctimeMs = st.birthtimeMs > 0 ? st.birthtimeMs : st.ctimeMs;
    mtimeMs = st.mtimeMs;
    if (text == null) {
      const fd = fs.openSync(filePath, 'r');
      const buf = Buffer.alloc(16 * 1024);
      const read = fs.readSync(fd, buf, 0, buf.length, 0);
      fs.closeSync(fd);
      text = buf.slice(0, read).toString('utf8');
    }
  } catch {
    text = text ?? '';
  }
  return resolveNoteDate(text || '', {
    fileName: path.basename(filePath),
    ctimeMs,
    mtimeMs,
  });
}

/**
 * @param {string} fmText
 * @returns {string}
 */
function iconFromFrontmatterBlock(fmText) {
  for (const line of String(fmText ?? '').split(/\r?\n/)) {
    const m = /^icon\s*:\s*(.*)$/i.exec(line);
    if (!m) {
      continue;
    }
    const icon = unquoteYamlScalar(m[1]);
    if (icon && isNoteTreeEmojiIcon(icon)) {
      return icon;
    }
  }
  return '';
}

/**
 * @param {string} value
 * @returns {boolean}
 */
function isNoteTreeEmojiIcon(value) {
  const v = String(value ?? '').trim();
  if (!v || [...v].length > 8) {
    return false;
  }
  if (/^https?:\/\//i.test(v) || /[\\/]/.test(v)) {
    return false;
  }
  if (/\.(png|jpe?g|gif|svg|webp|avif|ico)$/i.test(v)) {
    return false;
  }
  return true;
}

/**
 * @param {string} text
 * @returns {{ title: string, icon: string }}
 */
function extractNoteMetaFromMarkdown(text) {
  const src = stripBom(text);
  const fmMatch = FRONTMATTER_RE.exec(src);
  let title = '';
  let icon = '';
  if (fmMatch) {
    title = titleFromFrontmatterBlock(fmMatch[1]) || firstH1AfterFrontmatter(src.slice(fmMatch[0].length));
    icon = iconFromFrontmatterBlock(fmMatch[1]);
  } else {
    title = firstH1AfterFrontmatter(src);
  }
  return { title: stripHtmlComments(title), icon };
}

module.exports = {
  noteStemFromName,
  extractTitleFromMarkdown,
  titleFromId,
  resolveNoteTitle,
  dateNameSortKey,
  compareNamesNewestDatesFirst,
  parseDateFromFileName,
  parseDateFromYaml,
  parseDateValue,
  resolveNoteDate,
  resolveNoteDateForPath,
  extractNoteMetaFromMarkdown,
  titleFromFrontmatterBlock,
  firstH1AfterFrontmatter,
  iconFromFrontmatterBlock,
  isNoteTreeEmojiIcon,
  unquoteYamlScalar,
  stripHtmlComments,
};
