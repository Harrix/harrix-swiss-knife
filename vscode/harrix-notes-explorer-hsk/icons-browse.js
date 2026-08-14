/**
 * Icons Browse — editor-area WebviewPanel for folder drill-down (Android-like grid).
 */

const vscode = require('vscode');
const path = require('node:path');
const fs = require('node:fs');

const PANEL_VIEW_TYPE = 'harrixNotesExplorerHsk.iconsBrowse';

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
 *   }>,
 *   onDidChangeTreeData: import('vscode').Event<unknown>,
 *   refresh?: () => void,
 * }} provider
 * @property {(uri: import('vscode').Uri) => Promise<void>} openNote
 */

/** @type {import('vscode').WebviewPanel | undefined} */
let panel;
/** @type {IconsBrowseCrumb[]} */
let crumbs = [];
/** @type {IconsBrowseDeps | undefined} */
let deps;

/**
 * @param {IconsBrowseDeps} nextDeps
 */
function activateIconsBrowse(nextDeps) {
  deps = nextDeps;
  const { context, provider } = nextDeps;

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.openIconsBrowse', async (treeItemOrUri) => {
      const startPath = resolveStartFolderPath(treeItemOrUri, provider);
      await showIconsBrowsePanel(startPath);
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

  panel.webview.html = getHtml(panel.webview, deps.context.extensionUri);

  panel.onDidDispose(
    () => {
      panel = undefined;
    },
    null,
    deps.context.subscriptions,
  );

  panel.webview.onDidReceiveMessage(
    async (message) => {
      await handleWebviewMessage(message);
    },
    null,
    deps.context.subscriptions,
  );

  postState();
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

function postState() {
  if (!panel || !deps) {
    return;
  }
  const dirPath = currentDirPath();
  const entries = deps.provider.listIconsBrowseEntries(dirPath);
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
    iconStyle,
    icons: {
      folder: folderIcon,
      note: noteIcon,
    },
  });
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
    default:
      break;
  }
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
  <script src="${jsUri}"></script>
</body>
</html>`;
}

module.exports = {
  activateIconsBrowse,
  refreshIconsBrowseIfOpen,
  PANEL_VIEW_TYPE,
};
