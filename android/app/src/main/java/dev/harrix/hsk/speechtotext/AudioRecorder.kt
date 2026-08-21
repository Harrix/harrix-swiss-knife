package dev.harrix.hsk.speechtotext

import android.annotation.SuppressLint
import android.content.Context
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import java.io.File
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.UUID
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.math.max
import kotlin.math.min

class AudioRecorderException(
    message: String,
    cause: Throwable? = null,
) : Exception(message, cause)

data class WaveformBucket(
    val peakNeg: Float,
    val peakPos: Float,
)

/**
 * Records microphone audio to mono 16-bit WAV for waveform and continue-recording.
 * Upload compression to AAC/M4A happens in [AudioCompress] (desktop Speech to Text parity).
 */
class AudioRecorder(
    private val context: Context,
) {
    private var audioRecord: AudioRecord? = null
    private var outputFile: File? = null
    private var writeThread: Thread? = null
    private val recording = AtomicBoolean(false)
    private var pcmDataBytes: Long = 0L
    private var basePcmDataBytes: Long = 0L
    private var onEnvelope: ((WaveformBucket) -> Unit)? = null

    val isRecording: Boolean
        get() = recording.get()

    val recordedFile: File?
        get() = outputFile?.takeIf { it.isFile }

    fun setEnvelopeListener(listener: ((WaveformBucket) -> Unit)?) {
        onEnvelope = listener
    }

    fun durationSeconds(): Float {
        val bytes = if (recording.get()) pcmDataBytes else (outputFile?.let { wavDataSize(it) } ?: 0L)
        return bytes.toFloat() / BYTES_PER_SECOND
    }

    fun canContinue(): Boolean {
        val file = outputFile
        return !recording.get() &&
            file != null &&
            file.isFile &&
            file.length() > WAV_HEADER_SIZE + MIN_AUDIO_BYTES
    }

    @SuppressLint("MissingPermission")
    fun start(appendTo: File? = null): File {
        if (recording.get()) {
            throw AudioRecorderException("Recording already in progress")
        }
        val recorder = createAudioRecord()
        val prepared = prepareOutputFile(appendTo)
        outputFile = prepared.file

        recording.set(true)
        audioRecord = recorder
        recorder.startRecording()
        writeThread =
            Thread(
                {
                    writeLoop(recorder, prepared.file, prepared.startDataOffset)
                },
                "hsk-audio-record",
            ).also { it.start() }
        return prepared.file
    }

    @SuppressLint("MissingPermission")
    private fun createAudioRecord(): AudioRecord {
        val minBuf =
            AudioRecord.getMinBufferSize(SAMPLE_RATE, CHANNEL_CONFIG, ENCODING)
        if (minBuf <= 0) {
            throw AudioRecorderException("Could not initialize microphone")
        }
        // Keep the hardware buffer modest so read() returns often (~50 FPS waveform).
        val recorderBufferBytes = max(minBuf, READ_SAMPLES * BYTES_PER_SAMPLE) * 2
        val recorder =
            AudioRecord(
                MediaRecorder.AudioSource.MIC,
                SAMPLE_RATE,
                CHANNEL_CONFIG,
                ENCODING,
                recorderBufferBytes,
            )
        if (recorder.state != AudioRecord.STATE_INITIALIZED) {
            recorder.release()
            throw AudioRecorderException("Could not initialize microphone")
        }
        return recorder
    }

    private data class PreparedOutput(
        val file: File,
        val startDataOffset: Long,
    )

    private fun prepareOutputFile(appendTo: File?): PreparedOutput {
        if (appendTo != null && appendTo.isFile && appendTo.length() > WAV_HEADER_SIZE) {
            basePcmDataBytes = wavDataSize(appendTo)
            pcmDataBytes = basePcmDataBytes
            return PreparedOutput(file = appendTo, startDataOffset = appendTo.length())
        }
        val file =
            File(
                context.cacheDir,
                "hsk-speech-${UUID.randomUUID()}.wav",
            )
        writeWavHeader(file, dataSize = 0)
        basePcmDataBytes = 0L
        pcmDataBytes = 0L
        outputFile?.takeIf { it != file }?.delete()
        return PreparedOutput(file = file, startDataOffset = WAV_HEADER_SIZE.toLong())
    }

    /**
     * Stops recording and returns the WAV file with MIME type.
     */
    fun stop(): Pair<File, String> {
        if (!recording.getAndSet(false)) {
            return existingRecordingOrThrow()
        }
        releaseCapture()
        val file =
            outputFile
                ?: throw AudioRecorderException("Recording file missing")
        finalizeWavHeader(file, pcmDataBytes)
        if (file.length() < WAV_HEADER_SIZE + MIN_AUDIO_BYTES) {
            file.delete()
            outputFile = null
            pcmDataBytes = 0L
            throw AudioRecorderException("Recording is too short or empty")
        }
        return file to MIME_WAV
    }

    fun cancel() {
        recording.set(false)
        releaseCapture()
        outputFile?.delete()
        outputFile = null
        pcmDataBytes = 0L
        basePcmDataBytes = 0L
    }

    fun clear() {
        if (recording.get()) {
            cancel()
            return
        }
        outputFile?.delete()
        outputFile = null
        pcmDataBytes = 0L
        basePcmDataBytes = 0L
    }

    private fun existingRecordingOrThrow(): Pair<File, String> {
        val existing = outputFile
        if (existing != null && existing.isFile && existing.length() > WAV_HEADER_SIZE + MIN_AUDIO_BYTES) {
            return existing to MIME_WAV
        }
        throw AudioRecorderException("Not recording")
    }

    private fun releaseCapture() {
        val recorder = audioRecord
        audioRecord = null
        // Stop first so the write thread can leave read(); release only after join.
        // Releasing while read() is still running can block join() for the full timeout.
        runCatching { recorder?.stop() }
        writeThread?.join(2_000)
        writeThread = null
        runCatching { recorder?.release() }
    }

    private fun writeLoop(
        recorder: AudioRecord,
        file: File,
        startOffset: Long,
    ) {
        // Small reads so envelopes fire at ~WAVEFORM_FPS like the desktop action.
        val buffer = ShortArray(READ_SAMPLES)
        val envelope = EnvelopeAccumulator()
        try {
            RandomAccessFile(file, "rw").use { raf ->
                writePcmFrames(raf, recorder, buffer, startOffset, envelope)
            }
        } catch (_: Exception) {
            recording.set(false)
        }
    }

    private fun writePcmFrames(
        raf: RandomAccessFile,
        recorder: AudioRecord,
        buffer: ShortArray,
        startOffset: Long,
        envelope: EnvelopeAccumulator,
    ) {
        var fileOffset = startOffset
        raf.seek(fileOffset)
        while (recording.get()) {
            val read = recorder.read(buffer, 0, buffer.size)
            if (read <= 0) {
                continue
            }
            val bytes = encodePcmChunk(buffer, read, envelope)
            raf.write(bytes)
            fileOffset += bytes.size
            pcmDataBytes = basePcmDataBytes + (fileOffset - startOffset)
        }
        envelope.flush(::emitEnvelope)
    }

    private fun encodePcmChunk(
        buffer: ShortArray,
        read: Int,
        envelope: EnvelopeAccumulator,
    ): ByteArray {
        val bytes = ByteArray(read * 2)
        val bb = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN)
        for (i in 0 until read) {
            val sample = buffer[i].toInt()
            bb.putShort(sample.toShort())
            envelope.accept(sample, ::emitEnvelope)
        }
        return bytes
    }

    private fun emitEnvelope(
        peakNeg: Int,
        peakPos: Int,
    ) {
        val gain = LEVEL_GAIN
        val neg = ((peakNeg / 32768f) * gain).coerceIn(-1f, 0f)
        val pos = ((peakPos / 32768f) * gain).coerceIn(0f, 1f)
        onEnvelope?.invoke(WaveformBucket(neg, pos))
    }

    private class EnvelopeAccumulator {
        private var samples = 0
        private var peakNeg = 0
        private var peakPos = 0

        fun accept(
            sample: Int,
            emit: (Int, Int) -> Unit,
        ) {
            peakNeg = min(peakNeg, sample)
            peakPos = max(peakPos, sample)
            samples++
            if (samples >= ENVELOPE_SAMPLES) {
                emit(peakNeg, peakPos)
                samples = 0
                peakNeg = 0
                peakPos = 0
            }
        }

        fun flush(emit: (Int, Int) -> Unit) {
            if (samples > 0) {
                emit(peakNeg, peakPos)
                samples = 0
                peakNeg = 0
                peakPos = 0
            }
        }
    }

    companion object {
        const val MIME_WAV = "audio/wav"
        const val MIME_M4A = "audio/m4a"
        const val MIN_AUDIO_BYTES = 512
        const val SAMPLE_RATE = 44_100
        const val LIVE_BUCKET_COUNT = 120

        /** Target live waveform updates per second (desktop action is similarly snappy). */
        const val WAVEFORM_FPS = 50
        private const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
        private const val ENCODING = AudioFormat.ENCODING_PCM_16BIT
        private const val WAV_HEADER_SIZE = 44
        private const val BYTES_PER_SAMPLE = 2
        private const val BYTES_PER_SECOND = SAMPLE_RATE * BYTES_PER_SAMPLE
        private const val READ_SAMPLES = SAMPLE_RATE / WAVEFORM_FPS
        private const val ENVELOPE_SAMPLES = READ_SAMPLES
        private const val LEVEL_GAIN = 2f

        fun formatDuration(totalSeconds: Float): String {
            val total = max(0, totalSeconds.toInt())
            val minutes = total / 60
            val seconds = total % 60
            return "%d:%02d".format(minutes, seconds)
        }

        private fun writeWavHeader(
            file: File,
            dataSize: Long,
        ) {
            RandomAccessFile(file, "rw").use { raf ->
                raf.setLength(0)
                raf.write(buildWavHeader(dataSize))
            }
        }

        private fun finalizeWavHeader(
            file: File,
            dataSize: Long,
        ) {
            RandomAccessFile(file, "rw").use { raf ->
                raf.seek(0)
                raf.write(buildWavHeader(dataSize))
            }
        }

        private fun wavDataSize(file: File): Long = max(0L, file.length() - WAV_HEADER_SIZE)

        private fun buildWavHeader(dataSize: Long): ByteArray {
            val data = dataSize.coerceAtLeast(0L)
            val buffer = ByteBuffer.allocate(WAV_HEADER_SIZE).order(ByteOrder.LITTLE_ENDIAN)
            buffer.put("RIFF".toByteArray(Charsets.US_ASCII))
            buffer.putInt((36 + data).toInt())
            buffer.put("WAVE".toByteArray(Charsets.US_ASCII))
            buffer.put("fmt ".toByteArray(Charsets.US_ASCII))
            buffer.putInt(16)
            buffer.putShort(1) // PCM
            buffer.putShort(1) // mono
            buffer.putInt(SAMPLE_RATE)
            buffer.putInt(SAMPLE_RATE * 2) // byte rate
            buffer.putShort(2) // block align
            buffer.putShort(16) // bits
            buffer.put("data".toByteArray(Charsets.US_ASCII))
            buffer.putInt(data.toInt())
            return buffer.array()
        }
    }
}
