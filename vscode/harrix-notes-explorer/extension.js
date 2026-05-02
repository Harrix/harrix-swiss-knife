const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

/**
 * @param {string} baseDir
 * @param {string} rawName
 * @param {boolean} withImages
 */
function runHarrixMarkdownNewNote(baseDir, rawName, withImages) {
  const stem = rawName.trim();
  if (!stem) {
    return Promise.reject(new Error('Empty note name'));
  }
  const nameArg = stem.toLowerCase().endsWith('.md') ? stem.slice(0, -3) : stem;

  const subcommand = withImages ? 'new-note-with-images' : 'new-note';
  const args = ['markdown', subcommand, '--folder', baseDir, '--name', nameArg];

  return new Promise((resolve, reject) => {
    const child = spawn('harrix-swiss-knife-cli', args, {
      shell: process.platform === 'win32',
      windowsHide: true
    });
    let stderr = '';
    let stdout = '';
    child.stderr?.on('data', (d) => { stderr += d.toString(); });
    child.stdout?.on('data', (d) => { stdout += d.toString(); });
    child.on('error', (err) => reject(err));
    child.on('close', (code) => {
      if (code === 0) {
        resolve({ stdout, stderr });
      } else {
        const msg = (stderr || stdout || '').trim() || `harrix-swiss-knife-cli exited with code ${code}`;
        reject(new Error(msg));
      }
    });
  });
}

// --- Helper functions ---

function safeReaddir(dir) {
  try { return fs.readdirSync(dir, { withFileTypes: true }); }
  catch (e) { return []; }
}

function isMd(name) { return name.toLowerCase().endsWith('.md'); }
function isGMd(name) { return name.toLowerCase().endsWith('.g.md'); }

/** Combined folder note: _<FolderName>.g.md next to sibling .md files */
function mergedNotePath(folderPath, folderName) {
  return path.join(folderPath, `_${folderName}.g.md`);
}

function hasMergedNoteFs(folderPath, folderName) {
  return pathExists(mergedNotePath(folderPath, folderName));
}

function uriToFsPath(uri) {
  return uri instanceof vscode.Uri ? uri.fsPath : undefined;
}

function pathExists(fsPath) {
  try { fs.accessSync(fsPath); return true; } catch { return false; }
}

function isDirectoryPath(fsPath) {
  try { return fs.statSync(fsPath).isDirectory(); } catch { return false; }
}

function isFilePath(fsPath) {
  try { return fs.statSync(fsPath).isFile(); } catch { return false; }
}

// Check whether a folder contains at least one .md file (recursively)
function hasMarkdownRecursive(dir) {
  for (const entry of safeReaddir(dir)) {
    if (entry.isFile() && isMd(entry.name)) return true;
    if (entry.isDirectory()) {
      if (hasMarkdownRecursive(path.join(dir, entry.name))) return true;
    }
  }
  return false;
}

// --- TreeDataProvider ---

class NotesProvider {
  constructor(rootPath) {
    this.rootPath = rootPath;
    this._emitter = new vscode.EventEmitter();
    this.onDidChangeTreeData = this._emitter.event;
  }

  refresh() { this._emitter.fire(); }

  getTreeItem(el) { return el; }

  getChildren(element) {
    const dir = element ? element.dirPath : this.rootPath;
    if (!dir || !fs.existsSync(dir)) return [];

    const entries = safeReaddir(dir);

    // Folders that contain at least one .md file (recursively)
    const folders = entries
      .filter(e => e.isDirectory())
      .filter(e => hasMarkdownRecursive(path.join(dir, e.name)));

    // .md files in the current folder (folder merge artifacts *.g.md are hidden here)
    const mdFiles = entries.filter(e => e.isFile() && isMd(e.name) && !isGMd(e.name));

    const items = [];

    // --- folders ---
    for (const folder of folders) {
      const folderPath = path.join(dir, folder.name);
      const sub = safeReaddir(folderPath);
      const subMd = sub.filter(e => e.isFile() && isMd(e.name) && !isGMd(e.name));
      const subFolders = sub
        .filter(e => e.isDirectory())
        .filter(e => hasMarkdownRecursive(path.join(folderPath, e.name)));

      const sameNameMdPath = path.join(folderPath, folder.name + '.md');
      const hasSameNameMd = fs.existsSync(sameNameMdPath);

      // Rule: folder + exactly one .md with the same name + no "visible" subfolders
      // => collapse into a single file
      if (hasSameNameMd && subMd.length === 1 && subFolders.length === 0) {
        items.push(this.createFileItem(sameNameMdPath, folder.name));
      } else {
        items.push(this.createFolderItem(folderPath, folder.name));
      }
    }

    // --- .md files ---
    for (const file of mdFiles) {
      const filePath = path.join(dir, file.name);
      const displayName = file.name.replace(/\.md$/i, '');
      items.push(this.createFileItem(filePath, displayName));
    }

    const labelToString = (label) => {
      if (!label) return '';
      if (typeof label === 'string') return label;
      if (typeof label === 'object' && typeof label.label === 'string') return label.label;
      return String(label);
    };

    return items.sort((a, b) =>
      labelToString(a.label).localeCompare(labelToString(b.label), undefined, { numeric: true, sensitivity: 'base' })
    );
  }

  createFolderItem(folderPath, name) {
    const item = new vscode.TreeItem(name, vscode.TreeItemCollapsibleState.Collapsed);
    item.resourceUri = vscode.Uri.file(folderPath);
    item.dirPath = folderPath;
    item.contextValue = hasMergedNoteFs(folderPath, name) ? 'notesFolderWithMerged' : 'notesFolder';
    item.iconPath = vscode.ThemeIcon.Folder;
    return item;
  }

  createFileItem(filePath, displayName) {
    const item = new vscode.TreeItem(displayName, vscode.TreeItemCollapsibleState.None);
    item.resourceUri = vscode.Uri.file(filePath);
    item.tooltip = filePath;
    item.command = {
      command: 'vscode.open',
      title: 'Open',
      arguments: [vscode.Uri.file(filePath)]
    };

    item.iconPath = new vscode.ThemeIcon('markdown');
    item.contextValue = 'note';
    return item;
  }
}

function activate(context) {
  const folders = vscode.workspace.workspaceFolders;
  if (!folders || folders.length === 0) return;
  const rootPath = folders[0].uri.fsPath;

  const provider = new NotesProvider(rootPath);
  const view = vscode.window.createTreeView('notesExplorer', {
    treeDataProvider: provider,
    showCollapseAll: true
  });
  context.subscriptions.push(view);

  context.subscriptions.push(
    vscode.commands.registerCommand('notesExplorer.refresh', () => provider.refresh())
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('notesExplorer.openMergedNote', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath || !isDirectoryPath(fsPath)) return;

      const folderName = path.basename(fsPath);
      const gPath = mergedNotePath(fsPath, folderName);
      if (!pathExists(gPath)) {
        vscode.window.showWarningMessage('No merged note for this folder (_' + folderName + '.g.md).');
        return;
      }
      await vscode.commands.executeCommand('vscode.open', vscode.Uri.file(gPath));
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('notesExplorer.revealInOS', async (uri) => {
      const targetUri =
        uri instanceof vscode.Uri
          ? uri
          : vscode.window.activeTextEditor?.document?.uri;

      if (!targetUri) return;

      await vscode.commands.executeCommand('revealFileInOS', targetUri);
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('notesExplorer.createNote', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);

      const baseDir =
        fsPath && isDirectoryPath(fsPath)
          ? fsPath
          : fsPath && isFilePath(fsPath)
            ? path.dirname(fsPath)
            : rootPath;

      const name = await vscode.window.showInputBox({
        title: 'Create Note',
        prompt: 'Enter note name (without extension)',
        placeHolder: 'My-note'
      });
      if (!name) return;

      const safeName = name.trim();
      if (!safeName) return;

      try {
        await runHarrixMarkdownNewNote(baseDir, safeName, false);
        provider.refresh();
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Create note failed: ${msg}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('notesExplorer.createNoteWithImages', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);

      const baseDir =
        fsPath && isDirectoryPath(fsPath)
          ? fsPath
          : rootPath;

      if (!baseDir || !isDirectoryPath(baseDir)) {
        vscode.window.showErrorMessage('Choose a folder in Notes.');
        return;
      }

      const name = await vscode.window.showInputBox({
        title: 'Create Note with Images',
        prompt: 'Enter note name (without extension)',
        placeHolder: 'My-note'
      });
      if (!name) return;

      const safeName = name.trim();
      if (!safeName) return;

      try {
        await runHarrixMarkdownNewNote(baseDir, safeName, true);
        provider.refresh();
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        vscode.window.showErrorMessage(`Create note with images failed: ${msg}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('notesExplorer.renameItem', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath) return;

      const isDir = isDirectoryPath(fsPath);
      const isFile = isFilePath(fsPath);
      if (!isDir && !isFile) return;

      const parentDir = path.dirname(fsPath);
      const oldBaseName = path.basename(fsPath);

      const fileExt = isFile
        ? (isGMd(oldBaseName) ? '.g.md' : '.md')
        : '';

      const defaultValue = isFile
        ? (isGMd(oldBaseName)
          ? oldBaseName.replace(/\.g\.md$/i, '')
          : oldBaseName.replace(/\.md$/i, ''))
        : oldBaseName;

      const newName = await vscode.window.showInputBox({
        title: 'Rename',
        prompt: isDir ? 'Enter new folder name' : 'Enter new note name (without extension)',
        value: defaultValue
      });
      if (!newName) return;

      const safeNew = newName.trim();
      if (!safeNew) return;

      const newBaseName = isFile
        ? (safeNew.toLowerCase().endsWith('.md') ? safeNew : `${safeNew}${fileExt}`)
        : safeNew;

      const newPath = path.join(parentDir, newBaseName);

      if (newPath === fsPath) return;
      if (pathExists(newPath)) {
        vscode.window.showErrorMessage('Target name already exists.');
        return;
      }

      await vscode.workspace.fs.rename(vscode.Uri.file(fsPath), vscode.Uri.file(newPath), { overwrite: false });
      provider.refresh();

      if (isFile) {
        await vscode.commands.executeCommand('vscode.open', vscode.Uri.file(newPath));
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('notesExplorer.deleteItem', async (treeItemOrUri) => {
      const itemUri = treeItemOrUri?.resourceUri ?? treeItemOrUri;
      const fsPath = uriToFsPath(itemUri);
      if (!fsPath) return;

      const isDir = isDirectoryPath(fsPath);
      const isFile = isFilePath(fsPath);
      if (!isDir && !isFile) return;

      const choice = await vscode.window.showWarningMessage(
        `Delete ${isDir ? 'folder' : 'note'} "${path.basename(fsPath)}"?`,
        { modal: true },
        'Delete'
      );
      if (choice !== 'Delete') return;

      await vscode.workspace.fs.delete(vscode.Uri.file(fsPath), { recursive: isDir, useTrash: true });
      provider.refresh();
    })
  );

  // Auto-refresh when .md files change
  const watcher = vscode.workspace.createFileSystemWatcher('**/*.md');
  watcher.onDidCreate(() => provider.refresh());
  watcher.onDidDelete(() => provider.refresh());
  watcher.onDidChange(() => provider.refresh());
  context.subscriptions.push(watcher);
}

function deactivate() { }

module.exports = { activate, deactivate };

