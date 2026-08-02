package dev.harrix.hsk.ui.gallery

import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import dev.harrix.hsk.gallery.CameraVideo

/**
 * Survives configuration changes (rotation). Cleared explicitly when leaving Video Cleaner.
 */
class VideoCleanerViewModel : ViewModel() {
    val selectedIds = mutableStateOf<Set<Long>>(emptySet())
    val pendingTrashIds = mutableStateOf<Set<Long>>(emptySet())
    val pendingTrashBytes = mutableLongStateOf(0L)
    val sort = mutableStateOf(VideoSort.DATE_DESC)
    val playingVideo = mutableStateOf<CameraVideo?>(null)
    val statusMessage = mutableStateOf<String?>(null)
    val sessionDeletedCount = mutableIntStateOf(0)
    val sessionFreedBytes = mutableLongStateOf(0L)
    val showStatsDialog = mutableStateOf(false)

    /** First index / offset restored via [LazyGridState] in the UI. */
    var gridFirstVisibleIndex: Int = 0
    var gridFirstVisibleOffset: Int = 0

    var sessionInitialized: Boolean = false

    fun resetSession() {
        selectedIds.value = emptySet()
        pendingTrashIds.value = emptySet()
        pendingTrashBytes.longValue = 0L
        sort.value = VideoSort.DATE_DESC
        playingVideo.value = null
        statusMessage.value = null
        sessionDeletedCount.intValue = 0
        sessionFreedBytes.longValue = 0L
        showStatsDialog.value = false
        gridFirstVisibleIndex = 0
        gridFirstVisibleOffset = 0
        sessionInitialized = false
    }
}
