package dev.harrix.hsk.ui.speechtotext

import android.app.Application
import android.os.Handler
import android.os.Looper
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import dev.harrix.hsk.bothub.BothubConfig
import dev.harrix.hsk.speechtotext.AudioRecorder
import dev.harrix.hsk.speechtotext.AudioRecorderException
import dev.harrix.hsk.speechtotext.SpeechToTextRepository
import dev.harrix.hsk.speechtotext.WaveformBucket
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

enum class SpeechToTextPhase {
    Idle,
    Recording,
    Recorded,
    Recognizing,
    Fixing,
    Result,
    Rewriting,
}

class SpeechToTextViewModel(
    application: Application,
) : AndroidViewModel(application) {
    private val audioRecorder = AudioRecorder(application.applicationContext)
    private val repository = SpeechToTextRepository(application.applicationContext)
    private val mainHandler = Handler(Looper.getMainLooper())

    val phase = mutableStateOf(SpeechToTextPhase.Idle)
    val resultText = mutableStateOf("")
    val errorMessage = mutableStateOf<String?>(null)
    val infoMessage = mutableStateOf<String?>(null)
    val hasApiKey = mutableStateOf(BothubConfig.hasApiKey)
    val recordingDurationSeconds = mutableFloatStateOf(0f)
    val waveformBuckets = mutableStateListOf<WaveformBucket>()

    private var recordedFile: File? = null
    private var recordedMime: String = AudioRecorder.MIME_WAV
    private var workJob: Job? = null
    private var durationJob: Job? = null
    private val pendingEnvelopes = ArrayDeque<WaveformBucket>()
    private var envelopeFlushPosted = false

    init {
        audioRecorder.setEnvelopeListener { bucket ->
            synchronized(pendingEnvelopes) {
                pendingEnvelopes.addLast(bucket)
                if (envelopeFlushPosted) {
                    return@setEnvelopeListener
                }
                envelopeFlushPosted = true
            }
            mainHandler.post {
                val batch =
                    synchronized(pendingEnvelopes) {
                        envelopeFlushPosted = false
                        if (pendingEnvelopes.isEmpty()) {
                            return@post
                        }
                        ArrayList<WaveformBucket>(pendingEnvelopes.size).also { out ->
                            while (pendingEnvelopes.isNotEmpty()) {
                                out.add(pendingEnvelopes.removeFirst())
                            }
                        }
                    }
                if (phase.value != SpeechToTextPhase.Recording || batch.isEmpty()) {
                    return@post
                }
                waveformBuckets.addAll(batch)
            }
        }
    }

    fun clearError() {
        errorMessage.value = null
    }

    fun clearInfo() {
        infoMessage.value = null
    }

    fun startRecording(append: Boolean = false) {
        if (phase.value == SpeechToTextPhase.Recording || isBusyNetwork()) {
            return
        }
        errorMessage.value = null
        infoMessage.value = null
        try {
            val appendFile = if (append) recordedFile else null
            if (!append) {
                recordedFile?.delete()
                recordedFile = null
                waveformBuckets.clear()
                resultText.value = ""
            }
            recordedFile = audioRecorder.start(appendTo = appendFile)
            phase.value = SpeechToTextPhase.Recording
            startDurationTicker()
        } catch (e: AudioRecorderException) {
            errorMessage.value = e.message
            phase.value =
                if (recordedFile != null) {
                    SpeechToTextPhase.Recorded
                } else {
                    SpeechToTextPhase.Idle
                }
            stopDurationTicker()
        }
    }

    fun stopRecording() {
        if (phase.value != SpeechToTextPhase.Recording) {
            return
        }
        stopDurationTicker()
        val stopped =
            try {
                audioRecorder.stop()
            } catch (e: AudioRecorderException) {
                errorMessage.value = e.message
                phase.value =
                    when {
                        recordedFile != null -> SpeechToTextPhase.Recorded
                        resultText.value.isBlank() -> SpeechToTextPhase.Idle
                        else -> SpeechToTextPhase.Result
                    }
                return
            }
        recordedFile = stopped.first
        recordedMime = stopped.second
        recordingDurationSeconds.floatValue = audioRecorder.durationSeconds()
        phase.value = SpeechToTextPhase.Recorded
    }

    fun continueRecording() {
        if (phase.value != SpeechToTextPhase.Recorded || !audioRecorder.canContinue()) {
            return
        }
        startRecording(append = true)
    }

    fun rerecord() {
        if (isBusyNetwork()) {
            return
        }
        audioRecorder.clear()
        recordedFile = null
        waveformBuckets.clear()
        recordingDurationSeconds.floatValue = 0f
        resultText.value = ""
        errorMessage.value = null
        infoMessage.value = null
        startRecording(append = false)
    }

    fun recognizeRecording() {
        if (phase.value != SpeechToTextPhase.Recorded) {
            return
        }
        val file = recordedFile
        if (file == null || !file.isFile) {
            errorMessage.value = "Recording file missing"
            phase.value = SpeechToTextPhase.Idle
            return
        }
        processRecording(file, recordedMime)
    }

    fun cancelRecording() {
        if (phase.value != SpeechToTextPhase.Recording) {
            return
        }
        stopDurationTicker()
        audioRecorder.cancel()
        recordedFile = null
        waveformBuckets.clear()
        recordingDurationSeconds.floatValue = 0f
        phase.value =
            if (resultText.value.isBlank()) {
                SpeechToTextPhase.Idle
            } else {
                SpeechToTextPhase.Result
            }
    }

    fun discardRecording() {
        if (phase.value != SpeechToTextPhase.Recorded) {
            return
        }
        audioRecorder.clear()
        recordedFile = null
        waveformBuckets.clear()
        recordingDurationSeconds.floatValue = 0f
        phase.value =
            if (resultText.value.isBlank()) {
                SpeechToTextPhase.Idle
            } else {
                SpeechToTextPhase.Result
            }
    }

    fun recordNew() {
        if (isBusyNetwork()) {
            return
        }
        resultText.value = ""
        errorMessage.value = null
        infoMessage.value = null
        audioRecorder.clear()
        recordedFile = null
        waveformBuckets.clear()
        recordingDurationSeconds.floatValue = 0f
        startRecording(append = false)
    }

    fun rewrite() {
        val text = resultText.value
        if (text.isBlank() || isBusyNetwork()) {
            return
        }
        errorMessage.value = null
        workJob?.cancel()
        workJob =
            viewModelScope.launch {
                phase.value = SpeechToTextPhase.Rewriting
                val result =
                    withContext(Dispatchers.IO) {
                        runCatching { repository.rewrite(text) }
                    }
                result
                    .onSuccess { rewritten ->
                        resultText.value = rewritten
                        phase.value = SpeechToTextPhase.Result
                    }.onFailure { e ->
                        errorMessage.value = e.message ?: e.toString()
                        phase.value = SpeechToTextPhase.Result
                    }
            }
    }

    fun collapseToSingleLine() {
        val current = resultText.value
        if (current.isBlank()) {
            return
        }
        resultText.value = SpeechToTextRepository.toSingleLine(current)
    }

    fun resetSession() {
        workJob?.cancel()
        workJob = null
        stopDurationTicker()
        if (audioRecorder.isRecording) {
            audioRecorder.cancel()
        } else {
            audioRecorder.clear()
        }
        recordedFile = null
        waveformBuckets.clear()
        recordingDurationSeconds.floatValue = 0f
        phase.value = SpeechToTextPhase.Idle
        resultText.value = ""
        errorMessage.value = null
        infoMessage.value = null
        hasApiKey.value = BothubConfig.hasApiKey
    }

    private fun startDurationTicker() {
        durationJob?.cancel()
        durationJob =
            viewModelScope.launch {
                while (isActive && phase.value == SpeechToTextPhase.Recording) {
                    recordingDurationSeconds.floatValue = audioRecorder.durationSeconds()
                    delay(200)
                }
            }
    }

    private fun stopDurationTicker() {
        durationJob?.cancel()
        durationJob = null
    }

    private fun processRecording(
        file: File,
        mimeType: String,
    ) {
        workJob?.cancel()
        workJob =
            viewModelScope.launch {
                phase.value = SpeechToTextPhase.Recognizing
                val transcribedOutcome =
                    withContext(Dispatchers.IO) {
                        runCatching { repository.transcribe(file, mimeType) }
                    }
                if (transcribedOutcome.isFailure) {
                    errorMessage.value =
                        transcribedOutcome.exceptionOrNull()?.message
                            ?: transcribedOutcome.exceptionOrNull()?.toString()
                    phase.value = SpeechToTextPhase.Recorded
                    return@launch
                }
                val transcribed = transcribedOutcome.getOrThrow()
                phase.value = SpeechToTextPhase.Fixing
                val fixedOutcome =
                    withContext(Dispatchers.IO) {
                        runCatching { repository.fixText(transcribed) }
                    }
                cleanupRecording(file)
                fixedOutcome
                    .onSuccess { fixed ->
                        resultText.value = fixed
                        phase.value = SpeechToTextPhase.Result
                    }.onFailure { e ->
                        errorMessage.value = e.message ?: e.toString()
                        phase.value = SpeechToTextPhase.Idle
                    }
            }
    }

    private fun cleanupRecording(file: File) {
        file.delete()
        if (recordedFile == file) {
            recordedFile = null
        }
        waveformBuckets.clear()
        recordingDurationSeconds.floatValue = 0f
    }

    private fun isBusyNetwork(): Boolean = phase.value == SpeechToTextPhase.Recognizing ||
        phase.value == SpeechToTextPhase.Fixing ||
        phase.value == SpeechToTextPhase.Rewriting

    override fun onCleared() {
        audioRecorder.setEnvelopeListener(null)
        resetSession()
        super.onCleared()
    }
}
