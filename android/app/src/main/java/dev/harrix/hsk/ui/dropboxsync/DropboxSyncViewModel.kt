package dev.harrix.hsk.ui.dropboxsync

import android.app.Application
import android.content.Intent
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import dev.harrix.hsk.dropboxsync.DropboxApiClient
import dev.harrix.hsk.dropboxsync.DropboxAuthManager
import dev.harrix.hsk.dropboxsync.DropboxRemoteItem
import dev.harrix.hsk.dropboxsync.DropboxSyncPreferences
import dev.harrix.hsk.dropboxsync.DropboxSyncWorker
import dev.harrix.hsk.dropboxsync.FolderPair
import dev.harrix.hsk.dropboxsync.SyncEngine
import dev.harrix.hsk.dropboxsync.SyncLogRow
import dev.harrix.hsk.dropboxsync.SyncProgress
import dev.harrix.hsk.dropboxsync.SyncResult
import dev.harrix.hsk.dropboxsync.SyncStateDatabase
import dev.harrix.hsk.dropboxsync.SyncTrigger
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class DropboxSyncViewModel(
    application: Application,
) : AndroidViewModel(application) {
    private val preferences = DropboxSyncPreferences(application)
    private val database = SyncStateDatabase(application)
    private val authManager = DropboxAuthManager(application, preferences)
    private val apiClient = DropboxApiClient(authManager)
    private val engine = SyncEngine.get(application)

    private val _pairs = MutableStateFlow<List<FolderPair>>(emptyList())
    val pairs: StateFlow<List<FolderPair>> = _pairs.asStateFlow()

    private val _accountLabel = MutableStateFlow(authManager.accountLabel())
    val accountLabel: StateFlow<String> = _accountLabel.asStateFlow()

    private val _connected = MutableStateFlow(authManager.isConnected())
    val connected: StateFlow<Boolean> = _connected.asStateFlow()

    private val _message = MutableStateFlow<String?>(null)
    val message: StateFlow<String?> = _message.asStateFlow()

    private val _dryRunResult = MutableStateFlow<SyncResult?>(null)
    val dryRunResult: StateFlow<SyncResult?> = _dryRunResult.asStateFlow()

    private val _logs = MutableStateFlow<List<SyncLogRow>>(emptyList())
    val logs: StateFlow<List<SyncLogRow>> = _logs.asStateFlow()

    private val _remoteItems = MutableStateFlow<List<DropboxRemoteItem>>(emptyList())
    val remoteItems: StateFlow<List<DropboxRemoteItem>> = _remoteItems.asStateFlow()

    private val _remotePath = MutableStateFlow("")
    val remotePath: StateFlow<String> = _remotePath.asStateFlow()

    val progress: StateFlow<SyncProgress?> =
        engine.progress.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)

    init {
        refresh()
    }

    fun refresh() {
        _pairs.value = database.listPairs()
        _connected.value = authManager.isConnected()
        _accountLabel.value = authManager.accountLabel()
    }

    fun clearMessage() {
        _message.value = null
    }

    fun clearDryRun() {
        _dryRunResult.value = null
    }

    fun beginConnect(openUri: (Uri) -> Unit) {
        runCatching {
            if (!authManager.isConfigured()) {
                _message.value = "Configure Dropbox App Key in settings first"
                return
            }
            openUri(authManager.buildAuthorizeUri())
        }.onFailure {
            _message.value = it.message
        }
    }

    fun handleOAuthRedirect(uri: Uri) {
        viewModelScope.launch {
            val result = withContext(Dispatchers.IO) { authManager.handleRedirect(uri) }
            result
                .onSuccess {
                    runCatching {
                        withContext(Dispatchers.IO) {
                            val account = apiClient.getCurrentAccount()
                            preferences.saveAccount(account.displayName, account.email)
                        }
                    }
                    refresh()
                    _message.value = "Dropbox connected"
                }.onFailure {
                    _message.value = it.message
                }
        }
    }

    fun disconnect() {
        authManager.disconnect()
        refresh()
    }

    fun savePair(pair: FolderPair) {
        viewModelScope.launch(Dispatchers.IO) {
            if (pair.id == 0L) {
                database.insertPair(pair)
            } else {
                database.updatePair(pair)
            }
            withContext(Dispatchers.Main) { refresh() }
        }
    }

    fun deletePair(id: Long) {
        viewModelScope.launch(Dispatchers.IO) {
            database.deletePair(id)
            withContext(Dispatchers.Main) { refresh() }
        }
    }

    fun clearBaseline(id: Long) {
        viewModelScope.launch(Dispatchers.IO) {
            database.clearBaseline(id)
            withContext(Dispatchers.Main) {
                _message.value = "Sync state cache cleared"
            }
        }
    }

    fun syncPair(id: Long) {
        DropboxSyncWorker.enqueueOneShot(getApplication(), id, SyncTrigger.Manual)
        _message.value = "Sync started"
    }

    fun syncAll() {
        DropboxSyncWorker.enqueueOneShot(getApplication(), null, SyncTrigger.Manual)
        _message.value = "Sync all started"
    }

    fun dryRun(id: Long) {
        viewModelScope.launch {
            val result = engine.syncPair(id, SyncTrigger.Manual, dryRun = true)
            _dryRunResult.value = result
        }
    }

    fun loadLogs(pairId: Long) {
        viewModelScope.launch(Dispatchers.IO) {
            _logs.value = database.listLogs(pairId)
        }
    }

    fun pendingConfirmation(pairId: Long) = engine.getPendingConfirmation(pairId)

    fun applyConfirmation(
        pairId: Long,
        selected: Set<String>,
    ) {
        viewModelScope.launch {
            val result = engine.applyPendingConfirmation(pairId, selected)
            _message.value = result.summary
            refresh()
        }
    }

    fun loadRemoteFolder(path: String = _remotePath.value) {
        viewModelScope.launch {
            runCatching {
                withContext(Dispatchers.IO) {
                    apiClient.listFolderChildren(path)
                }
            }.onSuccess {
                _remotePath.value = path
                _remoteItems.value = it
            }.onFailure {
                _message.value = it.message
            }
        }
    }

    fun createRemoteFolder(name: String) {
        viewModelScope.launch {
            val parent = _remotePath.value
            val full =
                if (parent.isBlank() || parent == "/") {
                    "/$name"
                } else {
                    "${parent.trimEnd('/')}/$name"
                }
            runCatching {
                withContext(Dispatchers.IO) { apiClient.createFolder(full) }
            }.onSuccess {
                loadRemoteFolder(parent)
            }.onFailure {
                _message.value = it.message
            }
        }
    }

    fun openAuthorizeUri(uri: Uri) {
        val intent = Intent(Intent.ACTION_VIEW, uri).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        getApplication<Application>().startActivity(intent)
    }

    fun preferences(): DropboxSyncPreferences = preferences

    fun resolveAppKey(): String = authManager.resolveAppKey()
}
