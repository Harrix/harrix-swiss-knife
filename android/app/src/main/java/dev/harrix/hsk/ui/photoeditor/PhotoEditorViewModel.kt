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
    val isLoading = mutableStateOf(false)

    /** Last inbound URI applied so the same share is not re-opened after consume. */
    var lastAppliedIncomingUri: String? = null
        private set

    fun loadFromUri(uri: Uri): Boolean {
        isLoading.value = true
        val photo = EditableImageLoader.load(getApplication(), uri)
        isLoading.value = false
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
        currentPhoto.value = photo.copy(sizeBytes = sizeBytes)
        imageRevision.intValue += 1
    }

    fun clearPhoto() {
        currentPhoto.value = null
        imageRevision.intValue = 0
        isLoading.value = false
    }

    fun resetSession() {
        photoEditSaver.clearAllEditBackups()
        clearPhoto()
        lastAppliedIncomingUri = null
    }

    override fun onCleared() {
        photoEditSaver.clearAllEditBackups()
        super.onCleared()
    }
}
