package dev.harrix.hsk.ui.health

import android.app.Application
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import dev.harrix.hsk.health.HealthConnectAvailability
import dev.harrix.hsk.health.HealthConnectReader
import dev.harrix.hsk.health.HealthConnectSnapshot
import kotlinx.coroutines.launch

/** UI phase for the Health Connect test screen. */
sealed class HealthConnectUiState {
    data object Loading : HealthConnectUiState()

    data class Unavailable(
        val availability: HealthConnectAvailability,
    ) : HealthConnectUiState()

    data object NeedsPermission : HealthConnectUiState()

    data class Ready(
        val snapshot: HealthConnectSnapshot,
    ) : HealthConnectUiState()

    data class Error(
        val message: String,
    ) : HealthConnectUiState()
}

/**
 * Loads steps and Other workout sessions from Health Connect.
 */
class HealthConnectViewModel(
    application: Application,
) : AndroidViewModel(application) {
    private val reader = HealthConnectReader(application.applicationContext)

    var uiState by mutableStateOf<HealthConnectUiState>(HealthConnectUiState.Loading)
        private set

    val permissionContract = reader.createPermissionContract()
    val requiredPermissions: Set<String>
        get() = reader.clientOrNull()?.let(reader::permissionsToRequest) ?: reader.permissions

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            uiState = HealthConnectUiState.Loading
            val availability = reader.availability()
            if (availability != HealthConnectAvailability.Available) {
                uiState = HealthConnectUiState.Unavailable(availability)
                return@launch
            }
            val client = reader.clientOrNull()
            if (client == null) {
                uiState =
                    HealthConnectUiState.Unavailable(HealthConnectAvailability.Unavailable)
                return@launch
            }
            runCatching {
                if (!reader.hasAllPermissions(client)) {
                    uiState = HealthConnectUiState.NeedsPermission
                    return@launch
                }
                val snapshot = reader.loadSnapshot(client)
                uiState = HealthConnectUiState.Ready(snapshot)
            }.onFailure { error ->
                uiState =
                    HealthConnectUiState.Error(
                        error.message?.takeIf { it.isNotBlank() }
                            ?: error.javaClass.simpleName,
                    )
            }
        }
    }

    fun onPermissionsResult(granted: Set<String>) {
        if (granted.containsAll(reader.permissions)) {
            refresh()
        } else {
            uiState = HealthConnectUiState.NeedsPermission
        }
    }

    fun openHealthConnectSettings() {
        reader.openHealthConnectSettings()
    }
}
