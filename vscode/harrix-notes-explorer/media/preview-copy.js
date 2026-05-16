(function () {
  if (window.__hneMarkdownCopyInit) {
    return;
  }
  window.__hneMarkdownCopyInit = true;

  const BUTTON_BASE_CLASS = 'hne-copy-btn';
  const WRAPPER_CLASS = 'hne-code-wrapper';

  const CLIPBOARD_ICON =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';

  const CHECK_ICON =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>';

  function isMultiLineCode(codeEl) {
    const text = codeEl.textContent || '';
    return text.includes('\n');
  }

  function buttonSelector(position) {
    return '.' + BUTTON_BASE_CLASS + '-' + position;
  }

  function setButtonsCopied(preElement, copied) {
    preElement.querySelectorAll('.' + BUTTON_BASE_CLASS).forEach((btn) => {
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
    const selector = buttonSelector(position);
    let button = preElement.querySelector(selector);
    if (button) {
      return;
    }

    button = document.createElement('button');
    button.type = 'button';
    button.className = BUTTON_BASE_CLASS + ' ' + BUTTON_BASE_CLASS + '-' + position;
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
        preElement.querySelectorAll('.' + BUTTON_BASE_CLASS).forEach((btn) => {
          btn.setAttribute('title', 'Failed to copy');
        });
        setTimeout(() => {
          preElement.querySelectorAll('.' + BUTTON_BASE_CLASS).forEach((btn) => {
            btn.setAttribute('title', 'Copy');
          });
        }, 2000);
      }
    });

    preElement.appendChild(button);
  }

  function ensureButton(preElement, code, position) {
    attachCopyButton(preElement, code, position);
  }

  function addCopyButton(preElement) {
    const code = preElement.querySelector('code');
    if (!code) {
      return;
    }

    preElement.classList.add(WRAPPER_CLASS);
    ensureButton(preElement, code, 'top');

    if (isMultiLineCode(code)) {
      ensureButton(preElement, code, 'bottom');
    } else {
      preElement.querySelector(buttonSelector('bottom'))?.remove();
    }
  }

  function processAllCodeBlocks() {
    document.querySelectorAll('pre').forEach((pre) => {
      if (pre.querySelector('code')) {
        addCopyButton(pre);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', processAllCodeBlocks);
  } else {
    processAllCodeBlocks();
  }

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
})();
