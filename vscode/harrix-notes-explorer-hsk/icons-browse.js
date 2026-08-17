/**
 * Icons Browse — editor-area WebviewPanel for folder drill-down (Android-like grid/list).
 *
 * @hsk-sync:notes-browse — layout, sort, and the Sort and view menu stay aligned with
 * Harrix Notes Android (`NotesBrowseLayout`, `NotesListingOptions`, folder overflow).
 */

const vscode = require('vscode');
const path = require('node:path');
const fs = require('node:fs');
const { execFile } = require('node:child_process');
const { buildIconsBrowseContextMenu } = require('./icons-browse-menu');
const listing = require('./icons-browse-listing');
const noteMeta = require('./note-meta');

const PANEL_VIEW_TYPE = 'harrixNotesExplorerHsk.iconsBrowse';
const ICONS_BROWSE_FOLDER_KEY = 'harrixNotesExplorerHsk.iconsBrowse.currentFolder.v1';

/**
 * @typedef {{ path: string, name: string }} IconsBrowseCrumb
 */

/**
 * @typedef {object} IconsBrowseDeps
 * @property {import('vscode').ExtensionContext} context
 * @property {{
 *   rootEntries: Array<{ path: string, name: string }>,
 *   rootPath: string | undefined,
 *   listIconsBrowseEntries: (dirPath: string | null | undefined) => Array<{
 *     kind: 'folder' | 'note',
 *     path: string,
 *     name: string,
 *     label: string,
 *     iconEmoji: string,
 *     description: string,
 *     contextValue?: string,
 *     isWorkspaceRoot?: boolean,
 *   }>,
 *   getIconsBrowseFolderEntry?: (dirPath: string | null | undefined) => {
 *     kind: 'folder',
 *     path: string,
 *     name: string,
 *     label: string,
 *     contextValue: string,
 *     isWorkspaceRoot: boolean,
 *   } | null,
 *   onDidChangeTreeData: import('vscode').Event<unknown>,
 *   refresh?: () => void,
 * }} provider
 * @property {(uri: import('vscode').Uri) => Promise<void>} openNote
 * @property {() => boolean} [getCanPaste]
 * @property {() => string[]} [getCutPaths]
 */

/** @type {import('vscode').WebviewPanel | undefined} */
let panel;
/** @type {IconsBrowseCrumb[]} */
let crumbs = [];
/** @type {IconsBrowseDeps | undefined} */
let deps;

function killLeftoverFileDragHelpers() {
  if (process.platform !== 'win32') {
    return;
  }
  execFile(
    'powershell.exe',
    [
      '-NoProfile',
      '-WindowStyle',
      'Hidden',
      '-Command',
      "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*file-drag-helper.ps1*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }",
    ],
    { windowsHide: true },
    () => {},
  );
}

/**
 * @param {IconsBrowseDeps} nextDeps
 */
function activateIconsBrowse(nextDeps) {
  deps = nextDeps;
  const { context, provider } = nextDeps;
  killLeftoverFileDragHelpers();

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.openIconsBrowse', async (treeItemOrUri) => {
      const explicit = treeItemOrUri != null;
      let startPath = resolveStartFolderPath(treeItemOrUri, provider);
      if (!explicit) {
        const restored = restoreSavedFolderPath(provider);
        if (restored !== undefined) {
          startPath = restored;
        }
      }
      await showIconsBrowsePanel(startPath);
    }),
  );

  context.subscriptions.push(
    vscode.window.registerWebviewPanelSerializer(PANEL_VIEW_TYPE, {
      async deserializeWebviewPanel(webviewPanel, _state) {
        panel = webviewPanel;
        const restored = restoreSavedFolderPath(provider);
        const startPath =
          restored === undefined ? (provider.rootEntries.length === 1 ? provider.rootEntries[0].path : null) : restored;
        crumbs = buildCrumbsForStart(startPath, provider);
        wirePanel(webviewPanel);
        postState();
      },
    }),
  );

  context.subscriptions.push(
    provider.onDidChangeTreeData(() => {
      if (panel) {
        postState();
      }
    }),
  );

  context.subscriptions.push({
    dispose: () => {
      panel?.dispose();
      panel = undefined;
      crumbs = [];
      browseTreeExpanded.clear();
      deps = undefined;
      if (persistTimer) {
        clearTimeout(persistTimer);
        persistTimer = null;
      }
    },
  });
}

/**
 * @param {unknown} treeItemOrUri
 * @param {IconsBrowseDeps['provider']} provider
 * @returns {string | null}
 */
function resolveStartFolderPath(treeItemOrUri, provider) {
  const item = treeItemOrUri && typeof treeItemOrUri === 'object' ? treeItemOrUri : undefined;
  if (item && typeof item.dirPath === 'string' && item.dirPath) {
    return item.dirPath;
  }
  if (item && typeof item.noteDirPath === 'string' && item.noteDirPath) {
    return item.noteDirPath;
  }
  const uri = item?.resourceUri ?? treeItemOrUri;
  const fsPath = filePathFromUriLike(uri);
  if (fsPath) {
    try {
      const stat = fs.statSync(fsPath);
      if (stat.isDirectory()) {
        return fsPath;
      }
      if (stat.isFile()) {
        return path.dirname(fsPath);
      }
    } catch {
      // fall through
    }
  }

  if (provider.rootEntries.length === 1) {
    return provider.rootEntries[0].path;
  }
  return null;
}

/**
 * @param {unknown} uri
 * @returns {string}
 */
function filePathFromUriLike(uri) {
  if (uri instanceof vscode.Uri) {
    return uri.scheme === 'file' ? uri.fsPath : '';
  }
  if (uri && typeof uri === 'object' && uri.scheme === 'file' && typeof uri.fsPath === 'string') {
    return uri.fsPath;
  }
  return '';
}

/**
 * @param {string | null} startFolderPath
 */
async function showIconsBrowsePanel(startFolderPath) {
  if (!deps) {
    return;
  }

  crumbs = buildCrumbsForStart(startFolderPath, deps.provider);

  if (panel) {
    panel.reveal(vscode.ViewColumn.Active, false);
    postState();
    return;
  }

  panel = vscode.window.createWebviewPanel(
    PANEL_VIEW_TYPE,
    'Notes Icons Browse',
    { viewColumn: vscode.ViewColumn.Active, preserveFocus: false },
    {
      enableScripts: true,
      retainContextWhenHidden: true,
      localResourceRoots: webviewResourceRoots(),
    },
  );

  wirePanel(panel);
  postState();
}

/**
 * @param {import('vscode').WebviewPanel} webviewPanel
 */
function wirePanel(webviewPanel) {
  if (!deps) {
    return;
  }
  webviewPanel.webview.options = {
    enableScripts: true,
    localResourceRoots: webviewResourceRoots(),
  };
  webviewPanel.webview.html = getHtml(webviewPanel.webview, deps.context.extensionUri);

  webviewPanel.onDidDispose(
    () => {
      panel = undefined;
    },
    null,
    deps.context.subscriptions,
  );

  webviewPanel.webview.onDidReceiveMessage(
    async (message) => {
      await handleWebviewMessage(message);
    },
    null,
    deps.context.subscriptions,
  );
}

/**
 * Refresh the open panel after external FS / tree changes.
 */
function refreshIconsBrowseIfOpen() {
  if (panel) {
    postState();
  }
}

/**
 * @param {string | null} startFolderPath
 * @param {IconsBrowseDeps['provider']} provider
 * @returns {IconsBrowseCrumb[]}
 */
function buildCrumbsForStart(startFolderPath, provider) {
  if (startFolderPath == null || startFolderPath === '') {
    return [{ path: '', name: 'Notes' }];
  }

  const root = provider.rootEntries.find((entry) => {
    const rootNorm = normalizePath(entry.path);
    const startNorm = normalizePath(startFolderPath);
    return startNorm === rootNorm || startNorm.startsWith(rootNorm + path.sep);
  });

  if (!root) {
    return [
      { path: '', name: 'Notes' },
      { path: startFolderPath, name: path.basename(startFolderPath) },
    ];
  }

  /** @type {IconsBrowseCrumb[]} */
  const result = [{ path: root.path, name: root.name }];
  const rootNorm = normalizePath(root.path);
  const startNorm = normalizePath(startFolderPath);
  if (startNorm === rootNorm) {
    return result;
  }

  const relative = path.relative(root.path, startFolderPath);
  if (!relative || relative.startsWith('..')) {
    return result;
  }

  let cur = root.path;
  for (const part of relative.split(path.sep).filter(Boolean)) {
    cur = path.join(cur, part);
    result.push({ path: cur, name: part });
  }
  return result;
}

/**
 * @param {string} p
 */
function normalizePath(p) {
  const resolved = path.resolve(String(p));
  return process.platform === 'win32' ? resolved.toLowerCase() : resolved;
}

function currentDirPath() {
  if (crumbs.length === 0) {
    return null;
  }
  const last = crumbs[crumbs.length - 1];
  return last.path ? last.path : null;
}

const FOLDER_TREE_MAX_DEPTH = 16;

/** @type {Set<string>} normalized folder paths the user (or Expand all) opened */
const browseTreeExpanded = new Set();

/**
 * @param {string} folderPath
 * @returns {string}
 */
function folderTreeKey(folderPath) {
  const raw = String(folderPath || '');
  return raw ? normalizePath(raw) : '';
}

/**
 * Ancestors of the current folder — kept expanded so the working folder stays visible.
 *
 * @returns {string[]}
 */
function currentPathAncestorKeys() {
  return crumbs.slice(0, -1).map((crumb) => folderTreeKey(crumb.path || ''));
}

function ensureCurrentPathExpanded() {
  for (const key of currentPathAncestorKeys()) {
    browseTreeExpanded.add(key);
  }
}

/**
 * @param {ReturnType<typeof getBrowseOptionsFromConfig>} browse
 * @param {string | null} dirPath
 * @returns {Array<{ path: string, name: string, label?: string }>}
 */
function listedChildFolders(browse, dirPath) {
  if (!deps) {
    return [];
  }
  return listing.applyListingOptions(
    deps.provider
      .listIconsBrowseEntries(dirPath)
      .filter((entry) => entry.kind === 'folder')
      .map((entry) => {
        let mtimeMs = 0;
        let sizeBytes = 0;
        try {
          const st = fs.statSync(entry.path);
          mtimeMs = st.mtimeMs;
          sizeBytes = st.size;
        } catch {
          // missing path
        }
        return { ...entry, mtimeMs, sizeBytes };
      }),
    browse,
  );
}

/**
 * @param {ReturnType<typeof getBrowseOptionsFromConfig>} browse
 * @returns {string[]}
 */
function collectAllFolderTreeKeys(browse) {
  /** @type {string[]} */
  const keys = [];
  const root = crumbs[0];
  if (!root) {
    return keys;
  }

  /**
   * @param {string | null} dirPath
   * @param {number} depth
   */
  const walk = (dirPath, depth) => {
    if (depth > FOLDER_TREE_MAX_DEPTH) {
      return;
    }
    for (const folder of listedChildFolders(browse, dirPath)) {
      keys.push(folderTreeKey(folder.path));
      walk(folder.path, depth + 1);
    }
  };

  keys.push(folderTreeKey(root.path || ''));
  walk(root.path ? root.path : null, 1);
  return keys;
}

/**
 * Visible folders for Tree layout (collapsed branches omitted).
 *
 * @param {ReturnType<typeof getBrowseOptionsFromConfig>} browse
 * @returns {Array<{ path: string, name: string, depth: number, hasChildren: boolean, expanded: boolean }>}
 */
function buildFolderTree(browse) {
  if (!deps) {
    return [];
  }
  ensureCurrentPathExpanded();
  /** @type {Array<{ path: string, name: string, depth: number, hasChildren: boolean, expanded: boolean }>} */
  const rows = [];
  const root = crumbs[0];
  if (!root) {
    return rows;
  }

  /**
   * @param {string} folderPath
   * @param {string} name
   * @param {number} depth
   * @param {string | null} listPath
   */
  const pushNode = (folderPath, name, depth, listPath) => {
    const childFolders = depth >= FOLDER_TREE_MAX_DEPTH ? [] : listedChildFolders(browse, listPath);
    const key = folderTreeKey(folderPath);
    const expanded = browseTreeExpanded.has(key);
    rows.push({
      path: folderPath,
      name,
      depth,
      hasChildren: childFolders.length > 0,
      expanded,
    });
    if (!expanded) {
      return;
    }
    for (const folder of childFolders) {
      pushNode(folder.path, folder.name || folder.label || folder.path, depth + 1, folder.path);
    }
  };

  pushNode(root.path || '', root.name, 0, root.path ? root.path : null);
  return rows;
}

/** @type {ReturnType<typeof setTimeout> | null} */
let persistTimer = null;

function persistCurrentFolder() {
  if (!deps) {
    return;
  }
  if (persistTimer) {
    clearTimeout(persistTimer);
  }
  persistTimer = setTimeout(() => {
    persistTimer = null;
    if (!deps) {
      return;
    }
    void deps.context.workspaceState.update(ICONS_BROWSE_FOLDER_KEY, currentDirPath() || '');
  }, 250);
}

/**
 * Last Icons Browse folder, or `null` for the multi-root home, or `undefined` if none saved.
 * @param {IconsBrowseDeps['provider']} provider
 * @returns {string | null | undefined}
 */
function restoreSavedFolderPath(provider) {
  if (!deps) {
    return undefined;
  }
  const saved = deps.context.workspaceState.get(ICONS_BROWSE_FOLDER_KEY);
  if (saved == null) {
    return undefined;
  }
  const raw = String(saved);
  if (!raw) {
    return null;
  }
  let cur = raw;
  for (;;) {
    try {
      if (fs.existsSync(cur) && fs.statSync(cur).isDirectory()) {
        const inWorkspace = provider.rootEntries.some((entry) => {
          const rootNorm = normalizePath(entry.path);
          const curNorm = normalizePath(cur);
          return curNorm === rootNorm || curNorm.startsWith(rootNorm + path.sep);
        });
        if (inWorkspace) {
          return cur;
        }
      }
    } catch {
      // walk up
    }
    const parent = path.dirname(cur);
    if (parent === cur) {
      break;
    }
    cur = parent;
  }
  return undefined;
}

function postState() {
  if (!panel || !deps) {
    return;
  }
  const dirPath = currentDirPath();
  const rawEntries = deps.provider.listIconsBrowseEntries(dirPath);
  const currentFolder =
    typeof deps.provider.getIconsBrowseFolderEntry === 'function'
      ? deps.provider.getIconsBrowseFolderEntry(dirPath)
      : null;
  const canPaste = typeof deps.getCanPaste === 'function' ? deps.getCanPaste() : false;
  const cutPaths = new Set(
    (typeof deps.getCutPaths === 'function' ? deps.getCutPaths() : []).map((cutPath) => normalizePath(cutPath)),
  );
  const openNotesInPreview =
    vscode.workspace.getConfiguration('harrixNotesExplorerHsk').get('openNotesInPreview') !== false;
  const browse = getBrowseOptionsFromConfig();
  const listed = listing.applyListingOptions(
    rawEntries.map((entry) => enrichBrowseEntry(entry, browse)),
    browse,
  );
  const imageDirs = [
    ...new Set(
      listed.map((entry) => (entry.thumbnailImagePath ? path.dirname(entry.thumbnailImagePath) : '')).filter(Boolean),
    ),
  ];
  panel.webview.options = {
    enableScripts: true,
    localResourceRoots: webviewResourceRoots(imageDirs),
  };
  const entries = listed.map((entry) => ({
    ...entry,
    description: listing.browseCaption(entry, browse),
    tableDate: listing.formatBrowseDate(entry),
    tableSize: listing.formatByteSize(entry.sizeBytes),
    tableType: entry.kind === 'folder' ? 'Folder' : 'Note',
    thumbnailImage: entry.thumbnailImagePath
      ? panel.webview.asWebviewUri(vscode.Uri.file(entry.thumbnailImagePath)).toString()
      : '',
    thumbnailImagePath: undefined,
    isCut: cutPaths.has(
      normalizePath(
        entry.kind === 'note' && String(entry.contextValue || '').includes('NamedFolder')
          ? path.dirname(entry.path)
          : entry.path,
      ),
    ),
    menu: buildIconsBrowseContextMenu(entry.contextValue || '', {
      canPaste,
      openNotesInPreview,
      isWorkspaceRoot: entry.isWorkspaceRoot === true,
    }),
  }));
  const iconStyle = getNotesIconStyleFromConfig();
  const folderIcon = panel.webview
    .asWebviewUri(vscode.Uri.joinPath(deps.context.extensionUri, 'media', 'icons', 'it__folder_01.svg'))
    .toString();
  const noteIcon = panel.webview
    .asWebviewUri(vscode.Uri.joinPath(deps.context.extensionUri, 'media', 'icons', 'it__file-text_01.svg'))
    .toString();
  void panel.webview.postMessage({
    type: 'state',
    crumbs,
    entries,
    folderTree: browse.layout === 'tree' ? buildFolderTree(browse) : [],
    currentFolder,
    iconStyle,
    browse,
    icons: {
      folder: folderIcon,
      note: noteIcon,
    },
  });
  persistCurrentFolder();
}

/**
 * @returns {'harrix' | 'material'}
 */
function getNotesIconStyleFromConfig() {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  const raw = String(config.get('iconStyle') || 'harrix')
    .trim()
    .toLowerCase();
  return raw === 'material' ? 'material' : 'harrix';
}

/**
 * @returns {import('./icons-browse-listing').BrowseOptions}
 */
function getBrowseOptionsFromConfig() {
  return listing.browseOptionsFromConfig(vscode.workspace.getConfiguration('harrixNotesExplorerHsk'));
}

/**
 * @param {string[]} [extraDirs]
 */
function webviewResourceRoots(extraDirs = []) {
  const roots = [vscode.Uri.joinPath(deps.context.extensionUri, 'media')];
  for (const folder of vscode.workspace.workspaceFolders || []) {
    roots.push(folder.uri);
  }
  for (const dir of extraDirs) {
    if (dir) {
      roots.push(vscode.Uri.file(dir));
    }
  }
  return roots;
}

const THUMBNAIL_IMAGE_EXT = new Set(['.png', '.jpg', '.jpeg', '.webp', '.avif', '.gif']);

/**
 * @param {string} name
 */
function isFeaturedThumbnailName(name) {
  const ext = path.extname(name);
  const base = name.slice(0, name.length - ext.length).toLowerCase();
  return base === 'featured-image' || base === 'featured_image';
}

/**
 * @param {string} notePath
 * @param {string} [markdown]
 * @returns {string | null}
 */
function findThumbnailImagePath(notePath, markdown = '') {
  const noteDir = path.dirname(notePath);
  let entries = [];
  try {
    entries = fs.readdirSync(noteDir, { withFileTypes: true });
  } catch {
    entries = [];
  }
  for (const entry of entries) {
    if (entry.isFile() && isFeaturedThumbnailName(entry.name)) {
      return path.join(noteDir, entry.name);
    }
  }
  const imgDir = path.join(noteDir, 'img');
  let images = [];
  try {
    images = fs
      .readdirSync(imgDir, { withFileTypes: true })
      .filter((entry) => entry.isFile() && THUMBNAIL_IMAGE_EXT.has(path.extname(entry.name).toLowerCase()));
  } catch {
    images = [];
  }
  const canvas = images.find((entry) => /^canvas(?:_\d{2})?\.png$/i.test(entry.name));
  if (canvas) {
    return path.join(imgDir, canvas.name);
  }
  const fromMarkdown = resolveNoteRelativeImage(notePath, listing.firstMarkdownImageSrc(markdown));
  if (fromMarkdown) {
    return fromMarkdown;
  }
  images.sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }));
  if (images[0]) {
    return path.join(imgDir, images[0].name);
  }
  return null;
}

/**
 * @param {string} notePath
 * @param {string} rel
 * @returns {string | null}
 */
function resolveNoteRelativeImage(notePath, rel) {
  const cleaned = String(rel || '')
    .trim()
    .replace(/\\/g, '/')
    .replace(/^\/+/, '');
  if (!cleaned) {
    return null;
  }
  const abs = path.normalize(path.join(path.dirname(notePath), cleaned));
  try {
    if (fs.statSync(abs).isFile()) {
      return abs;
    }
  } catch {
    // missing
  }
  return null;
}

/**
 * @param {{ kind: string, path: string, name: string, label: string, description: string }} entry
 * @param {import('./icons-browse-listing').BrowseOptions} browse
 */
function enrichBrowseEntry(entry, browse) {
  let mtimeMs = 0;
  let sizeBytes = 0;
  try {
    const st = fs.statSync(entry.path);
    mtimeMs = st.mtimeMs;
    sizeBytes = st.size;
  } catch {
    // missing path
  }
  const isGmd = entry.kind === 'note' && listing.isGmdFileName(path.basename(entry.path));
  /** @type {{ dateSource?: string, dateValue?: string, thumbnailExcerpt?: string, thumbnailImagePath?: string }} */
  const extra = {};
  if (entry.kind === 'note' && (browse.layout === 'table' || (browse.showDates && browse.layout === 'list'))) {
    const resolved = noteMeta.resolveNoteDateForPath(entry.path);
    if (resolved) {
      extra.dateSource = resolved.source;
      extra.dateValue = resolved.value;
    }
  }
  if (browse.layout === 'thumbnails' && entry.kind === 'note') {
    let markdown = '';
    try {
      const fd = fs.openSync(entry.path, 'r');
      const buf = Buffer.alloc(16 * 1024);
      const read = fs.readSync(fd, buf, 0, buf.length, 0);
      fs.closeSync(fd);
      markdown = buf.slice(0, read).toString('utf8');
    } catch {
      markdown = '';
    }
    extra.thumbnailExcerpt = listing.excerptFromMarkdown(markdown);
    const imagePath = findThumbnailImagePath(entry.path, markdown);
    if (imagePath) {
      extra.thumbnailImagePath = imagePath;
    }
  }
  return {
    ...entry,
    isGmd,
    mtimeMs,
    sizeBytes,
    sortLabel: entry.label || entry.name,
    ...extra,
  };
}

/**
 * @param {string | undefined} key
 * @param {unknown} value
 */
async function updateBrowseOption(key, value) {
  const config = vscode.workspace.getConfiguration('harrixNotesExplorerHsk');
  if (key === 'layout') {
    await config.update('iconsBrowse.layout', listing.parseLayout(value), vscode.ConfigurationTarget.Global);
    return;
  }
  if (key === 'sortBy') {
    await config.update('iconsBrowse.sortBy', listing.parseSortBy(value), vscode.ConfigurationTarget.Global);
    return;
  }
  if (key === 'foldersFirst' || key === 'reverseOrder' || key === 'showGmdFiles' || key === 'showDates') {
    await config.update(`iconsBrowse.${key}`, value === true, vscode.ConfigurationTarget.Global);
  }
}

/**
 * @param {unknown} message
 */
async function handleWebviewMessage(message) {
  if (!deps || !message || typeof message !== 'object') {
    return;
  }
  const msg =
    /** @type {{ type?: string, path?: string, name?: string, index?: number, key?: string, value?: unknown }} */ (
      message
    );

  switch (msg.type) {
    case 'ready':
      postState();
      break;
    case 'openFolder': {
      if (typeof msg.path !== 'string') {
        break;
      }
      crumbs = buildCrumbsForStart(msg.path || null, deps.provider);
      postState();
      break;
    }
    case 'openNote': {
      if (typeof msg.path !== 'string' || !msg.path) {
        break;
      }
      await deps.openNote(vscode.Uri.file(msg.path));
      break;
    }
    case 'goBack': {
      if (crumbs.length > 1) {
        crumbs = crumbs.slice(0, -1);
        postState();
      }
      break;
    }
    case 'goHome': {
      if (crumbs.length <= 1) {
        break;
      }
      const first = crumbs[0];
      crumbs = [first];
      postState();
      break;
    }
    case 'navigateTo': {
      if (typeof msg.index !== 'number' || msg.index < 0 || msg.index >= crumbs.length) {
        break;
      }
      crumbs = crumbs.slice(0, msg.index + 1);
      postState();
      break;
    }
    case 'toggleTreeFolder': {
      if (typeof msg.path !== 'string') {
        break;
      }
      const key = folderTreeKey(msg.path);
      if (browseTreeExpanded.has(key)) {
        browseTreeExpanded.delete(key);
      } else {
        browseTreeExpanded.add(key);
      }
      postState();
      break;
    }
    case 'expandAllTree': {
      const browse = getBrowseOptionsFromConfig();
      for (const key of collectAllFolderTreeKeys(browse)) {
        browseTreeExpanded.add(key);
      }
      postState();
      break;
    }
    case 'collapseAllTree': {
      browseTreeExpanded.clear();
      ensureCurrentPathExpanded();
      postState();
      break;
    }
    case 'setBrowseOption': {
      await updateBrowseOption(msg.key, msg.value);
      postState();
      break;
    }
    case 'sortByColumn': {
      const column = listing.parseSortBy(msg.value);
      const browse = getBrowseOptionsFromConfig();
      if (browse.sortBy === column) {
        await updateBrowseOption('reverseOrder', !browse.reverseOrder);
      } else {
        await updateBrowseOption('sortBy', column);
        await updateBrowseOption('reverseOrder', false);
      }
      postState();
      break;
    }
    case 'refresh': {
      if (typeof deps.provider.refresh === 'function') {
        deps.provider.refresh();
      }
      postState();
      break;
    }
    case 'runCommand': {
      await runIconsBrowseCommand(msg);
      break;
    }
    case 'requestContextMenu': {
      postContextMenu(msg);
      break;
    }
    default:
      break;
  }
}

/**
 * @param {{ path?: string, kind?: string, contextValue?: string, isWorkspaceRoot?: boolean, background?: boolean, x?: number, y?: number }} msg
 */
function postContextMenu(msg) {
  if (!panel || !deps) {
    return;
  }
  const background = msg.background === true;
  const currentFolder =
    typeof deps.provider.getIconsBrowseFolderEntry === 'function'
      ? deps.provider.getIconsBrowseFolderEntry(currentDirPath())
      : null;
  const folder = background ? currentFolder : null;
  const targetPath = background ? folder?.path : msg.path;
  if (typeof targetPath !== 'string' || !targetPath) {
    return;
  }
  const contextValue = background
    ? folder?.contextValue || ''
    : typeof msg.contextValue === 'string'
      ? msg.contextValue
      : '';
  const isWorkspaceRoot = background ? folder?.isWorkspaceRoot === true : msg.isWorkspaceRoot === true;
  const kind = background ? 'folder' : msg.kind || 'note';
  const canPaste = typeof deps.getCanPaste === 'function' ? deps.getCanPaste() : false;
  const openNotesInPreview =
    vscode.workspace.getConfiguration('harrixNotesExplorerHsk').get('openNotesInPreview') !== false;
  const menu = buildIconsBrowseContextMenu(contextValue, {
    canPaste,
    openNotesInPreview,
    isWorkspaceRoot,
    background,
  });
  void panel.webview.postMessage({
    type: 'contextMenu',
    path: targetPath,
    kind,
    contextValue,
    isWorkspaceRoot,
    x: typeof msg.x === 'number' ? msg.x : 0,
    y: typeof msg.y === 'number' ? msg.y : 0,
    menu,
  });
}

/**
 * @param {{ command?: string, path?: string, kind?: string, contextValue?: string, isWorkspaceRoot?: boolean }} msg
 */
async function runIconsBrowseCommand(msg) {
  if (!deps || typeof msg.command !== 'string' || !msg.command || typeof msg.path !== 'string' || !msg.path) {
    return;
  }
  let arg = buildTreeArgForIconsBrowse(msg);
  if (msg.command === 'harrixNotesExplorerHsk.paste' && msg.kind === 'note') {
    const dirPath = currentDirPath();
    if (dirPath) {
      const folder =
        typeof deps.provider.getIconsBrowseFolderEntry === 'function'
          ? deps.provider.getIconsBrowseFolderEntry(dirPath)
          : null;
      arg = buildTreeArgForIconsBrowse({
        path: dirPath,
        kind: 'folder',
        contextValue: folder?.contextValue || '',
        isWorkspaceRoot: folder?.isWorkspaceRoot === true,
      });
    }
  }
  try {
    await vscode.commands.executeCommand(msg.command, arg);
  } catch (e) {
    const errMsg = e instanceof Error ? e.message : String(e);
    void vscode.window.showErrorMessage(`Command failed: ${errMsg}`);
  }
  postState();
}

/**
 * @param {{ path: string, kind?: string, contextValue?: string, isWorkspaceRoot?: boolean }} msg
 */
function buildTreeArgForIconsBrowse(msg) {
  const uri = vscode.Uri.file(msg.path);
  const contextValue = typeof msg.contextValue === 'string' ? msg.contextValue : '';
  if (msg.kind === 'folder') {
    return {
      resourceUri: uri,
      dirPath: msg.path,
      contextValue,
      isWorkspaceRoot: msg.isWorkspaceRoot === true,
    };
  }
  return {
    resourceUri: uri,
    noteDirPath: path.dirname(msg.path),
    isNoteItem: true,
    contextValue,
  };
}

/**
 * @param {import('vscode').Webview} webview
 * @param {import('vscode').Uri} extensionUri
 */
function getHtml(webview, extensionUri) {
  const cssUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'icons-browse.css'));
  const jsUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'icons-browse.js'));
  const csp = [
    `default-src 'none'`,
    `style-src ${webview.cspSource}`,
    `script-src ${webview.cspSource}`,
    `img-src ${webview.cspSource} data:`,
    `font-src ${webview.cspSource}`,
  ].join('; ');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="Content-Security-Policy" content="${csp}" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="stylesheet" href="${cssUri}" />
  <title>Notes Icons Browse</title>
</head>
<body>
  <header class="chrome">
    <button type="button" id="backBtn" title="Back">Back</button>
    <button type="button" id="homeBtn" title="Home">Home</button>
    <div class="tree-expand-actions" id="treeExpandActions" hidden>
      <button type="button" id="expandAllBtn" title="Expand all">Expand all</button>
      <button type="button" id="collapseAllBtn" title="Collapse all">Collapse all</button>
    </div>
    <nav class="breadcrumbs" id="crumbs" aria-label="Path"></nav>
    <div class="chrome-actions">
      <button type="button" id="sortViewBtn" class="icon-btn" title="Sort and view" aria-label="Sort and view" aria-haspopup="true" aria-expanded="false">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
          <path d="M3 18h6v-2H3v2zM3 6v2h18V6H3zm0 7h12v-2H3v2z"/>
        </svg>
      </button>
      <button type="button" id="refreshBtn" class="icon-btn" title="Refresh" aria-label="Refresh">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
          <path d="M17.65 6.35A7.95 7.95 0 0 0 12 4V1L7 6l5 5V7c2.76 0 5 2.24 5 5a4.99 4.99 0 0 1-.86 2.82l1.46 1.46A6.97 6.97 0 0 0 19 12c0-1.94-.78-3.7-2.35-5.65zM6 12c0-.85.17-1.66.48-2.4L4.95 8.07A6.97 6.97 0 0 0 5 12c0 1.94.78 3.7 2.35 5.65A7.95 7.95 0 0 0 12 20v3l5-5-5-5v3c-2.76 0-5-2.24-5-5z"/>
        </svg>
      </button>
    </div>
  </header>
  <main class="main">
    <div id="status" class="status" hidden>Loading…</div>
    <div id="grid" class="grid" role="list"></div>
  </main>
  <div id="ctxMenu" class="ctx-menu" hidden role="menu"></div>
  <div id="sortMenu" class="ctx-menu sort-menu" hidden role="menu"></div>
  <script src="${jsUri}"></script>
</body>
</html>`;
}

module.exports = {
  activateIconsBrowse,
  refreshIconsBrowseIfOpen,
  PANEL_VIEW_TYPE,
};
