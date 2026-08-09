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

data class PhotoSyncPendingConfirm(
    val endpoint: PhotoSyncEndpoint,
    val choices: List<String>,
)

data class PhotoSyncUiState(
    val pairedHost: String = "",
    val pairedPort: Int = PhotoSyncPreferences.DEFAULT_PORT,
    val isPaired: Boolean = false,
    val pendingConfirm: PhotoSyncPendingConfirm? = null,
    val isSyncing: Boolean = false,
    val isEstimating: Boolean = false,
    val connectionStatus: PhotoSyncConnectionStatus = PhotoSyncConnectionStatus.Unknown,
    val pendingCount: Int? = null,
    val pendingBytes: Long? = null,
    val progress: PhotoSyncProgress? = null,
    val lastResult: PhotoSyncResult? = null,
    val lifetime: PhotoSyncLifetimeStats = PhotoSyncLifetimeStats(),
    val errorMessage: String? = null,
) {
    /** Sync is allowed only while the desktop receiver accepts this session token. */
    val isDesktopReady: Boolean
        get() = isPaired && connectionStatus == PhotoSyncConnectionStatus.Connected && !isSyncing
}

class PhotoSyncViewModel(
    application: Application,
) : AndroidViewModel(application) {
    private val prefs = PhotoSyncPreferences(application)
    private val statsStore = PhotoSyncStatsStore(application)
    private val engine = PhotoSyncEngine(application)

    private val _uiState =
        MutableStateFlow(
            PhotoSyncUiState(
                lifetime = statsStore.load(),
            ).withSavedEndpoint(prefs.getEndpoint()),
        )
    val uiState: StateFlow<PhotoSyncUiState> = _uiState.asStateFlow()

    private var syncJob: Job? = null
    private var monitorJob: Job? = null
    private var estimateJob: Job? = null
    private var wasConnected: Boolean = false
    private var savedEndpoint: PhotoSyncEndpoint? = prefs.getEndpoint()

    init {
        startMonitoring()
    }

    fun beginPairingFromQr(raw: String) {
        val parsed = PhotoSyncPairing.parse(raw)
        if (parsed == null) {
            _uiState.update {
                it.copy(errorMessage = "Could not read QR. Use Photo sync listen on the computer.")
            }
            return
        }
        _uiState.update {
            it.copy(
                pendingConfirm =
                PhotoSyncPendingConfirm(
                    endpoint = parsed,
                    choices = PhotoSyncPairing.buildConfirmChoices(parsed.confirmCode),
                ),
                errorMessage = null,
                lastResult = null,
            )
        }
    }

    fun confirmPairingChoice(choice: String) {
        val pending = _uiState.value.pendingConfirm ?: return
        if (choice.trim() != pending.endpoint.confirmCode) {
            _uiState.update {
                it.copy(errorMessage = "Wrong number. Pick the code shown on the computer.")
            }
            return
        }
        prefs.saveConnection(pending.endpoint)
        savedEndpoint = pending.endpoint
        _uiState.update {
            it
                .withSavedEndpoint(pending.endpoint)
                .copy(
                    pendingConfirm = null,
                    errorMessage = null,
                    pendingCount = null,
                    pendingBytes = null,
                )
        }
        scheduleEstimateRefresh(immediate = true)
    }

    fun cancelPendingConfirm() {
        _uiState.update { it.copy(pendingConfirm = null, errorMessage = null) }
    }

    fun forgetDesktop() {
        prefs.clearConnection()
        savedEndpoint = null
        wasConnected = false
        _uiState.update {
            it.copy(
                pairedHost = "",
                pairedPort = PhotoSyncPreferences.DEFAULT_PORT,
                isPaired = false,
                pendingConfirm = null,
                connectionStatus = PhotoSyncConnectionStatus.MissingConfig,
                pendingCount = null,
                pendingBytes = null,
                errorMessage = null,
                lastResult = null,
            )
        }
    }

    fun refreshLifetimeStats() {
        _uiState.update { it.copy(lifetime = statsStore.load()) }
    }

    fun startSync() {
        if (!_uiState.value.isDesktopReady) {
            return
        }
        val endpoint = currentEndpoint() ?: return
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
                    if (!_uiState.value.isSyncing && _uiState.value.pendingConfirm == null) {
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
                it.copy(errorMessage = "Scan the QR code from Photo sync listen on the computer")
            }
        }
        return endpoint
    }

    private fun endpointOrNull(): PhotoSyncEndpoint? = savedEndpoint

    companion object {
        private const val MONITOR_INTERVAL_MS = 8_000L
    }
}

private fun PhotoSyncUiState.withSavedEndpoint(endpoint: PhotoSyncEndpoint?): PhotoSyncUiState = if (endpoint == null) {
    copy(
        pairedHost = "",
        pairedPort = PhotoSyncPreferences.DEFAULT_PORT,
        isPaired = false,
    )
} else {
    copy(
        pairedHost = endpoint.host,
        pairedPort = endpoint.port,
        isPaired = true,
    )
}
