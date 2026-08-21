package dev.harrix.hsk.ui.speechtotext

import dev.harrix.hsk.speechtotext.SpeechMessageStatus
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
 * Runs per-item speech recognition / rewrite jobs with cancellable HTTP.
 */
class SpeechRecognitionCoordinator(
    private val scope: CoroutineScope,
    private val repository: SpeechToTextRepository,
    private val queueStore: SpeechToTextQueueStore,
    private val onItemChanged: (SpeechQueueItem) -> Unit,
    private val onAverageChanged: (Long) -> Unit,
    private val onErrorMessage: (String) -> Unit,
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
                            queueStore.recordSuccessfulRecognition(durationMs)
                        }
                        onAverageChanged(queueStore.averageRecognitionMs() ?: 0L)
                        onItemChanged(
                            processing.copy(
                                status = SpeechMessageStatus.Done,
                                text = fixed,
                                errorMessage = "",
                                recognitionStartedAtMs = 0L,
                                recognitionElapsedMs = durationMs,
                                lastRecognitionDurationMs = durationMs,
                            ),
                        )
                    }.onFailure { error ->
                        if (error is CancellationException) {
                            onItemChanged(
                                processing.copy(
                                    status = SpeechMessageStatus.Cancelled,
                                    recognitionStartedAtMs = 0L,
                                    recognitionElapsedMs = 0L,
                                ),
                            )
                        } else {
                            onItemChanged(
                                processing.copy(
                                    status = SpeechMessageStatus.Error,
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
        if (item.status != SpeechMessageStatus.Done || item.text.isBlank()) {
            return
        }
        jobs[item.id]?.cancel()
        val startedAt = System.currentTimeMillis()
        val originalText = item.text
        val processing =
            item.copy(
                status = SpeechMessageStatus.Processing,
                recognitionStartedAtMs = startedAt,
                recognitionElapsedMs = 0L,
                errorMessage = "",
            )
        onItemChanged(processing)
        jobs[item.id] =
            scope.launch {
                val outcome =
                    runCatching {
                        val rewritten =
                            withContext(Dispatchers.IO) {
                                repository.rewrite(originalText, cancellationKey = item.id)
                            }
                        ensureActive()
                        rewritten
                    }
                outcome
                    .onSuccess { rewritten ->
                        onItemChanged(
                            processing.copy(
                                status = SpeechMessageStatus.Done,
                                text = rewritten,
                                recognitionStartedAtMs = 0L,
                                recognitionElapsedMs = 0L,
                            ),
                        )
                    }.onFailure { error ->
                        onItemChanged(
                            processing.copy(
                                status = SpeechMessageStatus.Done,
                                text = originalText,
                                errorMessage =
                                if (error is CancellationException) {
                                    ""
                                } else {
                                    error.message ?: error.toString()
                                },
                                recognitionStartedAtMs = 0L,
                                recognitionElapsedMs = 0L,
                            ),
                        )
                        if (error !is CancellationException) {
                            onErrorMessage(error.message ?: error.toString())
                        }
                    }
                jobs.remove(item.id)
            }
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
}
