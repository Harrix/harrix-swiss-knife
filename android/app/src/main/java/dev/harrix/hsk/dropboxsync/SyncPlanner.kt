package dev.harrix.hsk.dropboxsync

/**
 * Pure 3-way sync planner for TwoWay and DownloadMirror.
 *
 * [hashProvider] is called only when sizes match and a content comparison is required.
 */
class SyncPlanner(
    private val hashProvider: (relativePath: String) -> String,
) {
    fun plan(
        mode: SyncMode,
        conflictPolicy: ConflictPolicy,
        confirmLocalChanges: Boolean,
        localEntries: Collection<SyncTreeEntry>,
        remoteEntries: Collection<SyncTreeEntry>,
        baselineEntries: Map<String, SyncBaselineEntry>,
    ): SyncPlan {
        val local = localEntries.associateBy { it.pathLower }
        val remote = remoteEntries.associateBy { it.pathLower }
        val keys =
            LinkedHashSet<String>().apply {
                addAll(local.keys)
                addAll(remote.keys)
                addAll(baselineEntries.keys)
            }
        val safe = mutableListOf<SyncAction>()
        val confirm = mutableListOf<SyncAction>()
        var skippedIdentical = 0

        for (key in keys.sorted()) {
            val l = local[key]
            val r = remote[key]
            val b = baselineEntries[key]
            when (mode) {
                SyncMode.TwoWay ->
                    planTwoWay(l, r, b, conflictPolicy) { action, identical ->
                        if (identical) skippedIdentical += 1
                        safe += action
                    }

                SyncMode.DownloadMirror ->
                    planMirror(l, r, b, confirmLocalChanges) { action, identical, needsConfirm ->
                        if (identical) skippedIdentical += 1
                        if (needsConfirm) {
                            confirm += action
                        } else {
                            safe += action
                        }
                    }
            }
        }
        return SyncPlan(safe, confirm, skippedIdentical)
    }

    private fun planTwoWay(
        local: SyncTreeEntry?,
        remote: SyncTreeEntry?,
        baseline: SyncBaselineEntry?,
        conflictPolicy: ConflictPolicy,
        emit: (SyncAction, identical: Boolean) -> Unit,
    ) {
        when {
            local == null && remote == null -> return

            local != null && remote == null -> {
                if (baseline == null) {
                    if (local.isDir) {
                        emit(SyncAction.MkdirRemote(local.relativePath, local.pathLower), false)
                    } else {
                        emit(SyncAction.Upload(local.relativePath, local.pathLower, local, false), false)
                    }
                } else if (!localChanged(local, baseline)) {
                    // Remote deleted, local unchanged → delete local.
                    emit(SyncAction.DeleteLocal(local.relativePath, local.pathLower, local), false)
                } else {
                    // Local still changing after remote delete → re-upload.
                    emit(SyncAction.Upload(local.relativePath, local.pathLower, local, true), false)
                }
            }

            local == null && remote != null -> {
                if (baseline == null) {
                    if (remote.isDir) {
                        emit(SyncAction.MkdirLocal(remote.relativePath, remote.pathLower), false)
                    } else {
                        emit(
                            SyncAction.Download(remote.relativePath, remote.pathLower, remote, false),
                            false,
                        )
                    }
                } else if (!remoteChanged(remote, baseline)) {
                    // Local deleted, remote unchanged → delete remote.
                    emit(SyncAction.DeleteRemote(remote.relativePath, remote.pathLower, remote), false)
                } else {
                    emit(
                        SyncAction.Download(remote.relativePath, remote.pathLower, remote, true),
                        false,
                    )
                }
            }

            local != null && remote != null -> {
                if (local.isDir || remote.isDir) {
                    if (local.isDir && remote.isDir) {
                        emit(
                            SyncAction.RecordBaselineOnly(
                                local.relativePath,
                                local.pathLower,
                                local,
                                remote,
                                null,
                            ),
                            true,
                        )
                    } else {
                        emit(
                            SyncAction.ResolveConflict(
                                local.relativePath,
                                local.pathLower,
                                local,
                                remote,
                                conflictPolicy,
                            ),
                            false,
                        )
                    }
                    return
                }

                if (baseline != null && !localChanged(local, baseline) && !remoteChanged(remote, baseline)) {
                    emit(SyncAction.Skip(local.relativePath, local.pathLower), true)
                    return
                }

                if (sameContent(local, remote)) {
                    emit(
                        SyncAction.RecordBaselineOnly(
                            local.relativePath,
                            local.pathLower,
                            local,
                            remote,
                            remote.contentHash ?: local.contentHash,
                        ),
                        true,
                    )
                    return
                }

                val localDirty = baseline == null || localChanged(local, baseline)
                val remoteDirty = baseline == null || remoteChanged(remote, baseline)
                when {
                    localDirty && !remoteDirty ->
                        emit(SyncAction.Upload(local.relativePath, local.pathLower, local, true), false)

                    remoteDirty && !localDirty ->
                        emit(
                            SyncAction.Download(remote.relativePath, remote.pathLower, remote, true),
                            false,
                        )

                    else ->
                        emit(
                            SyncAction.ResolveConflict(
                                local.relativePath,
                                local.pathLower,
                                local,
                                remote,
                                conflictPolicy,
                            ),
                            false,
                        )
                }
            }
        }
    }

    private fun planMirror(
        local: SyncTreeEntry?,
        remote: SyncTreeEntry?,
        baseline: SyncBaselineEntry?,
        confirmLocalChanges: Boolean,
        emit: (SyncAction, identical: Boolean, needsConfirm: Boolean) -> Unit,
    ) {
        when {
            local == null && remote == null -> return

            local == null && remote != null -> {
                if (remote.isDir) {
                    emit(SyncAction.MkdirLocal(remote.relativePath, remote.pathLower), false, false)
                } else {
                    emit(
                        SyncAction.Download(remote.relativePath, remote.pathLower, remote, false),
                        false,
                        false,
                    )
                }
            }

            local != null && remote == null -> {
                val needsConfirm = confirmLocalChanges
                emit(
                    SyncAction.DeleteLocal(
                        local.relativePath,
                        local.pathLower,
                        local,
                        needsConfirmation = needsConfirm,
                    ),
                    false,
                    needsConfirm,
                )
            }

            local != null && remote != null -> {
                if (local.isDir && remote.isDir) {
                    emit(
                        SyncAction.RecordBaselineOnly(
                            local.relativePath,
                            local.pathLower,
                            local,
                            remote,
                            null,
                        ),
                        true,
                        false,
                    )
                    return
                }
                if (local.isDir != remote.isDir) {
                    val needsConfirm = confirmLocalChanges
                    emit(
                        SyncAction.Download(
                            remote.relativePath,
                            remote.pathLower,
                            remote,
                            overwrite = true,
                            needsConfirmation = needsConfirm,
                        ),
                        false,
                        needsConfirm,
                    )
                    return
                }
                if (baseline != null && !localChanged(local, baseline) && !remoteChanged(remote, baseline)) {
                    emit(SyncAction.Skip(local.relativePath, local.pathLower), true, false)
                    return
                }
                if (sameContent(local, remote)) {
                    emit(
                        SyncAction.RecordBaselineOnly(
                            local.relativePath,
                            local.pathLower,
                            local,
                            remote,
                            remote.contentHash,
                        ),
                        true,
                        false,
                    )
                    return
                }
                val localDirty = baseline == null || localChanged(local, baseline)
                val needsConfirm = confirmLocalChanges && localDirty
                emit(
                    SyncAction.Download(
                        remote.relativePath,
                        remote.pathLower,
                        remote,
                        overwrite = true,
                        needsConfirmation = needsConfirm,
                    ),
                    false,
                    needsConfirm,
                )
            }
        }
    }

    private fun localChanged(
        local: SyncTreeEntry,
        baseline: SyncBaselineEntry,
    ): Boolean {
        if (local.isDir) return false
        return local.size != baseline.localSize || local.mtimeMs != baseline.localMtimeMs
    }

    private fun remoteChanged(
        remote: SyncTreeEntry,
        baseline: SyncBaselineEntry,
    ): Boolean {
        if (remote.isDir) return false
        if (!baseline.remoteRev.isNullOrBlank() && !remote.remoteRev.isNullOrBlank()) {
            return remote.remoteRev != baseline.remoteRev
        }
        return remote.contentHash != baseline.contentHash || remote.size != baseline.localSize
    }

    private fun sameContent(
        local: SyncTreeEntry,
        remote: SyncTreeEntry,
    ): Boolean {
        if (local.size != remote.size) return false
        val remoteHash = remote.contentHash ?: return false
        val localHash = local.contentHash ?: hashProvider(local.relativePath)
        return localHash.equals(remoteHash, ignoreCase = true)
    }
}
