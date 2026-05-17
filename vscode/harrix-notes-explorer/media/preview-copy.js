(function () {
  const BUTTON_BASE_CLASS = 'hne-copy-btn';
  const WRAPPER_CLASS = 'hne-code-wrapper';

  const DEFAULT_CONFIG = {
    enabled: true,
    showTop: true,
    showBottom: true,
    topAlwaysVisible: true,
    bottomHoverZonePx: 80,
    backgroundColor: '#fefefe',
    borderColor: '#7f7f7f',
    copiedColor: '#388a34'
  };

  const CLIPBOARD_ICON =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';

  const CHECK_ICON =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>';

  /** @type {typeof DEFAULT_CONFIG} */
  let activeConfig = { ...DEFAULT_CONFIG };

  function readConfigFromDom() {
    const el = document.getElementById('hne-preview-copy-config');
    if (!el) {
      return { ...DEFAULT_CONFIG };
    }
    try {
      const parsed = JSON.parse(el.getAttribute('data-config') || '{}');
      return {
        enabled: parsed.enabled !== false,
        showTop: parsed.showTop !== false,
        showBottom: parsed.showBottom !== false,
        topAlwaysVisible: parsed.topAlwaysVisible !== false,
        bottomHoverZonePx:
          typeof parsed.bottomHoverZonePx === 'number' && parsed.bottomHoverZonePx >= 0
            ? parsed.bottomHoverZonePx
            : DEFAULT_CONFIG.bottomHoverZonePx,
        backgroundColor: parsed.backgroundColor || DEFAULT_CONFIG.backgroundColor,
        borderColor: parsed.borderColor || DEFAULT_CONFIG.borderColor,
        copiedColor: parsed.copiedColor || DEFAULT_CONFIG.copiedColor
      };
    } catch {
      return { ...DEFAULT_CONFIG };
    }
  }

  function applyConfig() {
    activeConfig = readConfigFromDom();
    const root = document.documentElement;
    root.style.setProperty('--hne-copy-bg', activeConfig.backgroundColor);
    root.style.setProperty('--hne-copy-border', activeConfig.borderColor);
    root.style.setProperty('--hne-copy-copied', activeConfig.copiedColor);
    document.body.classList.toggle('hne-preview-copy-disabled', !activeConfig.enabled);
    document.body.classList.toggle('hne-preview-copy-top-always', activeConfig.topAlwaysVisible);
  }

  function getLineCount(codeEl) {
    return (codeEl.textContent || '').trim().split(/\r?\n/).length;
  }

  function isSingleLineCode(codeEl) {
    return getLineCount(codeEl) <= 1;
  }

  function buttonSelector(position) {
    return 'button[data-hne-copy="' + position + '"]';
  }

  function removeAllCopyButtons(preElement) {
    preElement.querySelectorAll('button.' + BUTTON_BASE_CLASS).forEach((btn) => btn.remove());
    preElement.classList.remove(
      WRAPPER_CLASS,
      'hne-single-line',
      'hne-show-bottom-copy',
      'hne-show-top-copy'
    );
    delete preElement.dataset.hneBottomCopyHoverBound;
  }

  function removeLegacyButtons(preElement) {
    preElement.querySelectorAll('button.' + BUTTON_BASE_CLASS).forEach((btn) => {
      const position = btn.getAttribute('data-hne-copy');
      if (position !== 'top' && position !== 'bottom') {
        btn.remove();
      }
    });
  }

  function setButtonsCopied(preElement, copied) {
    preElement.querySelectorAll('button.' + BUTTON_BASE_CLASS).forEach((btn) => {
      if (copied) {
        btn.innerHTML = CHECK_ICON;
        btn.setAttribute('title', 'Copied!');
        btn.classList.add('hne-copied');
      } else {
        btn.innerHTML = CLIPBOARD_ICON;
        btn.setAttribute('title', 'Copy');
        btn.classList.remove('hne-copied');
      }
    });
  }

  function attachCopyButton(preElement, code, position) {
    if (preElement.querySelector(buttonSelector(position))) {
      return;
    }

    const button = document.createElement('button');
    button.type = 'button';
    button.className = BUTTON_BASE_CLASS + ' ' + BUTTON_BASE_CLASS + '-' + position;
    button.setAttribute('data-hne-copy', position);
    button.innerHTML = CLIPBOARD_ICON;
    button.setAttribute('title', 'Copy');
    button.setAttribute('aria-label', 'Copy code to clipboard');

    button.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();

      try {
        await navigator.clipboard.writeText(code.textContent || '');
        setButtonsCopied(preElement, true);
        setTimeout(() => {
          setButtonsCopied(preElement, false);
        }, 2000);
      } catch {
        preElement.querySelectorAll('button.' + BUTTON_BASE_CLASS).forEach((btn) => {
          btn.setAttribute('title', 'Failed to copy');
        });
        setTimeout(() => {
          preElement.querySelectorAll('button.' + BUTTON_BASE_CLASS).forEach((btn) => {
            btn.setAttribute('title', 'Copy');
          });
        }, 2000);
      }
    });

    preElement.appendChild(button);
  }

  function updateCopyHoverVisibility(preElement, e) {
    const rect = preElement.getBoundingClientRect();
    const fromBottom = rect.bottom - e.clientY;
    const zone = activeConfig.bottomHoverZonePx;

    if (activeConfig.showBottom && !preElement.classList.contains('hne-single-line')) {
      if (fromBottom <= zone) {
        preElement.classList.add('hne-show-bottom-copy');
      } else {
        preElement.classList.remove('hne-show-bottom-copy');
      }
    }

    if (activeConfig.showTop && !activeConfig.topAlwaysVisible) {
      if (fromBottom > zone) {
        preElement.classList.add('hne-show-top-copy');
      } else {
        preElement.classList.remove('hne-show-top-copy');
      }
    }
  }

  function setupCopyHover(preElement) {
    if (preElement.dataset.hneCopyHoverBound === '1') {
      return;
    }
    preElement.dataset.hneCopyHoverBound = '1';

    preElement.addEventListener('mousemove', (e) => {
      updateCopyHoverVisibility(preElement, e);
    });

    preElement.addEventListener('mouseleave', () => {
      preElement.classList.remove('hne-show-bottom-copy', 'hne-show-top-copy');
    });
  }

  function addCopyButton(preElement) {
    const code = preElement.querySelector('code');
    if (!code) {
      return;
    }

    if (!activeConfig.enabled) {
      removeAllCopyButtons(preElement);
      return;
    }

    removeLegacyButtons(preElement);
    preElement.classList.add(WRAPPER_CLASS);

    const singleLine = isSingleLineCode(code);
    const needsHover =
      (activeConfig.showBottom && !singleLine) ||
      (activeConfig.showTop && !activeConfig.topAlwaysVisible);

    if (activeConfig.showTop) {
      attachCopyButton(preElement, code, 'top');
    } else {
      preElement.querySelector(buttonSelector('top'))?.remove();
    }

    if (activeConfig.showBottom && !singleLine) {
      preElement.classList.remove('hne-single-line');
      attachCopyButton(preElement, code, 'bottom');
    } else {
      preElement.classList.toggle('hne-single-line', singleLine);
      preElement.classList.remove('hne-show-bottom-copy');
      preElement.querySelector(buttonSelector('bottom'))?.remove();
    }

    if (singleLine) {
      preElement.classList.add('hne-single-line');
    }

    if (needsHover) {
      setupCopyHover(preElement);
    } else {
      delete preElement.dataset.hneCopyHoverBound;
      preElement.classList.remove('hne-show-bottom-copy', 'hne-show-top-copy');
    }
  }

  function processAllCodeBlocks() {
    applyConfig();
    document.querySelectorAll('pre').forEach((pre) => {
      if (pre.querySelector('code')) {
        addCopyButton(pre);
      }
    });
  }

  function initOnce() {
    if (window.__hneMarkdownCopyInit) {
      return;
    }
    window.__hneMarkdownCopyInit = true;

    const observer = new MutationObserver((mutations) => {
      let shouldProcess = false;
      for (const mutation of mutations) {
        if (mutation.type === 'characterData') {
          shouldProcess = true;
          break;
        }
        if (
          mutation.type === 'childList' &&
          (mutation.addedNodes.length > 0 || mutation.removedNodes.length > 0)
        ) {
          shouldProcess = true;
          break;
        }
      }
      if (shouldProcess) {
        processAllCodeBlocks();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    window.addEventListener('vscode.markdown.updateContent', () => {
      processAllCodeBlocks();
    });
  }

  initOnce();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', processAllCodeBlocks);
  } else {
    processAllCodeBlocks();
  }
})();
