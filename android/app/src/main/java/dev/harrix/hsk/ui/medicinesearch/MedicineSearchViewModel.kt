package dev.harrix.hsk.ui.medicinesearch

import android.app.Application
import android.content.Intent
import android.net.Uri
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import dev.harrix.hsk.R
import dev.harrix.hsk.bothub.BothubApiException
import dev.harrix.hsk.bothub.BothubClient
import dev.harrix.hsk.bothub.BothubConfig
import dev.harrix.hsk.bothub.BothubPrompts
import dev.harrix.hsk.medicinesearch.MedicineSearchPreferences
import dev.harrix.hsk.medicinesearch.MedicineSearchRepository
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

enum class MedicineSearchPhase {
    Idle,
    LoadingFile,
    Searching,
    Result,
}

data class MedicineSearchTurn(
    val question: String,
    val answer: String,
)

class MedicineSearchViewModel(
    application: Application,
) : AndroidViewModel(application) {
    private val preferences = MedicineSearchPreferences(application.applicationContext)
    private val repository = MedicineSearchRepository(application.applicationContext)

    val phase = mutableStateOf(MedicineSearchPhase.Idle)
    val queryText = mutableStateOf("")
    val followUpText = mutableStateOf("")
    val attachedPhotos = mutableStateOf<List<Uri>>(emptyList())
    val conversation = mutableStateOf<List<MedicineSearchTurn>>(emptyList())
    val resultText = mutableStateOf("")
    val isFollowUpRequest = mutableStateOf(false)
    val fileDisplayName = mutableStateOf<String?>(null)
    val medicinesUri = mutableStateOf<Uri?>(null)
    val hasMedicinesFile = mutableStateOf(false)
    val errorMessage = mutableStateOf<String?>(null)
    val hasApiKey = mutableStateOf(BothubConfig.hasApiKey)

    private var medicinesMarkdown: String? = null
    private var fileJob: Job? = null
    private var searchJob: Job? = null

    init {
        reloadFromPreferences()
    }

    fun clearError() {
        errorMessage.value = null
    }

    fun onQueryChange(value: String) {
        queryText.value = value
    }

    fun onFollowUpChange(value: String) {
        followUpText.value = value
    }

    fun addPhotos(uris: List<Uri>) {
        if (uris.isEmpty()) {
            return
        }
        attachedPhotos.value =
            (attachedPhotos.value + uris)
                .distinct()
                .take(MAX_PHOTOS)
    }

    fun removePhoto(uri: Uri) {
        attachedPhotos.value = attachedPhotos.value.filterNot { it == uri }
    }

    fun reloadFromPreferences() {
        hasApiKey.value = BothubConfig.hasApiKey
        // Do not interrupt an in-flight BotHub request when settings/file reload.
        if (searchJob?.isActive == true || phase.value == MedicineSearchPhase.Searching) {
            return
        }
        val uri = preferences.getMedicinesUri()
        if (uri == null) {
            clearFileState()
            phase.value =
                if (resultText.value.isBlank()) {
                    MedicineSearchPhase.Idle
                } else {
                    MedicineSearchPhase.Result
                }
            return
        }
        loadUri(uri, persist = false)
    }

    fun onMedicinesFilePicked(uri: Uri) {
        val previous = preferences.getMedicinesUri()
        takePersistableReadPermission(uri)
        preferences.setMedicinesUri(uri)
        if (previous != null && previous != uri) {
            releasePersistableReadPermission(previous)
        }
        loadUri(uri, persist = false)
    }

    fun clearMedicinesFile() {
        fileJob?.cancel()
        fileJob = null
        val previous = preferences.getMedicinesUri()
        preferences.clearMedicinesUri()
        if (previous != null) {
            releasePersistableReadPermission(previous)
        }
        clearFileState()
        if (phase.value == MedicineSearchPhase.LoadingFile) {
            phase.value =
                if (resultText.value.isBlank()) {
                    MedicineSearchPhase.Idle
                } else {
                    MedicineSearchPhase.Result
                }
        }
    }

    fun search() {
        val query = queryText.value.trim()
        val photos = attachedPhotos.value
        if ((query.isEmpty() && photos.isEmpty()) || isBusy()) {
            return
        }
        startSearch(
            query = query,
            photos = photos,
            previousTurns = emptyList(),
            followUp = false,
        )
    }

    fun followUp() {
        val query = followUpText.value.trim()
        val previousTurns = conversation.value
        if (query.isEmpty() || previousTurns.isEmpty() || isBusy()) {
            return
        }
        startSearch(
            query = query,
            photos = attachedPhotos.value,
            previousTurns = previousTurns,
            followUp = true,
        )
    }

    fun resetSession() {
        searchJob?.cancel()
        searchJob = null
        fileJob?.cancel()
        fileJob = null
        queryText.value = ""
        followUpText.value = ""
        attachedPhotos.value = emptyList()
        conversation.value = emptyList()
        resultText.value = ""
        isFollowUpRequest.value = false
        errorMessage.value = null
        phase.value = MedicineSearchPhase.Idle
        reloadFromPreferences()
    }

    private fun startSearch(
        query: String,
        photos: List<Uri>,
        previousTurns: List<MedicineSearchTurn>,
        followUp: Boolean,
    ) {
        if (!BothubConfig.hasApiKey) {
            hasApiKey.value = false
            errorMessage.value = BothubClient.MISSING_API_KEY_MESSAGE
            return
        }
        errorMessage.value = null
        isFollowUpRequest.value = followUp
        searchJob?.cancel()
        searchJob =
            viewModelScope.launch {
                phase.value = MedicineSearchPhase.Searching
                val history = formatHistory(previousTurns)
                val outcome =
                    withContext(Dispatchers.IO) {
                        runCatching {
                            repository.search(
                                medicinesMarkdown = medicinesMarkdown,
                                query = query,
                                photos = photos,
                                history = history,
                            )
                        }
                    }
                ensureActive()
                outcome
                    .onSuccess { answer ->
                        val asked = askedQuestionLabel(query)
                        conversation.value = previousTurns + MedicineSearchTurn(asked, answer)
                        resultText.value = answer
                        if (previousTurns.isNotEmpty()) {
                            followUpText.value = ""
                        }
                        phase.value = MedicineSearchPhase.Result
                    }.onFailure { error ->
                        if (error is CancellationException) {
                            throw error
                        }
                        errorMessage.value = error.message?.takeIf { it.isNotBlank() }
                            ?: error.toString()
                        phase.value =
                            if (resultText.value.isBlank()) {
                                MedicineSearchPhase.Idle
                            } else {
                                MedicineSearchPhase.Result
                            }
                    }
            }
    }

    private fun askedQuestionLabel(query: String): String {
        val trimmed = query.trim()
        if (trimmed.isNotEmpty() && trimmed != BothubPrompts.PHOTO_ONLY_QUERY) {
            return trimmed
        }
        return getApplication<Application>().getString(R.string.medicine_search_photo_only_question)
    }

    private fun formatHistory(turns: List<MedicineSearchTurn>): String? {
        if (turns.isEmpty()) {
            return null
        }
        return turns.joinToString("\n\n") { turn ->
            "User: ${turn.question}\nAssistant: ${turn.answer}"
        }
    }

    private fun loadUri(
        uri: Uri,
        persist: Boolean,
    ) {
        if (persist) {
            preferences.setMedicinesUri(uri)
        }
        fileJob?.cancel()
        fileJob =
            viewModelScope.launch {
                val previousPhase = phase.value
                if (previousPhase != MedicineSearchPhase.Searching) {
                    phase.value = MedicineSearchPhase.LoadingFile
                }
                errorMessage.value = null
                val outcome =
                    withContext(Dispatchers.IO) {
                        runCatching { repository.loadMedicinesFile(uri) }
                    }
                ensureActive()
                outcome
                    .onSuccess { content ->
                        medicinesMarkdown = content.markdown
                        medicinesUri.value = content.uri
                        fileDisplayName.value = content.displayName
                        hasMedicinesFile.value = true
                        if (phase.value == MedicineSearchPhase.LoadingFile) {
                            phase.value =
                                if (resultText.value.isBlank()) {
                                    MedicineSearchPhase.Idle
                                } else {
                                    MedicineSearchPhase.Result
                                }
                        }
                    }.onFailure { error ->
                        if (error is CancellationException) {
                            throw error
                        }
                        clearFileState()
                        preferences.clearMedicinesUri()
                        errorMessage.value =
                            when (error) {
                                is BothubApiException -> error.message

                                else ->
                                    error.message?.takeIf { it.isNotBlank() }
                                        ?: error.toString()
                            }
                        if (phase.value == MedicineSearchPhase.LoadingFile) {
                            phase.value = MedicineSearchPhase.Idle
                        }
                    }
            }
    }

    private fun clearFileState() {
        medicinesMarkdown = null
        medicinesUri.value = null
        fileDisplayName.value = null
        hasMedicinesFile.value = false
    }

    private fun isBusy(): Boolean = phase.value == MedicineSearchPhase.Searching ||
        phase.value == MedicineSearchPhase.LoadingFile

    private fun takePersistableReadPermission(uri: Uri) {
        runCatching {
            getApplication<Application>().contentResolver.takePersistableUriPermission(
                uri,
                Intent.FLAG_GRANT_READ_URI_PERMISSION,
            )
        }
    }

    private fun releasePersistableReadPermission(uri: Uri) {
        runCatching {
            getApplication<Application>().contentResolver.releasePersistableUriPermission(
                uri,
                Intent.FLAG_GRANT_READ_URI_PERMISSION,
            )
        }
    }

    override fun onCleared() {
        searchJob?.cancel()
        fileJob?.cancel()
        super.onCleared()
    }

    companion object {
        const val MAX_PHOTOS = 4
    }
}
