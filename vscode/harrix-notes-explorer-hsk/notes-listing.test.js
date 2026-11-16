'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');
const { collectNotesDirChildSpecs } = require('./notes-listing');

/**
 * @param {string} root
 * @param {string} relativePath
 * @param {string} [contents]
 */
function writeFile(root, relativePath, contents = '') {
  const full = path.join(root, relativePath);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  fs.writeFileSync(full, contents, 'utf8');
}

test('Notes-Diaries lists categories, not Dreams year notes', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'hsk-notes-listing-'));
  try {
    writeFile(root, path.join('Notes-Diaries', '_Notes-Diaries.g.md'), '# Notes-Diaries\n');
    writeFile(root, path.join('Notes-Diaries', 'Congratulations', 'Congratulations.md'), '# Congratulations\n');
    writeFile(root, path.join('Notes-Diaries', 'Diary', '_Diary.g.md'), '# Diary\n');
    writeFile(root, path.join('Notes-Diaries', 'Diary', '2026', '2026.md'), '# 2026\n');
    writeFile(root, path.join('Notes-Diaries', 'Dreams', '_Dreams.g.md'), '# Dreams\n');
    writeFile(root, path.join('Notes-Diaries', 'Dreams', '2026', '2026.md'), '# 2026\nСон э\n');
    writeFile(root, path.join('Notes-Diaries', 'Dreams', '2025', '2025.md'), '# 2025\n');
    writeFile(root, path.join('Notes-Diaries', 'Memories', '_Memories.g.md'), '# Memories\n');
    writeFile(root, path.join('Notes-Diaries', 'Memories', '2026', '2026.md'), '# 2026\n');
    writeFile(root, path.join('Notes-Diaries', 'Text', '_Text.g.md'), '# Text\n');
    writeFile(root, path.join('Notes-Diaries', 'Text', '2026', '2026.md'), '# 2026\n');

    const diaries = path.join(root, 'Notes-Diaries');
    const specs = collectNotesDirChildSpecs(diaries);
    const byName = Object.fromEntries(specs.map((s) => [s.name, s]));

    assert.deepEqual(
      specs.map((s) => s.name).sort(),
      ['Congratulations', 'Diary', 'Dreams', 'Memories', 'Text'],
    );
    assert.equal(byName.Congratulations.kind, 'note');
    assert.equal(byName.Diary.kind, 'folder');
    assert.equal(byName.Dreams.kind, 'folder');
    assert.equal(byName.Memories.kind, 'folder');
    assert.equal(byName.Text.kind, 'folder');
    assert.ok(!specs.some((s) => /^\d{4}$/.test(s.name)));

    const dreamSpecs = collectNotesDirChildSpecs(byName.Dreams.path);
    assert.deepEqual(dreamSpecs.map((s) => s.name).sort(), ['2025', '2026']);
    assert.ok(dreamSpecs.every((s) => s.kind === 'note'));
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('year folder with Year.md collapses to a note under Dreams', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'hsk-notes-year-'));
  try {
    writeFile(root, path.join('Dreams', '2026', '2026.md'), '# 2026\n');
    const specs = collectNotesDirChildSpecs(path.join(root, 'Dreams'));
    assert.equal(specs.length, 1);
    assert.equal(specs[0].kind, 'note');
    assert.equal(specs[0].name, '2026');
    assert.equal(path.basename(specs[0].path), '2026.md');
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
