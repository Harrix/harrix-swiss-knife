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
    private val pendingFile = File(pendingDir, PENDING_FILENAME)

    @Synchronized
    fun load(): PendingSpeechRecording? {
        if (!pendingFile.isFile || pendingFile.length() <= MIN_VALID_FILE_BYTES) {
            clear()
            return null
        }
        return PendingSpeechRecording(
            file = pendingFile,
            mimeType = prefs.getString(KEY_MIME_TYPE, null) ?: AudioRecorder.MIME_WAV,
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

        if (source.absolutePath != pendingFile.absolutePath) {
            val temporary = File(pendingDir, "$PENDING_FILENAME.tmp")
            temporary.delete()
            source.copyTo(temporary, overwrite = true)
            check(temporary.length() > MIN_VALID_FILE_BYTES) {
                "Could not preserve pending recording"
            }
            if (pendingFile.exists() && !pendingFile.delete()) {
                temporary.delete()
                error("Could not replace pending recording")
            }
            if (!temporary.renameTo(pendingFile)) {
                temporary.copyTo(pendingFile, overwrite = true)
                temporary.delete()
            }
        }

        check(pendingFile.isFile && pendingFile.length() > MIN_VALID_FILE_BYTES) {
            "Could not preserve pending recording"
        }
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
            file = pendingFile,
            mimeType = mimeType,
            durationSeconds = durationSeconds.coerceAtLeast(0f),
        )
    }

    @Synchronized
    fun clear() {
        pendingFile.delete()
        File(pendingDir, "$PENDING_FILENAME.tmp").delete()
        prefs.edit().clear().commit()
        pendingDir.delete()
    }

    private companion object {
        const val PREFS_NAME = "speech_to_text_pending"
        const val PENDING_DIR = "speech_to_text"
        const val PENDING_FILENAME = "pending-speech.wav"
        const val KEY_MIME_TYPE = "mime_type"
        const val KEY_DURATION_SECONDS = "duration_seconds"
        const val MIN_VALID_FILE_BYTES = 44L
    }
}
