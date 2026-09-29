(() => {
  const vscodeApi = acquireVsCodeApi();

  const refreshBtn = document.getElementById('refreshBtn');
  const helpBtn = document.getElementById('helpBtn');
  const gridEl = document.getElementById('grid');
  const statusEl = document.getElementById('status');
  const menuEl = document.getElementById('ctxMenu');

  /** @type {Array<{
   *   id: string,
   *   kind: string,
   *   path: string,
   *   label: string,
   *   description: string,
   *   iconEmoji: string,
   *   iconImage: string,
   *   index: number,
   *   canMoveUp: boolean,
   *   canMoveDown: boolean,
   *   missing: boolean,
   * }>} */
  let entries = [];
  let maxItems = 20;
  /** @type {'harrix' | 'material'} */
  let iconStyle = 'harrix';
  /** @type {{ folder: string, note: string }} */
  let iconUrls = { folder: '', note: '' };

  const HOME_SVG =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' +
    '<path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>';
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
   * @param {(typeof entries)[number]} entry
   */
  function glyphHtml(entry) {
    if (entry.kind === 'home') {
      return `<span class="glyph home">${HOME_SVG}</span>`;
    }
    if (entry.kind === 'folder') {
      if (iconStyle === 'harrix' && iconUrls.folder) {
        return `<span class="glyph">${imgHtml(iconUrls.folder)}</span>`;
      }
      return `<span class="glyph">${FOLDER_SVG}</span>`;
    }
    const emoji = String(entry.iconEmoji || '').trim();
    if (emoji) {
      return `<span class="glyph">${escapeHtml(emoji)}</span>`;
    }
    const iconImage = String(entry.iconImage || '').trim();
    if (iconImage) {
      return `<span class="glyph">${imgHtml(iconImage)}</span>`;
    }
    if (iconStyle === 'harrix' && iconUrls.note) {
      return `<span class="glyph">${imgHtml(iconUrls.note)}</span>`;
    }
    return `<span class="glyph">${NOTE_SVG}</span>`;
  }

  /**
   * @param {number} x
   * @param {number} y
   * @param {(typeof entries)[number]} entry
   */
  function showContextMenuAt(x, y, entry) {
    menuEl.replaceChildren();

    /** @type {Array<{ title: string, type: string } | { type: 'separator' }>} */
    const rows = [{ type: 'item', title: 'Open' }, { type: 'separator' }];
    if (entry.canMoveUp) {
      rows.push({ type: 'item', title: 'Move Up' });
    }
    if (entry.canMoveDown) {
      rows.push({ type: 'item', title: 'Move Down' });
    }
    if (entry.canMoveUp || entry.canMoveDown) {
      rows.push({ type: 'separator' });
    }
    rows.push({ type: 'item', title: 'Unpin' });

    for (const row of rows) {
      if (row.type === 'separator') {
        const hr = document.createElement('div');
        hr.className = 'ctx-sep';
        menuEl.appendChild(hr);
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
        if (row.title === 'Open') {
          vscodeApi.postMessage({ type: 'open', id: entry.id, path: entry.path, kind: entry.kind });
        } else if (row.title === 'Move Up') {
          vscodeApi.postMessage({ type: 'moveUp', id: entry.id });
        } else if (row.title === 'Move Down') {
          vscodeApi.postMessage({ type: 'moveDown', id: entry.id });
        } else if (row.title === 'Unpin') {
          vscodeApi.postMessage({ type: 'unpin', id: entry.id, path: entry.path });
        }
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

  function render() {
    hideContextMenu();
    gridEl.replaceChildren();

    if (!entries.length) {
      statusEl.hidden = false;
      statusEl.textContent =
        'No pinned folders or notes yet. Right-click a folder or note in Harrix Notes (HSK) and choose Pin. You can also pin from the editor title bar.';
      return;
    }

    statusEl.hidden = true;
    for (const entry of entries) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = entry.missing ? 'cell missing' : 'cell';
      btn.setAttribute('role', 'listitem');
      btn.title = entry.path || entry.label;
      btn.innerHTML =
        glyphHtml(entry) +
        `<span class="label">${escapeHtml(entry.label)}</span>` +
        (entry.description ? `<span class="caption">${escapeHtml(entry.description)}</span>` : '');
      btn.addEventListener('click', () => {
        vscodeApi.postMessage({ type: 'open', id: entry.id, path: entry.path, kind: entry.kind });
      });
      btn.addEventListener('contextmenu', (event) => {
        event.preventDefault();
        event.stopPropagation();
        showContextMenuAt(event.clientX, event.clientY, entry);
      });
      gridEl.appendChild(btn);
    }
  }

  refreshBtn.addEventListener('click', () => {
    vscodeApi.postMessage({ type: 'refresh' });
  });
  helpBtn.addEventListener('click', () => {
    vscodeApi.postMessage({ type: 'howToPin' });
  });

  document.addEventListener('click', () => {
    hideContextMenu();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      hideContextMenu();
    }
  });

  window.addEventListener('message', (event) => {
    const msg = event.data;
    if (!msg || typeof msg !== 'object') {
      return;
    }
    if (msg.type === 'state') {
      entries = Array.isArray(msg.entries) ? msg.entries : [];
      maxItems = typeof msg.maxItems === 'number' ? msg.maxItems : 20;
      iconStyle = msg.iconStyle === 'material' ? 'material' : 'harrix';
      iconUrls = {
        folder: msg.icons?.folder || '',
        note: msg.icons?.note || '',
      };
      void maxItems;
      render();
    }
  });

  vscodeApi.postMessage({ type: 'ready' });
})();
