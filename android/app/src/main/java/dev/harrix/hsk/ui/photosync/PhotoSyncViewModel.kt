package dev.harrix.hsk.ui.photosync

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import dev.harrix.hsk.photosync.PhotoSyncConnectionStatus
import dev.harrix.hsk.photosync.PhotoSyncEndpoint
import dev.harrix.hsk.photosync.PhotoSyncEngine
import dev.harrix.hsk.photosync.PhotoSyncFormat
import dev.harrix.hsk.photosync.PhotoSyncLifetimeStats
import dev.harrix.hsk.photosync.PhotoSyncPairing
import dev.harrix.hsk.photosync.PhotoSyncPreferences
import dev.harrix.hsk.photosync.PhotoSyncProgress
import dev.harrix.hsk.photosync.PhotoSyncResult
import dev.harrix.hsk.photosync.PhotoSyncStatsStore
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import org.json.JSONException
import java.io.IOException

data class PhotoSyncUiState(
    val host: String = "",
    val portText: String = PhotoSyncPreferences.DEFAULT_PORT.toString(),
    val token: String = "",
    val isSyncing: Boolean = false,
    val isEstimating: Boolean = false,
    val connectionStatus: PhotoSyncConnectionStatus = PhotoSyncConnectionStatus.Unknown,
    val pendingCount: Int? = null,
    val pendingBytes: Long? = null,
    val progress: PhotoSyncProgress? = null,
    val lastResult: PhotoSyncResult? = null,
    val lifetime: PhotoSyncLifetimeStats = PhotoSyncLifetimeStats(),
    val errorMessage: String? = null,
)

class PhotoSyncViewModel(
    application: Application,
) : AndroidViewModel(application) {
    private val prefs = PhotoSyncPreferences(application)
    private val statsStore = PhotoSyncStatsStore(application)
    private val engine = PhotoSyncEngine(application)

    private val _uiState =
        MutableStateFlow(
            PhotoSyncUiState(
                host = prefs.getHost(),
                portText = prefs.getPort().toString(),
                token = prefs.getToken(),
                lifetime = statsStore.load(),
            ),
        )
    val uiState: StateFlow<PhotoSyncUiState> = _uiState.asStateFlow()

    private var syncJob: Job? = null
    private var monitorJob: Job? = null
    private var estimateJob: Job? = null
    private var wasConnected: Boolean = false

    init {
        startMonitoring()
    }

    fun onHostChange(value: String) {
        _uiState.update {
            it.copy(host = value, errorMessage = null, pendingCount = null, pendingBytes = null)
        }
        persistConnection()
        scheduleEstimateRefresh()
    }

    fun onPortChange(value: String) {
        _uiState.update {
            it.copy(
                portText = value.filter { ch -> ch.isDigit() },
                errorMessage = null,
                pendingCount = null,
                pendingBytes = null,
            )
        }
        persistConnection()
        scheduleEstimateRefresh()
    }

    fun onTokenChange(value: String) {
        _uiState.update {
            it.copy(token = value, errorMessage = null, pendingCount = null, pendingBytes = null)
        }
        persistConnection()
        scheduleEstimateRefresh()
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
                pendingCount = null,
                pendingBytes = null,
            )
        }
        persistConnection()
        scheduleEstimateRefresh(immediate = true)
    }

    fun refreshLifetimeStats() {
        _uiState.update { it.copy(lifetime = statsStore.load()) }
    }

    fun startSync() {
        if (_uiState.value.isSyncing) {
            return
        }
        val endpoint = currentEndpoint() ?: return
        persistConnection()
        syncJob?.cancel()
        estimateJob?.cancel()
        syncJob =
            viewModelScope.launch {
                _uiState.update {
                    it.copy(
                        isSyncing = true,
                        isEstimating = false,
                        errorMessage = null,
                        lastResult = null,
                        progress = null,
                    )
                }
                try {
                    val result =
                        engine.sync(endpoint) { progress ->
                            _uiState.update { state -> state.copy(progress = progress) }
                        }
                    finishSession(result)
                } catch (_: CancellationException) {
                    val progress = _uiState.value.progress
                    val result =
                        PhotoSyncResult(
                            totalPhotos = progress?.total ?: 0,
                            uploaded = progress?.uploadedCount ?: 0,
                            skipped = 0,
                            failed = 0,
                            uploadedBytes = progress?.uploadedBytes ?: 0L,
                            elapsedMs = progress?.elapsedMs ?: 0L,
                            cancelled = true,
                            message =
                            "Cancelled: uploaded ${progress?.uploadedCount ?: 0}, " +
                                "${PhotoSyncFormat.formatBytes(progress?.uploadedBytes ?: 0L)}, " +
                                PhotoSyncFormat.formatElapsed(progress?.elapsedMs ?: 0L),
                        )
                    finishSession(result)
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
    }

    private fun finishSession(result: PhotoSyncResult) {
        statsStore.recordSession(result.uploaded, result.uploadedBytes)
        _uiState.update {
            it.copy(
                isSyncing = false,
                lastResult = result,
                progress = null,
                lifetime = statsStore.load(),
                errorMessage = if (result.cancelled) "Sync cancelled" else null,
            )
        }
        scheduleEstimateRefresh(immediate = true)
    }

    private fun startMonitoring() {
        monitorJob?.cancel()
        monitorJob =
            viewModelScope.launch {
                while (isActive) {
                    if (!_uiState.value.isSyncing) {
                        probeConnectionOnly()
                    }
                    delay(MONITOR_INTERVAL_MS)
                }
            }
        scheduleEstimateRefresh(immediate = true)
    }

    private fun scheduleEstimateRefresh(immediate: Boolean = false) {
        estimateJob?.cancel()
        estimateJob =
            viewModelScope.launch {
                if (!immediate) {
                    delay(500)
                }
                probeConnectionOnly(runEstimateIfConnected = true)
            }
    }

    private suspend fun probeConnectionOnly(runEstimateIfConnected: Boolean = false) {
        val endpoint = endpointOrNull()
        if (endpoint == null) {
            wasConnected = false
            _uiState.update {
                it.copy(
                    connectionStatus = PhotoSyncConnectionStatus.MissingConfig,
                    pendingCount = null,
                    pendingBytes = null,
                    isEstimating = false,
                )
            }
            return
        }
        _uiState.update { it.copy(connectionStatus = PhotoSyncConnectionStatus.Checking) }
        val connected = engine.probeConnection(endpoint)
        val becameConnected = connected && !wasConnected
        wasConnected = connected
        _uiState.update {
            it.copy(
                connectionStatus =
                if (connected) {
                    PhotoSyncConnectionStatus.Connected
                } else {
                    PhotoSyncConnectionStatus.Disconnected
                },
                pendingCount = if (connected) it.pendingCount else null,
                pendingBytes = if (connected) it.pendingBytes else null,
            )
        }
        if (!connected || _uiState.value.isSyncing) {
            return
        }
        if (runEstimateIfConnected || becameConnected || _uiState.value.pendingCount == null) {
            runEstimate(endpoint)
        }
    }

    private suspend fun runEstimate(endpoint: PhotoSyncEndpoint) {
        _uiState.update { it.copy(isEstimating = true) }
        try {
            val estimate = engine.estimatePending(endpoint)
            _uiState.update {
                it.copy(
                    isEstimating = false,
                    pendingCount = estimate.pendingCount,
                    pendingBytes = estimate.pendingBytes,
                    connectionStatus = PhotoSyncConnectionStatus.Connected,
                )
            }
        } catch (_: CancellationException) {
            _uiState.update { it.copy(isEstimating = false) }
            throw CancellationException()
        } catch (_: IOException) {
            wasConnected = false
            _uiState.update {
                it.copy(
                    isEstimating = false,
                    connectionStatus = PhotoSyncConnectionStatus.Disconnected,
                    pendingCount = null,
                    pendingBytes = null,
                )
            }
        } catch (_: JSONException) {
            wasConnected = false
            _uiState.update {
                it.copy(
                    isEstimating = false,
                    connectionStatus = PhotoSyncConnectionStatus.Disconnected,
                    pendingCount = null,
                    pendingBytes = null,
                )
            }
        } catch (_: IllegalStateException) {
            _uiState.update {
                it.copy(isEstimating = false, pendingCount = null, pendingBytes = null)
            }
        }
    }

    private fun failSync(error: Throwable) {
        val progress = _uiState.value.progress
        if (progress != null && progress.uploadedCount > 0) {
            statsStore.recordSession(progress.uploadedCount, progress.uploadedBytes)
        }
        _uiState.update {
            it.copy(
                isSyncing = false,
                progress = null,
                lifetime = statsStore.load(),
                errorMessage = error.message ?: error.toString(),
            )
        }
        scheduleEstimateRefresh(immediate = true)
    }

    private fun currentEndpoint(): PhotoSyncEndpoint? {
        val endpoint = endpointOrNull()
        if (endpoint == null) {
            _uiState.update {
                it.copy(errorMessage = "Enter host, port, and token from the desktop app")
            }
        }
        return endpoint
    }

    private fun endpointOrNull(): PhotoSyncEndpoint? {
        val state = _uiState.value
        val host = state.host.trim()
        val token = state.token.trim()
        val port = state.portText.toIntOrNull()
        if (host.isEmpty() || token.isEmpty() || port == null) {
            return null
        }
        return PhotoSyncEndpoint(host = host, port = port, token = token)
    }

    private fun persistConnection() {
        val state = _uiState.value
        val port = state.portText.toIntOrNull() ?: PhotoSyncPreferences.DEFAULT_PORT
        prefs.saveConnection(state.host, port, state.token)
    }

    companion object {
        private const val MONITOR_INTERVAL_MS = 8_000L
    }
}
