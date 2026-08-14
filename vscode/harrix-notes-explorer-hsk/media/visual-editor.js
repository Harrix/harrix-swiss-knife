(() => {
  const vscode = acquireVsCodeApi();
  const editor = document.getElementById('editor');
  const frontmatterBox = document.getElementById('frontmatterBox');
  const frontmatterEl = document.getElementById('frontmatter');

  const turndown = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced',
    emDelimiter: '*',
    bulletListMarker: '-',
    hr: '---',
  });
  turndown.addRule('mdImage', {
    filter: 'img',
    replacement(_content, node) {
      const src = node.getAttribute('data-md-src') || node.getAttribute('src') || '';
      if (!src || src.startsWith('vscode-webview:')) {
        return '';
      }
      const alt = node.getAttribute('alt') || '';
      const title = node.getAttribute('title');
      return title ? `![${alt}](${src} "${title}")` : `![${alt}](${src})`;
    },
  });
  turndown.addRule('mdLink', {
    filter: 'a',
    replacement(content, node) {
      const href = node.getAttribute('data-md-href') || node.getAttribute('href') || '';
      if (!href) {
        return content;
      }
      return `[${content}](${href})`;
    },
  });

  let applying = false;
  let editTimer = 0;
  let lastText = '';

  function splitFrontmatter(text) {
    const match = String(text || '').match(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/);
    if (!match) {
      return { frontmatter: '', body: String(text || '') };
    }
    return { frontmatter: match[0], body: String(text).slice(match[0].length) };
  }

  function parseMarkdown(body) {
    const parse = window.marked?.parse || window.marked;
    if (typeof parse !== 'function') {
      return `<p>${escapeHtml(body)}</p>`;
    }
    return parse(body, { gfm: true, breaks: false });
  }

  function escapeHtml(value) {
    return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  /**
   * @param {string} html
   * @param {Record<string, string>} imageUris
   */
  function rewriteMedia(html, imageUris) {
    const wrap = document.createElement('div');
    wrap.innerHTML = html;
    for (const img of wrap.querySelectorAll('img')) {
      const src = img.getAttribute('src') || '';
      if (src && !/^(https?:|data:|vscode-webview:)/i.test(src)) {
        img.setAttribute('data-md-src', src);
        if (imageUris[src]) {
          img.setAttribute('src', imageUris[src]);
        }
      }
    }
    for (const link of wrap.querySelectorAll('a')) {
      const href = link.getAttribute('href') || '';
      if (href && !/^(https?:|mailto:|#)/i.test(href)) {
        link.setAttribute('data-md-href', href);
      }
    }
    return wrap.innerHTML;
  }

  function currentMarkdown() {
    const fm = frontmatterEl.value;
    const body = turndown
      .turndown(editor.innerHTML)
      .replace(/\u00a0/g, ' ')
      .trimEnd();
    let text = fm;
    if (fm && body) {
      if (!fm.endsWith('\n')) {
        text += '\n';
      }
      text += body;
    } else if (body) {
      text = body;
    }
    if (lastText.endsWith('\n') && text && !text.endsWith('\n')) {
      text += '\n';
    }
    return text;
  }

  function scheduleSave() {
    if (applying) {
      return;
    }
    window.clearTimeout(editTimer);
    editTimer = window.setTimeout(() => {
      const text = currentMarkdown();
      if (text !== lastText) {
        lastText = text;
        vscode.postMessage({ type: 'edit', text });
      }
    }, 350);
  }

  function setDocument(text, imageUris) {
    applying = true;
    lastText = text;
    const { frontmatter, body } = splitFrontmatter(text);
    if (frontmatter) {
      frontmatterBox.hidden = false;
      frontmatterEl.value = frontmatter.replace(/\n$/, '');
    } else {
      frontmatterBox.hidden = true;
      frontmatterEl.value = '';
    }
    const html = rewriteMedia(parseMarkdown(body), imageUris || {});
    editor.innerHTML = html || '<p><br></p>';
    applying = false;
  }

  function runCommand(command) {
    editor.focus();
    if (command === 'code') {
      const sel = window.getSelection();
      const selected = sel ? String(sel) : '';
      document.execCommand('insertHTML', false, `<code>${escapeHtml(selected) || 'code'}</code>`);
      scheduleSave();
      return;
    }
    document.execCommand(command, false);
    scheduleSave();
  }

  function runBlock(tag) {
    editor.focus();
    document.execCommand('formatBlock', false, tag);
    scheduleSave();
  }

  document.querySelector('.toolbar')?.addEventListener('click', (event) => {
    const btn = event.target.closest('button');
    if (!btn) {
      return;
    }
    if (btn.dataset.cmd) {
      runCommand(btn.dataset.cmd);
      return;
    }
    if (btn.dataset.block) {
      runBlock(btn.dataset.block);
      return;
    }
    if (btn.dataset.action === 'link') {
      vscode.postMessage({ type: 'promptLink' });
      return;
    }
    if (btn.dataset.action === 'image') {
      vscode.postMessage({ type: 'pickImages' });
    }
  });

  editor.addEventListener('input', () => {
    scheduleSave();
  });
  frontmatterEl.addEventListener('input', () => {
    if (!frontmatterEl.value.startsWith('---')) {
      frontmatterEl.value = `---\n${frontmatterEl.value.replace(/^---\n?/, '')}\n---`;
    }
    scheduleSave();
  });

  editor.addEventListener('click', (event) => {
    const link = event.target.closest('a');
    if (link) {
      event.preventDefault();
    }
  });

  editor.addEventListener('keydown', (event) => {
    if (!(event.ctrlKey || event.metaKey)) {
      return;
    }
    const key = event.key.toLowerCase();
    if (key === 'b') {
      event.preventDefault();
      runCommand('bold');
    } else if (key === 'i') {
      event.preventDefault();
      runCommand('italic');
    }
  });

  /**
   * @param {File[]} files
   */
  async function sendFiles(files) {
    /** @type {Array<{ name: string, mime: string, base64: string }>} */
    const payload = [];
    for (const file of files) {
      const buffer = await file.arrayBuffer();
      const bytes = new Uint8Array(buffer);
      let binary = '';
      for (const byte of bytes) {
        binary += String.fromCharCode(byte);
      }
      payload.push({
        name: file.name || 'image.png',
        mime: file.type || 'application/octet-stream',
        base64: btoa(binary),
      });
    }
    if (payload.length > 0) {
      vscode.postMessage({ type: 'dropFiles', files: payload });
    }
  }

  editor.addEventListener('dragover', (event) => {
    event.preventDefault();
  });
  editor.addEventListener('drop', (event) => {
    event.preventDefault();
    const files = [...(event.dataTransfer?.files || [])];
    if (files.length > 0) {
      void sendFiles(files);
      return;
    }
    const uriList = event.dataTransfer?.getData('text/uri-list') || '';
    const uris = uriList
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line && !line.startsWith('#'));
    if (uris.length > 0) {
      vscode.postMessage({ type: 'dropUris', uris });
    }
  });

  editor.addEventListener('paste', (event) => {
    const items = [...(event.clipboardData?.items || [])];
    const files = items
      .filter((item) => item.kind === 'file')
      .map((item) => item.getAsFile())
      .filter((file) => file);
    if (files.length > 0) {
      event.preventDefault();
      void sendFiles(files);
    }
  });

  window.addEventListener('message', (event) => {
    const msg = event.data;
    if (!msg || typeof msg !== 'object') {
      return;
    }
    if (msg.type === 'setDocument') {
      setDocument(typeof msg.text === 'string' ? msg.text : '', msg.imageUris || {});
    }
    if (msg.type === 'insertLink' && typeof msg.url === 'string') {
      editor.focus();
      document.execCommand('createLink', false, msg.url);
      scheduleSave();
    }
    if (msg.type === 'insertHtml' && typeof msg.html === 'string') {
      editor.focus();
      document.execCommand('insertHTML', false, msg.html);
      scheduleSave();
    }
  });

  vscode.postMessage({ type: 'ready' });
})();
