package dev.harrix.hsk.ui.photosync

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import dev.harrix.hsk.photosync.PhotoSyncEndpoint
import dev.harrix.hsk.photosync.PhotoSyncEngine
import dev.harrix.hsk.photosync.PhotoSyncPairing
import dev.harrix.hsk.photosync.PhotoSyncPreferences
import dev.harrix.hsk.photosync.PhotoSyncProgress
import dev.harrix.hsk.photosync.PhotoSyncResult
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import org.json.JSONException
import java.io.IOException

data class PhotoSyncUiState(
    val host: String = "",
    val portText: String = PhotoSyncPreferences.DEFAULT_PORT.toString(),
    val token: String = "",
    val isSyncing: Boolean = false,
    val progress: PhotoSyncProgress? = null,
    val lastResult: PhotoSyncResult? = null,
    val errorMessage: String? = null,
)

class PhotoSyncViewModel(
    application: Application,
) : AndroidViewModel(application) {
    private val prefs = PhotoSyncPreferences(application)
    private val engine = PhotoSyncEngine(application)

    private val _uiState =
        MutableStateFlow(
            PhotoSyncUiState(
                host = prefs.getHost(),
                portText = prefs.getPort().toString(),
                token = prefs.getToken(),
            ),
        )
    val uiState: StateFlow<PhotoSyncUiState> = _uiState.asStateFlow()

    private var syncJob: Job? = null

    fun onHostChange(value: String) {
        _uiState.update { it.copy(host = value, errorMessage = null) }
    }

    fun onPortChange(value: String) {
        _uiState.update { it.copy(portText = value.filter { ch -> ch.isDigit() }, errorMessage = null) }
    }

    fun onTokenChange(value: String) {
        _uiState.update { it.copy(token = value, errorMessage = null) }
    }

    fun applyPairingText(raw: String) {
        val parsed = PhotoSyncPairing.parse(raw)
        if (parsed == null) {
            _uiState.update { it.copy(errorMessage = "Could not parse pairing data") }
            return
        }
        _uiState.update {
            it.copy(
                host = parsed.host,
                portText = parsed.port.toString(),
                token = parsed.token.ifEmpty { it.token },
                errorMessage = null,
            )
        }
        persistConnection()
    }

    fun startSync() {
        if (_uiState.value.isSyncing) {
            return
        }
        val endpoint = currentEndpoint() ?: return
        persistConnection()
        syncJob?.cancel()
        syncJob =
            viewModelScope.launch {
                _uiState.update {
                    it.copy(isSyncing = true, errorMessage = null, lastResult = null, progress = null)
                }
                try {
                    val result =
                        engine.sync(endpoint) { progress ->
                            _uiState.update { state -> state.copy(progress = progress) }
                        }
                    _uiState.update {
                        it.copy(isSyncing = false, lastResult = result, progress = null)
                    }
                } catch (error: CancellationException) {
                    throw error
                } catch (error: IOException) {
                    failSync(error)
                } catch (error: JSONException) {
                    failSync(error)
                } catch (error: IllegalStateException) {
                    failSync(error)
                }
            }
    }

    fun cancelSync() {
        syncJob?.cancel()
        syncJob = null
        _uiState.update {
            it.copy(isSyncing = false, progress = null, errorMessage = "Sync cancelled")
        }
    }

    private fun failSync(error: Throwable) {
        _uiState.update {
            it.copy(
                isSyncing = false,
                progress = null,
                errorMessage = error.message ?: error.toString(),
            )
        }
    }

    private fun currentEndpoint(): PhotoSyncEndpoint? {
        val state = _uiState.value
        val host = state.host.trim()
        val token = state.token.trim()
        val port = state.portText.toIntOrNull()
        if (host.isEmpty() || token.isEmpty() || port == null) {
            _uiState.update { it.copy(errorMessage = "Enter host, port, and token from the desktop app") }
            return null
        }
        return PhotoSyncEndpoint(host = host, port = port, token = token)
    }

    private fun persistConnection() {
        val state = _uiState.value
        val port = state.portText.toIntOrNull() ?: PhotoSyncPreferences.DEFAULT_PORT
        prefs.saveConnection(state.host, port, state.token)
    }
}
