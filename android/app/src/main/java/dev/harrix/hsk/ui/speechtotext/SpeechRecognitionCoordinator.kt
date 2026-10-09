package dev.harrix.hsk.ui.speechtotext

import dev.harrix.hsk.speechtotext.SpeechMessageStatus
import dev.harrix.hsk.speechtotext.SpeechProcessingKind
import dev.harrix.hsk.speechtotext.SpeechQueueItem
import dev.harrix.hsk.speechtotext.SpeechToTextQueueStore
import dev.harrix.hsk.speechtotext.SpeechToTextRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlin.coroutines.cancellation.CancellationException

/**
 * Runs per-item speech recognition / rewrite / answer jobs with cancellable HTTP.
 */
class SpeechRecognitionCoordinator(
    private val scope: CoroutineScope,
    private val repository: SpeechToTextRepository,
    private val queueStore: SpeechToTextQueueStore,
    private val onItemChanged: (SpeechQueueItem) -> Unit,
    private val onAverageChanged: (Long) -> Unit,
    private val onErrorMessage: (String) -> Unit,
    private val onRecognized: (SpeechQueueItem) -> Unit = {},
) {
    private val jobs = mutableMapOf<String, Job>()

    fun isBusy(id: String): Boolean = jobs[id]?.isActive == true

    fun recognize(item: SpeechQueueItem) {
        if (item.status == SpeechMessageStatus.Done || item.status == SpeechMessageStatus.Processing) {
            return
        }
        jobs[item.id]?.cancel()
        val startedAt = System.currentTimeMillis()
        val processing =
            item.copy(
                status = SpeechMessageStatus.Processing,
                processingKind = SpeechProcessingKind.Recognize,
                errorMessage = "",
                recognitionStartedAtMs = startedAt,
                recognitionElapsedMs = 0L,
            )
        onItemChanged(processing)
        jobs[item.id] =
            scope.launch {
                val cancellationKey = item.id
                val outcome =
                    runCatching {
                        val transcribed =
                            withContext(Dispatchers.IO) {
                                repository.transcribe(
                                    audioFile = processing.audioFile,
                                    mimeType = processing.mimeType,
                                    cancellationKey = cancellationKey,
                                )
                            }
                        ensureActive()
                        val fixed =
                            withContext(Dispatchers.IO) {
                                repository.fixText(
                                    text = transcribed,
                                    cancellationKey = cancellationKey,
                                )
                            }
                        ensureActive()
                        fixed
                    }
                outcome
                    .onSuccess { fixed ->
                        val durationMs = (System.currentTimeMillis() - startedAt).coerceAtLeast(1L)
                        withContext(Dispatchers.IO) {
                            queueStore.recordSuccessfulRecognition(
                                recognitionMs = durationMs,
                                audioDurationSeconds = processing.audioDurationSeconds,
                            )
                        }
                        onAverageChanged(queueStore.averageMsPerAudioSecond() ?: 0L)
                        val done =
                            processing.copy(
                                status = SpeechMessageStatus.Done,
                                processingKind = SpeechProcessingKind.None,
                                text = fixed,
                                errorMessage = "",
                                recognitionStartedAtMs = 0L,
                                recognitionElapsedMs = durationMs,
                                lastRecognitionDurationMs = durationMs,
                                markdownAnswer = false,
                            )
                        onItemChanged(done)
                        onRecognized(done)
                    }.onFailure { error ->
                        if (error is CancellationException) {
                            onItemChanged(
                                processing.copy(
                                    status = SpeechMessageStatus.Cancelled,
                                    processingKind = SpeechProcessingKind.None,
                                    recognitionStartedAtMs = 0L,
                                    recognitionElapsedMs = 0L,
                                ),
                            )
                        } else {
                            onItemChanged(
                                processing.copy(
                                    status = SpeechMessageStatus.Error,
                                    processingKind = SpeechProcessingKind.None,
                                    errorMessage = error.message ?: error.toString(),
                                    recognitionStartedAtMs = 0L,
                                    recognitionElapsedMs = 0L,
                                ),
                            )
                        }
                    }
                jobs.remove(item.id)
            }
    }

    fun rewrite(item: SpeechQueueItem) {
        transformText(
            item = item,
            kind = SpeechProcessingKind.Rewrite,
            transform = { text, key -> repository.rewrite(text, cancellationKey = key) },
        )
    }

    fun answer(
        item: SpeechQueueItem,
        model: String? = null,
    ) {
        transformText(
            item = item,
            kind = SpeechProcessingKind.Answer,
            transform = { text, key ->
                repository.answerQuestion(
                    text = text,
                    model = model,
                    cancellationKey = key,
                )
            },
        )
    }

    fun cancel(id: String) {
        repository.cancel(id)
        jobs.remove(id)?.cancel()
    }

    fun cancelAll() {
        jobs.keys.toList().forEach { id ->
            repository.cancel(id)
            jobs.remove(id)?.cancel()
        }
    }

    private fun transformText(
        item: SpeechQueueItem,
        kind: SpeechProcessingKind,
        transform: suspend (String, String) -> String,
    ) {
        if (item.status != SpeechMessageStatus.Done || item.text.isBlank()) {
            return
        }
        jobs[item.id]?.cancel()
        val startedAt = System.currentTimeMillis()
        val originalText = item.text
        val processing =
            item.copy(
                status = SpeechMessageStatus.Processing,
                processingKind = kind,
                recognitionStartedAtMs = startedAt,
                recognitionElapsedMs = 0L,
                errorMessage = "",
            )
        onItemChanged(processing)
        jobs[item.id] =
            scope.launch {
                val outcome =
                    runCatching {
                        val result =
                            withContext(Dispatchers.IO) {
                                transform(originalText, item.id)
                            }
                        ensureActive()
                        result
                    }
                val originalMarkdownAnswer = item.markdownAnswer
                outcome
                    .onSuccess { result ->
                        onItemChanged(
                            processing.copy(
                                status = SpeechMessageStatus.Done,
                                processingKind = SpeechProcessingKind.None,
                                text = result,
                                recognitionStartedAtMs = 0L,
                                recognitionElapsedMs = 0L,
                                markdownAnswer = kind == SpeechProcessingKind.Answer,
                            ),
                        )
                    }.onFailure { error ->
                        onItemChanged(
                            processing.copy(
                                status = SpeechMessageStatus.Done,
                                processingKind = SpeechProcessingKind.None,
                                text = originalText,
                                errorMessage =
                                if (error is CancellationException) {
                                    ""
                                } else {
                                    error.message ?: error.toString()
                                },
                                recognitionStartedAtMs = 0L,
                                recognitionElapsedMs = 0L,
                                markdownAnswer = originalMarkdownAnswer,
                            ),
                        )
                        if (error !is CancellationException) {
                            onErrorMessage(error.message ?: error.toString())
                        }
                    }
                jobs.remove(item.id)
            }
    }
}
