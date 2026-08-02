package dev.harrix.hsk.ui.gallery

import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import dev.harrix.hsk.gallery.CameraVideo

/**
 * Survives configuration changes (rotation). Cleared explicitly when leaving Video Cleaner.
 */
class VideoCleanerViewModel : ViewModel() {
    val selectedIds = mutableStateOf<Set<Long>>(emptySet())
    val pendingTrashIds = mutableStateOf<Set<Long>>(emptySet())
    val sort = mutableStateOf(VideoSort.DATE_DESC)
    val playingVideo = mutableStateOf<CameraVideo?>(null)
    val statusMessage = mutableStateOf<String?>(null)

    /** First index / offset restored via [LazyGridState] in the UI. */
    var gridFirstVisibleIndex: Int = 0
    var gridFirstVisibleOffset: Int = 0

    var sessionInitialized: Boolean = false

    fun resetSession() {
        selectedIds.value = emptySet()
        pendingTrashIds.value = emptySet()
        sort.value = VideoSort.DATE_DESC
        playingVideo.value = null
        statusMessage.value = null
        gridFirstVisibleIndex = 0
        gridFirstVisibleOffset = 0
        sessionInitialized = false
    }
}
