(() => {
  const vscode = acquireVsCodeApi();

  const backBtn = document.getElementById('backBtn');
  const homeBtn = document.getElementById('homeBtn');
  const refreshBtn = document.getElementById('refreshBtn');
  const crumbsEl = document.getElementById('crumbs');
  const gridEl = document.getElementById('grid');
  const statusEl = document.getElementById('status');
  const menuEl = document.getElementById('ctxMenu');

  /** @type {{ path: string, name: string }[]} */
  let crumbs = [];
  /** @type {Array<{ kind: string, path: string, name: string, label: string, iconEmoji: string, description: string, contextValue?: string, isWorkspaceRoot?: boolean, isCut?: boolean, fileUri?: string, menu?: Array<{ type: string, command?: string, title?: string }> }>} */
  let entries = [];
  /** @type {{ kind: string, path: string, name: string, contextValue?: string, isWorkspaceRoot?: boolean } | null} */
  let currentFolder = null;
  /** @type {'harrix' | 'material'} */
  let iconStyle = 'harrix';
  /** @type {{ folder: string, note: string }} */
  let iconUrls = { folder: '', note: '' };

  const FOLDER_SVG =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' +
    '<path d="M10 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg>';

  const NOTE_SVG =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' +
    '<path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm1 7V3.5L18.5 9H15z"/></svg>';

  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /**
   * @param {string} src
   */
  function imgHtml(src) {
    return `<img src="${escapeHtml(src)}" alt="" draggable="false" />`;
  }

  function hideContextMenu() {
    menuEl.hidden = true;
    menuEl.replaceChildren();
  }

  /**
   * @param {number} x
   * @param {number} y
   * @param {(typeof entries)[number]} entry
   * @param {Array<{ type: string, command?: string, title?: string }>} menu
   */
  function showContextMenuAt(x, y, entry, menu) {
    if (!menu.length) {
      hideContextMenu();
      return;
    }

    menuEl.replaceChildren();
    for (const row of menu) {
      if (row.type === 'separator') {
        const hr = document.createElement('div');
        hr.className = 'ctx-sep';
        menuEl.appendChild(hr);
        continue;
      }
      if (row.type !== 'item' || !row.command || !row.title) {
        continue;
      }
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'ctx-item';
      btn.textContent = row.title;
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        hideContextMenu();
        vscode.postMessage({
          type: 'runCommand',
          command: row.command,
          path: entry.path,
          kind: entry.kind,
          contextValue: entry.contextValue || '',
          isWorkspaceRoot: entry.isWorkspaceRoot === true,
        });
      });
      menuEl.appendChild(btn);
    }

    menuEl.hidden = false;
    const pad = 8;
    menuEl.style.left = '0px';
    menuEl.style.top = '0px';
    const rect = menuEl.getBoundingClientRect();
    let left = x;
    let top = y;
    if (left + rect.width > window.innerWidth - pad) {
      left = Math.max(pad, window.innerWidth - rect.width - pad);
    }
    if (top + rect.height > window.innerHeight - pad) {
      top = Math.max(pad, window.innerHeight - rect.height - pad);
    }
    menuEl.style.left = `${left}px`;
    menuEl.style.top = `${top}px`;
  }

  /**
   * @param {MouseEvent} event
   */
  function requestBackgroundContextMenu(event) {
    event.preventDefault();
    event.stopPropagation();
    if (!currentFolder?.path) {
      hideContextMenu();
      return;
    }
    vscode.postMessage({
      type: 'requestContextMenu',
      background: true,
      path: currentFolder.path,
      kind: 'folder',
      contextValue: currentFolder.contextValue || '',
      isWorkspaceRoot: currentFolder.isWorkspaceRoot === true,
      x: event.clientX,
      y: event.clientY,
    });
  }

  /**
   * @param {MouseEvent} event
   * @param {(typeof entries)[number]} entry
   */
  function requestContextMenu(event, entry) {
    event.preventDefault();
    event.stopPropagation();
    vscode.postMessage({
      type: 'requestContextMenu',
      path: entry.path,
      kind: entry.kind,
      contextValue: entry.contextValue || '',
      isWorkspaceRoot: entry.isWorkspaceRoot === true,
      x: event.clientX,
      y: event.clientY,
    });
  }

  function renderChrome() {
    const canGoUp = crumbs.length > 1;
    backBtn.disabled = !canGoUp;
    homeBtn.disabled = crumbs.length <= 1;

    crumbsEl.replaceChildren();
    crumbs.forEach((crumb, index) => {
      if (index > 0) {
        const sep = document.createElement('span');
        sep.className = 'sep';
        sep.textContent = '/';
        crumbsEl.appendChild(sep);
      }
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = index === crumbs.length - 1 ? 'crumb current' : 'crumb';
      btn.textContent = crumb.name || 'Notes';
      btn.title = crumb.path || crumb.name;
      if (index < crumbs.length - 1) {
        btn.addEventListener('click', () => {
          vscode.postMessage({ type: 'navigateTo', index });
        });
      }
      crumbsEl.appendChild(btn);
    });
  }

  function glyphHtml(entry) {
    if (entry.kind === 'folder') {
      if (iconStyle === 'harrix' && iconUrls.folder) {
        return imgHtml(iconUrls.folder);
      }
      return FOLDER_SVG;
    }
    const emoji = String(entry.iconEmoji || '').trim();
    if (emoji) {
      return escapeHtml(emoji);
    }
    if (iconStyle === 'harrix' && iconUrls.note) {
      return imgHtml(iconUrls.note);
    }
    return NOTE_SVG;
  }

  function fileNameFromPath(fsPath) {
    const p = String(fsPath || '').replace(/\\/g, '/');
    const i = p.lastIndexOf('/');
    return i >= 0 ? p.slice(i + 1) : p;
  }

  /**
   * @param {string} fsPath
   */
  function toFileUrl(fsPath) {
    let p = String(fsPath || '').replace(/\\/g, '/');
    if (!p) {
      return '';
    }
    if (!p.startsWith('/')) {
      p = `/${p}`;
    }
    return encodeURI(`file://${p}`).replace(/#/g, '%23');
  }

  /**
   * @param {DragEvent} event
   * @param {(typeof entries)[number]} entry
   */
  function onCellDragStart(event, entry) {
    const dt = event.dataTransfer;
    if (!dt || !entry.path) {
      event.preventDefault();
      return;
    }
    const fileUrl = entry.fileUri || toFileUrl(entry.path);
    const fileName = fileNameFromPath(entry.path).replace(/[:/\r\n]/g, '_');
    const mime = entry.kind === 'note' ? 'text/markdown' : 'application/octet-stream';
    dt.effectAllowed = 'copy';
    dt.setData('text/uri-list', `${fileUrl}\r\n`);
    dt.setData('application/vnd.code.uri-list', fileUrl);
    dt.setData('DownloadURL', `${mime}:${fileName}:${fileUrl}`);
  }

  function renderGrid() {
    hideContextMenu();
    gridEl.replaceChildren();
    if (!entries.length) {
      statusEl.hidden = false;
      statusEl.textContent = 'This folder has no notes or subfolders.';
      return;
    }
    statusEl.hidden = true;

    for (const entry of entries) {
      const fileUrl = entry.fileUri || toFileUrl(entry.path);
      const btn = document.createElement('a');
      btn.href = fileUrl;
      btn.className = entry.isCut ? 'cell is-cut' : 'cell';
      btn.title = entry.path;
      btn.setAttribute('role', 'button');

      const glyph = document.createElement('div');
      glyph.className = 'glyph';
      glyph.innerHTML = glyphHtml(entry);

      const label = document.createElement('div');
      label.className = 'label';
      label.textContent = entry.label || entry.name;

      btn.appendChild(glyph);
      btn.appendChild(label);

      if (entry.description) {
        const desc = document.createElement('div');
        desc.className = 'desc';
        desc.textContent = entry.description;
        btn.appendChild(desc);
      }

      btn.draggable = true;
      let skipClickAfterDrag = false;

      btn.addEventListener('dragstart', (event) => {
        skipClickAfterDrag = true;
        onCellDragStart(event, entry);
      });
      btn.addEventListener('dragend', () => {
        setTimeout(() => {
          skipClickAfterDrag = false;
        }, 0);
      });

      btn.addEventListener('click', (event) => {
        event.preventDefault();
        if (skipClickAfterDrag) {
          skipClickAfterDrag = false;
          return;
        }
        hideContextMenu();
        if (entry.kind === 'folder') {
          vscode.postMessage({ type: 'openFolder', path: entry.path, name: entry.name });
        } else {
          vscode.postMessage({ type: 'openNote', path: entry.path });
        }
      });
      btn.addEventListener('auxclick', (event) => {
        event.preventDefault();
      });

      btn.addEventListener('contextmenu', (event) => {
        requestContextMenu(event, entry);
      });

      gridEl.appendChild(btn);
    }
  }

  function applyState(msg) {
    crumbs = Array.isArray(msg.crumbs) ? msg.crumbs : [];
    entries = Array.isArray(msg.entries) ? msg.entries : [];
    currentFolder = msg.currentFolder && typeof msg.currentFolder === 'object' ? msg.currentFolder : null;
    iconStyle = msg.iconStyle === 'material' ? 'material' : 'harrix';
    const icons = msg.icons && typeof msg.icons === 'object' ? msg.icons : {};
    iconUrls = {
      folder: typeof icons.folder === 'string' ? icons.folder : '',
      note: typeof icons.note === 'string' ? icons.note : '',
    };
    renderChrome();
    renderGrid();
  }

  backBtn.addEventListener('click', () => {
    vscode.postMessage({ type: 'goBack' });
  });
  homeBtn.addEventListener('click', () => {
    vscode.postMessage({ type: 'goHome' });
  });
  refreshBtn.addEventListener('click', () => {
    vscode.postMessage({ type: 'refresh' });
  });

  const mainEl = document.querySelector('.main');
  if (mainEl) {
    mainEl.addEventListener('contextmenu', (event) => {
      if (event.target.closest('.cell')) {
        return;
      }
      requestBackgroundContextMenu(event);
    });
  }

  document.addEventListener('click', () => {
    hideContextMenu();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      hideContextMenu();
    }
  });
  window.addEventListener('blur', () => {
    hideContextMenu();
  });
  menuEl.addEventListener('click', (event) => {
    event.stopPropagation();
  });
  menuEl.addEventListener('contextmenu', (event) => {
    event.preventDefault();
  });

  window.addEventListener('message', (event) => {
    const msg = event.data;
    if (!msg || typeof msg !== 'object') {
      return;
    }
    if (msg.type === 'state') {
      applyState(msg);
    }
    if (msg.type === 'contextMenu') {
      const entry = entries.find((e) => e.path === msg.path) || {
        kind: msg.kind || 'note',
        path: msg.path,
        name: '',
        label: '',
        iconEmoji: '',
        description: '',
        contextValue: msg.contextValue || '',
        isWorkspaceRoot: msg.isWorkspaceRoot === true,
      };
      showContextMenuAt(msg.x || 0, msg.y || 0, entry, Array.isArray(msg.menu) ? msg.menu : []);
    }
  });

  vscode.postMessage({ type: 'ready' });
})();
