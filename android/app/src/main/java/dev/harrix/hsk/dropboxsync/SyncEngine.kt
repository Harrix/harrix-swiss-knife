package dev.harrix.hsk.dropboxsync

import android.content.Context
import android.os.PowerManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean

/** Executes sync plans with resumable pre-seed baseline writes. */
class SyncEngine(
    context: Context,
    private val database: SyncStateDatabase = SyncStateDatabase(context),
    private val preferences: DropboxSyncPreferences = DropboxSyncPreferences(context),
    private val authManager: DropboxAuthManager = DropboxAuthManager(context, preferences),
    private val apiClient: DropboxApiClient = DropboxApiClient(authManager),
) {
    private val appContext = context.applicationContext
    private val pairMutexes = ConcurrentHashMap<Long, Mutex>()
    private val cancelFlags = ConcurrentHashMap<Long, AtomicBoolean>()
    private val pendingConfirmations = ConcurrentHashMap<Long, PendingConfirmation>()

    private val _progress = MutableStateFlow<SyncProgress?>(null)
    val progress: StateFlow<SyncProgress?> = _progress.asStateFlow()

    fun getPendingConfirmation(pairId: Long): PendingConfirmation? = pendingConfirmations[pairId]

    fun clearPendingConfirmation(pairId: Long) {
        pendingConfirmations.remove(pairId)
    }

    fun requestCancel(pairId: Long) {
        cancelFlags.getOrPut(pairId) { AtomicBoolean(false) }.set(true)
    }

    suspend fun syncPair(
        pairId: Long,
        trigger: SyncTrigger,
        dryRun: Boolean = false,
        confirmedPathLowers: Set<String>? = null,
    ): SyncResult = withContext(Dispatchers.IO) {
        val mutex = pairMutexes.getOrPut(pairId) { Mutex() }
        mutex.withLock {
            val pair =
                database.getPair(pairId)
                    ?: return@withLock SyncResult(
                        pairId = pairId,
                        status = SyncRunStatus.Error,
                        errorMessage = "Folder pair not found",
                        summary = "Missing pair",
                    )
            runPair(pair, trigger, dryRun, confirmedPathLowers)
        }
    }

    @Suppress("NestedBlockDepth", "TooGenericExceptionCaught", "LoopWithTooManyJumpStatements")
    private fun runPair(
        pair: FolderPair,
        trigger: SyncTrigger,
        dryRun: Boolean,
        confirmedPathLowers: Set<String>?,
    ): SyncResult {
        val startedAt = System.currentTimeMillis()
        val cancelFlag = cancelFlags.getOrPut(pair.id) { AtomicBoolean(false) }
        cancelFlag.set(false)
        val wakeLock = acquireWakeLock(pair.name)
        try {
            publish(
                SyncProgress(
                    pairId = pair.id,
                    pairName = pair.name,
                    phase = SyncPhase.Listing,
                    message = "Listing local and Dropbox files",
                ),
            )
            val ignore =
                SyncIgnoreMatcher.forPair(
                    globalText = preferences.getGlobalIgnores(),
                    useGlobal = pair.useGlobalIgnores,
                    customText = pair.customIgnores,
                    ignoreHidden = pair.ignoreHidden,
                )
            val storage = SyncStorageAdapter.create(appContext, pair)
            val localEntries = storage.listFiles(ignore)
            checkCancelled(cancelFlag)

            val remoteEntries =
                apiClient
                    .listFolder(pair.remotePath, recursive = true)
                    .filterNot { ignore.ignores(it.relativePath) }
            checkCancelled(cancelFlag)

            publish(
                SyncProgress(
                    pairId = pair.id,
                    pairName = pair.name,
                    phase = SyncPhase.Comparing,
                    totalFiles = localEntries.size + remoteEntries.size,
                    message = "Comparing files",
                ),
            )

            val baseline = database.loadBaseline(pair.id)
            val hashCache = mutableMapOf<String, String>()
            val planner =
                SyncPlanner { relativePath ->
                    hashCache.getOrPut(relativePath) { storage.contentHash(relativePath) }
                }
            val plan =
                planner.plan(
                    mode = pair.mode,
                    conflictPolicy = pair.conflictPolicy,
                    confirmLocalChanges = pair.confirmLocalChanges && confirmedPathLowers == null,
                    localEntries = localEntries,
                    remoteEntries = remoteEntries,
                    baselineEntries = baseline,
                )

            if (dryRun) {
                val summary =
                    "Dry run: ↓${plan.downloadCount} ↑${plan.uploadCount} " +
                        "delL${plan.deleteLocalCount} delR${plan.deleteRemoteCount} " +
                        "same${plan.skippedIdentical} confirm${plan.confirmationActions.size}"
                return SyncResult(
                    pairId = pair.id,
                    status = SyncRunStatus.Success,
                    downloaded = plan.downloadCount,
                    uploaded = plan.uploadCount,
                    deletedLocal = plan.deleteLocalCount,
                    deletedRemote = plan.deleteRemoteCount,
                    skippedIdentical = plan.skippedIdentical,
                    conflicts = plan.conflictCount,
                    pendingConfirmation = plan.confirmationActions,
                    summary = summary,
                )
            }

            val actions = mutableListOf<SyncAction>()
            actions += plan.safeActions
            if (confirmedPathLowers != null) {
                actions +=
                    plan.confirmationActions.filter { it.pathLower in confirmedPathLowers }
            }

            var downloaded = 0
            var uploaded = 0
            var deletedLocal = 0
            var deletedRemote = 0
            var conflicts = 0
            var skippedIdentical = plan.skippedIdentical
            val pendingBaseline = mutableListOf<SyncBaselineEntry>()
            var lastFlush = System.currentTimeMillis()
            var processedBytes = 0L
            val compareBytes =
                localEntries.filter { !it.isDir }.sumOf { it.size }.coerceAtLeast(1L)

            fun flushBaseline(force: Boolean = false) {
                val now = System.currentTimeMillis()
                if (pendingBaseline.isEmpty()) return
                if (!force && pendingBaseline.size < 25 && now - lastFlush < 5000L) return
                database.upsertBaselines(pair.id, pendingBaseline.toList())
                pendingBaseline.clear()
                lastFlush = now
            }

            fun remember(
                local: SyncTreeEntry?,
                remote: SyncTreeEntry?,
                hash: String?,
            ) {
                val relative = local?.relativePath ?: remote?.relativePath ?: return
                val pathLower = normalizePathLower(relative)
                pendingBaseline +=
                    SyncBaselineEntry(
                        relativePath = relative,
                        pathLower = pathLower,
                        isDir = local?.isDir == true || remote?.isDir == true,
                        localSize = local?.size ?: remote?.size ?: 0L,
                        localMtimeMs = local?.mtimeMs ?: 0L,
                        contentHash = hash ?: local?.contentHash ?: remote?.contentHash,
                        remoteId = remote?.remoteId,
                        remoteRev = remote?.remoteRev,
                        remoteServerModifiedMs = remote?.remoteServerModifiedMs ?: 0L,
                    )
                flushBaseline()
            }

            publish(
                SyncProgress(
                    pairId = pair.id,
                    pairName = pair.name,
                    phase = SyncPhase.Transferring,
                    totalFiles = actions.size,
                    skippedIdentical = skippedIdentical,
                    totalBytes = compareBytes,
                    message = "Transferring",
                ),
            )

            for ((index, action) in actions.withIndex()) {
                checkCancelled(cancelFlag)
                publish(
                    SyncProgress(
                        pairId = pair.id,
                        pairName = pair.name,
                        phase = SyncPhase.Transferring,
                        currentPath = action.relativePath,
                        processedFiles = index,
                        totalFiles = actions.size,
                        processedBytes = processedBytes,
                        totalBytes = compareBytes,
                        skippedIdentical = skippedIdentical,
                        downloaded = downloaded,
                        uploaded = uploaded,
                        deletedLocal = deletedLocal,
                        deletedRemote = deletedRemote,
                    ),
                )
                when (action) {
                    is SyncAction.Skip -> skippedIdentical += 1

                    is SyncAction.RecordBaselineOnly -> {
                        skippedIdentical += 1
                        processedBytes += action.local?.size ?: action.remote?.size ?: 0L
                        remember(action.local, action.remote, action.contentHash)
                    }

                    is SyncAction.MkdirLocal -> {
                        storage.mkdir(action.relativePath)
                        remember(
                            storage.getEntry(action.relativePath),
                            remoteEntries.find { it.pathLower == action.pathLower },
                            null,
                        )
                    }

                    is SyncAction.MkdirRemote -> {
                        val remotePath = joinRemote(pair.remotePath, action.relativePath)
                        apiClient.createFolder(remotePath)
                        remember(storage.getEntry(action.relativePath), null, null)
                    }

                    is SyncAction.Download -> {
                        val remotePath = joinRemote(pair.remotePath, action.relativePath)
                        val written =
                            storage.writeFile(
                                relativePath = action.relativePath,
                                desiredMtimeMs = action.remote.mtimeMs.takeIf { it > 0L },
                            ) { output ->
                                apiClient.download(remotePath, output)
                            }
                        downloaded += 1
                        processedBytes += written.size
                        remember(written, action.remote, action.remote.contentHash)
                    }

                    is SyncAction.Upload -> {
                        val remotePath = joinRemote(pair.remotePath, action.relativePath)
                        val remoteMeta =
                            storage.openInput(action.relativePath).use { input ->
                                apiClient.upload(remotePath, input, action.local.size)
                            }
                        uploaded += 1
                        processedBytes += action.local.size
                        val localAfter = storage.getEntry(action.relativePath) ?: action.local
                        remember(
                            localAfter,
                            remoteMeta.copy(
                                relativePath = action.relativePath,
                                pathLower = action.pathLower,
                            ),
                            remoteMeta.contentHash,
                        )
                    }

                    is SyncAction.DeleteLocal -> {
                        storage.delete(action.relativePath)
                        database.deleteBaseline(pair.id, action.pathLower)
                        deletedLocal += 1
                    }

                    is SyncAction.DeleteRemote -> {
                        apiClient.delete(joinRemote(pair.remotePath, action.relativePath))
                        database.deleteBaseline(pair.id, action.pathLower)
                        deletedRemote += 1
                    }

                    is SyncAction.ResolveConflict -> {
                        conflicts += 1
                        resolveConflict(pair, storage, action)
                        val localAfter = storage.getEntry(action.relativePath)
                        val parentRemote =
                            joinRemote(
                                pair.remotePath,
                                action.relativePath.substringBeforeLast('/', ""),
                            )
                        val remoteAfter =
                            apiClient
                                .listFolder(parentRemote, recursive = false)
                                .find { it.pathLower == action.pathLower }
                        remember(localAfter, remoteAfter ?: action.remote, null)
                    }
                }
            }
            flushBaseline(force = true)

            val confirmationLeft =
                if (confirmedPathLowers == null) {
                    plan.confirmationActions
                } else {
                    emptyList()
                }
            if (confirmationLeft.isNotEmpty()) {
                pendingConfirmations[pair.id] =
                    PendingConfirmation(
                        pairId = pair.id,
                        pairName = pair.name,
                        actions = confirmationLeft,
                    )
                val summary =
                    "Needs confirmation: ${confirmationLeft.size} local change(s); " +
                        "↓$downloaded ↑$uploaded same$skippedIdentical"
                val result =
                    SyncResult(
                        pairId = pair.id,
                        status = SyncRunStatus.NeedsConfirmation,
                        downloaded = downloaded,
                        uploaded = uploaded,
                        deletedLocal = deletedLocal,
                        deletedRemote = deletedRemote,
                        skippedIdentical = skippedIdentical,
                        conflicts = conflicts,
                        pendingConfirmation = confirmationLeft,
                        summary = summary,
                    )
                database.updatePairStatus(pair.id, result.status, result.summary)
                database.insertLog(pair.id, trigger, result, startedAt)
                publish(
                    SyncProgress(
                        pairId = pair.id,
                        pairName = pair.name,
                        phase = SyncPhase.WaitingConfirmation,
                        message = summary,
                        downloaded = downloaded,
                        uploaded = uploaded,
                        skippedIdentical = skippedIdentical,
                    ),
                )
                return result
            }

            pendingConfirmations.remove(pair.id)
            val summary =
                "↓$downloaded ↑$uploaded delL$deletedLocal delR$deletedRemote same$skippedIdentical"
            val result =
                SyncResult(
                    pairId = pair.id,
                    status = SyncRunStatus.Success,
                    downloaded = downloaded,
                    uploaded = uploaded,
                    deletedLocal = deletedLocal,
                    deletedRemote = deletedRemote,
                    skippedIdentical = skippedIdentical,
                    skippedByUser = 0,
                    conflicts = conflicts,
                    summary = summary,
                )
            database.updatePairStatus(pair.id, result.status, result.summary)
            database.insertLog(pair.id, trigger, result, startedAt)
            publish(
                SyncProgress(
                    pairId = pair.id,
                    pairName = pair.name,
                    phase = SyncPhase.Finishing,
                    message = summary,
                    downloaded = downloaded,
                    uploaded = uploaded,
                    skippedIdentical = skippedIdentical,
                    deletedLocal = deletedLocal,
                    deletedRemote = deletedRemote,
                ),
            )
            return result
        } catch (cancelled: CancellationException) {
            val result =
                SyncResult(
                    pairId = pair.id,
                    status = SyncRunStatus.Cancelled,
                    summary = "Cancelled",
                    errorMessage = cancelled.message,
                )
            database.updatePairStatus(pair.id, result.status, result.summary)
            database.insertLog(pair.id, trigger, result, startedAt)
            return result
        } catch (error: Exception) {
            val result =
                SyncResult(
                    pairId = pair.id,
                    status = SyncRunStatus.Error,
                    summary = "Error",
                    errorMessage = error.message ?: error.toString(),
                )
            database.updatePairStatus(pair.id, result.status, result.summary)
            database.insertLog(pair.id, trigger, result, startedAt)
            return result
        } finally {
            wakeLock?.release()
            if (_progress.value?.pairId == pair.id) {
                _progress.value = null
            }
        }
    }

    @Suppress("LoopWithTooManyJumpStatements")
    suspend fun applyPendingConfirmation(
        pairId: Long,
        selectedPathLowers: Set<String>,
        trigger: SyncTrigger = SyncTrigger.Manual,
    ): SyncResult = withContext(Dispatchers.IO) {
        val pending =
            pendingConfirmations[pairId]
                ?: return@withContext SyncResult(
                    pairId = pairId,
                    status = SyncRunStatus.Error,
                    errorMessage = "No pending confirmation",
                    summary = "Nothing to confirm",
                )
        val pair =
            database.getPair(pairId)
                ?: return@withContext SyncResult(
                    pairId = pairId,
                    status = SyncRunStatus.Error,
                    errorMessage = "Folder pair not found",
                    summary = "Missing pair",
                )
        val storage = SyncStorageAdapter.create(appContext, pair)
        var downloaded = 0
        var deletedLocal = 0
        var skippedByUser = 0
        val startedAt = System.currentTimeMillis()
        for (action in pending.actions) {
            if (action.pathLower !in selectedPathLowers) {
                skippedByUser += 1
                when (action) {
                    is SyncAction.DeleteLocal -> {
                        val local = storage.getEntry(action.relativePath) ?: continue
                        database.upsertBaseline(
                            pairId,
                            SyncBaselineEntry(
                                relativePath = local.relativePath,
                                pathLower = local.pathLower,
                                isDir = local.isDir,
                                localSize = local.size,
                                localMtimeMs = local.mtimeMs,
                                contentHash = null,
                            ),
                        )
                    }

                    is SyncAction.Download -> {
                        val local = storage.getEntry(action.relativePath) ?: continue
                        database.upsertBaseline(
                            pairId,
                            SyncBaselineEntry(
                                relativePath = local.relativePath,
                                pathLower = local.pathLower,
                                isDir = local.isDir,
                                localSize = local.size,
                                localMtimeMs = local.mtimeMs,
                                contentHash = null,
                                remoteId = action.remote.remoteId,
                                remoteRev = action.remote.remoteRev,
                                remoteServerModifiedMs = action.remote.remoteServerModifiedMs,
                            ),
                        )
                    }

                    else -> Unit
                }
                continue
            }
            when (action) {
                is SyncAction.DeleteLocal -> {
                    storage.delete(action.relativePath)
                    database.deleteBaseline(pairId, action.pathLower)
                    deletedLocal += 1
                }

                is SyncAction.Download -> {
                    val remotePath = joinRemote(pair.remotePath, action.relativePath)
                    val written =
                        storage.writeFile(
                            relativePath = action.relativePath,
                            desiredMtimeMs = action.remote.mtimeMs.takeIf { it > 0L },
                        ) { output ->
                            apiClient.download(remotePath, output)
                        }
                    database.upsertBaseline(
                        pairId,
                        SyncBaselineEntry(
                            relativePath = written.relativePath,
                            pathLower = written.pathLower,
                            isDir = false,
                            localSize = written.size,
                            localMtimeMs = written.mtimeMs,
                            contentHash = action.remote.contentHash,
                            remoteId = action.remote.remoteId,
                            remoteRev = action.remote.remoteRev,
                            remoteServerModifiedMs = action.remote.remoteServerModifiedMs,
                        ),
                    )
                    downloaded += 1
                }

                else -> Unit
            }
        }
        pendingConfirmations.remove(pairId)
        val summary = "Confirmed: ↓$downloaded delL$deletedLocal skipped$skippedByUser"
        val result =
            SyncResult(
                pairId = pairId,
                status = SyncRunStatus.Success,
                downloaded = downloaded,
                deletedLocal = deletedLocal,
                skippedByUser = skippedByUser,
                summary = summary,
            )
        database.updatePairStatus(pairId, result.status, result.summary)
        database.insertLog(pairId, trigger, result, startedAt)
        result
    }

    private fun resolveConflict(
        pair: FolderPair,
        storage: SyncStorageAdapter,
        action: SyncAction.ResolveConflict,
    ) {
        when (action.policy) {
            ConflictPolicy.PreferLocal -> {
                val remotePath = joinRemote(pair.remotePath, action.relativePath)
                storage.openInput(action.relativePath).use { input ->
                    apiClient.upload(remotePath, input, action.local.size)
                }
            }

            ConflictPolicy.PreferRemote -> {
                val remotePath = joinRemote(pair.remotePath, action.relativePath)
                storage.writeFile(action.relativePath, desiredMtimeMs = action.remote.mtimeMs) { output ->
                    apiClient.download(remotePath, output)
                }
            }

            ConflictPolicy.NewerWins -> {
                if (action.local.mtimeMs >= action.remote.remoteServerModifiedMs) {
                    resolveConflict(pair, storage, action.copy(policy = ConflictPolicy.PreferLocal))
                } else {
                    resolveConflict(pair, storage, action.copy(policy = ConflictPolicy.PreferRemote))
                }
            }

            ConflictPolicy.KeepBoth -> {
                val stamp =
                    SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(Date())
                val conflictName = conflictName(action.relativePath, stamp)
                // Keep local as conflict copy, download remote onto original path.
                val localBytes = storage.openInput(action.relativePath).use { it.readBytes() }
                storage.writeFile(conflictName) { output -> output.write(localBytes) }
                val remotePath = joinRemote(pair.remotePath, action.relativePath)
                storage.writeFile(action.relativePath, desiredMtimeMs = action.remote.mtimeMs) { output ->
                    apiClient.download(remotePath, output)
                }
                // Upload conflict copy to Dropbox too for visibility on other devices.
                val conflictRemote = joinRemote(pair.remotePath, conflictName)
                storage.openInput(conflictName).use { input ->
                    val entry = storage.getEntry(conflictName)
                    apiClient.upload(conflictRemote, input, entry?.size ?: localBytes.size.toLong())
                }
            }
        }
    }

    private fun conflictName(
        relativePath: String,
        stamp: String,
    ): String {
        val slash = relativePath.lastIndexOf('/')
        val parent = if (slash >= 0) relativePath.substring(0, slash + 1) else ""
        val name = if (slash >= 0) relativePath.substring(slash + 1) else relativePath
        val dot = name.lastIndexOf('.')
        return if (dot > 0) {
            parent + name.substring(0, dot) + ".sync-conflict-$stamp" + name.substring(dot)
        } else {
            parent + "$name.sync-conflict-$stamp"
        }
    }

    private fun joinRemote(
        root: String,
        relative: String,
    ): String {
        val rootNorm = DropboxApiClient.normalizeDropboxPath(root)
        val rel = normalizeRelativePath(relative)
        return if (rootNorm.isEmpty()) {
            "/$rel"
        } else if (rel.isEmpty()) {
            rootNorm
        } else {
            "$rootNorm/$rel"
        }
    }

    private fun publish(progress: SyncProgress) {
        _progress.value = progress
    }

    private fun checkCancelled(flag: AtomicBoolean) {
        if (flag.get()) {
            throw CancellationException("Cancelled by user")
        }
    }

    private fun acquireWakeLock(name: String): PowerManager.WakeLock? = runCatching {
        val pm = appContext.getSystemService(Context.POWER_SERVICE) as PowerManager
        pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "hsk:dropboxsync:$name").apply {
            setReferenceCounted(false)
            acquire(3 * 60 * 60 * 1000L)
        }
    }.getOrNull()

    private class CancellationException(
        message: String,
    ) : Exception(message)

    data class PendingConfirmation(
        val pairId: Long,
        val pairName: String,
        val actions: List<SyncAction>,
    )

    companion object {
        @Volatile
        private var instance: SyncEngine? = null

        fun get(context: Context): SyncEngine = instance ?: synchronized(this) {
            instance ?: SyncEngine(context.applicationContext).also { instance = it }
        }
    }
}
