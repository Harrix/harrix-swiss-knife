/**
 * Icons Browse — editor-area WebviewPanel for folder drill-down (Android-like grid).
 */

const vscode = require('vscode');
const path = require('node:path');
const fs = require('node:fs');
const { execFile } = require('node:child_process');
const { buildIconsBrowseContextMenu } = require('./icons-browse-menu');

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
  const uri = item?.resourceUri ?? treeItemOrUri;
  if (uri instanceof vscode.Uri && uri.scheme === 'file') {
    const fsPath = uri.fsPath;
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
      localResourceRoots: [vscode.Uri.joinPath(deps.context.extensionUri, 'media')],
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
    localResourceRoots: [vscode.Uri.joinPath(deps.context.extensionUri, 'media')],
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
  const entries = rawEntries.map((entry) => ({
    ...entry,
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
    currentFolder,
    iconStyle,
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
 * @param {unknown} message
 */
async function handleWebviewMessage(message) {
  if (!deps || !message || typeof message !== 'object') {
    return;
  }
  const msg = /** @type {{ type?: string, path?: string, name?: string, index?: number }} */ (message);

  switch (msg.type) {
    case 'ready':
      postState();
      break;
    case 'openFolder': {
      if (typeof msg.path !== 'string' || !msg.path) {
        break;
      }
      const name = typeof msg.name === 'string' && msg.name ? msg.name : path.basename(msg.path);
      crumbs = [...crumbs, { path: msg.path, name }];
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
    <nav class="breadcrumbs" id="crumbs" aria-label="Path"></nav>
    <button type="button" id="refreshBtn" class="icon-btn" title="Refresh" aria-label="Refresh">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
        <path d="M17.65 6.35A7.95 7.95 0 0 0 12 4V1L7 6l5 5V7c2.76 0 5 2.24 5 5a4.99 4.99 0 0 1-.86 2.82l1.46 1.46A6.97 6.97 0 0 0 19 12c0-1.94-.78-3.7-2.35-5.65zM6 12c0-.85.17-1.66.48-2.4L4.95 8.07A6.97 6.97 0 0 0 5 12c0 1.94.78 3.7 2.35 5.65A7.95 7.95 0 0 0 12 20v3l5-5-5-5v3c-2.76 0-5-2.24-5-5z"/>
      </svg>
    </button>
  </header>
  <main class="main">
    <div id="status" class="status" hidden>Loading…</div>
    <div id="grid" class="grid" role="list"></div>
  </main>
  <div id="ctxMenu" class="ctx-menu" hidden role="menu"></div>
  <script src="${jsUri}"></script>
</body>
</html>`;
}

module.exports = {
  activateIconsBrowse,
  refreshIconsBrowseIfOpen,
  PANEL_VIEW_TYPE,
};
