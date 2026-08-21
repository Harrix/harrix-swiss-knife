package dev.harrix.hsk.speechtotext

import android.media.MediaCodec
import android.media.MediaCodecInfo
import android.media.MediaFormat
import android.media.MediaMuxer
import android.os.SystemClock
import java.io.File
import java.io.IOException
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt

data class SpeechUploadAudio(
    val file: File,
    val mimeType: String,
    val temporary: Boolean = false,
)

/**
 * Compresses speech WAV to AAC/M4A before upload (desktop `wav_to_m4a` parity).
 */
object AudioCompress {
    const val TARGET_SAMPLE_RATE = 16_000
    const val BIT_RATE = 64_000

    fun prepareForUpload(
        source: File,
        mimeType: String = AudioRecorder.MIME_WAV,
    ): SpeechUploadAudio {
        if (!source.isFile) {
            throw IOException("Recording file missing")
        }
        if (!isWav(source, mimeType)) {
            return SpeechUploadAudio(
                file = source,
                mimeType = mimeType.ifBlank { mimeFromName(source) },
            )
        }
        val destination = File(source.parentFile, "${source.nameWithoutExtension}.m4a")
        return try {
            encodeWavToM4a(source, destination)
            if (!destination.isFile || destination.length() < AudioRecorder.MIN_AUDIO_BYTES) {
                destination.delete()
                SpeechUploadAudio(source, AudioRecorder.MIME_WAV)
            } else {
                SpeechUploadAudio(
                    file = destination,
                    mimeType = AudioRecorder.MIME_M4A,
                    temporary = destination.absolutePath != source.absolutePath,
                )
            }
        } catch (_: Exception) {
            destination.delete()
            SpeechUploadAudio(source, AudioRecorder.MIME_WAV)
        }
    }

    fun mimeFromName(file: File): String {
        val name = file.name.lowercase()
        return when {
            name.endsWith(".m4a") || name.endsWith(".mp4") || name.endsWith(".aac") -> AudioRecorder.MIME_M4A
            name.endsWith(".mp3") -> "audio/mpeg"
            name.endsWith(".ogg") -> "audio/ogg"
            name.endsWith(".webm") -> "audio/webm"
            else -> AudioRecorder.MIME_WAV
        }
    }

    private fun isWav(
        source: File,
        mimeType: String,
    ): Boolean {
        val mime = mimeType.lowercase()
        return mime.contains("wav") ||
            (mime.isBlank() && source.name.lowercase().endsWith(".wav"))
    }

    private fun encodeWavToM4a(
        wavFile: File,
        output: File,
    ) {
        val wav = readPcmWav(wavFile)
        val pcm =
            if (wav.sampleRate == TARGET_SAMPLE_RATE) {
                wav.pcm
            } else {
                resampleMono16(wav.pcm, wav.sampleRate, TARGET_SAMPLE_RATE)
            }
        if (pcm.size < AudioRecorder.MIN_AUDIO_BYTES) {
            throw IOException("Recording is too short or empty")
        }
        output.parentFile?.mkdirs()
        if (output.exists() && !output.delete()) {
            throw IOException("Could not replace compressed audio")
        }
        encodeAacM4a(pcm, TARGET_SAMPLE_RATE, output)
    }

    private fun encodeAacM4a(
        pcm: ByteArray,
        sampleRate: Int,
        output: File,
    ) {
        val format =
            MediaFormat.createAudioFormat(MediaFormat.MIMETYPE_AUDIO_AAC, sampleRate, 1).apply {
                setInteger(MediaFormat.KEY_AAC_PROFILE, MediaCodecInfo.CodecProfileLevel.AACObjectLC)
                setInteger(MediaFormat.KEY_BIT_RATE, BIT_RATE)
                setInteger(MediaFormat.KEY_MAX_INPUT_SIZE, AAC_MAX_INPUT_BYTES)
            }
        val codec = MediaCodec.createEncoderByType(MediaFormat.MIMETYPE_AUDIO_AAC)
        val muxer = MediaMuxer(output.absolutePath, MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4)
        try {
            codec.configure(format, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE)
            codec.start()
            if (!runEncoder(codec, muxer, pcm, sampleRate)) {
                throw IOException("AAC encoder produced no output")
            }
        } finally {
            runCatching { codec.stop() }
            codec.release()
            runCatching { muxer.stop() }
            muxer.release()
        }
        if (!output.isFile || output.length() < AudioRecorder.MIN_AUDIO_BYTES) {
            output.delete()
            throw IOException("Compressed audio is empty")
        }
    }

    private class EncodeState {
        var offset = 0
        var inputEos = false
        var outputEos = false
        var trackIndex = -1
        var muxerStarted = false
        var totalSamples = 0L
        val info = MediaCodec.BufferInfo()
    }

    private fun runEncoder(
        codec: MediaCodec,
        muxer: MediaMuxer,
        pcm: ByteArray,
        sampleRate: Int,
    ): Boolean {
        val state = EncodeState()
        val deadlineMs =
            SystemClock.elapsedRealtime() +
                ENCODE_TIMEOUT_BASE_MS +
                (pcm.size / 2L) * 1000L / sampleRate
        while (!state.outputEos) {
            if (SystemClock.elapsedRealtime() > deadlineMs) {
                throw IOException("AAC encode timed out")
            }
            feedEncoderInput(codec, pcm, sampleRate, state)
            drainEncoderOutput(codec, muxer, state)
        }
        return state.muxerStarted
    }

    private fun feedEncoderInput(
        codec: MediaCodec,
        pcm: ByteArray,
        sampleRate: Int,
        state: EncodeState,
    ) {
        if (state.inputEos) {
            return
        }
        val inIndex = codec.dequeueInputBuffer(DEQUEUE_TIMEOUT_US)
        if (inIndex < 0) {
            return
        }
        val queued = queuePcmInput(codec, inIndex, pcm, state.offset, sampleRate, state.totalSamples)
        if (queued < 0) {
            state.inputEos = true
            return
        }
        state.totalSamples += queued
        state.offset += queued * BYTES_PER_SAMPLE
    }

    private fun drainEncoderOutput(
        codec: MediaCodec,
        muxer: MediaMuxer,
        state: EncodeState,
    ) {
        val outIndex = codec.dequeueOutputBuffer(state.info, DEQUEUE_TIMEOUT_US)
        when {
            outIndex == MediaCodec.INFO_OUTPUT_FORMAT_CHANGED -> {
                state.trackIndex = muxer.addTrack(codec.outputFormat)
                muxer.start()
                state.muxerStarted = true
            }

            outIndex >= 0 -> {
                writeEncodedSample(codec, muxer, outIndex, state.info, state.trackIndex, state.muxerStarted)
                if (state.info.flags and MediaCodec.BUFFER_FLAG_END_OF_STREAM != 0) {
                    state.outputEos = true
                }
            }
        }
    }

    /**
     * @return sample count submitted, or `-1` when EOS was queued
     */
    private fun queuePcmInput(
        codec: MediaCodec,
        index: Int,
        pcm: ByteArray,
        offset: Int,
        sampleRate: Int,
        totalSamples: Long,
    ): Int {
        val buffer =
            codec.getInputBuffer(index)
                ?: throw IOException("AAC encoder input buffer missing")
        buffer.clear()
        val remaining = pcm.size - offset
        if (remaining <= 0) {
            codec.queueInputBuffer(index, 0, 0, 0, MediaCodec.BUFFER_FLAG_END_OF_STREAM)
            return -1
        }
        val toCopy = min(buffer.remaining(), remaining) and 1.inv()
        if (toCopy <= 0) {
            codec.queueInputBuffer(index, 0, 0, 0, MediaCodec.BUFFER_FLAG_END_OF_STREAM)
            return -1
        }
        buffer.put(pcm, offset, toCopy)
        val ptsUs = totalSamples * MICROS_PER_SECOND / sampleRate
        codec.queueInputBuffer(index, 0, toCopy, ptsUs, 0)
        return toCopy / BYTES_PER_SAMPLE
    }

    private fun writeEncodedSample(
        codec: MediaCodec,
        muxer: MediaMuxer,
        index: Int,
        info: MediaCodec.BufferInfo,
        trackIndex: Int,
        muxerStarted: Boolean,
    ) {
        val outBuf = codec.getOutputBuffer(index)
        if (outBuf != null && shouldWriteEncodedSample(info, muxerStarted)) {
            outBuf.position(info.offset)
            outBuf.limit(info.offset + info.size)
            muxer.writeSampleData(trackIndex, outBuf, info)
        }
        codec.releaseOutputBuffer(index, false)
    }

    private fun shouldWriteEncodedSample(
        info: MediaCodec.BufferInfo,
        muxerStarted: Boolean,
    ): Boolean {
        if (info.size <= 0 || !muxerStarted) {
            return false
        }
        return info.flags and MediaCodec.BUFFER_FLAG_CODEC_CONFIG == 0
    }

    private class PcmWav(
        val pcm: ByteArray,
        val sampleRate: Int,
    )

    private class WavLayout(
        val sampleRate: Int,
        val channels: Int,
        val bits: Int,
        val dataOffset: Long,
        val dataSize: Int,
    )

    private fun readPcmWav(file: File): PcmWav {
        RandomAccessFile(file, "r").use { raf ->
            requireRiffWave(raf)
            val layout = readWavLayout(raf)
            requirePcm16(layout)
            raf.seek(layout.dataOffset)
            val raw = ByteArray(layout.dataSize)
            raf.readFully(raw)
            val pcm = if (layout.channels <= 1) raw else downmixToMono16(raw, layout.channels)
            return PcmWav(pcm = pcm, sampleRate = max(1, layout.sampleRate))
        }
    }

    private fun requireRiffWave(raf: RandomAccessFile) {
        if (raf.length() < WAV_HEADER_MIN) {
            throw IOException("WAV file is too short")
        }
        val header = ByteArray(12)
        raf.readFully(header)
        val riff = ByteBuffer.wrap(header).order(ByteOrder.LITTLE_ENDIAN)
        if (riff.ascii(0, 4) != "RIFF" || riff.ascii(8, 4) != "WAVE") {
            throw IOException("Not a WAV file")
        }
    }

    private fun requirePcm16(layout: WavLayout) {
        if (layout.dataOffset < 0 || layout.dataSize < AudioRecorder.MIN_AUDIO_BYTES) {
            throw IOException("WAV data chunk missing")
        }
        if (layout.bits != 16) {
            throw IOException("Unsupported WAV sample width")
        }
    }

    private fun readWavLayout(raf: RandomAccessFile): WavLayout {
        var sampleRate = AudioRecorder.SAMPLE_RATE
        var channels = 1
        var bits = 16
        var dataOffset = -1L
        var dataSize = 0
        while (raf.filePointer + 8 <= raf.length()) {
            val chunkHeader = ByteArray(8)
            raf.readFully(chunkHeader)
            val chunk = ByteBuffer.wrap(chunkHeader).order(ByteOrder.LITTLE_ENDIAN)
            val chunkId = chunk.ascii(0, 4)
            val chunkSize = chunk.intAt(4).toLong() and 0xFFFF_FFFFL
            val next = raf.filePointer + chunkSize + (chunkSize and 1)
            when (chunkId) {
                "fmt " -> {
                    val fmt = readFmtChunk(raf, chunkSize)
                    channels = fmt.channels
                    sampleRate = fmt.sampleRate
                    bits = fmt.bits
                }

                "data" -> {
                    dataOffset = raf.filePointer
                    dataSize = min(chunkSize, raf.length() - dataOffset).toInt()
                    break
                }
            }
            raf.seek(min(next, raf.length()))
        }
        return WavLayout(
            sampleRate = sampleRate,
            channels = channels,
            bits = bits,
            dataOffset = dataOffset,
            dataSize = dataSize,
        )
    }

    private class WavFmt(
        val sampleRate: Int,
        val channels: Int,
        val bits: Int,
    )

    private fun readFmtChunk(
        raf: RandomAccessFile,
        chunkSize: Long,
    ): WavFmt {
        val fmt = ByteArray(min(chunkSize, 16).toInt())
        raf.readFully(fmt)
        val fmtBuf = ByteBuffer.wrap(fmt).order(ByteOrder.LITTLE_ENDIAN)
        val audioFormat = fmtBuf.shortAt(0).toInt() and 0xFFFF
        if (audioFormat != 1) {
            throw IOException("Unsupported WAV encoding")
        }
        return WavFmt(
            sampleRate = fmtBuf.intAt(4),
            channels = fmtBuf.shortAt(2).toInt() and 0xFFFF,
            bits = fmtBuf.shortAt(14).toInt() and 0xFFFF,
        )
    }

    private fun downmixToMono16(
        interleaved: ByteArray,
        channels: Int,
    ): ByteArray {
        val frameBytes = channels * BYTES_PER_SAMPLE
        val frames = interleaved.size / frameBytes
        val mono = ByteArray(frames * BYTES_PER_SAMPLE)
        val src = ByteBuffer.wrap(interleaved).order(ByteOrder.LITTLE_ENDIAN)
        val dst = ByteBuffer.wrap(mono).order(ByteOrder.LITTLE_ENDIAN)
        repeat(frames) {
            var sum = 0
            repeat(channels) { sum += src.short.toInt() }
            dst.putShort((sum / channels).toShort())
        }
        return mono
    }

    private fun resampleMono16(
        pcm: ByteArray,
        fromRate: Int,
        toRate: Int,
    ): ByteArray {
        if (fromRate <= 0 || toRate <= 0 || fromRate == toRate) {
            return pcm
        }
        val srcSamples = pcm.size / BYTES_PER_SAMPLE
        if (srcSamples <= 1) {
            return pcm
        }
        val dstSamples = max(1, (srcSamples.toLong() * toRate / fromRate).toInt())
        val src = ShortArray(srcSamples)
        ByteBuffer.wrap(pcm).order(ByteOrder.LITTLE_ENDIAN).asShortBuffer().get(src)
        val dst = ByteArray(dstSamples * BYTES_PER_SAMPLE)
        val out = ByteBuffer.wrap(dst).order(ByteOrder.LITTLE_ENDIAN)
        val step = fromRate.toDouble() / toRate
        for (i in 0 until dstSamples) {
            val position = i * step
            val i0 = position.toInt().coerceIn(0, src.lastIndex)
            val i1 = min(i0 + 1, src.lastIndex)
            val frac = position - i0
            val sample = src[i0] * (1.0 - frac) + src[i1] * frac
            out.putShort(sample.roundToInt().coerceIn(Short.MIN_VALUE.toInt(), Short.MAX_VALUE.toInt()).toShort())
        }
        return dst
    }

    private fun ByteBuffer.ascii(
        offset: Int,
        length: Int,
    ): String = String(this.array(), offset, length, Charsets.US_ASCII)

    private fun ByteBuffer.intAt(offset: Int): Int = this.order(ByteOrder.LITTLE_ENDIAN).getInt(offset)

    private fun ByteBuffer.shortAt(offset: Int): Short = this.order(ByteOrder.LITTLE_ENDIAN).getShort(offset)

    private const val BYTES_PER_SAMPLE = 2
    private const val AAC_MAX_INPUT_BYTES = 16_384
    private const val DEQUEUE_TIMEOUT_US = 50_000L
    private const val ENCODE_TIMEOUT_BASE_MS = 30_000L
    private const val MICROS_PER_SECOND = 1_000_000L
    private const val WAV_HEADER_MIN = 44L
}
