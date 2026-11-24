package dev.harrix.hsk.dropboxsync

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class SyncPlannerTwoWayTest {
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
    fun identicalPreseededFilesAreRecordedWithoutTransfer() {
        val planner = SyncPlanner { hash }
        val local = listOf(entry("Books/a.epub", contentHash = null))
        val remote = listOf(entry("Books/a.epub"))
        val plan =
            planner.plan(
                mode = SyncMode.TwoWay,
                conflictPolicy = ConflictPolicy.KeepBoth,
                confirmLocalChanges = true,
                localEntries = local,
                remoteEntries = remote,
                baselineEntries = emptyMap(),
            )
        assertEquals(0, plan.downloadCount)
        assertEquals(0, plan.uploadCount)
        assertEquals(1, plan.skippedIdentical)
        assertTrue(plan.safeActions.first() is SyncAction.RecordBaselineOnly)
    }

    @Test
    fun localOnlyNewFileUploads() {
        val planner = SyncPlanner { hash }
        val plan =
            planner.plan(
                mode = SyncMode.TwoWay,
                conflictPolicy = ConflictPolicy.KeepBoth,
                confirmLocalChanges = true,
                localEntries = listOf(entry("new.txt")),
                remoteEntries = emptyList(),
                baselineEntries = emptyMap(),
            )
        assertEquals(1, plan.uploadCount)
    }

    @Test
    fun remoteDeleteRemovesUnchangedLocal() {
        val planner = SyncPlanner { hash }
        val plan =
            planner.plan(
                mode = SyncMode.TwoWay,
                conflictPolicy = ConflictPolicy.KeepBoth,
                confirmLocalChanges = true,
                localEntries = listOf(entry("gone.txt")),
                remoteEntries = emptyList(),
                baselineEntries = mapOf(normalizePathLower("gone.txt") to baseline("gone.txt")),
            )
        assertEquals(1, plan.deleteLocalCount)
    }
}
