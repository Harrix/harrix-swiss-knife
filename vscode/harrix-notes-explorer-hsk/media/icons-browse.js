(() => {
  const vscode = acquireVsCodeApi();

  const backBtn = document.getElementById('backBtn');
  const homeBtn = document.getElementById('homeBtn');
  const refreshBtn = document.getElementById('refreshBtn');
  const sortViewBtn = document.getElementById('sortViewBtn');
  const crumbsEl = document.getElementById('crumbs');
  const gridEl = document.getElementById('grid');
  const statusEl = document.getElementById('status');
  const menuEl = document.getElementById('ctxMenu');
  const sortMenuEl = document.getElementById('sortMenu');

  /** @type {{ path: string, name: string }[]} */
  let crumbs = [];
  /** @type {Array<{ path: string, name: string, depth: number }>} */
  let folderTree = [];
  /** @type {Array<{ kind: string, path: string, name: string, label: string, iconEmoji: string, description: string, thumbnailImage?: string, thumbnailExcerpt?: string, contextValue?: string, isWorkspaceRoot?: boolean, isCut?: boolean, menu?: Array<{ type: string, command?: string, title?: string }> }>} */
  let entries = [];
  /** @type {{ kind: string, path: string, name: string, contextValue?: string, isWorkspaceRoot?: boolean } | null} */
  let currentFolder = null;
  /** @type {'harrix' | 'material'} */
  let iconStyle = 'harrix';
  /** @type {{ layout: 'icons' | 'list' | 'thumbnails' | 'tree', sortBy: 'name' | 'date' | 'size', foldersFirst: boolean, reverseOrder: boolean, showGmdFiles: boolean, showDates: boolean }} */
  let browse = {
    layout: 'icons',
    sortBy: 'name',
    foldersFirst: false,
    reverseOrder: false,
    showGmdFiles: false,
    showDates: false,
  };
  /** @type {{ folder: string, note: string }} */
  let iconUrls = { folder: '', note: '' };

  const LIST_SVG =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' +
    '<path d="M4 6h2v2H4V6zm4 0h12v2H8V6zM4 11h2v2H4v-2zm4 0h12v2H8v-2zM4 16h2v2H4v-2zm4 0h12v2H8v-2z"/></svg>';
  const GRID_SVG =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' +
    '<path d="M4 4h7v7H4V4zm9 0h7v7h-7V4zM4 13h7v7H4v-7zm9 0h7v7h-7v-7z"/></svg>';
  const DASHBOARD_SVG =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' +
    '<path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/></svg>';
  const TREE_SVG =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' +
    '<path d="M22 11V3h-7v3H9V3H2v8h7V8h2v10h4v3h7v-8h-7v3h-2V8h2v3z"/></svg>';
  const CHECK_SVG =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' +
    '<path d="M9 16.17 4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>';

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

  function hideSortMenu() {
    sortMenuEl.hidden = true;
    sortViewBtn.setAttribute('aria-expanded', 'false');
  }

  function hideAllMenus() {
    hideContextMenu();
    hideSortMenu();
  }

  /**
   * @param {number} x
   * @param {number} y
   * @param {(typeof entries)[number]} entry
   * @param {Array<{ type: string, command?: string, title?: string }>} menu
   */
  function showContextMenuAt(x, y, entry, menu) {
    hideSortMenu();
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

  function syncLayoutClass() {
    document.body.classList.toggle('layout-list', browse.layout === 'list');
    document.body.classList.toggle('layout-icons', browse.layout === 'icons');
    document.body.classList.toggle('layout-thumbs', browse.layout === 'thumbnails');
    document.body.classList.toggle('layout-tree', browse.layout === 'tree');
  }

  /**
   * @param {string} title
   * @param {{
   *   lead?: string,
   *   checked?: boolean,
   *   check?: 'lead' | 'trail',
   *   onClick: () => void,
   * }} opts
   */
  function sortMenuItem(title, opts) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'ctx-item menu-row';
    btn.setAttribute('role', 'menuitem');

    const lead = document.createElement('span');
    lead.className = 'ctx-lead';
    if (opts.lead) {
      lead.innerHTML = opts.lead;
    } else if (opts.checked && opts.check === 'lead') {
      lead.innerHTML = CHECK_SVG;
    }

    const label = document.createElement('span');
    label.className = 'ctx-item-label';
    label.textContent = title;

    const trail = document.createElement('span');
    trail.className = 'ctx-trail';
    if (opts.checked && opts.check === 'trail') {
      trail.innerHTML = CHECK_SVG;
    }

    btn.appendChild(lead);
    btn.appendChild(label);
    btn.appendChild(trail);
    btn.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopPropagation();
      opts.onClick();
    });
    return btn;
  }

  function renderSortMenu() {
    sortMenuEl.replaceChildren();
    sortMenuEl.appendChild(
      sortMenuItem('List', {
        lead: LIST_SVG,
        checked: browse.layout === 'list',
        check: 'trail',
        onClick: () => vscode.postMessage({ type: 'setBrowseOption', key: 'layout', value: 'list' }),
      }),
    );
    sortMenuEl.appendChild(
      sortMenuItem('Icons', {
        lead: GRID_SVG,
        checked: browse.layout === 'icons',
        check: 'trail',
        onClick: () => vscode.postMessage({ type: 'setBrowseOption', key: 'layout', value: 'icons' }),
      }),
    );
    sortMenuEl.appendChild(
      sortMenuItem('Thumbnails', {
        lead: DASHBOARD_SVG,
        checked: browse.layout === 'thumbnails',
        check: 'trail',
        onClick: () => vscode.postMessage({ type: 'setBrowseOption', key: 'layout', value: 'thumbnails' }),
      }),
    );
    sortMenuEl.appendChild(
      sortMenuItem('Tree', {
        lead: TREE_SVG,
        checked: browse.layout === 'tree',
        check: 'trail',
        onClick: () => vscode.postMessage({ type: 'setBrowseOption', key: 'layout', value: 'tree' }),
      }),
    );
    const sep1 = document.createElement('div');
    sep1.className = 'ctx-sep';
    sortMenuEl.appendChild(sep1);
    for (const [value, title] of [
      ['name', 'Name'],
      ['date', 'Date'],
      ['size', 'Size'],
    ]) {
      sortMenuEl.appendChild(
        sortMenuItem(title, {
          checked: browse.sortBy === value,
          check: 'lead',
          onClick: () => vscode.postMessage({ type: 'setBrowseOption', key: 'sortBy', value }),
        }),
      );
    }
    const sep2 = document.createElement('div');
    sep2.className = 'ctx-sep';
    sortMenuEl.appendChild(sep2);
    sortMenuEl.appendChild(
      sortMenuItem('Folders on top', {
        checked: browse.foldersFirst,
        check: 'trail',
        onClick: () =>
          vscode.postMessage({ type: 'setBrowseOption', key: 'foldersFirst', value: !browse.foldersFirst }),
      }),
    );
    sortMenuEl.appendChild(
      sortMenuItem('Reverse order', {
        checked: browse.reverseOrder,
        check: 'trail',
        onClick: () =>
          vscode.postMessage({ type: 'setBrowseOption', key: 'reverseOrder', value: !browse.reverseOrder }),
      }),
    );
    sortMenuEl.appendChild(
      sortMenuItem('Show .g.md files', {
        checked: browse.showGmdFiles,
        check: 'trail',
        onClick: () =>
          vscode.postMessage({ type: 'setBrowseOption', key: 'showGmdFiles', value: !browse.showGmdFiles }),
      }),
    );
    sortMenuEl.appendChild(
      sortMenuItem('Show dates', {
        checked: browse.showDates,
        check: 'trail',
        onClick: () => vscode.postMessage({ type: 'setBrowseOption', key: 'showDates', value: !browse.showDates }),
      }),
    );
  }

  function positionSortMenu() {
    const pad = 8;
    const btnRect = sortViewBtn.getBoundingClientRect();
    sortMenuEl.style.left = '0px';
    sortMenuEl.style.top = '0px';
    const rect = sortMenuEl.getBoundingClientRect();
    let left = btnRect.right - rect.width;
    let top = btnRect.bottom + 4;
    if (left < pad) {
      left = pad;
    }
    if (left + rect.width > window.innerWidth - pad) {
      left = Math.max(pad, window.innerWidth - rect.width - pad);
    }
    if (top + rect.height > window.innerHeight - pad) {
      top = Math.max(pad, btnRect.top - rect.height - 4);
    }
    sortMenuEl.style.left = `${left}px`;
    sortMenuEl.style.top = `${top}px`;
  }

  function showSortMenu() {
    hideContextMenu();
    renderSortMenu();
    sortMenuEl.hidden = false;
    sortViewBtn.setAttribute('aria-expanded', 'true');
    positionSortMenu();
  }

  /**
   * @param {(typeof entries)[number]} entry
   * @param {'row' | 'thumb' | 'cell'} itemClass
   */
  function createEntryButton(entry, itemClass) {
    const isList = itemClass === 'row';
    const isThumbs = itemClass === 'thumb';
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = entry.isCut ? `${itemClass} is-cut` : itemClass;
    btn.title = entry.path;

    const label = document.createElement('div');
    label.className = 'label';
    label.textContent = entry.label || entry.name;

    if (isThumbs) {
      const preview = document.createElement('div');
      preview.className = entry.kind === 'folder' ? 'thumb-preview is-folder' : 'thumb-preview';
      if (entry.kind === 'folder') {
        preview.innerHTML = glyphHtml(entry);
      } else if (entry.thumbnailImage) {
        preview.innerHTML = imgHtml(entry.thumbnailImage);
      } else {
        const excerpt = document.createElement('div');
        excerpt.className = 'thumb-excerpt';
        excerpt.textContent = entry.thumbnailExcerpt || '';
        preview.appendChild(excerpt);
      }
      btn.appendChild(preview);
      btn.appendChild(label);
    } else {
      const glyph = document.createElement('div');
      glyph.className = 'glyph';
      glyph.innerHTML = glyphHtml(entry);
      btn.appendChild(glyph);
      if (isList) {
        const text = document.createElement('div');
        text.className = 'row-text';
        text.appendChild(label);
        if (entry.description) {
          const desc = document.createElement('div');
          desc.className = 'desc';
          desc.textContent = entry.description;
          text.appendChild(desc);
        }
        btn.appendChild(text);
      } else {
        btn.appendChild(label);
        if (entry.description) {
          const desc = document.createElement('div');
          desc.className = 'desc';
          desc.textContent = entry.description;
          btn.appendChild(desc);
        }
      }
    }

    btn.addEventListener('click', () => {
      hideContextMenu();
      if (entry.kind === 'folder') {
        vscode.postMessage({ type: 'openFolder', path: entry.path, name: entry.name });
      } else {
        vscode.postMessage({ type: 'openNote', path: entry.path });
      }
    });
    btn.addEventListener('contextmenu', (event) => {
      requestContextMenu(event, entry);
    });
    return btn;
  }

  function sameFsPath(left, right) {
    const a = String(left || '')
      .replace(/\\/g, '/')
      .replace(/\/+$/, '');
    const b = String(right || '')
      .replace(/\\/g, '/')
      .replace(/\/+$/, '');
    return a === b || a.toLowerCase() === b.toLowerCase();
  }

  function appendTreeZone(depth) {
    const zone = document.createElement('div');
    zone.className = 'tree-zone';
    zone.style.setProperty('--tree-zone-inset', `${Math.max(0, depth) * 16}px`);
    statusEl.hidden = true;
    if (!entries.length) {
      const empty = document.createElement('div');
      empty.className = 'status';
      empty.textContent = 'This folder has no notes or subfolders.';
      zone.appendChild(empty);
    } else {
      const inner = document.createElement('div');
      inner.className = 'grid';
      for (const entry of entries) {
        inner.appendChild(createEntryButton(entry, 'cell'));
      }
      zone.appendChild(inner);
    }
    gridEl.appendChild(zone);
  }

  function renderTreeBrowse() {
    gridEl.className = 'tree-browse';
    const currentPath = currentFolder?.path || crumbs[crumbs.length - 1]?.path || '';
    const nodes =
      folderTree.length > 0
        ? folderTree
        : crumbs.map((crumb, index) => ({
            path: crumb.path || '',
            name: crumb.name,
            depth: index,
          }));
    let placedZone = false;
    for (const node of nodes) {
      const isCurrent = sameFsPath(node.path, currentPath);
      const row = document.createElement('button');
      row.type = 'button';
      row.className = isCurrent ? 'tree-level is-current' : 'tree-level';
      row.style.setProperty('--tree-depth', String(node.depth));
      row.title = node.path || node.name;
      const glyph = document.createElement('div');
      glyph.className = 'glyph';
      glyph.innerHTML = glyphHtml({ kind: 'folder', iconEmoji: '' });
      const label = document.createElement('div');
      label.className = 'label';
      label.textContent = node.name || 'Notes';
      row.appendChild(glyph);
      row.appendChild(label);
      if (!isCurrent) {
        row.addEventListener('click', () => {
          hideContextMenu();
          vscode.postMessage({ type: 'openFolder', path: node.path, name: node.name });
        });
      }
      gridEl.appendChild(row);
      if (isCurrent) {
        appendTreeZone(node.depth);
        placedZone = true;
      }
    }
    if (!placedZone) {
      appendTreeZone(Math.max(0, crumbs.length - 1));
    }
  }

  function renderEntries() {
    hideContextMenu();
    gridEl.replaceChildren();
    const isList = browse.layout === 'list';
    const isThumbs = browse.layout === 'thumbnails';
    const isTree = browse.layout === 'tree';
    syncLayoutClass();
    if (!sortMenuEl.hidden) {
      renderSortMenu();
      positionSortMenu();
    }

    if (isTree) {
      renderTreeBrowse();
      return;
    }

    gridEl.className = isList ? 'list' : isThumbs ? 'thumbs' : 'grid';

    if (!entries.length) {
      statusEl.hidden = false;
      statusEl.textContent = 'This folder has no notes or subfolders.';
      return;
    }
    statusEl.hidden = true;

    const itemClass = isList ? 'row' : isThumbs ? 'thumb' : 'cell';
    for (const entry of entries) {
      gridEl.appendChild(createEntryButton(entry, itemClass));
    }
  }

  function applyState(msg) {
    crumbs = Array.isArray(msg.crumbs) ? msg.crumbs : [];
    entries = Array.isArray(msg.entries) ? msg.entries : [];
    folderTree = Array.isArray(msg.folderTree) ? msg.folderTree : [];
    currentFolder = msg.currentFolder && typeof msg.currentFolder === 'object' ? msg.currentFolder : null;
    iconStyle = msg.iconStyle === 'material' ? 'material' : 'harrix';
    const nextBrowse = msg.browse && typeof msg.browse === 'object' ? msg.browse : {};
    browse = {
      layout:
        nextBrowse.layout === 'list'
          ? 'list'
          : nextBrowse.layout === 'thumbnails'
            ? 'thumbnails'
            : nextBrowse.layout === 'tree'
              ? 'tree'
              : 'icons',
      sortBy: nextBrowse.sortBy === 'date' || nextBrowse.sortBy === 'size' ? nextBrowse.sortBy : 'name',
      foldersFirst: nextBrowse.foldersFirst === true,
      reverseOrder: nextBrowse.reverseOrder === true,
      showGmdFiles: nextBrowse.showGmdFiles === true,
      showDates: nextBrowse.showDates === true,
    };
    const icons = msg.icons && typeof msg.icons === 'object' ? msg.icons : {};
    iconUrls = {
      folder: typeof icons.folder === 'string' ? icons.folder : '',
      note: typeof icons.note === 'string' ? icons.note : '',
    };
    renderChrome();
    renderEntries();
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
  sortViewBtn.addEventListener('click', (event) => {
    event.stopPropagation();
    if (sortMenuEl.hidden) {
      showSortMenu();
    } else {
      hideSortMenu();
    }
  });

  const mainEl = document.querySelector('.main');
  if (mainEl) {
    mainEl.addEventListener('contextmenu', (event) => {
      if (event.target.closest('.cell, .row, .thumb, .tree-level')) {
        return;
      }
      requestBackgroundContextMenu(event);
    });
  }

  document.addEventListener('click', () => {
    hideAllMenus();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      hideAllMenus();
    }
  });
  window.addEventListener('blur', () => {
    hideAllMenus();
  });
  menuEl.addEventListener('click', (event) => {
    event.stopPropagation();
  });
  menuEl.addEventListener('contextmenu', (event) => {
    event.preventDefault();
  });
  sortMenuEl.addEventListener('click', (event) => {
    event.stopPropagation();
  });
  sortMenuEl.addEventListener('contextmenu', (event) => {
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
