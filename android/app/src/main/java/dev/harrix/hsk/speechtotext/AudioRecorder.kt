package dev.harrix.hsk.speechtotext

import android.content.Context
import android.media.MediaRecorder
import android.os.Build
import java.io.File
import java.util.UUID

class AudioRecorderException(
    message: String,
    cause: Throwable? = null,
) : Exception(message, cause)

/**
 * Records microphone audio to AAC/M4A (`audio/m4a`) for BotHub speech input.
 */
class AudioRecorder(
    private val context: Context,
) {
    private var mediaRecorder: MediaRecorder? = null
    private var outputFile: File? = null

    val isRecording: Boolean
        get() = mediaRecorder != null

    fun start(): File {
        if (mediaRecorder != null) {
            throw AudioRecorderException("Recording already in progress")
        }
        val file =
            File(
                context.cacheDir,
                "hsk-speech-${UUID.randomUUID()}.m4a",
            )
        val recorder = createMediaRecorder()
        val startError =
            runCatching {
                recorder.setAudioSource(MediaRecorder.AudioSource.MIC)
                recorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                recorder.setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
                recorder.setAudioEncodingBitRate(128_000)
                recorder.setAudioSamplingRate(44_100)
                recorder.setOutputFile(file.absolutePath)
                recorder.prepare()
                recorder.start()
            }.exceptionOrNull()
        if (startError != null) {
            recorder.release()
            file.delete()
            throw AudioRecorderException("Could not start recording", startError)
        }
        mediaRecorder = recorder
        outputFile = file
        return file
    }

    /**
     * Stops recording and returns the file with MIME type, or null if nothing was recorded.
     */
    fun stop(): Pair<File, String>? {
        val recorder = mediaRecorder ?: return null
        val file = outputFile
        mediaRecorder = null
        outputFile = null
        val stopError =
            runCatching {
                recorder.stop()
            }.exceptionOrNull()
        recorder.release()
        if (stopError != null) {
            file?.delete()
            throw AudioRecorderException("Could not stop recording", stopError)
        }
        if (file == null || !file.isFile || file.length() < MIN_AUDIO_BYTES) {
            file?.delete()
            throw AudioRecorderException("Recording is too short or empty")
        }
        return file to MIME_M4A
    }

    fun cancel() {
        val recorder = mediaRecorder
        mediaRecorder = null
        val file = outputFile
        outputFile = null
        if (recorder != null) {
            runCatching { recorder.stop() }
            recorder.release()
        }
        file?.delete()
    }

    private fun createMediaRecorder(): MediaRecorder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        MediaRecorder(context)
    } else {
        @Suppress("DEPRECATION")
        MediaRecorder()
    }

    companion object {
        const val MIME_M4A = "audio/m4a"
        const val MIN_AUDIO_BYTES = 512
    }
}
