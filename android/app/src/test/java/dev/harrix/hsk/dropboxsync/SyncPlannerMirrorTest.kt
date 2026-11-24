package dev.harrix.hsk.dropboxsync

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class SyncPlannerMirrorTest {
    private val hash = "abc123"

    private fun entry(
        path: String,
        size: Long = 10,
        mtime: Long = 1000,
        contentHash: String? = hash,
        rev: String? = "rev1",
    ) = SyncTreeEntry(
        relativePath = path,
        pathLower = normalizePathLower(path),
        isDir = false,
        size = size,
        mtimeMs = mtime,
        contentHash = contentHash,
        remoteRev = rev,
        remoteServerModifiedMs = mtime,
    )

    private fun baseline(
        path: String,
        size: Long = 10,
        mtime: Long = 1000,
        rev: String = "rev1",
    ) = SyncBaselineEntry(
        relativePath = path,
        pathLower = normalizePathLower(path),
        isDir = false,
        localSize = size,
        localMtimeMs = mtime,
        contentHash = hash,
        remoteRev = rev,
        remoteServerModifiedMs = mtime,
    )

    @Test
    fun identicalFilesSkipDownloadOnFirstMirror() {
        val planner = SyncPlanner { hash }
        val plan =
            planner.plan(
                mode = SyncMode.DownloadMirror,
                conflictPolicy = ConflictPolicy.KeepBoth,
                confirmLocalChanges = true,
                localEntries = listOf(entry("Books/a.epub", contentHash = null)),
                remoteEntries = listOf(entry("Books/a.epub")),
                baselineEntries = emptyMap(),
            )
        assertEquals(0, plan.downloadCount)
        assertEquals(1, plan.skippedIdentical)
    }

    @Test
    fun locallyChangedFileNeedsConfirmationWhenEnabled() {
        val planner = SyncPlanner { "local-hash" }
        val plan =
            planner.plan(
                mode = SyncMode.DownloadMirror,
                conflictPolicy = ConflictPolicy.KeepBoth,
                confirmLocalChanges = true,
                localEntries = listOf(entry("note.txt", size = 11, mtime = 5000, contentHash = null)),
                remoteEntries = listOf(entry("note.txt", size = 10, mtime = 1000, contentHash = hash)),
                baselineEntries = mapOf(normalizePathLower("note.txt") to baseline("note.txt")),
            )
        assertEquals(1, plan.confirmationActions.size)
        assertTrue(plan.confirmationActions.first() is SyncAction.Download)
        assertEquals(0, plan.safeActions.count { it is SyncAction.Download })
    }

    @Test
    fun locallyChangedFileAutoOverwritesWhenConfirmationDisabled() {
        val planner = SyncPlanner { "local-hash" }
        val plan =
            planner.plan(
                mode = SyncMode.DownloadMirror,
                conflictPolicy = ConflictPolicy.KeepBoth,
                confirmLocalChanges = false,
                localEntries = listOf(entry("note.txt", size = 11, mtime = 5000, contentHash = null)),
                remoteEntries = listOf(entry("note.txt", size = 10, mtime = 1000, contentHash = hash)),
                baselineEntries = mapOf(normalizePathLower("note.txt") to baseline("note.txt")),
            )
        assertEquals(0, plan.confirmationActions.size)
        assertEquals(1, plan.downloadCount)
    }

    @Test
    fun localOnlyFileNeedsDeleteConfirmation() {
        val planner = SyncPlanner { hash }
        val plan =
            planner.plan(
                mode = SyncMode.DownloadMirror,
                conflictPolicy = ConflictPolicy.KeepBoth,
                confirmLocalChanges = true,
                localEntries = listOf(entry("extra.txt")),
                remoteEntries = emptyList(),
                baselineEntries = emptyMap(),
            )
        assertEquals(1, plan.confirmationActions.size)
        assertTrue(plan.confirmationActions.first() is SyncAction.DeleteLocal)
    }
}
