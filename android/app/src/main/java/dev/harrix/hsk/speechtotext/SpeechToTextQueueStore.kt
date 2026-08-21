package dev.harrix.hsk.speechtotext

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.util.UUID

/**
 * Persistent speech message queue and recognition-time statistics.
 *
 * Audio files live under [Context.getFilesDir]/ messages survive process restarts.
 * Successful recognition durations stay in stats even after messages are deleted.
 */
class SpeechToTextQueueStore(
    context: Context,
) {
    private val appContext = context.applicationContext
    private val rootDir = File(appContext.filesDir, ROOT_DIR)
    private val indexFile = File(rootDir, INDEX_FILENAME)
    private val statsPrefs = appContext.getSharedPreferences(STATS_PREFS, Context.MODE_PRIVATE)

    @Synchronized
    fun loadAll(): List<SpeechQueueItem> {
        migrateLegacyPending()
        if (!indexFile.isFile) {
            return emptyList()
        }
        return try {
            val root = JSONObject(indexFile.readText())
            val items = root.optJSONArray(KEY_ITEMS) ?: JSONArray()
            buildList {
                for (i in 0 until items.length()) {
                    val obj = items.optJSONObject(i) ?: continue
                    parseItem(obj)?.let { add(it) }
                }
            }
        } catch (_: Exception) {
            emptyList()
        }
    }

    @Synchronized
    fun saveAll(items: List<SpeechQueueItem>) {
        rootDir.mkdirs()
        val array = JSONArray()
        items.forEach { item ->
            array.put(item.toJson())
        }
        val payload =
            JSONObject()
                .put(KEY_ITEMS, array)
                .toString()
        val temporary = File(rootDir, "$INDEX_FILENAME.tmp")
        temporary.writeText(payload)
        if (indexFile.exists() && !indexFile.delete()) {
            temporary.copyTo(indexFile, overwrite = true)
            temporary.delete()
        } else if (!temporary.renameTo(indexFile)) {
            temporary.copyTo(indexFile, overwrite = true)
            temporary.delete()
        }
    }

    @Synchronized
    fun addFromRecording(
        source: File,
        mimeType: String,
        audioDurationSeconds: Float,
    ): SpeechQueueItem {
        require(source.isFile) { "Recording file missing" }
        rootDir.mkdirs()
        val id = UUID.randomUUID().toString()
        val upload = AudioCompress.prepareForUpload(source, mimeType)
        val extension =
            when {
                upload.mimeType.contains("m4a", ignoreCase = true) -> ".m4a"
                upload.mimeType.contains("wav", ignoreCase = true) -> ".wav"
                else -> source.extension.ifBlank { "wav" }.let { ".$it" }
            }
        val destination = File(rootDir, "$id$extension")
        if (upload.file.absolutePath != destination.absolutePath) {
            upload.file.copyTo(destination, overwrite = true)
            if (upload.temporary && upload.file.absolutePath != source.absolutePath) {
                upload.file.delete()
            }
        }
        check(destination.isFile && destination.length() > MIN_VALID_FILE_BYTES) {
            "Could not store speech recording"
        }
        val item =
            SpeechQueueItem(
                id = id,
                audioFile = destination,
                mimeType = upload.mimeType,
                audioDurationSeconds = audioDurationSeconds.coerceAtLeast(0f),
                status = SpeechMessageStatus.Recorded,
                createdAtMs = System.currentTimeMillis(),
            )
        val items = loadAll().toMutableList()
        items.add(item)
        saveAll(items)
        return item
    }

    @Synchronized
    fun delete(id: String) {
        val items = loadAll().toMutableList()
        val index = items.indexOfFirst { it.id == id }
        if (index < 0) {
            return
        }
        val removed = items.removeAt(index)
        removed.audioFile.delete()
        saveAll(items)
    }

    @Synchronized
    fun update(item: SpeechQueueItem) {
        val items = loadAll().toMutableList()
        val index = items.indexOfFirst { it.id == item.id }
        if (index < 0) {
            items.add(item)
        } else {
            items[index] = item
        }
        saveAll(items)
    }

    fun averageRecognitionMs(): Long? {
        val count = statsPrefs.getInt(KEY_SUCCESS_COUNT, 0)
        val total = statsPrefs.getLong(KEY_SUCCESS_TOTAL_MS, 0L)
        if (count <= 0 || total <= 0L) {
            return null
        }
        return total / count
    }

    fun recordSuccessfulRecognition(durationMs: Long) {
        if (durationMs <= 0L) {
            return
        }
        val count = statsPrefs.getInt(KEY_SUCCESS_COUNT, 0) + 1
        val total = statsPrefs.getLong(KEY_SUCCESS_TOTAL_MS, 0L) + durationMs
        statsPrefs
            .edit()
            .putInt(KEY_SUCCESS_COUNT, count)
            .putLong(KEY_SUCCESS_TOTAL_MS, total)
            .apply()
    }

    private fun migrateLegacyPending() {
        val prefs = appContext.getSharedPreferences(LEGACY_PREFS, Context.MODE_PRIVATE)
        val legacyWav = File(rootDir, LEGACY_WAV)
        val legacyM4a = File(rootDir, LEGACY_M4A)
        val legacy =
            listOf(legacyM4a, legacyWav).firstOrNull {
                it.isFile && it.length() > MIN_VALID_FILE_BYTES
            } ?: return
        if (indexFile.isFile) {
            // Already on queue format; drop orphan legacy files if index exists.
            return
        }
        val mime =
            prefs.getString(LEGACY_KEY_MIME, null)
                ?: AudioCompress.mimeFromName(legacy)
        val duration = prefs.getFloat(LEGACY_KEY_DURATION, 0f).coerceAtLeast(0f)
        rootDir.mkdirs()
        val id = UUID.randomUUID().toString()
        val extension = if (legacy.name.endsWith(".m4a")) ".m4a" else ".wav"
        val destination = File(rootDir, "$id$extension")
        legacy.copyTo(destination, overwrite = true)
        legacyWav.delete()
        legacyM4a.delete()
        prefs.edit().clear().commit()
        val item =
            SpeechQueueItem(
                id = id,
                audioFile = destination,
                mimeType = mime,
                audioDurationSeconds = duration,
                status = SpeechMessageStatus.Recorded,
                createdAtMs = System.currentTimeMillis(),
            )
        saveAll(listOf(item))
    }

    private fun parseItem(obj: JSONObject): SpeechQueueItem? {
        val id = obj.optString(KEY_ID).ifBlank { return null }
        val fileName = obj.optString(KEY_FILE).ifBlank { return null }
        val file = File(rootDir, fileName)
        if (!file.isFile || file.length() <= MIN_VALID_FILE_BYTES) {
            return null
        }
        val statusName = obj.optString(KEY_STATUS, SpeechMessageStatus.Recorded.name)
        var status =
            runCatching { SpeechMessageStatus.valueOf(statusName) }
                .getOrDefault(SpeechMessageStatus.Recorded)
        // In-flight jobs do not survive process death.
        if (status == SpeechMessageStatus.Processing) {
            status = SpeechMessageStatus.Recorded
        }
        return SpeechQueueItem(
            id = id,
            audioFile = file,
            mimeType = obj.optString(KEY_MIME, AudioCompress.mimeFromName(file)),
            audioDurationSeconds = obj.optDouble(KEY_AUDIO_DURATION, 0.0).toFloat().coerceAtLeast(0f),
            status = status,
            text = obj.optString(KEY_TEXT),
            errorMessage = obj.optString(KEY_ERROR),
            createdAtMs = obj.optLong(KEY_CREATED_AT, System.currentTimeMillis()),
            recognitionStartedAtMs = 0L,
            recognitionElapsedMs = 0L,
            lastRecognitionDurationMs = obj.optLong(KEY_LAST_RECOGNITION_MS, 0L),
        )
    }

    private fun SpeechQueueItem.toJson(): JSONObject = JSONObject()
        .put(KEY_ID, id)
        .put(KEY_FILE, audioFile.name)
        .put(KEY_MIME, mimeType)
        .put(KEY_AUDIO_DURATION, audioDurationSeconds.toDouble())
        .put(
            KEY_STATUS,
            if (status == SpeechMessageStatus.Processing) {
                SpeechMessageStatus.Recorded.name
            } else {
                status.name
            },
        ).put(KEY_TEXT, text)
        .put(KEY_ERROR, errorMessage)
        .put(KEY_CREATED_AT, createdAtMs)
        .put(KEY_LAST_RECOGNITION_MS, lastRecognitionDurationMs)

    private companion object {
        const val ROOT_DIR = "speech_to_text"
        const val INDEX_FILENAME = "index.json"
        const val STATS_PREFS = "speech_to_text_stats"
        const val KEY_SUCCESS_COUNT = "success_count"
        const val KEY_SUCCESS_TOTAL_MS = "success_total_ms"
        const val KEY_ITEMS = "items"
        const val KEY_ID = "id"
        const val KEY_FILE = "file"
        const val KEY_MIME = "mime"
        const val KEY_AUDIO_DURATION = "audio_duration"
        const val KEY_STATUS = "status"
        const val KEY_TEXT = "text"
        const val KEY_ERROR = "error"
        const val KEY_CREATED_AT = "created_at"
        const val KEY_LAST_RECOGNITION_MS = "last_recognition_ms"
        const val MIN_VALID_FILE_BYTES = 44L
        const val LEGACY_PREFS = "speech_to_text_pending"
        const val LEGACY_WAV = "pending-speech.wav"
        const val LEGACY_M4A = "pending-speech.m4a"
        const val LEGACY_KEY_MIME = "mime_type"
        const val LEGACY_KEY_DURATION = "duration_seconds"
    }
}
