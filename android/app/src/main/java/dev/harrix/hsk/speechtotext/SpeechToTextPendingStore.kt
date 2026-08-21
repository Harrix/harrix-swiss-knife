package dev.harrix.hsk.speechtotext

import android.content.Context
import java.io.File

/** A durable audio recording waiting to be sent to the AI service. */
data class PendingSpeechRecording(
    val file: File,
    val mimeType: String,
    val durationSeconds: Float,
)

/**
 * Stores the latest not-yet-successfully-processed speech recording.
 *
 * The audio lives in [Context.getFilesDir], not the evictable cache directory, so it survives
 * process restarts and cache cleanup.
 */
class SpeechToTextPendingStore(
    context: Context,
) {
    private val appContext = context.applicationContext
    private val prefs = appContext.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val pendingDir = File(appContext.filesDir, PENDING_DIR)
    private val pendingWav = File(pendingDir, PENDING_FILENAME_WAV)
    private val pendingM4a = File(pendingDir, PENDING_FILENAME_M4A)

    @Synchronized
    fun load(): PendingSpeechRecording? {
        val storedMime = prefs.getString(KEY_MIME_TYPE, null)
        val file = resolveExistingFile(storedMime)
        if (file == null) {
            clear()
            return null
        }
        return PendingSpeechRecording(
            file = file,
            mimeType = storedMime ?: AudioCompress.mimeFromName(file),
            durationSeconds = prefs.getFloat(KEY_DURATION_SECONDS, 0f).coerceAtLeast(0f),
        )
    }

    @Synchronized
    fun save(
        source: File,
        mimeType: String,
        durationSeconds: Float,
    ): PendingSpeechRecording {
        require(source.isFile) { "Recording file missing" }
        pendingDir.mkdirs()
        require(pendingDir.isDirectory) { "Could not create pending recording folder" }

        val destination = pendingFileForMime(mimeType)
        if (source.absolutePath != destination.absolutePath) {
            val temporary = File(pendingDir, "${destination.name}.tmp")
            temporary.delete()
            source.copyTo(temporary, overwrite = true)
            check(temporary.length() > MIN_VALID_FILE_BYTES) {
                "Could not preserve pending recording"
            }
            if (destination.exists() && !destination.delete()) {
                temporary.delete()
                error("Could not replace pending recording")
            }
            if (!temporary.renameTo(destination)) {
                temporary.copyTo(destination, overwrite = true)
                temporary.delete()
            }
        }

        check(destination.isFile && destination.length() > MIN_VALID_FILE_BYTES) {
            "Could not preserve pending recording"
        }
        deleteOtherPending(destination)
        check(
            prefs
                .edit()
                .putString(KEY_MIME_TYPE, mimeType)
                .putFloat(KEY_DURATION_SECONDS, durationSeconds.coerceAtLeast(0f))
                .commit(),
        ) {
            "Could not save pending recording metadata"
        }
        return PendingSpeechRecording(
            file = destination,
            mimeType = mimeType,
            durationSeconds = durationSeconds.coerceAtLeast(0f),
        )
    }

    @Synchronized
    fun clear() {
        pendingWav.delete()
        pendingM4a.delete()
        File(pendingDir, "$PENDING_FILENAME_WAV.tmp").delete()
        File(pendingDir, "$PENDING_FILENAME_M4A.tmp").delete()
        prefs.edit().clear().commit()
        pendingDir.delete()
    }

    private fun resolveExistingFile(storedMime: String?): File? {
        val preferred = storedMime?.let { pendingFileForMime(it) }
        if (preferred != null && preferred.isFile && preferred.length() > MIN_VALID_FILE_BYTES) {
            return preferred
        }
        return listOf(pendingM4a, pendingWav).firstOrNull {
            it.isFile && it.length() > MIN_VALID_FILE_BYTES
        }
    }

    private fun pendingFileForMime(mimeType: String): File {
        val mime = mimeType.lowercase()
        return if ("m4a" in mime || "mp4" in mime || "aac" in mime) {
            pendingM4a
        } else {
            pendingWav
        }
    }

    private fun deleteOtherPending(keep: File) {
        listOf(pendingWav, pendingM4a)
            .filter { it.absolutePath != keep.absolutePath }
            .forEach { it.delete() }
    }

    private companion object {
        const val PREFS_NAME = "speech_to_text_pending"
        const val PENDING_DIR = "speech_to_text"
        const val PENDING_FILENAME_WAV = "pending-speech.wav"
        const val PENDING_FILENAME_M4A = "pending-speech.m4a"
        const val KEY_MIME_TYPE = "mime_type"
        const val KEY_DURATION_SECONDS = "duration_seconds"
        const val MIN_VALID_FILE_BYTES = 44L
    }
}
