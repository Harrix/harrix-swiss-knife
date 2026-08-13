(() => {
  const vscode = acquireVsCodeApi();

  const backBtn = document.getElementById('backBtn');
  const homeBtn = document.getElementById('homeBtn');
  const crumbsEl = document.getElementById('crumbs');
  const gridEl = document.getElementById('grid');
  const statusEl = document.getElementById('status');

  /** @type {{ path: string, name: string }[]} */
  let crumbs = [];
  /** @type {Array<{ kind: string, path: string, name: string, label: string, iconEmoji: string, description: string }>} */
  let entries = [];
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

  function renderGrid() {
    gridEl.replaceChildren();
    if (!entries.length) {
      statusEl.hidden = false;
      statusEl.textContent = 'This folder has no notes or subfolders.';
      return;
    }
    statusEl.hidden = true;

    for (const entry of entries) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'cell';
      btn.title = entry.path;

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

      btn.addEventListener('click', () => {
        if (entry.kind === 'folder') {
          vscode.postMessage({ type: 'openFolder', path: entry.path, name: entry.name });
        } else {
          vscode.postMessage({ type: 'openNote', path: entry.path });
        }
      });

      gridEl.appendChild(btn);
    }
  }

  function applyState(msg) {
    crumbs = Array.isArray(msg.crumbs) ? msg.crumbs : [];
    entries = Array.isArray(msg.entries) ? msg.entries : [];
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

  window.addEventListener('message', (event) => {
    const msg = event.data;
    if (!msg || typeof msg !== 'object') {
      return;
    }
    if (msg.type === 'state') {
      applyState(msg);
    }
  });

  vscode.postMessage({ type: 'ready' });
})();
