package dev.harrix.hsk.ui.speechtotext

import android.app.Application
import android.net.Uri
import android.os.Handler
import android.os.Looper
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import dev.harrix.hsk.R
import dev.harrix.hsk.ai.AiConfig
import dev.harrix.hsk.bothub.BothubConfig
import dev.harrix.hsk.speechtotext.AudioCompress
import dev.harrix.hsk.speechtotext.AudioRecorder
import dev.harrix.hsk.speechtotext.AudioRecorderException
import dev.harrix.hsk.speechtotext.SpeechMessageStatus
import dev.harrix.hsk.speechtotext.SpeechQueueItem
import dev.harrix.hsk.speechtotext.SpeechToTextQueueStore
import dev.harrix.hsk.speechtotext.SpeechToTextRepository
import dev.harrix.hsk.speechtotext.SpeechUploadAudio
import dev.harrix.hsk.speechtotext.WaveformBucket
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

enum class ComposerPhase {
    Idle,
    Recording,
    Recorded,
}

class SpeechToTextViewModel(
    application: Application,
) : AndroidViewModel(application) {
    private val audioRecorder = AudioRecorder(application.applicationContext)
    private val repository = SpeechToTextRepository(application.applicationContext)
    private val queueStore = SpeechToTextQueueStore(application.applicationContext)
    private val mainHandler = Handler(Looper.getMainLooper())
    private val recognition =
        SpeechRecognitionCoordinator(
            scope = viewModelScope,
            repository = repository,
            queueStore = queueStore,
            onItemChanged = { item ->
                replaceItem(item)
                persistItem(item)
            },
            onAverageChanged = { averageRecognitionMs.longValue = it },
            onErrorMessage = { errorMessage.value = it },
        )

    val items = mutableStateListOf<SpeechQueueItem>()
    val composerPhase = mutableStateOf(ComposerPhase.Idle)
    val errorMessage = mutableStateOf<String?>(null)
    val infoMessage = mutableStateOf<String?>(null)
    val hasApiKey = mutableStateOf(isAiConfigured())
    val recordingDurationSeconds = mutableFloatStateOf(0f)
    val waveformBuckets = mutableStateListOf<WaveformBucket>()
    val averageRecognitionMs = mutableLongStateOf(queueStore.averageRecognitionMs() ?: 0L)

    private var draftFile: File? = null
    private var draftMime: String = AudioRecorder.MIME_WAV
    private var durationJob: Job? = null
    private var elapsedTickerJob: Job? = null
    private val pendingEnvelopes = ArrayDeque<WaveformBucket>()
    private var envelopeFlushPosted = false

    init {
        items.addAll(queueStore.loadAll())
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
                if (composerPhase.value != ComposerPhase.Recording || batch.isEmpty()) {
                    return@post
                }
                waveformBuckets.addAll(batch)
            }
        }
        startElapsedTicker()
    }

    fun clearError() {
        errorMessage.value = null
    }

    fun clearInfo() {
        infoMessage.value = null
    }

    fun startRecording(append: Boolean = false) {
        if (composerPhase.value == ComposerPhase.Recording) {
            return
        }
        errorMessage.value = null
        infoMessage.value = null
        try {
            val appendFile = if (append) draftFile else null
            if (!append) {
                clearDraftAudio()
                waveformBuckets.clear()
            }
            draftFile = audioRecorder.start(appendTo = appendFile)
            draftMime = AudioRecorder.MIME_WAV
            composerPhase.value = ComposerPhase.Recording
            startDurationTicker()
        } catch (e: AudioRecorderException) {
            errorMessage.value = e.message
            composerPhase.value =
                if (draftFile != null) {
                    ComposerPhase.Recorded
                } else {
                    ComposerPhase.Idle
                }
            stopDurationTicker()
        }
    }

    fun stopRecording() {
        if (composerPhase.value != ComposerPhase.Recording) {
            return
        }
        stopDurationTicker()
        val stopped =
            try {
                audioRecorder.stop()
            } catch (e: AudioRecorderException) {
                errorMessage.value = e.message
                composerPhase.value =
                    if (draftFile != null) {
                        ComposerPhase.Recorded
                    } else {
                        ComposerPhase.Idle
                    }
                return
            }
        draftFile = stopped.first
        draftMime = stopped.second
        recordingDurationSeconds.floatValue = audioRecorder.durationSeconds()
        composerPhase.value = ComposerPhase.Recorded
    }

    fun continueRecording() {
        if (composerPhase.value != ComposerPhase.Recorded || !audioRecorder.canContinue()) {
            return
        }
        startRecording(append = true)
    }

    fun rerecord() {
        clearDraftAudio()
        waveformBuckets.clear()
        recordingDurationSeconds.floatValue = 0f
        errorMessage.value = null
        infoMessage.value = null
        startRecording(append = false)
    }

    fun cancelRecording() {
        if (composerPhase.value != ComposerPhase.Recording) {
            return
        }
        stopDurationTicker()
        audioRecorder.cancel()
        draftFile = null
        waveformBuckets.clear()
        recordingDurationSeconds.floatValue = 0f
        composerPhase.value = ComposerPhase.Idle
    }

    fun discardDraft() {
        if (composerPhase.value != ComposerPhase.Recorded) {
            return
        }
        clearDraftAudio()
        waveformBuckets.clear()
        recordingDurationSeconds.floatValue = 0f
        composerPhase.value = ComposerPhase.Idle
    }

    fun enqueueDraftAndRecognize() {
        enqueueDraft { item ->
            recognize(item.id)
        }
    }

    fun enqueueDraftAndRecordNew() {
        enqueueDraft {
            startRecording(append = false)
        }
    }

    private fun enqueueDraft(onEnqueued: (SpeechQueueItem) -> Unit) {
        val file = draftFile?.takeIf { it.isFile } ?: return
        val duration = recordingDurationSeconds.floatValue
        val mime = draftMime
        viewModelScope.launch {
            val outcome =
                withContext(Dispatchers.IO) {
                    runCatching {
                        queueStore.addFromRecording(
                            source = file,
                            mimeType = mime,
                            audioDurationSeconds = duration,
                        )
                    }
                }
            outcome
                .onSuccess { item ->
                    clearDraftAudio()
                    waveformBuckets.clear()
                    recordingDurationSeconds.floatValue = 0f
                    composerPhase.value = ComposerPhase.Idle
                    items.add(item)
                    onEnqueued(item)
                }.onFailure { e ->
                    errorMessage.value = e.message ?: e.toString()
                }
        }
    }

    fun recognize(id: String) {
        val item = items.firstOrNull { it.id == id } ?: return
        if (!hasApiKey.value) {
            errorMessage.value =
                getApplication<Application>().getString(R.string.speech_to_text_missing_api_key)
            return
        }
        recognition.recognize(item)
    }

    fun cancelRecognition(id: String) {
        recognition.cancel(id)
        val index = items.indexOfFirst { it.id == id }
        if (index < 0) {
            return
        }
        val current = items[index]
        if (current.status != SpeechMessageStatus.Processing) {
            return
        }
        val cancelled =
            current.copy(
                status = SpeechMessageStatus.Cancelled,
                recognitionStartedAtMs = 0L,
                recognitionElapsedMs = 0L,
            )
        replaceItem(cancelled)
        persistItem(cancelled)
    }

    fun deleteItem(id: String) {
        recognition.cancel(id)
        val index = items.indexOfFirst { it.id == id }
        if (index < 0) {
            return
        }
        items.removeAt(index)
        viewModelScope.launch(Dispatchers.IO) {
            queueStore.delete(id)
        }
    }

    fun updateItemText(
        id: String,
        text: String,
    ) {
        val index = items.indexOfFirst { it.id == id }
        if (index < 0) {
            return
        }
        val updated = items[index].copy(text = text)
        replaceItem(updated)
        persistItem(updated)
    }

    fun collapseItemToSingleLine(id: String) {
        val index = items.indexOfFirst { it.id == id }
        if (index < 0) {
            return
        }
        val current = items[index]
        if (current.text.isBlank()) {
            return
        }
        updateItemText(id, SpeechToTextRepository.toSingleLine(current.text))
    }

    fun rewriteItem(id: String) {
        val item = items.firstOrNull { it.id == id } ?: return
        if (!hasApiKey.value) {
            errorMessage.value =
                getApplication<Application>().getString(R.string.speech_to_text_missing_api_key)
            return
        }
        recognition.rewrite(item)
    }

    fun suggestedAudioFileName(id: String? = null): String {
        val stamp = LocalDateTime.now().format(AUDIO_FILE_TIMESTAMP)
        return if (id != null) {
            "hsk-speech-$stamp-$id.m4a"
        } else {
            "hsk-speech-$stamp.m4a"
        }
    }

    fun saveItemAudio(
        id: String,
        destination: Uri,
    ) {
        val item = items.firstOrNull { it.id == id } ?: return
        viewModelScope.launch {
            val result =
                withContext(Dispatchers.IO) {
                    runCatching {
                        val upload = resolveSaveUpload(item)
                        try {
                            val resolver = getApplication<Application>().contentResolver
                            resolver.openOutputStream(destination, "wt")?.use { output ->
                                upload.file.inputStream().use { input -> input.copyTo(output) }
                            } ?: error("Could not open destination")
                        } finally {
                            if (upload.temporary &&
                                upload.file.absolutePath != item.audioFile.absolutePath
                            ) {
                                upload.file.delete()
                            }
                        }
                    }
                }
            result
                .onSuccess {
                    infoMessage.value =
                        getApplication<Application>().getString(R.string.speech_to_text_audio_saved)
                }.onFailure {
                    errorMessage.value =
                        getApplication<Application>()
                            .getString(R.string.speech_to_text_save_audio_failed)
                }
        }
    }

    fun saveDraftAudio(destination: Uri) {
        val source = draftFile?.takeIf { it.isFile } ?: return
        viewModelScope.launch {
            val result =
                withContext(Dispatchers.IO) {
                    runCatching {
                        val upload = AudioCompress.prepareForUpload(source, draftMime)
                        try {
                            check(upload.mimeType == AudioRecorder.MIME_M4A) {
                                "Could not compress recording"
                            }
                            val resolver = getApplication<Application>().contentResolver
                            resolver.openOutputStream(destination, "wt")?.use { output ->
                                upload.file.inputStream().use { input -> input.copyTo(output) }
                            } ?: error("Could not open destination")
                        } finally {
                            if (upload.temporary && upload.file.absolutePath != source.absolutePath) {
                                upload.file.delete()
                            }
                        }
                    }
                }
            result
                .onSuccess {
                    infoMessage.value =
                        getApplication<Application>().getString(R.string.speech_to_text_audio_saved)
                }.onFailure {
                    errorMessage.value =
                        getApplication<Application>()
                            .getString(R.string.speech_to_text_save_audio_failed)
                }
        }
    }

    fun resetComposerOnly() {
        stopDurationTicker()
        if (audioRecorder.isRecording) {
            audioRecorder.cancel()
        } else {
            audioRecorder.clear()
        }
        draftFile = null
        waveformBuckets.clear()
        recordingDurationSeconds.floatValue = 0f
        composerPhase.value = ComposerPhase.Idle
        hasApiKey.value = isAiConfigured()
    }

    fun leaveScreen() {
        recognition.cancelAll()
        items.forEachIndexed { index, item ->
            if (item.status == SpeechMessageStatus.Processing) {
                val restored =
                    item.copy(
                        status = SpeechMessageStatus.Recorded,
                        recognitionStartedAtMs = 0L,
                        recognitionElapsedMs = 0L,
                    )
                items[index] = restored
                persistItem(restored)
            }
        }
        resetComposerOnly()
    }

    private fun resolveSaveUpload(item: SpeechQueueItem): SpeechUploadAudio {
        if (item.mimeType.contains("m4a", ignoreCase = true) && item.audioFile.isFile) {
            return SpeechUploadAudio(item.audioFile, AudioRecorder.MIME_M4A)
        }
        val upload = AudioCompress.prepareForUpload(item.audioFile, item.mimeType)
        check(upload.mimeType == AudioRecorder.MIME_M4A) { "Could not compress recording" }
        return upload
    }

    private fun replaceItem(item: SpeechQueueItem) {
        val index = items.indexOfFirst { it.id == item.id }
        if (index >= 0) {
            items[index] = item
        }
    }

    private fun persistItem(item: SpeechQueueItem) {
        viewModelScope.launch(Dispatchers.IO) {
            queueStore.update(item)
        }
    }

    private fun clearDraftAudio() {
        if (audioRecorder.isRecording) {
            audioRecorder.cancel()
        } else {
            audioRecorder.clear()
        }
        draftFile = null
    }

    private fun isAiConfigured(): Boolean = AiConfig.supportsSpeech && AiConfig.hasSpeechApiKey && BothubConfig.hasApiKey

    private fun startDurationTicker() {
        durationJob?.cancel()
        durationJob =
            viewModelScope.launch {
                while (isActive && composerPhase.value == ComposerPhase.Recording) {
                    recordingDurationSeconds.floatValue = audioRecorder.durationSeconds()
                    delay(200)
                }
            }
    }

    private fun stopDurationTicker() {
        durationJob?.cancel()
        durationJob = null
    }

    private fun startElapsedTicker() {
        elapsedTickerJob?.cancel()
        elapsedTickerJob =
            viewModelScope.launch {
                while (isActive) {
                    val now = System.currentTimeMillis()
                    items.forEachIndexed { index, item ->
                        if (item.status == SpeechMessageStatus.Processing &&
                            item.recognitionStartedAtMs > 0L
                        ) {
                            val elapsed = (now - item.recognitionStartedAtMs).coerceAtLeast(0L)
                            if (elapsed != item.recognitionElapsedMs) {
                                items[index] = item.copy(recognitionElapsedMs = elapsed)
                            }
                        }
                    }
                    delay(250)
                }
            }
    }

    override fun onCleared() {
        audioRecorder.setEnvelopeListener(null)
        elapsedTickerJob?.cancel()
        leaveScreen()
        super.onCleared()
    }

    private companion object {
        val AUDIO_FILE_TIMESTAMP: DateTimeFormatter = DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss")
    }
}
