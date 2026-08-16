/**
 * Filter and sort Icons Browse entries.
 *
 * @hsk-sync:notes-browse — keep aligned with
 * `D:\GitHub\harrix-notes-android` `NotesListingOptions` / `NotesBrowseLayout` /
 * `NotesSortBy` and the folder **Sort and view** menu.
 */

/**
 * @typedef {{
 *   layout: 'icons' | 'list' | 'thumbnails',
 *   sortBy: 'name' | 'date' | 'size',
 *   foldersFirst: boolean,
 *   reverseOrder: boolean,
 *   showGmdFiles: boolean,
 *   showDates: boolean,
 * }} BrowseOptions
 */

/**
 * @param {string | undefined} name
 * @returns {boolean}
 */
function isGmdFileName(name) {
  return String(name || '')
    .toLowerCase()
    .endsWith('.g.md');
}

/**
 * @param {unknown} raw
 * @returns {'icons' | 'list' | 'thumbnails'}
 */
function parseLayout(raw) {
  const value = String(raw || '')
    .trim()
    .toLowerCase();
  if (value === 'list' || value === 'thumbnails') {
    return value;
  }
  return 'icons';
}

/**
 * @param {unknown} raw
 * @returns {'name' | 'date' | 'size'}
 */
function parseSortBy(raw) {
  const value = String(raw || '')
    .trim()
    .toLowerCase();
  if (value === 'date' || value === 'size') {
    return value;
  }
  return 'name';
}

/**
 * @param {{ get: (key: string) => unknown }} config
 * @returns {BrowseOptions}
 */
function browseOptionsFromConfig(config) {
  return {
    layout: parseLayout(config.get('iconsBrowse.layout')),
    sortBy: parseSortBy(config.get('iconsBrowse.sortBy')),
    foldersFirst: config.get('iconsBrowse.foldersFirst') === true,
    reverseOrder: config.get('iconsBrowse.reverseOrder') === true,
    showGmdFiles: config.get('iconsBrowse.showGmdFiles') === true,
    showDates: config.get('iconsBrowse.showDates') === true,
  };
}

/**
 * @param {string} isoDate YYYY-MM-DD
 * @returns {string} dd.MM.yyyy
 */
function formatListDate(isoDate) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(isoDate || ''));
  if (!m) {
    return '';
  }
  return `${m[3]}.${m[2]}.${m[1]}`;
}

/**
 * @param {number} epochMs
 * @returns {string} dd.MM.yyyy, HH:mm
 */
function formatListDateTime(epochMs) {
  const dt = new Date(epochMs);
  if (Number.isNaN(dt.getTime())) {
    return '';
  }
  const dd = String(dt.getDate()).padStart(2, '0');
  const mm = String(dt.getMonth() + 1).padStart(2, '0');
  const yyyy = String(dt.getFullYear());
  const hh = String(dt.getHours()).padStart(2, '0');
  const min = String(dt.getMinutes()).padStart(2, '0');
  return `${dd}.${mm}.${yyyy}, ${hh}:${min}`;
}

/**
 * @param {{
 *   kind: string,
 *   dateSource?: string,
 *   dateValue?: string,
 *   mtimeMs?: number,
 * }} entry
 * @returns {string}
 */
function formatBrowseDate(entry) {
  if (entry.kind === 'note' && (entry.dateSource === 'filename' || entry.dateSource === 'yaml') && entry.dateValue) {
    return formatListDate(entry.dateValue);
  }
  if (typeof entry.mtimeMs === 'number' && entry.mtimeMs > 0) {
    return formatListDateTime(entry.mtimeMs);
  }
  return '';
}

/**
 * @param {{
 *   kind: string,
 *   isGmd?: boolean,
 *   description?: string,
 *   dateSource?: string,
 *   dateValue?: string,
 *   mtimeMs?: number,
 * }} entry
 * @param {BrowseOptions} options
 * @returns {string}
 */
function browseCaption(entry, options) {
  const parts = [];
  if (entry.isGmd) {
    parts.push('.g.md');
  }
  if (entry.description) {
    parts.push(entry.description);
  }
  if (options.showDates && options.layout === 'list') {
    const dateText = formatBrowseDate(entry);
    if (dateText) {
      parts.push(dateText);
    }
  }
  return parts.join(' · ');
}

/**
 * @template {{ kind: string, isGmd?: boolean, sortLabel?: string, label?: string, name?: string, mtimeMs?: number, sizeBytes?: number }} T
 * @param {T[]} entries
 * @param {Pick<BrowseOptions, 'sortBy' | 'foldersFirst' | 'reverseOrder' | 'showGmdFiles'>} options
 * @returns {T[]}
 */
function applyListingOptions(entries, options) {
  const filtered = options.showGmdFiles ? entries : entries.filter((entry) => entry.kind !== 'note' || !entry.isGmd);

  const nameCmp = (a, b) =>
    String(a.sortLabel || a.label || a.name || '').localeCompare(
      String(b.sortLabel || b.label || b.name || ''),
      undefined,
      {
        sensitivity: 'base',
      },
    );

  const fieldCmp = (a, b) => {
    if (options.sortBy === 'date') {
      const delta = (a.mtimeMs || 0) - (b.mtimeMs || 0);
      return delta !== 0 ? delta : nameCmp(a, b);
    }
    if (options.sortBy === 'size') {
      const delta = (a.sizeBytes || 0) - (b.sizeBytes || 0);
      return delta !== 0 ? delta : nameCmp(a, b);
    }
    return nameCmp(a, b);
  };
  const ordered = options.reverseOrder ? (a, b) => fieldCmp(b, a) : fieldCmp;

  return filtered.slice().sort((a, b) => {
    if (options.foldersFirst) {
      const af = a.kind === 'folder' ? 0 : 1;
      const bf = b.kind === 'folder' ? 0 : 1;
      if (af !== bf) {
        return af - bf;
      }
    }
    return ordered(a, b);
  });
}

const TOC_DETAILS_BLOCK = /<details\b[^>]*>[\s\S]*?<\/details>/gi;
const TOC_HINT = /содержан|оглавлени|table\s+of\s+contents|\bcontents\b/i;
const TOC_HEADING = /^(?:содержание|оглавление|contents|table of contents)$/i;
const TOC_HASH_LINK = /^\[[^\]]+\]\(#[^)]+\)$/;
const DETAILS_OR_SUMMARY_TAG = /^<\/?(?:details|summary)\b/i;

/**
 * Drop collapsible TOC (`<details>` with Contents / Содержание) and leftover TOC lines.
 *
 * @param {string} text
 * @returns {string}
 */
function stripTocBlocks(text) {
  return String(text || '').replace(TOC_DETAILS_BLOCK, (block) => (TOC_HINT.test(block) ? '' : block));
}

/**
 * @param {string} raw
 * @returns {boolean}
 */
function isTocOnlyLine(raw) {
  const line = String(raw || '').trim();
  if (!line || DETAILS_OR_SUMMARY_TAG.test(line)) {
    return true;
  }
  const heading = line
    .replace(/^#{1,6}\s+/, '')
    .replace(/<[^>]+>/g, '')
    .replace(/[`*_]/g, '')
    .replace(/[^\p{L}\p{N}\s]/gu, '')
    .replace(/\s+/g, ' ')
    .trim();
  if (TOC_HEADING.test(heading)) {
    return true;
  }
  const withoutList = line
    .replace(/^[-*+]\s+/, '')
    .replace(/^\d+\.\s+/, '')
    .trim();
  return TOC_HASH_LINK.test(withoutList);
}

/**
 * Plain-text card preview from Markdown (Samsung Notes-style thumbnails).
 *
 * @param {string} text
 * @param {number} [maxLen]
 * @returns {string}
 */
function excerptFromMarkdown(text, maxLen = 220) {
  let src = String(text || '').replace(/^\uFEFF/, '');
  src = src.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, '');
  src = src.replace(/<!--[\s\S]*?-->/g, '');
  src = stripTocBlocks(src);
  const lines = [];
  for (const raw of src.split(/\r?\n/)) {
    let line = raw.trim();
    if (!line || /^```/.test(line) || isTocOnlyLine(line)) {
      continue;
    }
    line = line
      .replace(/^#{1,6}\s+/, '')
      .replace(/^[-*+]\s+/, '')
      .replace(/^\d+\.\s+/, '')
      .replace(/!\[[^\]]*\]\([^)]+\)/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/[`*_>#]/g, '')
      .trim();
    if (line) {
      lines.push(line);
    }
    if (lines.join(' ').length >= maxLen) {
      break;
    }
  }
  const out = lines.join(' ');
  if (out.length > maxLen) {
    return `${out.slice(0, maxLen).trim()}…`;
  }
  return out;
}

/**
 * First local Markdown image target (`![alt](path)`), or empty.
 *
 * @param {string} text
 * @returns {string}
 */
function firstMarkdownImageSrc(text) {
  let src = String(text || '').replace(/^\uFEFF/, '');
  src = src.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, '');
  const re = /!\[[^\]]*]\(([^)]+)\)/g;
  let match = re.exec(src);
  while (match) {
    const raw = String(match[1] || '')
      .trim()
      .replace(/^<|>$/g, '')
      .split(/\s+/)[0];
    if (raw && !/^(https?:|data:|mailto:)/i.test(raw)) {
      return raw;
    }
    match = re.exec(src);
  }
  return '';
}

module.exports = {
  applyListingOptions,
  browseCaption,
  browseOptionsFromConfig,
  excerptFromMarkdown,
  firstMarkdownImageSrc,
  formatBrowseDate,
  formatListDate,
  formatListDateTime,
  isGmdFileName,
  parseLayout,
  parseSortBy,
};
