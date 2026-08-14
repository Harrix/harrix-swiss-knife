/**
 * Native Windows file drag (CF_HDROP) for Notes Icons Browse.
 * Webview HTML5 drag cannot open files in apps like Notepad++ and can leave
 * the VS Code cursor stuck in a grabbing state.
 */

const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const vscode = require('vscode');

/** @type {import('node:child_process').ChildProcessWithoutNullStreams | undefined} */
let helper;
let helperReady = false;
/** @type {((line: string) => void) | undefined} */
let pendingLine;
let helperBuf = '';

function isWindows() {
  return process.platform === 'win32';
}

/**
 * @param {string} fsPath
 */
function normalizePath(fsPath) {
  const resolved = path.resolve(String(fsPath));
  return process.platform === 'win32' ? resolved.toLowerCase() : resolved;
}

/**
 * @param {string} fsPath
 * @param {Array<{ path: string }>} rootEntries
 */
function isPathUnderNotesRoots(fsPath, rootEntries) {
  const normalized = normalizePath(fsPath);
  return rootEntries.some((entry) => {
    const root = normalizePath(entry.path);
    return normalized === root || normalized.startsWith(root + path.sep);
  });
}

function stopFileDragHelper() {
  helperReady = false;
  pendingLine = undefined;
  helperBuf = '';
  const child = helper;
  helper = undefined;
  if (!child || child.killed) {
    return;
  }
  try {
    child.stdin.write('exit\n');
  } catch {
    // already closed
  }
  child.kill();
}

/**
 * @param {import('vscode').ExtensionContext} context
 */
function startFileDragHelper(context) {
  if (!isWindows()) {
    return;
  }
  if (helper && !helper.killed) {
    return;
  }

  const script = vscode.Uri.joinPath(context.extensionUri, 'media', 'file-drag-helper.ps1').fsPath;
  const child = spawn('powershell.exe', ['-NoProfile', '-STA', '-ExecutionPolicy', 'Bypass', '-File', script], {
    windowsHide: true,
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  helper = child;
  helperReady = false;
  helperBuf = '';

  child.stdout.setEncoding('utf8');
  child.stdout.on('data', (chunk) => {
    helperBuf += String(chunk);
    let idx = helperBuf.indexOf('\n');
    while (idx >= 0) {
      const line = helperBuf.slice(0, idx).replace(/\r$/, '');
      helperBuf = helperBuf.slice(idx + 1);
      if (line === 'ready') {
        helperReady = true;
      } else if (pendingLine) {
        const resolve = pendingLine;
        pendingLine = undefined;
        resolve(line);
      }
      idx = helperBuf.indexOf('\n');
    }
  });

  child.on('exit', () => {
    if (helper === child) {
      helper = undefined;
      helperReady = false;
    }
  });
}

/**
 * @param {number} ms
 */
function delay(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

/**
 * @param {import('vscode').ExtensionContext} context
 */
async function waitUntilHelperReady(context) {
  startFileDragHelper(context);
  const started = Date.now();
  while (!helperReady && Date.now() - started < 4000) {
    if (!helper) {
      break;
    }
    await delay(40);
  }
  return Boolean(helper && helperReady);
}

/**
 * @param {import('vscode').ExtensionContext} context
 * @param {string} fsPath
 * @param {Array<{ path: string }>} rootEntries
 */
async function runOsFileDrag(context, fsPath, rootEntries) {
  if (!isWindows() || !fsPath) {
    return;
  }
  if (!isPathUnderNotesRoots(fsPath, rootEntries)) {
    return;
  }
  try {
    if (!fs.existsSync(fsPath)) {
      return;
    }
  } catch {
    return;
  }

  const ready = await waitUntilHelperReady(context);
  if (!ready || !helper) {
    void vscode.window.showErrorMessage('Could not start Windows file drag helper');
    return;
  }

  const linePromise = new Promise((resolve) => {
    const timer = setTimeout(() => {
      if (pendingLine === resolveOnce) {
        pendingLine = undefined;
      }
      resolve('timeout');
    }, 120000);
    const resolveOnce = (line) => {
      clearTimeout(timer);
      resolve(line);
    };
    pendingLine = resolveOnce;
  });

  helper.stdin.write(`${JSON.stringify({ paths: [fsPath] })}\n`, 'utf8');
  const line = await linePromise;
  if (typeof line === 'string' && line.startsWith('error')) {
    void vscode.window.showErrorMessage(`File drag failed: ${line.slice(6).trim()}`);
  }
}

module.exports = {
  isWindows,
  startFileDragHelper,
  stopFileDragHelper,
  runOsFileDrag,
};
