package dev.harrix.hsk.speechtotext

import java.io.File

enum class SpeechMessageStatus {
    Recorded,
    Processing,
    Done,
    Cancelled,
    Error,
}

data class SpeechQueueItem(
    val id: String,
    val audioFile: File,
    val mimeType: String,
    val audioDurationSeconds: Float,
    val status: SpeechMessageStatus,
    val text: String = "",
    val errorMessage: String = "",
    val createdAtMs: Long,
    val recognitionStartedAtMs: Long = 0L,
    val recognitionElapsedMs: Long = 0L,
    val lastRecognitionDurationMs: Long = 0L,
)
