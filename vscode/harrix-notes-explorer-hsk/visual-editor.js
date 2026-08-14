/**
 * Visual Markdown custom text editor (WYSIWYG) for notes.
 */

const vscode = require('vscode');
const path = require('node:path');
const fs = require('node:fs');

const VIEW_TYPE = 'harrixNotesExplorerHsk.visualMarkdown';

/**
 * @typedef {object} VisualEditorDeps
 * @property {(treeItemOrUri: unknown) => import('vscode').Uri | undefined} noteUriFromTreeArg
 * @property {(noteMdPath: string, sourceUris: import('vscode').Uri[], settings: object) => Promise<{ destPaths: string[], copiedCount: number }>} materializeDroppedFilesForNote
 * @property {() => object} getNoteDropSettings
 * @property {(destPath: string, noteDir: string, settings: object) => string} formatDroppedMarkdownSnippet
 * @property {(fromDir: string, toFile: string) => string} toMarkdownRelativePath
 */

/**
 * @param {import('vscode').ExtensionContext} context
 * @param {VisualEditorDeps} deps
 */
function activateVisualEditor(context, deps) {
  context.subscriptions.push(
    vscode.window.registerCustomEditorProvider(VIEW_TYPE, new VisualMarkdownEditorProvider(context, deps), {
      webviewOptions: { retainContextWhenHidden: true },
      supportsMultipleEditorsPerDocument: false,
    }),
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('harrixNotesExplorerHsk.openNoteInVisualEditor', async (treeItemOrUri) => {
      const uri = resolveMarkdownUri(treeItemOrUri, deps.noteUriFromTreeArg);
      if (!uri) {
        void vscode.window.showErrorMessage('Open a markdown note or select one in Harrix Notes (HSK).');
        return;
      }
      await vscode.commands.executeCommand('vscode.openWith', uri, VIEW_TYPE, { preview: false });
    }),
  );
}

/**
 * @param {unknown} treeItemOrUri
 * @param {(arg: unknown) => import('vscode').Uri | undefined} noteUriFromTreeArg
 */
function resolveMarkdownUri(treeItemOrUri, noteUriFromTreeArg) {
  const fromArg = noteUriFromTreeArg(treeItemOrUri);
  if (fromArg) {
    return fromArg;
  }
  const tab = vscode.window.tabGroups.activeTabGroup?.activeTab;
  const input = tab?.input;
  if (input && typeof input === 'object' && input.uri instanceof vscode.Uri && input.uri.scheme === 'file') {
    return input.uri;
  }
  return undefined;
}

class VisualMarkdownEditorProvider {
  /**
   * @param {import('vscode').ExtensionContext} context
   * @param {VisualEditorDeps} deps
   */
  constructor(context, deps) {
    this.context = context;
    this.deps = deps;
  }

  /**
   * @param {import('vscode').TextDocument} document
   * @param {import('vscode').WebviewPanel} webviewPanel
   */
  async resolveCustomTextEditor(document, webviewPanel) {
    const webview = webviewPanel.webview;
    webview.options = {
      enableScripts: true,
      localResourceRoots: webviewRoots(this.context, document),
    };
    webview.html = getHtml(webview, this.context.extensionUri);

    let updatingFromWebview = false;

    const postDocument = () => {
      void webview.postMessage({
        type: 'setDocument',
        text: document.getText(),
        imageUris: collectImageUris(webview, document),
      });
    };

    const changeDoc = vscode.workspace.onDidChangeTextDocument((event) => {
      if (event.document.uri.toString() !== document.uri.toString()) {
        return;
      }
      if (updatingFromWebview) {
        return;
      }
      postDocument();
    });

    webviewPanel.onDidDispose(() => {
      changeDoc.dispose();
    });

    webview.onDidReceiveMessage(async (message) => {
      if (!message || typeof message !== 'object') {
        return;
      }
      if (message.type === 'ready') {
        postDocument();
        return;
      }
      if (message.type === 'edit' && typeof message.text === 'string') {
        if (message.text === document.getText()) {
          return;
        }
        updatingFromWebview = true;
        try {
          await replaceDocumentText(document, message.text);
        } finally {
          updatingFromWebview = false;
        }
        return;
      }
      if (message.type === 'promptLink') {
        const url = await vscode.window.showInputBox({
          prompt: 'Link URL',
          placeHolder: 'https://',
          ignoreFocusOut: true,
        });
        if (url) {
          void webview.postMessage({ type: 'insertLink', url });
        }
        return;
      }
      if (message.type === 'pickImages') {
        const picked = await vscode.window.showOpenDialog({
          canSelectMany: true,
          canSelectFiles: true,
          canSelectFolders: false,
          filters: { Images: ['png', 'jpg', 'jpeg', 'gif', 'webp', 'avif', 'bmp', 'svg'] },
        });
        if (picked?.length) {
          await insertDroppedFiles(webview, document, this.deps, picked);
        }
        return;
      }
      if (message.type === 'dropUris' && Array.isArray(message.uris)) {
        const uris = message.uris
          .map((value) => {
            try {
              return vscode.Uri.parse(String(value));
            } catch {
              return undefined;
            }
          })
          .filter((uri) => uri && uri.scheme === 'file');
        if (uris.length > 0) {
          await insertDroppedFiles(webview, document, this.deps, uris);
        }
        return;
      }
      if (message.type === 'dropFiles' && Array.isArray(message.files)) {
        await insertPastedFiles(webview, document, this.deps, message.files);
      }
    });
  }
}

/**
 * @param {import('vscode').ExtensionContext} context
 * @param {import('vscode').TextDocument} document
 */
function webviewRoots(context, document) {
  /** @type {import('vscode').Uri[]} */
  const roots = [vscode.Uri.joinPath(context.extensionUri, 'media')];
  for (const folder of vscode.workspace.workspaceFolders || []) {
    roots.push(folder.uri);
  }
  roots.push(vscode.Uri.file(path.dirname(document.uri.fsPath)));
  return roots;
}

/**
 * @param {import('vscode').Webview} webview
 * @param {import('vscode').TextDocument} document
 * @returns {Record<string, string>}
 */
function collectImageUris(webview, document) {
  const noteDir = path.dirname(document.uri.fsPath);
  const text = document.getText();
  /** @type {Record<string, string>} */
  const map = {};
  const add = (raw) => {
    const src = String(raw || '').trim();
    if (!src || /^(https?:|data:|mailto:|#)/i.test(src)) {
      return;
    }
    const abs = path.isAbsolute(src) ? src : path.resolve(noteDir, src.replace(/\\/g, '/'));
    if (!fs.existsSync(abs)) {
      return;
    }
    map[src] = webview.asWebviewUri(vscode.Uri.file(abs)).toString();
  };
  const mdRe = /!\[[^\]]*]\(\s*<?([^>\s)]+)>?/g;
  let match = mdRe.exec(text);
  while (match) {
    add(match[1]);
    match = mdRe.exec(text);
  }
  const htmlRe = /<img\b[^>]*\bsrc\s*=\s*["']([^"']+)["']/gi;
  match = htmlRe.exec(text);
  while (match) {
    add(match[1]);
    match = htmlRe.exec(text);
  }
  return map;
}

/**
 * @param {import('vscode').TextDocument} document
 * @param {string} text
 */
async function replaceDocumentText(document, text) {
  const lastLine = document.lineAt(Math.max(0, document.lineCount - 1));
  const range = new vscode.Range(0, 0, lastLine.lineNumber, lastLine.text.length);
  const edit = new vscode.WorkspaceEdit();
  edit.replace(document.uri, range, text);
  await vscode.workspace.applyEdit(edit);
}

/**
 * @param {import('vscode').Webview} webview
 * @param {import('vscode').TextDocument} document
 * @param {VisualEditorDeps} deps
 * @param {import('vscode').Uri[]} sourceUris
 */
async function insertDroppedFiles(webview, document, deps, sourceUris) {
  const settings = deps.getNoteDropSettings();
  const { destPaths } = await deps.materializeDroppedFilesForNote(document.uri.fsPath, sourceUris, settings);
  await postInsertFromDestPaths(webview, document, deps, destPaths, settings);
}

/**
 * @param {import('vscode').Webview} webview
 * @param {import('vscode').TextDocument} document
 * @param {VisualEditorDeps} deps
 * @param {Array<{ name?: string, mime?: string, base64?: string }>} files
 */
async function insertPastedFiles(webview, document, deps, files) {
  const settings = deps.getNoteDropSettings();
  const noteDir = path.dirname(document.uri.fsPath);
  const imagesFolder = String(settings.imagesFolderName || 'img');
  const destDir = path.join(noteDir, imagesFolder);
  await fs.promises.mkdir(destDir, { recursive: true });
  /** @type {string[]} */
  const destPaths = [];
  for (const file of files) {
    const name = sanitizeFileName(String(file.name || 'image.png'));
    const raw = String(file.base64 || '');
    if (!raw) {
      continue;
    }
    const destPath = uniqueFilePath(destDir, name);
    await fs.promises.writeFile(destPath, Buffer.from(raw, 'base64'));
    destPaths.push(destPath);
  }
  await postInsertFromDestPaths(webview, document, deps, destPaths, settings);
}

/**
 * @param {import('vscode').Webview} webview
 * @param {import('vscode').TextDocument} document
 * @param {VisualEditorDeps} deps
 * @param {string[]} destPaths
 * @param {object} settings
 */
async function postInsertFromDestPaths(webview, document, deps, destPaths, settings) {
  if (destPaths.length === 0) {
    return;
  }
  const noteDir = path.dirname(document.uri.fsPath);
  const html = destPaths
    .map((destPath) => {
      const rel = deps.toMarkdownRelativePath(noteDir, destPath);
      const snippet = deps.formatDroppedMarkdownSnippet(destPath, noteDir, settings);
      const webviewSrc = webview.asWebviewUri(vscode.Uri.file(destPath)).toString();
      if (snippet.startsWith('![')) {
        return `<img src="${escapeHtml(webviewSrc)}" data-md-src="${escapeHtml(rel)}" alt="" />`;
      }
      const label = path.basename(destPath);
      return `<a href="${escapeHtml(rel)}" data-md-href="${escapeHtml(rel)}"><code>${escapeHtml(label)}</code></a>`;
    })
    .join('');
  void webview.postMessage({ type: 'insertHtml', html });
}

/**
 * @param {string} name
 */
function sanitizeFileName(name) {
  // biome-ignore lint/suspicious/noControlCharactersInRegex: strip ASCII control chars from pasted names
  return name.replace(/[<>:"/\\|?*\u0000-\u001f]/g, '_') || 'image.png';
}

/**
 * @param {string} dir
 * @param {string} baseName
 */
function uniqueFilePath(dir, baseName) {
  const ext = path.extname(baseName);
  const stem = path.basename(baseName, ext) || 'image';
  let dest = path.join(dir, `${stem}${ext}`);
  let i = 2;
  while (fs.existsSync(dest)) {
    dest = path.join(dir, `${stem}-${i}${ext}`);
    i += 1;
  }
  return dest;
}

/**
 * @param {string} value
 */
function escapeHtml(value) {
  return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/**
 * @param {import('vscode').Webview} webview
 * @param {import('vscode').Uri} extensionUri
 */
function getHtml(webview, extensionUri) {
  const cssUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'visual-editor.css'));
  const jsUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'visual-editor.js'));
  const markedUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'vendor', 'marked.min.js'));
  const turndownUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'vendor', 'turndown.js'));
  const csp = [
    `default-src 'none'`,
    `style-src ${webview.cspSource}`,
    `script-src ${webview.cspSource}`,
    `img-src ${webview.cspSource} https: data:`,
    `font-src ${webview.cspSource}`,
  ].join('; ');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="Content-Security-Policy" content="${csp}" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="stylesheet" href="${cssUri}" />
  <title>Visual Markdown</title>
</head>
<body>
  <div class="toolbar" role="toolbar" aria-label="Format">
    <button type="button" data-cmd="bold" title="Bold (Ctrl+B)"><b>B</b></button>
    <button type="button" data-cmd="italic" title="Italic (Ctrl+I)"><i>I</i></button>
    <button type="button" data-cmd="strikeThrough" title="Strikethrough"><s>S</s></button>
    <button type="button" data-cmd="code" title="Inline code">&lt;/&gt;</button>
    <span class="sep"></span>
    <button type="button" data-block="h1" title="Heading 1">H1</button>
    <button type="button" data-block="h2" title="Heading 2">H2</button>
    <button type="button" data-block="h3" title="Heading 3">H3</button>
    <button type="button" data-block="p" title="Paragraph">P</button>
    <span class="sep"></span>
    <button type="button" data-cmd="insertUnorderedList" title="Bullet list">• List</button>
    <button type="button" data-cmd="insertOrderedList" title="Numbered list">1. List</button>
    <button type="button" data-block="blockquote" title="Quote">Quote</button>
    <span class="sep"></span>
    <button type="button" data-action="link" title="Link">Link</button>
    <button type="button" data-action="image" title="Insert image">Image</button>
    <button type="button" data-cmd="insertHorizontalRule" title="Horizontal line">—</button>
  </div>
  <details class="frontmatter" id="frontmatterBox" hidden>
    <summary>YAML</summary>
    <textarea id="frontmatter" spellcheck="false"></textarea>
  </details>
  <div id="editor" class="editor" contenteditable="true" role="textbox" aria-multiline="true" data-placeholder="Type here…"></div>
  <script src="${markedUri}"></script>
  <script src="${turndownUri}"></script>
  <script src="${jsUri}"></script>
</body>
</html>`;
}

module.exports = {
  activateVisualEditor,
  VIEW_TYPE,
};
