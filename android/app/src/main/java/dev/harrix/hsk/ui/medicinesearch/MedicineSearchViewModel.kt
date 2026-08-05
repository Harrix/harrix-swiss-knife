package dev.harrix.hsk.ui.medicinesearch

import android.app.Application
import android.content.Intent
import android.net.Uri
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import dev.harrix.hsk.bothub.BothubApiException
import dev.harrix.hsk.bothub.BothubConfig
import dev.harrix.hsk.medicinesearch.MedicineSearchPreferences
import dev.harrix.hsk.medicinesearch.MedicineSearchRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
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
    val medicineNames = mutableStateOf<List<String>>(emptyList())
    val fileDisplayName = mutableStateOf<String?>(null)
    val hasMedicinesFile = mutableStateOf(false)
    val errorMessage = mutableStateOf<String?>(null)
    val hasApiKey = mutableStateOf(BothubConfig.hasApiKey)

    private var medicinesMarkdown: String? = null
    private var workJob: Job? = null

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
        val previous = preferences.getMedicinesUri()
        preferences.clearMedicinesUri()
        if (previous != null) {
            releasePersistableReadPermission(previous)
        }
        clearFileState()
        if (phase.value == MedicineSearchPhase.LoadingFile) {
            phase.value = MedicineSearchPhase.Idle
        }
    }

    fun search() {
        val query = queryText.value.trim()
        if (query.isEmpty() || isBusy()) {
            return
        }
        errorMessage.value = null
        workJob?.cancel()
        workJob =
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
                outcome
                    .onSuccess { answer ->
                        resultText.value = answer
                        phase.value = MedicineSearchPhase.Result
                    }.onFailure { error ->
                        errorMessage.value = error.message ?: error.toString()
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
        workJob?.cancel()
        workJob = null
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
        workJob?.cancel()
        workJob =
            viewModelScope.launch {
                phase.value = MedicineSearchPhase.LoadingFile
                errorMessage.value = null
                val outcome =
                    withContext(Dispatchers.IO) {
                        runCatching { repository.loadMedicinesFile(uri) }
                    }
                outcome
                    .onSuccess { content ->
                        medicinesMarkdown = content.markdown
                        medicineNames.value = content.names
                        fileDisplayName.value = content.displayName
                        hasMedicinesFile.value = true
                        phase.value =
                            if (resultText.value.isBlank()) {
                                MedicineSearchPhase.Idle
                            } else {
                                MedicineSearchPhase.Result
                            }
                    }.onFailure { error ->
                        clearFileState()
                        preferences.clearMedicinesUri()
                        errorMessage.value =
                            when (error) {
                                is BothubApiException -> error.message
                                else -> error.message ?: error.toString()
                            }
                        phase.value = MedicineSearchPhase.Idle
                    }
            }
    }

    private fun clearFileState() {
        medicinesMarkdown = null
        medicineNames.value = emptyList()
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
        workJob?.cancel()
        super.onCleared()
    }
}
