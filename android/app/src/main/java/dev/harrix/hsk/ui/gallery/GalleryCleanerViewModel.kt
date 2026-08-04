package dev.harrix.hsk.ui.gallery

import android.app.Application
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import dev.harrix.hsk.gallery.CameraGalleryRepository
import dev.harrix.hsk.gallery.CameraPhoto
import dev.harrix.hsk.gallery.GalleryCleanerPreferences
import dev.harrix.hsk.gallery.GalleryDateFilter
import dev.harrix.hsk.gallery.GalleryReviewOrder
import dev.harrix.hsk.gallery.GallerySessionUndo
import dev.harrix.hsk.gallery.PhotoEditSaver

/**
 * Survives configuration changes (rotation). Cleared explicitly when leaving Gallery Cleaner.
 */
class GalleryCleanerViewModel(
    application: Application,
) : AndroidViewModel(application) {
    val repository = CameraGalleryRepository(application.applicationContext)
    val preferences = GalleryCleanerPreferences(application.applicationContext)
    val photoEditSaver = PhotoEditSaver(application.applicationContext)

    val remainingPhotos = mutableStateOf<List<CameraPhoto>>(emptyList())
    val currentPhoto = mutableStateOf<CameraPhoto?>(null)
    val remainingCount = mutableIntStateOf(0)
    val undoStack = mutableStateOf<List<GallerySessionUndo>>(emptyList())
    val cardResetKey = mutableIntStateOf(0)
    val dateFilter = mutableStateOf(GalleryDateFilter(enabled = false))
    val unreviewedOnlyMode = mutableStateOf(preferences.isUnreviewedOnlyModeEnabled())
    val reviewOrder = mutableStateOf(preferences.getReviewOrder())
    val sessionReviewedCount = mutableIntStateOf(0)
    val sessionDeletedCount = mutableIntStateOf(0)
    val sessionFreedBytes = mutableLongStateOf(0L)
    val isEditing = mutableStateOf(false)
    val editImageRevision = mutableIntStateOf(0)
    val pendingTrashPhoto = mutableStateOf<CameraPhoto?>(null)
    val pendingRestorePhoto = mutableStateOf<CameraPhoto?>(null)
    val pendingWritePhoto = mutableStateOf<CameraPhoto?>(null)
    val showIntro = mutableStateOf(preferences.shouldShowIntro())
    val dontShowAgain = mutableStateOf(false)
    val showStatsDialog = mutableStateOf(false)
    val statusMessage = mutableStateOf<String?>(null)
    val isLoading = mutableStateOf(false)

    /** Unreviewed photos in folder ignoring the date filter (for empty-state hints). */
    val unreviewedCountIgnoringDateFilter = mutableIntStateOf(0)

    /** False until the first successful session bootstrap after opening the utility. */
    var sessionInitialized: Boolean = false
        private set

    var appliedSettingsRevision: Int = -1
        private set

    fun markSessionInitialized(settingsRevision: Int) {
        sessionInitialized = true
        appliedSettingsRevision = settingsRevision
    }

    fun markSettingsApplied(settingsRevision: Int) {
        appliedSettingsRevision = settingsRevision
    }

    fun bootstrapDateFilter() {
        preferences.clearDateFilter()
        dateFilter.value = preferences.loadDateFilter()
    }

    fun resetSession() {
        photoEditSaver.clearAllEditBackups()
        remainingPhotos.value = emptyList()
        currentPhoto.value = null
        remainingCount.intValue = 0
        undoStack.value = emptyList()
        cardResetKey.intValue = 0
        dateFilter.value = GalleryDateFilter(enabled = false)
        unreviewedOnlyMode.value = preferences.isUnreviewedOnlyModeEnabled()
        reviewOrder.value = preferences.getReviewOrder()
        sessionReviewedCount.intValue = 0
        sessionDeletedCount.intValue = 0
        sessionFreedBytes.longValue = 0L
        isEditing.value = false
        editImageRevision.intValue = 0
        pendingTrashPhoto.value = null
        pendingRestorePhoto.value = null
        pendingWritePhoto.value = null
        showIntro.value = preferences.shouldShowIntro()
        dontShowAgain.value = false
        showStatsDialog.value = false
        statusMessage.value = null
        isLoading.value = false
        unreviewedCountIgnoringDateFilter.intValue = 0
        sessionInitialized = false
        appliedSettingsRevision = -1
    }

    override fun onCleared() {
        photoEditSaver.clearAllEditBackups()
        super.onCleared()
    }
}
