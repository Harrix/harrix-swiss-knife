(function () {
  if (window.__hneMarkdownCopyInit) {
    return;
  }
  window.__hneMarkdownCopyInit = true;

  const BUTTON_CLASS = 'hne-copy-btn';
  const WRAPPER_CLASS = 'hne-code-wrapper';

  const CLIPBOARD_ICON =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';

  const CHECK_ICON =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>';

  function addCopyButton(preElement) {
    if (preElement.classList.contains(WRAPPER_CLASS)) {
      return;
    }
    if (preElement.querySelector('.' + BUTTON_CLASS)) {
      return;
    }
    preElement.classList.add(WRAPPER_CLASS);

    const button = document.createElement('button');
    button.type = 'button';
    button.className = BUTTON_CLASS;
    button.innerHTML = CLIPBOARD_ICON;
    button.setAttribute('title', 'Copy');
    button.setAttribute('aria-label', 'Copy code to clipboard');

    button.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();

      const code = preElement.querySelector('code');
      if (!code) {
        return;
      }

      try {
        await navigator.clipboard.writeText(code.textContent || '');
        button.innerHTML = CHECK_ICON;
        button.setAttribute('title', 'Copied!');
        button.classList.add('hne-copied');
        setTimeout(() => {
          button.innerHTML = CLIPBOARD_ICON;
          button.setAttribute('title', 'Copy');
          button.classList.remove('hne-copied');
        }, 2000);
      } catch {
        button.setAttribute('title', 'Failed to copy');
        setTimeout(() => {
          button.setAttribute('title', 'Copy');
        }, 2000);
      }
    });

    preElement.appendChild(button);
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
      if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
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
