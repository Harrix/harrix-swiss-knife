package dev.harrix.hsk.ui.speechtotext

import android.app.Application
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import dev.harrix.hsk.bothub.BothubConfig
import dev.harrix.hsk.speechtotext.AudioRecorder
import dev.harrix.hsk.speechtotext.AudioRecorderException
import dev.harrix.hsk.speechtotext.SpeechToTextRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

enum class SpeechToTextPhase {
    Idle,
    Recording,
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

    val phase = mutableStateOf(SpeechToTextPhase.Idle)
    val resultText = mutableStateOf("")
    val errorMessage = mutableStateOf<String?>(null)
    val infoMessage = mutableStateOf<String?>(null)
    val hasApiKey = mutableStateOf(BothubConfig.hasApiKey)

    private var recordedFile: File? = null
    private var workJob: Job? = null

    fun clearError() {
        errorMessage.value = null
    }

    fun clearInfo() {
        infoMessage.value = null
    }

    fun startRecording() {
        if (phase.value == SpeechToTextPhase.Recording || isBusyNetwork()) {
            return
        }
        errorMessage.value = null
        infoMessage.value = null
        try {
            recordedFile?.delete()
            recordedFile = audioRecorder.start()
            phase.value = SpeechToTextPhase.Recording
            resultText.value = ""
        } catch (e: AudioRecorderException) {
            errorMessage.value = e.message
            phase.value = SpeechToTextPhase.Idle
        }
    }

    fun stopRecordingAndProcess() {
        if (phase.value != SpeechToTextPhase.Recording) {
            return
        }
        val stopped =
            try {
                audioRecorder.stop()
            } catch (e: AudioRecorderException) {
                errorMessage.value = e.message
                phase.value =
                    if (resultText.value.isBlank()) {
                        SpeechToTextPhase.Idle
                    } else {
                        SpeechToTextPhase.Result
                    }
                return
            }
        if (stopped == null) {
            phase.value = SpeechToTextPhase.Idle
            return
        }
        val (file, _) = stopped
        recordedFile = file
        processRecording(file)
    }

    fun cancelRecording() {
        if (phase.value != SpeechToTextPhase.Recording) {
            return
        }
        audioRecorder.cancel()
        recordedFile = null
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
        startRecording()
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
        if (audioRecorder.isRecording) {
            audioRecorder.cancel()
        }
        recordedFile?.delete()
        recordedFile = null
        phase.value = SpeechToTextPhase.Idle
        resultText.value = ""
        errorMessage.value = null
        infoMessage.value = null
        hasApiKey.value = BothubConfig.hasApiKey
    }

    private fun processRecording(file: File) {
        workJob?.cancel()
        workJob =
            viewModelScope.launch {
                phase.value = SpeechToTextPhase.Recognizing
                val transcribedOutcome =
                    withContext(Dispatchers.IO) {
                        runCatching { repository.transcribe(file) }
                    }
                if (transcribedOutcome.isFailure) {
                    cleanupRecording(file)
                    errorMessage.value =
                        transcribedOutcome.exceptionOrNull()?.message
                            ?: transcribedOutcome.exceptionOrNull()?.toString()
                    phase.value = SpeechToTextPhase.Idle
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
    }

    private fun isBusyNetwork(): Boolean = phase.value == SpeechToTextPhase.Recognizing ||
        phase.value == SpeechToTextPhase.Fixing ||
        phase.value == SpeechToTextPhase.Rewriting

    override fun onCleared() {
        resetSession()
        super.onCleared()
    }
}
