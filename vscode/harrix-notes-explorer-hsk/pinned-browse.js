/**
 * Notes Pinned — editor-area WebviewPanel for quick-access pinned folders and notes
 * (Android `NotesPinnedBar` analogue as a full panel like Notes Icons Browse).
 */

const vscode = require('vscode');
const path = require('node:path');
const { createPinnedStore, normalizePath } = require('./pinned-items');

const PANEL_VIEW_TYPE = 'harrixNotesExplorerHsk.pinnedBrowse';
const CTX_ACTIVE_PINNED = 'harrixNotesExplorerHsk.activeNotePinned';

/**
 * @typedef {object} PinnedBrowseDeps
 * @property {import('vscode').ExtensionContext} context
 * @property {{
 *   rootEntries: Array<{ path: string, name: string }>,
 *   rootPath: string | undefined,
 *   findRootForPath?: (fsPath: string) => { path: string, name: string } | undefined,
 *   isWorkspaceRootPath?: (fsPath: string) => boolean,
 *   refresh?: () => void,
 *   onDidChangeTreeData: import('vscode').Event<unknown>,
 * }} provider
 * @property {(uri: import('vscode').Uri) => Promise<void>} openNote
 * @property {(filePath: string) => string} getNoteDisplayLabel
 * @property {(filePath: string) => string} getNoteIcon
 * @property {(noteDir: string) => string} findFeaturedImagePath
 * @property {(filePath: string) => string} noteStemFromPath
 * @property {(name: string) => boolean} isMd
 * @property {(fsPath: string) => boolean} isDirectoryPath
 * @property {(fsPath: string) => boolean} isFilePath
 * @property {(uri: unknown) => string | undefined} uriToFsPath
 * @property {(treeItemOrUri: unknown) => import('vscode').Uri | undefined} noteUriFromTreeArg
 */

/** @type {import('vscode').WebviewPanel | undefined} */
let panel;
/** @type {PinnedBrowseDeps | undefined} */
let deps;
/** @type {ReturnType<typeof createPinnedStore> | undefined} */
let store;

/**
 * @param {PinnedBrowseDeps} nextDeps
 */
function activatePinnedBrowse(nextDeps) {
  deps = nextDeps;
  const { context, provider } = nextDeps;

  store = createPinnedStore(context, {
    getConfiguration: () => vscode.workspace.getConfiguration('harrixNotesExplorerHsk'),
  });

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.openPinnedBrowse', async () => {
      await showPinnedBrowsePanel();
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.pinItem', async (treeItemOrUri) => {
      await pinFromArg(treeItemOrUri);
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.unpinItem', async (treeItemOrUri) => {
      await unpinFromArg(treeItemOrUri);
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.togglePinItem', async (treeItemOrUri) => {
      await togglePinFromArg(treeItemOrUri);
    }),
  );

  context.subscriptions.push(
    vscode.window.registerWebviewPanelSerializer(PANEL_VIEW_TYPE, {
      async deserializeWebviewPanel(webviewPanel, _state) {
        panel = webviewPanel;
        wirePanel(webviewPanel);
        await refreshPinnedState();
      },
    }),
  );

  context.subscriptions.push(
    provider.onDidChangeTreeData(() => {
      void refreshPinnedState();
    }),
  );

  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (
        e.affectsConfiguration('harrixNotesExplorerHsk.pinned') ||
        e.affectsConfiguration('harrixNotesExplorerHsk.iconStyle') ||
        e.affectsConfiguration('harrixNotesExplorerHsk.showNoteTitleFromContent') ||
        e.affectsConfiguration('harrixNotesExplorerHsk.showNoteFileNameBesideTitle')
      ) {
        void refreshPinnedState();
      }
    }),
  );

  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor(() => {
      void updateActivePinnedContext();
    }),
  );

  context.subscriptions.push({
    dispose: () => {
      panel?.dispose();
      panel = undefined;
      deps = undefined;
      store = undefined;
      void vscode.commands.executeCommand('setContext', CTX_ACTIVE_PINNED, false);
    },
  });

  void store.pruneMissing().then(() => {
    void updateActivePinnedContext();
    refreshPinnedBrowseIfOpen();
  });
}

/**
 * Refresh the open panel after FS / tree / pin changes.
 */
function refreshPinnedBrowseIfOpen() {
  if (panel) {
    void refreshPinnedState();
  }
}

/**
 * @returns {ReturnType<typeof createPinnedStore> | undefined}
 */
function getPinnedStore() {
  return store;
}

async function showPinnedBrowsePanel() {
  if (!deps) {
    return;
  }

  if (panel) {
    panel.reveal(vscode.ViewColumn.Active, false);
    await refreshPinnedState();
    return;
  }

  panel = vscode.window.createWebviewPanel(
    PANEL_VIEW_TYPE,
    'Notes Pinned',
    { viewColumn: vscode.ViewColumn.Active, preserveFocus: false },
    {
      enableScripts: true,
      retainContextWhenHidden: true,
      localResourceRoots: webviewResourceRoots(),
    },
  );

  wirePanel(panel);
  await refreshPinnedState();
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
 * @param {string[]} [extraDirs]
 * @returns {import('vscode').Uri[]}
 */
function webviewResourceRoots(extraDirs = []) {
  if (!deps) {
    return [];
  }
  const roots = [vscode.Uri.joinPath(deps.context.extensionUri, 'media')];
  for (const dir of extraDirs) {
    if (dir) {
      roots.push(vscode.Uri.file(dir));
    }
  }
  for (const entry of deps.provider.rootEntries) {
    roots.push(vscode.Uri.file(entry.path));
  }
  return roots;
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

async function updateActivePinnedContext() {
  if (!deps || !store) {
    await vscode.commands.executeCommand('setContext', CTX_ACTIVE_PINNED, false);
    return;
  }
  const uri = vscode.window.activeTextEditor?.document?.uri;
  const pinned = uri?.scheme === 'file' && deps.isMd(path.basename(uri.fsPath)) ? store.isPinned(uri.fsPath) : false;
  await vscode.commands.executeCommand('setContext', CTX_ACTIVE_PINNED, pinned);
}

/**
 * Refresh stored note titles/icons from disk when possible.
 * @param {import('./pinned-items').PinnedItem[]} items
 * @returns {Promise<import('./pinned-items').PinnedItem[]>}
 */
async function enrichItems(items) {
  if (!deps || !store) {
    return items;
  }
  /** @type {import('./pinned-items').PinnedItem[]} */
  const out = [];
  let changed = false;
  for (const item of items) {
    if (item.kind === 'note' && deps.isFilePath(item.path)) {
      const title = deps.getNoteDisplayLabel(item.path);
      const icon = deps.getNoteIcon(item.path) || '';
      const featuredIconPath = deps.findFeaturedImagePath(path.dirname(item.path)) || '';
      const fileName = path.basename(item.path);
      if (
        title !== item.title ||
        icon !== (item.icon || '') ||
        featuredIconPath !== (item.featuredIconPath || '') ||
        fileName !== (item.fileName || '')
      ) {
        changed = true;
        await store.updateItem(item.id, { title, icon, featuredIconPath, fileName });
        out.push({ ...item, title, icon, featuredIconPath, fileName });
        continue;
      }
    }
    if ((item.kind === 'folder' || item.kind === 'home') && deps.isDirectoryPath(item.path)) {
      const root =
        typeof deps.provider.findRootForPath === 'function' ? deps.provider.findRootForPath(item.path) : undefined;
      const isRoot =
        typeof deps.provider.isWorkspaceRootPath === 'function' ? deps.provider.isWorkspaceRootPath(item.path) : false;
      const title = isRoot && root ? root.name : path.basename(item.path);
      if (title && title !== item.title) {
        changed = true;
        await store.updateItem(item.id, { title });
        out.push({ ...item, title });
        continue;
      }
    }
    out.push(item);
  }
  return changed ? store.list() : out;
}

async function refreshPinnedState() {
  if (!deps || !store) {
    return;
  }
  const pruned = await store.pruneMissing();
  const items = await enrichItems(pruned.items);
  await updateActivePinnedContext();
  if (typeof deps.provider.refresh === 'function' && pruned.changed) {
    deps.provider.refresh();
  }
  postState(items);
}

/**
 * @param {import('./pinned-items').PinnedItem[]} [items]
 */
function postState(items) {
  if (!panel || !deps || !store) {
    return;
  }
  const list = items || store.list();
  const imageDirs = [
    ...new Set(list.map((item) => (item.featuredIconPath ? path.dirname(item.featuredIconPath) : '')).filter(Boolean)),
  ];
  panel.webview.options = {
    enableScripts: true,
    localResourceRoots: webviewResourceRoots(imageDirs),
  };

  const iconStyle = getNotesIconStyleFromConfig();
  const folderIcon = panel.webview
    .asWebviewUri(vscode.Uri.joinPath(deps.context.extensionUri, 'media', 'icons', 'it__folder_01.svg'))
    .toString();
  const noteIcon = panel.webview
    .asWebviewUri(vscode.Uri.joinPath(deps.context.extensionUri, 'media', 'icons', 'it__file-text_01.svg'))
    .toString();

  const entries = list.map((item, index) => {
    const label =
      item.kind === 'home'
        ? item.title || 'Home'
        : item.title || (item.kind === 'note' ? deps.noteStemFromPath(item.path) : path.basename(item.path));
    const missing = item.kind === 'note' ? !deps.isFilePath(item.path) : !deps.isDirectoryPath(item.path);
    return {
      id: item.id,
      kind: item.kind,
      path: item.path,
      label,
      description: item.kind === 'note' && item.fileName && item.fileName !== label ? item.fileName : '',
      iconEmoji: item.icon || '',
      iconImage: item.featuredIconPath
        ? panel.webview.asWebviewUri(vscode.Uri.file(item.featuredIconPath)).toString()
        : '',
      index,
      canMoveUp: index > 0,
      canMoveDown: index < list.length - 1,
      missing,
    };
  });

  void panel.webview.postMessage({
    type: 'state',
    entries,
    maxItems: store.maxItems(),
    iconStyle,
    icons: {
      folder: folderIcon,
      note: noteIcon,
    },
  });
}

/**
 * @param {unknown} treeItemOrUri
 * @returns {{ kind: 'folder' | 'note', path: string } | null}
 */
function resolvePinTarget(treeItemOrUri) {
  if (!deps) {
    return null;
  }

  const item = treeItemOrUri && typeof treeItemOrUri === 'object' ? treeItemOrUri : undefined;

  if (item && item.isNoteItem === true) {
    const notePath =
      (item.resourceUri && deps.uriToFsPath(item.resourceUri)) || (typeof item.path === 'string' ? item.path : '');
    if (notePath && deps.isFilePath(notePath) && deps.isMd(path.basename(notePath))) {
      return { kind: 'note', path: notePath };
    }
  }

  if (item && typeof item.dirPath === 'string' && item.dirPath && deps.isDirectoryPath(item.dirPath)) {
    return { kind: 'folder', path: item.dirPath };
  }

  if (item && typeof item.noteDirPath === 'string' && item.isNoteItem !== true) {
    // named-folder note rows still carry noteDirPath; prefer resourceUri note
  }

  const uri = item?.resourceUri ?? treeItemOrUri;
  const fsPath = deps.uriToFsPath(uri);
  if (fsPath) {
    if (deps.isDirectoryPath(fsPath)) {
      return { kind: 'folder', path: fsPath };
    }
    if (deps.isFilePath(fsPath) && deps.isMd(path.basename(fsPath))) {
      return { kind: 'note', path: fsPath };
    }
  }

  const noteUri = deps.noteUriFromTreeArg(treeItemOrUri);
  if (noteUri && deps.isFilePath(noteUri.fsPath) && deps.isMd(path.basename(noteUri.fsPath))) {
    return { kind: 'note', path: noteUri.fsPath };
  }

  return null;
}

/**
 */
async function afterPinChange() {
  if (!deps) {
    return;
  }
  if (typeof deps.provider.refresh === 'function') {
    deps.provider.refresh();
  }
  await updateActivePinnedContext();
  refreshPinnedBrowseIfOpen();
  try {
    const { refreshIconsBrowseIfOpen } = require('./icons-browse');
    refreshIconsBrowseIfOpen();
  } catch {
    // ignore
  }
}

/**
 * @param {unknown} treeItemOrUri
 */
async function pinFromArg(treeItemOrUri) {
  if (!deps || !store) {
    return;
  }
  const target = resolvePinTarget(treeItemOrUri);
  if (!target) {
    void vscode.window.showErrorMessage('Select a notes folder or markdown note to pin.');
    return;
  }
  if (store.isPinned(target.path)) {
    return;
  }

  /** @type {import('./pinned-items').PinnedItem} */
  let item;
  if (target.kind === 'folder') {
    const root =
      typeof deps.provider.findRootForPath === 'function' ? deps.provider.findRootForPath(target.path) : undefined;
    const isRoot =
      typeof deps.provider.isWorkspaceRootPath === 'function' ? deps.provider.isWorkspaceRootPath(target.path) : false;
    const title = isRoot && root ? root.name : path.basename(target.path);
    item = {
      id: normalizePath(target.path),
      kind: isRoot ? 'home' : 'folder',
      path: target.path,
      title,
      icon: '',
      featuredIconPath: '',
      fileName: '',
    };
  } else {
    item = {
      id: normalizePath(target.path),
      kind: 'note',
      path: target.path,
      title: deps.getNoteDisplayLabel(target.path),
      icon: deps.getNoteIcon(target.path) || '',
      featuredIconPath: deps.findFeaturedImagePath(path.dirname(target.path)) || '',
      fileName: path.basename(target.path),
    };
  }

  const result = await store.pin(item);
  if (!result.ok) {
    if (result.reason === 'full') {
      void vscode.window.showWarningMessage(
        `Pinned list is full (max ${store.maxItems()}). Unpin something first or raise harrixNotesExplorerHsk.pinned.maxItems.`,
      );
    }
    return;
  }

  await afterPinChange();
}

/**
 * @param {unknown} treeItemOrUri
 */
async function unpinFromArg(treeItemOrUri) {
  if (!deps || !store) {
    return;
  }

  if (treeItemOrUri && typeof treeItemOrUri === 'object' && typeof treeItemOrUri.id === 'string') {
    const byId = await store.unpin(treeItemOrUri.id);
    if (byId.ok) {
      await afterPinChange();
      return;
    }
  }

  const target = resolvePinTarget(treeItemOrUri);
  if (!target) {
    void vscode.window.showErrorMessage('Select a pinned folder or note to unpin.');
    return;
  }
  const result = await store.unpin(target.path);
  if (!result.ok) {
    return;
  }
  await afterPinChange();
}

/**
 * @param {unknown} treeItemOrUri
 */
async function togglePinFromArg(treeItemOrUri) {
  if (!deps || !store) {
    return;
  }
  const target = resolvePinTarget(treeItemOrUri);
  if (!target) {
    void vscode.window.showErrorMessage('Select a notes folder or markdown note to pin or unpin.');
    return;
  }
  if (store.isPinned(target.path)) {
    await unpinFromArg(treeItemOrUri);
  } else {
    await pinFromArg(treeItemOrUri);
  }
}

/**
 * @param {unknown} message
 */
async function handleWebviewMessage(message) {
  if (!deps || !store || !message || typeof message !== 'object') {
    return;
  }
  const msg = /** @type {{ type?: string, id?: string, path?: string, kind?: string }} */ (message);

  switch (msg.type) {
    case 'ready':
      await refreshPinnedState();
      break;
    case 'refresh':
      if (typeof deps.provider.refresh === 'function') {
        deps.provider.refresh();
      }
      await refreshPinnedState();
      break;
    case 'open': {
      await openPinnedEntry(msg);
      break;
    }
    case 'unpin': {
      if (typeof msg.id === 'string' && msg.id) {
        await store.unpin(msg.id);
      } else if (typeof msg.path === 'string' && msg.path) {
        await store.unpin(msg.path);
      }
      if (typeof deps.provider.refresh === 'function') {
        deps.provider.refresh();
      }
      await updateActivePinnedContext();
      await refreshPinnedState();
      break;
    }
    case 'moveUp': {
      if (typeof msg.id === 'string') {
        await store.move(msg.id, -1);
        await refreshPinnedState();
      }
      break;
    }
    case 'moveDown': {
      if (typeof msg.id === 'string') {
        await store.move(msg.id, 1);
        await refreshPinnedState();
      }
      break;
    }
    case 'howToPin': {
      void vscode.window.showInformationMessage(
        'Pin a folder or note from the Harrix Notes (HSK) tree (right-click → Pin), from Notes Icons Browse, or from the editor title bar while a markdown note is open. Unpin the same way or from this panel.',
      );
      break;
    }
    default:
      break;
  }
}

/**
 * @param {{ id?: string, path?: string, kind?: string }} msg
 */
async function openPinnedEntry(msg) {
  if (!deps || !store) {
    return;
  }
  const items = store.list();
  const item =
    (typeof msg.id === 'string' && items.find((row) => row.id === msg.id)) ||
    (typeof msg.path === 'string' && items.find((row) => normalizePath(row.path) === normalizePath(msg.path))) ||
    null;
  if (!item) {
    return;
  }

  if (item.kind === 'note') {
    if (!deps.isFilePath(item.path)) {
      void vscode.window.showWarningMessage('Pinned note no longer exists.');
      await refreshPinnedState();
      return;
    }
    await deps.openNote(vscode.Uri.file(item.path));
    return;
  }

  if (!deps.isDirectoryPath(item.path)) {
    void vscode.window.showWarningMessage('Pinned folder no longer exists.');
    await refreshPinnedState();
    return;
  }

  await vscode.commands.executeCommand('harrixNotesExplorerHsk.openIconsBrowse', {
    dirPath: item.path,
    resourceUri: vscode.Uri.file(item.path),
  });
}

/**
 * @param {import('vscode').Webview} webview
 * @param {import('vscode').Uri} extensionUri
 */
function getHtml(webview, extensionUri) {
  const cssUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'pinned-browse.css'));
  const jsUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'pinned-browse.js'));
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
  <title>Notes Pinned</title>
</head>
<body>
  <header class="chrome">
    <div class="chrome-title">Pinned</div>
    <div class="chrome-actions">
      <button type="button" id="helpBtn" class="icon-btn" title="How to pin" aria-label="How to pin">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
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
    <div id="status" class="status" hidden></div>
    <div id="grid" class="grid" role="list"></div>
  </main>
  <div id="ctxMenu" class="ctx-menu" hidden role="menu"></div>
  <script src="${jsUri}"></script>
</body>
</html>`;
}

module.exports = {
  activatePinnedBrowse,
  refreshPinnedBrowseIfOpen,
  getPinnedStore,
  PANEL_VIEW_TYPE,
  CTX_ACTIVE_PINNED,
};
