package dev.harrix.hsk.ui.medicinesearch

import android.app.Application
import android.content.Intent
import android.net.Uri
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import dev.harrix.hsk.bothub.BothubApiException
import dev.harrix.hsk.bothub.BothubClient
import dev.harrix.hsk.bothub.BothubConfig
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

class MedicineSearchViewModel(
    application: Application,
) : AndroidViewModel(application) {
    private val preferences = MedicineSearchPreferences(application.applicationContext)
    private val repository = MedicineSearchRepository(application.applicationContext)

    val phase = mutableStateOf(MedicineSearchPhase.Idle)
    val queryText = mutableStateOf("")
    val resultText = mutableStateOf("")
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
        if (query.isEmpty() || isBusy()) {
            return
        }
        if (!BothubConfig.hasApiKey) {
            hasApiKey.value = false
            errorMessage.value = BothubClient.MISSING_API_KEY_MESSAGE
            return
        }
        errorMessage.value = null
        searchJob?.cancel()
        searchJob =
            viewModelScope.launch {
                phase.value = MedicineSearchPhase.Searching
                val outcome =
                    withContext(Dispatchers.IO) {
                        runCatching {
                            repository.search(
                                medicinesMarkdown = medicinesMarkdown,
                                query = query,
                            )
                        }
                    }
                ensureActive()
                outcome
                    .onSuccess { answer ->
                        resultText.value = answer
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

    fun resetSession() {
        searchJob?.cancel()
        searchJob = null
        fileJob?.cancel()
        fileJob = null
        queryText.value = ""
        resultText.value = ""
        errorMessage.value = null
        phase.value = MedicineSearchPhase.Idle
        reloadFromPreferences()
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
}
