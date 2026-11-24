package dev.harrix.hsk.dropboxsync

/** Sync mode for a folder pair. */
enum class SyncMode {
    TwoWay,
    DownloadMirror,
}

/** How TwoWay resolves content conflicts. */
enum class ConflictPolicy {
    KeepBoth,
    NewerWins,
    PreferRemote,
    PreferLocal,
}

/** Local storage backend for a folder pair. */
enum class StorageType {
    Direct,
    Saf,
}

/** What triggered a sync run. */
enum class SyncTrigger {
    Manual,
    Widget,
    Scheduled,
}

/** High-level outcome of a sync run. */
enum class SyncRunStatus {
    Success,
    NeedsConfirmation,
    Cancelled,
    Error,
}

/** One local or remote file/folder entry used by the planner. */
data class SyncTreeEntry(
    val relativePath: String,
    val pathLower: String,
    val isDir: Boolean,
    val size: Long = 0L,
    val mtimeMs: Long = 0L,
    val contentHash: String? = null,
    val remoteId: String? = null,
    val remoteRev: String? = null,
    val remoteServerModifiedMs: Long = 0L,
)

/** Persisted baseline row for a relative path. */
data class SyncBaselineEntry(
    val relativePath: String,
    val pathLower: String,
    val isDir: Boolean,
    val localSize: Long = 0L,
    val localMtimeMs: Long = 0L,
    val contentHash: String? = null,
    val remoteId: String? = null,
    val remoteRev: String? = null,
    val remoteServerModifiedMs: Long = 0L,
)

/** Folder pair configuration. */
data class FolderPair(
    val id: Long = 0L,
    val name: String,
    val localPathOrUri: String,
    val storageType: StorageType,
    val remotePath: String,
    val mode: SyncMode = SyncMode.TwoWay,
    val conflictPolicy: ConflictPolicy = ConflictPolicy.KeepBoth,
    val confirmLocalChanges: Boolean = true,
    val useGlobalIgnores: Boolean = true,
    val customIgnores: String = "",
    val ignoreHidden: Boolean = false,
    val enabled: Boolean = true,
    val remoteCursor: String? = null,
    val lastSyncAtMs: Long? = null,
    val lastStatus: SyncRunStatus? = null,
    val lastSummary: String? = null,
)

/** One planned sync action. */
sealed class SyncAction {
    abstract val relativePath: String
    abstract val pathLower: String
    abstract val needsConfirmation: Boolean

    data class Skip(
        override val relativePath: String,
        override val pathLower: String,
        val reason: String = "unchanged",
    ) : SyncAction() {
        override val needsConfirmation: Boolean = false
    }

    data class RecordBaselineOnly(
        override val relativePath: String,
        override val pathLower: String,
        val local: SyncTreeEntry?,
        val remote: SyncTreeEntry?,
        val contentHash: String?,
    ) : SyncAction() {
        override val needsConfirmation: Boolean = false
    }

    data class Upload(
        override val relativePath: String,
        override val pathLower: String,
        val local: SyncTreeEntry,
        val overwrite: Boolean,
    ) : SyncAction() {
        override val needsConfirmation: Boolean = false
    }

    data class Download(
        override val relativePath: String,
        override val pathLower: String,
        val remote: SyncTreeEntry,
        val overwrite: Boolean,
        override val needsConfirmation: Boolean = false,
    ) : SyncAction()

    data class DeleteLocal(
        override val relativePath: String,
        override val pathLower: String,
        val local: SyncTreeEntry,
        override val needsConfirmation: Boolean = false,
    ) : SyncAction()

    data class DeleteRemote(
        override val relativePath: String,
        override val pathLower: String,
        val remote: SyncTreeEntry,
    ) : SyncAction() {
        override val needsConfirmation: Boolean = false
    }

    data class MkdirLocal(
        override val relativePath: String,
        override val pathLower: String,
    ) : SyncAction() {
        override val needsConfirmation: Boolean = false
    }

    data class MkdirRemote(
        override val relativePath: String,
        override val pathLower: String,
    ) : SyncAction() {
        override val needsConfirmation: Boolean = false
    }

    data class ResolveConflict(
        override val relativePath: String,
        override val pathLower: String,
        val local: SyncTreeEntry,
        val remote: SyncTreeEntry,
        val policy: ConflictPolicy,
    ) : SyncAction() {
        override val needsConfirmation: Boolean = false
    }
}

/** Planner output for one folder pair. */
data class SyncPlan(
    val safeActions: List<SyncAction>,
    val confirmationActions: List<SyncAction>,
    val skippedIdentical: Int,
) {
    val allActions: List<SyncAction>
        get() = safeActions + confirmationActions

    val downloadCount: Int
        get() = allActions.count { it is SyncAction.Download }

    val uploadCount: Int
        get() = allActions.count { it is SyncAction.Upload }

    val deleteLocalCount: Int
        get() = allActions.count { it is SyncAction.DeleteLocal }

    val deleteRemoteCount: Int
        get() = allActions.count { it is SyncAction.DeleteRemote }

    val conflictCount: Int
        get() = allActions.count { it is SyncAction.ResolveConflict }
}

/** Live progress published during a sync. */
data class SyncProgress(
    val pairId: Long,
    val pairName: String,
    val phase: SyncPhase,
    val currentPath: String? = null,
    val processedBytes: Long = 0L,
    val totalBytes: Long = 0L,
    val processedFiles: Int = 0,
    val totalFiles: Int = 0,
    val skippedIdentical: Int = 0,
    val downloaded: Int = 0,
    val uploaded: Int = 0,
    val deletedLocal: Int = 0,
    val deletedRemote: Int = 0,
    val message: String? = null,
)

enum class SyncPhase {
    Listing,
    Comparing,
    Transferring,
    WaitingConfirmation,
    Finishing,
}

/** Result of executing a sync plan. */
data class SyncResult(
    val pairId: Long,
    val status: SyncRunStatus,
    val downloaded: Int = 0,
    val uploaded: Int = 0,
    val deletedLocal: Int = 0,
    val deletedRemote: Int = 0,
    val skippedIdentical: Int = 0,
    val skippedByUser: Int = 0,
    val conflicts: Int = 0,
    val pendingConfirmation: List<SyncAction> = emptyList(),
    val errorMessage: String? = null,
    val summary: String = "",
)

/** Dropbox account summary for UI. */
data class DropboxAccount(
    val accountId: String,
    val displayName: String,
    val email: String,
)

/** One remote folder listing entry for the Dropbox picker. */
data class DropboxRemoteItem(
    val name: String,
    val pathDisplay: String,
    val pathLower: String,
    val isDir: Boolean,
)

internal fun normalizePathLower(path: String): String {
    val trimmed = path.trim().trimStart('/').replace('\\', '/')
    return java.text.Normalizer
        .normalize(trimmed, java.text.Normalizer.Form.NFC)
        .lowercase()
}

internal fun normalizeRelativePath(path: String): String = path.trim().trimStart('/').replace('\\', '/')
