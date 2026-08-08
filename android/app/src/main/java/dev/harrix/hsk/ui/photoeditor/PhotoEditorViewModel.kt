package dev.harrix.hsk.ui.photoeditor

import android.app.Application
import android.net.Uri
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import dev.harrix.hsk.gallery.CameraGalleryRepository
import dev.harrix.hsk.gallery.CameraPhoto
import dev.harrix.hsk.gallery.EditableImageLoader
import dev.harrix.hsk.gallery.PhotoEditSaver

/**
 * Survives configuration changes. Cleared when leaving Photo Editor.
 */
class PhotoEditorViewModel(
    application: Application,
) : AndroidViewModel(application) {
    val repository = CameraGalleryRepository(application.applicationContext)
    val photoEditSaver = PhotoEditSaver(application.applicationContext)

    val currentPhoto = mutableStateOf<CameraPhoto?>(null)
    val imageRevision = mutableIntStateOf(0)
    val isOpeningPhoto = mutableStateOf(false)
    val galleryPhotos = mutableStateOf<List<CameraPhoto>>(emptyList())
    val isGalleryLoading = mutableStateOf(false)

    /** Bumps Coil cache keys so overwritten gallery thumbs reload. */
    val galleryThumbRevisions = mutableStateOf<Map<Long, Int>>(emptyMap())
    var galleryInitialized = false
    var gridFirstVisibleIndex = 0
    var gridFirstVisibleOffset = 0
    var appliedSettingsRevision = -1

    /** Last inbound URI applied so the same share is not re-opened after consume. */
    var lastAppliedIncomingUri: String? = null
        private set

    fun openGalleryPhoto(photo: CameraPhoto) {
        currentPhoto.value = photo
        imageRevision.intValue = 0
    }

    fun loadFromUri(uri: Uri): Boolean {
        isOpeningPhoto.value = true
        val photo = EditableImageLoader.load(getApplication(), uri)
        isOpeningPhoto.value = false
        if (photo == null) {
            return false
        }
        currentPhoto.value = photo
        imageRevision.intValue = 0
        lastAppliedIncomingUri = uri.toString()
        return true
    }

    fun applyIncomingUri(uri: Uri): Boolean {
        if (lastAppliedIncomingUri == uri.toString() && currentPhoto.value != null) {
            return true
        }
        return loadFromUri(uri)
    }

    fun applySaved(
        photo: CameraPhoto,
        sizeBytes: Long,
    ) {
        val updated = photo.copy(sizeBytes = sizeBytes)
        currentPhoto.value = updated
        galleryPhotos.value =
            galleryPhotos.value.map { item ->
                if (item.id == updated.id) {
                    updated
                } else {
                    item
                }
            }
        val revisions = galleryThumbRevisions.value.toMutableMap()
        revisions[updated.id] = (revisions[updated.id] ?: 0) + 1
        galleryThumbRevisions.value = revisions
        imageRevision.intValue += 1
    }

    fun clearPhoto() {
        currentPhoto.value = null
        imageRevision.intValue = 0
        isOpeningPhoto.value = false
    }

    fun resetSession() {
        photoEditSaver.clearAllEditBackups()
        clearPhoto()
        galleryPhotos.value = emptyList()
        isGalleryLoading.value = false
        galleryThumbRevisions.value = emptyMap()
        galleryInitialized = false
        gridFirstVisibleIndex = 0
        gridFirstVisibleOffset = 0
        appliedSettingsRevision = -1
        lastAppliedIncomingUri = null
    }

    fun markSettingsApplied(revision: Int) {
        appliedSettingsRevision = revision
    }

    override fun onCleared() {
        photoEditSaver.clearAllEditBackups()
        super.onCleared()
    }
}
