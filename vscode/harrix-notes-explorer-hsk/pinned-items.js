/**
 * Pinned folders / notes store — mirrors Harrix Notes Android pinned bar data
 * (`NotesPinnedItems` / `NotesPinnedItemsStore`), adapted for VS Code workspaceState.
 */

const path = require('node:path');
const fs = require('node:fs');

const STORAGE_KEY = 'harrixNotesExplorerHsk.pinnedItems.v1';
const DEFAULT_MAX_ITEMS = 20;
const MIN_MAX_ITEMS = 1;
const MAX_MAX_ITEMS = 50;

/**
 * @typedef {'home' | 'folder' | 'note'} PinnedKind
 */

/**
 * @typedef {object} PinnedItem
 * @property {string} id
 * @property {PinnedKind} kind
 * @property {string} path absolute filesystem path
 * @property {string} title
 * @property {string} [icon] YAML emoji for notes
 * @property {string} [featuredIconPath]
 * @property {string} [fileName]
 */

/**
 * @param {string} p
 * @returns {string}
 */
function normalizePath(p) {
  const resolved = path.resolve(String(p));
  return process.platform === 'win32' ? resolved.toLowerCase() : resolved;
}

/**
 * @param {import('vscode').WorkspaceConfiguration} config
 * @returns {number}
 */
function maxPinnedItemsFromConfig(config) {
  const raw = config.get('pinned.maxItems');
  const n = typeof raw === 'number' && Number.isFinite(raw) ? Math.floor(raw) : DEFAULT_MAX_ITEMS;
  return Math.min(MAX_MAX_ITEMS, Math.max(MIN_MAX_ITEMS, n));
}

/**
 * @param {unknown} raw
 * @returns {PinnedItem | null}
 */
function parseItem(raw) {
  if (!raw || typeof raw !== 'object') {
    return null;
  }
  const obj = /** @type {Record<string, unknown>} */ (raw);
  const kind = obj.kind;
  if (kind !== 'home' && kind !== 'folder' && kind !== 'note') {
    return null;
  }
  const itemPath = typeof obj.path === 'string' ? obj.path.trim() : '';
  if (!itemPath) {
    return null;
  }
  const id =
    typeof obj.id === 'string' && obj.id.trim()
      ? obj.id.trim()
      : kind === 'home'
        ? `home:${normalizePath(itemPath)}`
        : normalizePath(itemPath);
  return {
    id,
    kind,
    path: itemPath,
    title: typeof obj.title === 'string' ? obj.title : '',
    icon: typeof obj.icon === 'string' ? obj.icon : '',
    featuredIconPath: typeof obj.featuredIconPath === 'string' ? obj.featuredIconPath : '',
    fileName: typeof obj.fileName === 'string' ? obj.fileName : '',
  };
}

/**
 * @param {import('vscode').ExtensionContext} context
 * @param {{
 *   getConfiguration: () => import('vscode').WorkspaceConfiguration,
 * }} opts
 */
function createPinnedStore(context, opts) {
  /** @returns {PinnedItem[]} */
  function loadRaw() {
    const saved = context.workspaceState.get(STORAGE_KEY);
    if (!Array.isArray(saved)) {
      return [];
    }
    /** @type {PinnedItem[]} */
    const items = [];
    for (const row of saved) {
      const item = parseItem(row);
      if (item) {
        items.push(item);
      }
    }
    return items;
  }

  /**
   * @param {PinnedItem[]} items
   */
  async function persist(items) {
    const max = maxPinnedItemsFromConfig(opts.getConfiguration());
    const trimmed = items.slice(0, max).map((item) => ({
      id: item.id,
      kind: item.kind,
      path: item.path,
      title: item.title || '',
      icon: item.icon || '',
      featuredIconPath: item.featuredIconPath || '',
      fileName: item.fileName || '',
    }));
    await context.workspaceState.update(STORAGE_KEY, trimmed);
  }

  /**
   * @param {string} fsPath
   * @returns {boolean}
   */
  function isDirectory(fsPath) {
    try {
      return fs.statSync(fsPath).isDirectory();
    } catch {
      return false;
    }
  }

  /**
   * @param {string} fsPath
   * @returns {boolean}
   */
  function isFile(fsPath) {
    try {
      return fs.statSync(fsPath).isFile();
    } catch {
      return false;
    }
  }

  /**
   * Drop missing paths; keep titles/icons as stored (caller may refresh metadata).
   * @returns {Promise<{ items: PinnedItem[], changed: boolean }>}
   */
  async function pruneMissing() {
    const before = loadRaw();
    const items = before.filter((item) => {
      if (item.kind === 'note') {
        return isFile(item.path);
      }
      return isDirectory(item.path);
    });
    const changed = items.length !== before.length;
    if (changed) {
      await persist(items);
    }
    return { items, changed };
  }

  /**
   * @returns {PinnedItem[]}
   */
  function list() {
    const max = maxPinnedItemsFromConfig(opts.getConfiguration());
    return loadRaw().slice(0, max);
  }

  /**
   * @param {string} fsPath
   * @returns {boolean}
   */
  function isPinned(fsPath) {
    if (!fsPath) {
      return false;
    }
    const key = normalizePath(fsPath);
    return list().some((item) => normalizePath(item.path) === key);
  }

  /**
   * @param {string} idOrPath
   * @returns {boolean}
   */
  function isPinnedId(idOrPath) {
    if (!idOrPath) {
      return false;
    }
    const key = String(idOrPath);
    const pathKey = normalizePath(key);
    return list().some((item) => item.id === key || normalizePath(item.path) === pathKey);
  }

  /**
   * @param {Omit<PinnedItem, 'id'> & { id?: string }} item
   * @returns {Promise<{ ok: boolean, reason?: string, items: PinnedItem[] }>}
   */
  async function pin(item) {
    const max = maxPinnedItemsFromConfig(opts.getConfiguration());
    const items = list();
    if (isPinned(item.path)) {
      return { ok: false, reason: 'already', items };
    }
    if (items.length >= max) {
      return { ok: false, reason: 'full', items };
    }
    const kind = item.kind;
    const id = item.id || (kind === 'home' ? `home:${normalizePath(item.path)}` : normalizePath(item.path));
    const next = [
      ...items,
      {
        id,
        kind,
        path: item.path,
        title: item.title || '',
        icon: item.icon || '',
        featuredIconPath: item.featuredIconPath || '',
        fileName: item.fileName || '',
      },
    ];
    await persist(next);
    return { ok: true, items: next };
  }

  /**
   * @param {string} idOrPath
   * @returns {Promise<{ ok: boolean, items: PinnedItem[] }>}
   */
  async function unpin(idOrPath) {
    const key = String(idOrPath || '');
    const pathKey = key ? normalizePath(key) : '';
    const before = list();
    const items = before.filter((item) => item.id !== key && normalizePath(item.path) !== pathKey);
    if (items.length === before.length) {
      return { ok: false, items };
    }
    await persist(items);
    return { ok: true, items };
  }

  /**
   * @param {string} idOrPath
   * @param {-1 | 1} delta
   * @returns {Promise<{ ok: boolean, items: PinnedItem[] }>}
   */
  async function move(idOrPath, delta) {
    const items = list();
    const key = String(idOrPath || '');
    const pathKey = key ? normalizePath(key) : '';
    const index = items.findIndex((item) => item.id === key || normalizePath(item.path) === pathKey);
    if (index < 0) {
      return { ok: false, items };
    }
    const nextIndex = index + delta;
    if (nextIndex < 0 || nextIndex >= items.length) {
      return { ok: false, items };
    }
    const next = [...items];
    const [row] = next.splice(index, 1);
    next.splice(nextIndex, 0, row);
    await persist(next);
    return { ok: true, items: next };
  }

  /**
   * @param {string} idOrPath
   * @param {Partial<PinnedItem>} patch
   * @returns {Promise<PinnedItem[]>}
   */
  async function updateItem(idOrPath, patch) {
    const key = String(idOrPath || '');
    const pathKey = key ? normalizePath(key) : '';
    const items = list().map((item) => {
      if (item.id !== key && normalizePath(item.path) !== pathKey) {
        return item;
      }
      return {
        ...item,
        ...patch,
        id: item.id,
        kind: item.kind,
        path: typeof patch.path === 'string' && patch.path ? patch.path : item.path,
      };
    });
    await persist(items);
    return items;
  }

  return {
    list,
    isPinned,
    isPinnedId,
    pin,
    unpin,
    move,
    updateItem,
    pruneMissing,
    maxItems: () => maxPinnedItemsFromConfig(opts.getConfiguration()),
    STORAGE_KEY,
  };
}

module.exports = {
  STORAGE_KEY,
  DEFAULT_MAX_ITEMS,
  MIN_MAX_ITEMS,
  MAX_MAX_ITEMS,
  normalizePath,
  createPinnedStore,
};
