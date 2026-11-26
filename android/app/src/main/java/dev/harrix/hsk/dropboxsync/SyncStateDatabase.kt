package dev.harrix.hsk.dropboxsync

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

/** SQLite persistence for folder pairs, baseline entries, logs, and widget bindings. */
class SyncStateDatabase(
    context: Context,
) : SQLiteOpenHelper(context, DB_NAME, null, DB_VERSION) {
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL(
            """
            CREATE TABLE folder_pairs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              local_path_or_uri TEXT NOT NULL,
              storage_type TEXT NOT NULL,
              remote_path TEXT NOT NULL,
              mode TEXT NOT NULL,
              conflict_policy TEXT NOT NULL,
              confirm_local_changes INTEGER NOT NULL DEFAULT 1,
              use_global_ignores INTEGER NOT NULL DEFAULT 1,
              custom_ignores TEXT NOT NULL DEFAULT '',
              ignore_hidden INTEGER NOT NULL DEFAULT 0,
              enabled INTEGER NOT NULL DEFAULT 1,
              remote_cursor TEXT,
              last_sync_at INTEGER,
              last_status TEXT,
              last_summary TEXT
            )
            """.trimIndent(),
        )
        db.execSQL(
            """
            CREATE TABLE sync_entries (
              pair_id INTEGER NOT NULL,
              relative_path TEXT NOT NULL,
              path_lower TEXT NOT NULL,
              is_dir INTEGER NOT NULL,
              local_size INTEGER NOT NULL DEFAULT 0,
              local_mtime INTEGER NOT NULL DEFAULT 0,
              content_hash TEXT,
              remote_id TEXT,
              remote_rev TEXT,
              remote_server_modified INTEGER NOT NULL DEFAULT 0,
              PRIMARY KEY(pair_id, path_lower)
            )
            """.trimIndent(),
        )
        db.execSQL(
            """
            CREATE TABLE sync_logs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              pair_id INTEGER NOT NULL,
              started_at INTEGER NOT NULL,
              finished_at INTEGER,
              trigger_name TEXT NOT NULL,
              status TEXT NOT NULL,
              downloaded INTEGER NOT NULL DEFAULT 0,
              uploaded INTEGER NOT NULL DEFAULT 0,
              deleted_local INTEGER NOT NULL DEFAULT 0,
              deleted_remote INTEGER NOT NULL DEFAULT 0,
              skipped_identical INTEGER NOT NULL DEFAULT 0,
              skipped_by_user INTEGER NOT NULL DEFAULT 0,
              conflicts INTEGER NOT NULL DEFAULT 0,
              error_message TEXT,
              details_json TEXT
            )
            """.trimIndent(),
        )
        db.execSQL(
            """
            CREATE TABLE widget_bindings (
              app_widget_id INTEGER PRIMARY KEY,
              pair_id INTEGER
            )
            """.trimIndent(),
        )
    }

    override fun onUpgrade(
        db: SQLiteDatabase,
        oldVersion: Int,
        newVersion: Int,
    ) {
        // v1 initial schema
    }

    fun listPairs(): List<FolderPair> {
        val sizes = localSizesByPairId()
        readableDatabase
            .query("folder_pairs", null, null, null, null, null, "name COLLATE NOCASE ASC")
            .use { cursor ->
                val out = mutableListOf<FolderPair>()
                while (cursor.moveToNext()) {
                    val pair = cursorToPair(cursor)
                    out += pair.copy(localSizeBytes = sizes[pair.id])
                }
                return out
            }
    }

    fun getPair(id: Long): FolderPair? {
        readableDatabase
            .query("folder_pairs", null, "id=?", arrayOf(id.toString()), null, null, null)
            .use { cursor ->
                if (!cursor.moveToFirst()) {
                    return null
                }
                val pair = cursorToPair(cursor)
                return pair.copy(localSizeBytes = localSizesByPairId(pair.id)[pair.id])
            }
    }

    private fun localSizesByPairId(pairId: Long? = null): Map<Long, Long> {
        val sql =
            if (pairId == null) {
                "SELECT pair_id, SUM(local_size) FROM sync_entries WHERE is_dir=0 GROUP BY pair_id"
            } else {
                "SELECT pair_id, SUM(local_size) FROM sync_entries WHERE is_dir=0 AND pair_id=? GROUP BY pair_id"
            }
        val args = pairId?.let { arrayOf(it.toString()) }
        readableDatabase.rawQuery(sql, args).use { cursor ->
            val out = mutableMapOf<Long, Long>()
            while (cursor.moveToNext()) {
                out[cursor.getLong(0)] = cursor.getLong(1)
            }
            return out
        }
    }

    fun insertPair(pair: FolderPair): Long {
        val values = pairToValues(pair)
        return writableDatabase.insert("folder_pairs", null, values)
    }

    fun updatePair(pair: FolderPair) {
        writableDatabase.update(
            "folder_pairs",
            pairToValues(pair),
            "id=?",
            arrayOf(pair.id.toString()),
        )
    }

    fun deletePair(id: Long) {
        val db = writableDatabase
        db.beginTransaction()
        try {
            db.delete("sync_entries", "pair_id=?", arrayOf(id.toString()))
            db.delete("sync_logs", "pair_id=?", arrayOf(id.toString()))
            db.delete("widget_bindings", "pair_id=?", arrayOf(id.toString()))
            db.delete("folder_pairs", "id=?", arrayOf(id.toString()))
            db.setTransactionSuccessful()
        } finally {
            db.endTransaction()
        }
    }

    fun updatePairStatus(
        id: Long,
        status: SyncRunStatus,
        summary: String,
        syncedAtMs: Long = System.currentTimeMillis(),
    ) {
        val values =
            ContentValues().apply {
                put("last_status", status.name)
                put("last_summary", summary)
                put("last_sync_at", syncedAtMs)
            }
        writableDatabase.update("folder_pairs", values, "id=?", arrayOf(id.toString()))
    }

    fun loadBaseline(pairId: Long): Map<String, SyncBaselineEntry> {
        readableDatabase
            .query("sync_entries", null, "pair_id=?", arrayOf(pairId.toString()), null, null, null)
            .use { cursor ->
                val out = linkedMapOf<String, SyncBaselineEntry>()
                while (cursor.moveToNext()) {
                    val entry =
                        SyncBaselineEntry(
                            relativePath = cursor.getString(cursor.getColumnIndexOrThrow("relative_path")),
                            pathLower = cursor.getString(cursor.getColumnIndexOrThrow("path_lower")),
                            isDir = cursor.getInt(cursor.getColumnIndexOrThrow("is_dir")) == 1,
                            localSize = cursor.getLong(cursor.getColumnIndexOrThrow("local_size")),
                            localMtimeMs = cursor.getLong(cursor.getColumnIndexOrThrow("local_mtime")),
                            contentHash = cursor.getString(cursor.getColumnIndexOrThrow("content_hash")),
                            remoteId = cursor.getString(cursor.getColumnIndexOrThrow("remote_id")),
                            remoteRev = cursor.getString(cursor.getColumnIndexOrThrow("remote_rev")),
                            remoteServerModifiedMs =
                            cursor.getLong(cursor.getColumnIndexOrThrow("remote_server_modified")),
                        )
                    out[entry.pathLower] = entry
                }
                return out
            }
    }

    fun upsertBaseline(
        pairId: Long,
        entry: SyncBaselineEntry,
    ) {
        val values =
            ContentValues().apply {
                put("pair_id", pairId)
                put("relative_path", entry.relativePath)
                put("path_lower", entry.pathLower)
                put("is_dir", if (entry.isDir) 1 else 0)
                put("local_size", entry.localSize)
                put("local_mtime", entry.localMtimeMs)
                put("content_hash", entry.contentHash)
                put("remote_id", entry.remoteId)
                put("remote_rev", entry.remoteRev)
                put("remote_server_modified", entry.remoteServerModifiedMs)
            }
        writableDatabase.insertWithOnConflict(
            "sync_entries",
            null,
            values,
            SQLiteDatabase.CONFLICT_REPLACE,
        )
    }

    fun upsertBaselines(
        pairId: Long,
        entries: Collection<SyncBaselineEntry>,
    ) {
        if (entries.isEmpty()) return
        val db = writableDatabase
        db.beginTransaction()
        try {
            for (entry in entries) {
                upsertBaseline(pairId, entry)
            }
            db.setTransactionSuccessful()
        } finally {
            db.endTransaction()
        }
    }

    fun deleteBaseline(
        pairId: Long,
        pathLower: String,
    ) {
        writableDatabase.delete(
            "sync_entries",
            "pair_id=? AND path_lower=?",
            arrayOf(pairId.toString(), pathLower),
        )
    }

    fun clearBaseline(pairId: Long) {
        writableDatabase.delete("sync_entries", "pair_id=?", arrayOf(pairId.toString()))
    }

    fun insertLog(
        pairId: Long,
        trigger: SyncTrigger,
        result: SyncResult,
        startedAtMs: Long,
        finishedAtMs: Long = System.currentTimeMillis(),
        detailsJson: String? = null,
    ): Long {
        val values =
            ContentValues().apply {
                put("pair_id", pairId)
                put("started_at", startedAtMs)
                put("finished_at", finishedAtMs)
                put("trigger_name", trigger.name)
                put("status", result.status.name)
                put("downloaded", result.downloaded)
                put("uploaded", result.uploaded)
                put("deleted_local", result.deletedLocal)
                put("deleted_remote", result.deletedRemote)
                put("skipped_identical", result.skippedIdentical)
                put("skipped_by_user", result.skippedByUser)
                put("conflicts", result.conflicts)
                put("error_message", result.errorMessage)
                put("details_json", detailsJson)
            }
        return writableDatabase.insert("sync_logs", null, values)
    }

    fun listLogs(
        pairId: Long,
        limit: Int = 50,
    ): List<SyncLogRow> {
        readableDatabase
            .query(
                "sync_logs",
                null,
                "pair_id=?",
                arrayOf(pairId.toString()),
                null,
                null,
                "started_at DESC",
                limit.toString(),
            ).use { cursor ->
                val out = mutableListOf<SyncLogRow>()
                while (cursor.moveToNext()) {
                    out +=
                        SyncLogRow(
                            id = cursor.getLong(cursor.getColumnIndexOrThrow("id")),
                            pairId = pairId,
                            startedAtMs = cursor.getLong(cursor.getColumnIndexOrThrow("started_at")),
                            finishedAtMs =
                            cursor
                                .getLong(cursor.getColumnIndexOrThrow("finished_at"))
                                .takeIf { !cursor.isNull(cursor.getColumnIndexOrThrow("finished_at")) },
                            trigger =
                            SyncTrigger.valueOf(
                                cursor.getString(cursor.getColumnIndexOrThrow("trigger_name")),
                            ),
                            status =
                            SyncRunStatus.valueOf(
                                cursor.getString(cursor.getColumnIndexOrThrow("status")),
                            ),
                            downloaded = cursor.getInt(cursor.getColumnIndexOrThrow("downloaded")),
                            uploaded = cursor.getInt(cursor.getColumnIndexOrThrow("uploaded")),
                            deletedLocal = cursor.getInt(cursor.getColumnIndexOrThrow("deleted_local")),
                            deletedRemote = cursor.getInt(cursor.getColumnIndexOrThrow("deleted_remote")),
                            skippedIdentical =
                            cursor.getInt(cursor.getColumnIndexOrThrow("skipped_identical")),
                            skippedByUser = cursor.getInt(cursor.getColumnIndexOrThrow("skipped_by_user")),
                            conflicts = cursor.getInt(cursor.getColumnIndexOrThrow("conflicts")),
                            errorMessage = cursor.getString(cursor.getColumnIndexOrThrow("error_message")),
                        )
                }
                return out
            }
    }

    fun bindWidget(
        appWidgetId: Int,
        pairId: Long?,
    ) {
        val values =
            ContentValues().apply {
                put("app_widget_id", appWidgetId)
                if (pairId == null) {
                    putNull("pair_id")
                } else {
                    put("pair_id", pairId)
                }
            }
        writableDatabase.insertWithOnConflict(
            "widget_bindings",
            null,
            values,
            SQLiteDatabase.CONFLICT_REPLACE,
        )
    }

    fun getWidgetPairId(appWidgetId: Int): Long? {
        readableDatabase
            .query(
                "widget_bindings",
                arrayOf("pair_id"),
                "app_widget_id=?",
                arrayOf(appWidgetId.toString()),
                null,
                null,
                null,
            ).use { cursor ->
                if (!cursor.moveToFirst()) return null
                val idx = cursor.getColumnIndexOrThrow("pair_id")
                return if (cursor.isNull(idx)) null else cursor.getLong(idx)
            }
    }

    fun deleteWidgetBinding(appWidgetId: Int) {
        writableDatabase.delete(
            "widget_bindings",
            "app_widget_id=?",
            arrayOf(appWidgetId.toString()),
        )
    }

    private fun cursorToPair(cursor: android.database.Cursor): FolderPair {
        fun str(column: String): String = cursor.getString(cursor.getColumnIndexOrThrow(column))

        fun longOrNull(column: String): Long? {
            val idx = cursor.getColumnIndexOrThrow(column)
            return if (cursor.isNull(idx)) null else cursor.getLong(idx)
        }
        return FolderPair(
            id = cursor.getLong(cursor.getColumnIndexOrThrow("id")),
            name = str("name"),
            localPathOrUri = str("local_path_or_uri"),
            storageType = StorageType.valueOf(str("storage_type")),
            remotePath = str("remote_path"),
            mode = SyncMode.valueOf(str("mode")),
            conflictPolicy = ConflictPolicy.valueOf(str("conflict_policy")),
            confirmLocalChanges = cursor.getInt(cursor.getColumnIndexOrThrow("confirm_local_changes")) == 1,
            useGlobalIgnores = cursor.getInt(cursor.getColumnIndexOrThrow("use_global_ignores")) == 1,
            customIgnores = str("custom_ignores"),
            ignoreHidden = cursor.getInt(cursor.getColumnIndexOrThrow("ignore_hidden")) == 1,
            enabled = cursor.getInt(cursor.getColumnIndexOrThrow("enabled")) == 1,
            remoteCursor = cursor.getString(cursor.getColumnIndexOrThrow("remote_cursor")),
            lastSyncAtMs = longOrNull("last_sync_at"),
            lastStatus =
            cursor.getString(cursor.getColumnIndexOrThrow("last_status"))?.let {
                runCatching { SyncRunStatus.valueOf(it) }.getOrNull()
            },
            lastSummary = cursor.getString(cursor.getColumnIndexOrThrow("last_summary")),
        )
    }

    private fun pairToValues(pair: FolderPair): ContentValues = ContentValues().apply {
        put("name", pair.name)
        put("local_path_or_uri", pair.localPathOrUri)
        put("storage_type", pair.storageType.name)
        put("remote_path", pair.remotePath)
        put("mode", pair.mode.name)
        put("conflict_policy", pair.conflictPolicy.name)
        put("confirm_local_changes", if (pair.confirmLocalChanges) 1 else 0)
        put("use_global_ignores", if (pair.useGlobalIgnores) 1 else 0)
        put("custom_ignores", pair.customIgnores)
        put("ignore_hidden", if (pair.ignoreHidden) 1 else 0)
        put("enabled", if (pair.enabled) 1 else 0)
        put("remote_cursor", pair.remoteCursor)
        put("last_sync_at", pair.lastSyncAtMs)
        put("last_status", pair.lastStatus?.name)
        put("last_summary", pair.lastSummary)
    }

    companion object {
        private const val DB_NAME = "dropbox_sync.db"
        private const val DB_VERSION = 1
    }
}

data class SyncLogRow(
    val id: Long,
    val pairId: Long,
    val startedAtMs: Long,
    val finishedAtMs: Long?,
    val trigger: SyncTrigger,
    val status: SyncRunStatus,
    val downloaded: Int,
    val uploaded: Int,
    val deletedLocal: Int,
    val deletedRemote: Int,
    val skippedIdentical: Int,
    val skippedByUser: Int,
    val conflicts: Int,
    val errorMessage: String?,
)
