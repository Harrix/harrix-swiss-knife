package dev.harrix.hsk.dropboxsync

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class SyncIgnoreMatcherTest {
    @Test
    fun defaultPatternsIgnoreGitAndVenv() {
        val matcher = SyncIgnoreMatcher(SyncIgnoreMatcher.DefaultPatterns)
        assertTrue(matcher.ignores(".git/config"))
        assertTrue(matcher.ignores("project/.venv/lib/python.py"))
        assertTrue(matcher.ignores("node_modules/leftpad/index.js"))
        assertTrue(matcher.ignores("notes.tmp"))
        assertFalse(matcher.ignores(".obsidian/workspace.json"))
        assertFalse(matcher.ignores("Books/novel.epub"))
    }

    @Test
    fun ignoreHiddenToggleCoversDotFolders() {
        val matcher = SyncIgnoreMatcher(emptyList(), ignoreHidden = true)
        assertTrue(matcher.ignores(".obsidian/app.json"))
        assertFalse(matcher.ignores("docs/readme.md"))
    }

    @Test
    fun customGlobsWork() {
        val matcher = SyncIgnoreMatcher(listOf("*.iso", "cache"))
        assertTrue(matcher.ignores("images/big.iso"))
        assertTrue(matcher.ignores("app/cache/file.bin"))
        assertFalse(matcher.ignores("images/big.jpg"))
    }
}
