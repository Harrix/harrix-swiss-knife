package dev.harrix.hsk.ui.gallery

import android.app.Activity
import android.content.IntentSender
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.IntentSenderRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.CameraPhoto
import dev.harrix.hsk.gallery.NormalizedCropRect
import dev.harrix.hsk.gallery.PendingEditUndo
import dev.harrix.hsk.gallery.PhotoEditSaver
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/** Outcome of a successful edit save from [EditablePhotoHost]. */
data class EditablePhotoSaveResult(
    val photo: CameraPhoto,
    val sizeBytes: Long,
    val backupCreated: Boolean,
    val savedAsCopy: Boolean,
    val outputUri: Uri,
)

/**
 * Shared crop/straighten editor with overwrite → write-request → optional copy fallback.
 */
@Composable
fun EditablePhotoHost(
    photo: CameraPhoto,
    imageRevision: Int,
    onSave: (EditablePhotoSaveResult) -> Unit,
    onDiscard: () -> Unit,
    onError: (String) -> Unit,
    createWriteRequest: (Uri) -> IntentSender,
    modifier: Modifier = Modifier,
    existingUndo: PendingEditUndo? = null,
    allowSaveCopyFallback: Boolean = false,
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val photoEditSaver = remember { PhotoEditSaver(context.applicationContext) }
    var rotationDegrees by remember(photo.id, imageRevision) { mutableFloatStateOf(0f) }
    var cropRect by remember(photo.id, imageRevision) { mutableStateOf(NormalizedCropRect.Full) }
    var isSaving by remember(photo.id, imageRevision) { mutableStateOf(false) }
    val saveFailedMessage = stringResource(R.string.gallery_cleaner_edit_save_failed)

    var pendingRetry by remember { mutableStateOf<(() -> Unit)?>(null) }
    val writeLauncher =
        rememberLauncherForActivityResult(
            ActivityResultContracts.StartIntentSenderForResult(),
        ) { result ->
            if (result.resultCode == Activity.RESULT_OK) {
                pendingRetry?.invoke()
            } else if (allowSaveCopyFallback) {
                pendingRetry = null
                performSaveAsCopy(
                    scope = scope,
                    photoEditSaver = photoEditSaver,
                    photo = photo,
                    rotationDegrees = rotationDegrees,
                    cropRect = cropRect,
                    isSavingSetter = { isSaving = it },
                    onSave = onSave,
                    onError = onError,
                    saveFailedMessage = saveFailedMessage,
                )
            } else {
                isSaving = false
                pendingRetry = null
                onError(saveFailedMessage)
            }
        }

    fun performOverwrite(requestWriteIfNeeded: Boolean) {
        isSaving = true
        scope.launch {
            val result =
                withContext(Dispatchers.IO) {
                    photoEditSaver.save(
                        photoId = photo.id,
                        uri = photo.uri,
                        mimeType = photo.mimeType,
                        rotationDegrees = rotationDegrees,
                        crop = cropRect,
                        existingUndo = existingUndo,
                    )
                }
            when (result) {
                is PhotoEditSaver.SaveResult.Success -> {
                    isSaving = false
                    onSave(
                        EditablePhotoSaveResult(
                            photo = photo,
                            sizeBytes = result.sizeBytes,
                            backupCreated = result.backupCreated,
                            savedAsCopy = false,
                            outputUri = photo.uri,
                        ),
                    )
                }

                PhotoEditSaver.SaveResult.NeedsWritePermission -> {
                    val canRequest =
                        requestWriteIfNeeded &&
                            PhotoEditSaver.canRequestMediaStoreWrite(photo.uri)
                    if (canRequest) {
                        pendingRetry = { performOverwrite(requestWriteIfNeeded = false) }
                        writeLauncher.launch(
                            IntentSenderRequest.Builder(createWriteRequest(photo.uri)).build(),
                        )
                    } else if (allowSaveCopyFallback) {
                        performSaveAsCopy(
                            scope = scope,
                            photoEditSaver = photoEditSaver,
                            photo = photo,
                            rotationDegrees = rotationDegrees,
                            cropRect = cropRect,
                            isSavingSetter = { isSaving = it },
                            onSave = onSave,
                            onError = onError,
                            saveFailedMessage = saveFailedMessage,
                        )
                    } else {
                        isSaving = false
                        onError(saveFailedMessage)
                    }
                }

                PhotoEditSaver.SaveResult.Failed -> {
                    if (allowSaveCopyFallback) {
                        performSaveAsCopy(
                            scope = scope,
                            photoEditSaver = photoEditSaver,
                            photo = photo,
                            rotationDegrees = rotationDegrees,
                            cropRect = cropRect,
                            isSavingSetter = { isSaving = it },
                            onSave = onSave,
                            onError = onError,
                            saveFailedMessage = saveFailedMessage,
                        )
                    } else {
                        isSaving = false
                        onError(saveFailedMessage)
                    }
                }
            }
        }
    }

    PhotoCropEditor(
        photo = photo,
        rotationDegrees = rotationDegrees,
        onRotationDegreesChange = { rotationDegrees = it },
        cropRect = cropRect,
        onCropRectChange = { cropRect = it },
        imageRevision = imageRevision,
        isSaving = isSaving,
        onSave = { performOverwrite(requestWriteIfNeeded = true) },
        onDiscard = onDiscard,
        modifier = modifier.fillMaxSize(),
    )
}

private fun performSaveAsCopy(
    scope: CoroutineScope,
    photoEditSaver: PhotoEditSaver,
    photo: CameraPhoto,
    rotationDegrees: Float,
    cropRect: NormalizedCropRect,
    isSavingSetter: (Boolean) -> Unit,
    onSave: (EditablePhotoSaveResult) -> Unit,
    onError: (String) -> Unit,
    saveFailedMessage: String,
) {
    isSavingSetter(true)
    scope.launch {
        val result =
            withContext(Dispatchers.IO) {
                photoEditSaver.saveAsCopy(
                    sourceUri = photo.uri,
                    mimeType = photo.mimeType,
                    rotationDegrees = rotationDegrees,
                    crop = cropRect,
                    displayName = photo.displayName,
                )
            }
        isSavingSetter(false)
        when (result) {
            is PhotoEditSaver.CopyResult.Success -> {
                onSave(
                    EditablePhotoSaveResult(
                        photo = photo.copy(uri = result.uri, sizeBytes = result.sizeBytes),
                        sizeBytes = result.sizeBytes,
                        backupCreated = false,
                        savedAsCopy = true,
                        outputUri = result.uri,
                    ),
                )
            }

            PhotoEditSaver.CopyResult.Failed -> onError(saveFailedMessage)
        }
    }
}
