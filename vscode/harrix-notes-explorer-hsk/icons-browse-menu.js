/**
 * Context menu for Icons Browse — mirrors `view/item/context` in package.json
 * for folders and notes (not asset rows).
 */

const CMD = {
  openIconsBrowse: 'harrixNotesExplorerHsk.openIconsBrowse',
  openNoteInEditor: 'harrixNotesExplorerHsk.openNoteInEditor',
  openNoteInPreview: 'harrixNotesExplorerHsk.openNoteInPreview',
  createNote: 'harrixNotesExplorerHsk.createNote',
  createFolder: 'harrixNotesExplorerHsk.createFolder',
  addFolderInNote: 'harrixNotesExplorerHsk.addFolderInNote',
  addFileInNote: 'harrixNotesExplorerHsk.addFileInNote',
  newDiaryNote: 'harrixNotesExplorerHsk.newDiaryNote',
  newDreamNote: 'harrixNotesExplorerHsk.newDreamNote',
  newCasesNote: 'harrixNotesExplorerHsk.newCasesNote',
  addFromTemplate: 'harrixNotesExplorerHsk.addFromTemplate',
  showNoteAssets: 'harrixNotesExplorerHsk.showNoteAssets',
  hideNoteAssets: 'harrixNotesExplorerHsk.hideNoteAssets',
  reloadNoteAssets: 'harrixNotesExplorerHsk.reloadNoteAssets',
  hideAllNoteAssets: 'harrixNotesExplorerHsk.hideAllNoteAssets',
  openMergedNote: 'harrixNotesExplorerHsk.openMergedNote',
  copyPath: 'harrixNotesExplorerHsk.copyPath',
  copyFilename: 'harrixNotesExplorerHsk.copyFilename',
  openInTerminal: 'harrixNotesExplorerHsk.openInTerminal',
  findInFolder: 'harrixNotesExplorerHsk.findInFolder',
  cut: 'harrixNotesExplorerHsk.cut',
  copy: 'harrixNotesExplorerHsk.copy',
  paste: 'harrixNotesExplorerHsk.paste',
  checkMarkdownInFolder: 'harrixNotesExplorerHsk.checkMarkdownInFolder',
  beautifyRegenerateGMd: 'harrixNotesExplorerHsk.beautifyRegenerateGMd',
  optimizeImagesFolder: 'harrixNotesExplorerHsk.optimizeImagesFolder',
  discardGitChangesInFolder: 'harrixNotesExplorerHsk.discardGitChangesInFolder',
  discardGitChangesInNote: 'harrixNotesExplorerHsk.discardGitChangesInNote',
  renameItem: 'harrixNotesExplorerHsk.renameItem',
  deleteItem: 'harrixNotesExplorerHsk.deleteItem',
  revealInOS: 'harrixNotesExplorerHsk.revealInOS',
};

/**
 * @param {string} contextValue
 * @returns {{ base: string, isGit: boolean }}
 */
function parseContextValue(contextValue) {
  const cv = String(contextValue || '');
  if (cv.startsWith('git') && cv.length > 3) {
    return {
      isGit: true,
      base: cv.charAt(3).toLowerCase() + cv.slice(4),
    };
  }
  return { isGit: false, base: cv };
}

/**
 * @param {string} command
 * @param {string} title
 * @returns {{ type: 'item', command: string, title: string }}
 */
function item(command, title) {
  return { type: 'item', command, title };
}

/** @returns {{ type: 'separator' }} */
function sep() {
  return { type: 'separator' };
}

/**
 * @param {string} contextValue
 * @param {{
 *   canPaste?: boolean,
 *   openNotesInPreview?: boolean,
 *   isWorkspaceRoot?: boolean,
 *   background?: boolean,
 * }} [opts]
 * @returns {Array<{ type: 'item', command: string, title: string } | { type: 'separator' }>}
 */
function buildIconsBrowseContextMenu(contextValue, opts) {
  const { base, isGit } = parseContextValue(contextValue);
  const canPaste = opts?.canPaste === true;
  const openNotesInPreview = opts?.openNotesInPreview !== false;
  const isWorkspaceRoot = opts?.isWorkspaceRoot === true;
  /** @type {Array<{ type: 'item', command: string, title: string } | { type: 'separator' }>} */
  const out = [];

  const pushCommonNav = () => {
    out.push(item(CMD.copyPath, 'Copy Path'));
    out.push(item(CMD.copyFilename, 'Copy Filename'));
    out.push(sep());
    out.push(item(CMD.openInTerminal, 'Open in Integrated Terminal'));
    out.push(item(CMD.findInFolder, 'Find in Folder...'));
  };

  const pushPaste = () => {
    if (canPaste) {
      out.push(sep());
      out.push(item(CMD.paste, 'Paste'));
    }
  };

  const pushCutCopyPaste = () => {
    if (isWorkspaceRoot) {
      pushPaste();
      return;
    }
    out.push(sep());
    out.push(item(CMD.cut, 'Cut'));
    out.push(item(CMD.copy, 'Copy'));
    if (canPaste) {
      out.push(item(CMD.paste, 'Paste'));
    }
  };

  const pushEdit = () => {
    out.push(sep());
    out.push(item(CMD.renameItem, 'Rename…'));
    out.push(item(CMD.deleteItem, 'Delete'));
    out.push(sep());
    out.push(item(CMD.revealInOS, 'Reveal in File Explorer'));
  };

  const pushFolderCli = () => {
    out.push(sep());
    out.push(item(CMD.checkMarkdownInFolder, 'Check Markdown in Folder ꟲᴸᴵ'));
    out.push(item(CMD.beautifyRegenerateGMd, 'Beautify Markdown and Regenerate .g.md in Folder ꟲᴸᴵ'));
    out.push(item(CMD.optimizeImagesFolder, 'Optimize Images in Folder ꟲᴸᴵ'));
    if (isGit) {
      out.push(item(CMD.discardGitChangesInFolder, 'Discard Git Changes in Folder…'));
    }
  };

  if (opts?.background === true) {
    out.push(item(CMD.createNote, 'New Note…'));
    out.push(item(CMD.createFolder, 'New Folder…'));
    if (base.includes('Diary')) {
      out.push(item(CMD.newDiaryNote, 'New Diary Note ꟲᴸᴵ'));
    }
    if (base.includes('Dreams')) {
      out.push(item(CMD.newDreamNote, 'New Dream Note ꟲᴸᴵ'));
    }
    if (base.includes('Cases')) {
      out.push(item(CMD.newCasesNote, 'New Cases Note ꟲᴸᴵ'));
    }
    if (base.includes('TemplateTarget')) {
      out.push(item(CMD.addFromTemplate, 'Add from Template… ꟲᴸᴵ'));
    }
    pushPaste();
    out.push(sep());
    pushCommonNav();
    out.push(sep());
    out.push(item(CMD.revealInOS, 'Reveal in File Explorer'));
    return out;
  }

  if (base.startsWith('notesFolder')) {
    out.push(item(CMD.openIconsBrowse, 'Open Notes Icons Browse'));
    out.push(sep());
    out.push(item(CMD.createNote, 'New Note…'));
    out.push(item(CMD.createFolder, 'New Folder…'));
    if (base.includes('Diary')) {
      out.push(item(CMD.newDiaryNote, 'New Diary Note ꟲᴸᴵ'));
    }
    if (base.includes('Dreams')) {
      out.push(item(CMD.newDreamNote, 'New Dream Note ꟲᴸᴵ'));
    }
    if (base.includes('Cases')) {
      out.push(item(CMD.newCasesNote, 'New Cases Note ꟲᴸᴵ'));
    }
    if (base.includes('TemplateTarget')) {
      out.push(item(CMD.addFromTemplate, 'Add from Template… ꟲᴸᴵ'));
    }
    if (base.includes('WithMerged')) {
      out.push(sep());
      out.push(item(CMD.openMergedNote, 'Show Merged Note'));
    }
    pushFolderCli();
    out.push(sep());
    pushCommonNav();
    pushCutCopyPaste();
    pushEdit();
    return out;
  }

  if (base.startsWith('note')) {
    if (openNotesInPreview) {
      out.push(item(CMD.openNoteInEditor, 'Open in Editor'));
    } else {
      out.push(item(CMD.openNoteInPreview, 'Open in Preview'));
    }
    out.push(sep());
    out.push(item(CMD.createNote, 'New Note…'));
    out.push(item(CMD.addFolderInNote, 'Add Folder in Note…'));
    out.push(item(CMD.addFileInNote, 'Add File in Note…'));

    if (base.includes('HasAttachments')) {
      out.push(sep());
      out.push(item(CMD.showNoteAssets, 'Show Attachments'));
    }
    if (base.includes('WithAssets')) {
      out.push(sep());
      out.push(item(CMD.hideNoteAssets, 'Hide Attachments'));
      out.push(item(CMD.reloadNoteAssets, 'Reload Attachments'));
      out.push(item(CMD.hideAllNoteAssets, 'Hide All Attachments'));
    }

    if (base.includes('NamedFolder')) {
      pushFolderCli();
    }
    if (isGit) {
      out.push(sep());
      out.push(item(CMD.discardGitChangesInNote, 'Discard Git Changes in Note…'));
    }

    out.push(sep());
    pushCommonNav();
    pushCutCopyPaste();
    pushEdit();
    return out;
  }

  // Fallback: basic actions
  pushCommonNav();
  pushCutCopyPaste();
  pushEdit();
  return out;
}

module.exports = {
  buildIconsBrowseContextMenu,
  parseContextValue,
  CMD,
};
