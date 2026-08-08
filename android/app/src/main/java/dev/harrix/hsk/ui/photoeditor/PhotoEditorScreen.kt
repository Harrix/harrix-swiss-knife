package dev.harrix.hsk.ui.photoeditor

import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Crop
import androidx.compose.material.icons.filled.Photo
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import dev.harrix.hsk.R
import dev.harrix.hsk.ui.AutoFitText
import dev.harrix.hsk.ui.gallery.EditablePhotoHost

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PhotoEditorScreen(
    onClose: () -> Unit,
    modifier: Modifier = Modifier,
    initialUri: Uri? = null,
    onInitialUriConsume: () -> Unit = {},
    viewModel: PhotoEditorViewModel = viewModel(),
) {
    var currentPhoto by viewModel.currentPhoto
    var imageRevision by viewModel.imageRevision
    var isLoading by viewModel.isLoading
    val repository = viewModel.repository
    val context = LocalContext.current
    val openFailedMessage = stringResource(R.string.photo_editor_open_failed)
    val savedMessage = stringResource(R.string.photo_editor_saved)
    val savedAsCopyFallbackFolder = "Pictures/HSK"
    val onInitialUriConsumeState = rememberUpdatedState(onInitialUriConsume)

    fun showToast(
        message: String,
        long: Boolean = false,
    ) {
        Toast
            .makeText(
                context,
                message,
                if (long) Toast.LENGTH_LONG else Toast.LENGTH_SHORT,
            ).show()
    }

    val pickMedia =
        rememberLauncherForActivityResult(
            ActivityResultContracts.PickVisualMedia(),
        ) { uri ->
            if (uri != null && !viewModel.loadFromUri(uri)) {
                showToast(openFailedMessage)
            }
        }

    LaunchedEffect(initialUri) {
        val uri = initialUri ?: return@LaunchedEffect
        if (!viewModel.applyIncomingUri(uri)) {
            showToast(openFailedMessage)
        }
        onInitialUriConsumeState.value()
    }

    fun leaveEditor() {
        viewModel.resetSession()
        onClose()
    }

    fun openPicker() {
        pickMedia.launch(
            PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly),
        )
    }

    BackHandler {
        if (currentPhoto != null) {
            viewModel.clearPhoto()
        } else {
            leaveEditor()
        }
    }

    Scaffold(
        modifier = modifier.fillMaxSize(),
        contentWindowInsets = WindowInsets.safeDrawing,
        topBar = {
            TopAppBar(
                title = {
                    AutoFitText(
                        text = stringResource(R.string.photo_editor_title),
                        maxLines = 1,
                    )
                },
                navigationIcon = {
                    IconButton(onClick = { leaveEditor() }) {
                        Icon(
                            imageVector = Icons.Filled.Close,
                            contentDescription = stringResource(R.string.photo_editor_close),
                        )
                    }
                },
                actions = {
                    if (currentPhoto != null) {
                        IconButton(onClick = { openPicker() }) {
                            Icon(
                                imageVector = Icons.Filled.Photo,
                                contentDescription =
                                stringResource(R.string.photo_editor_open_photo),
                            )
                        }
                    }
                },
            )
        },
    ) { innerPadding ->
        Box(
            modifier =
            Modifier
                .padding(innerPadding)
                .fillMaxSize(),
        ) {
            when {
                isLoading -> {
                    CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
                }

                currentPhoto != null -> {
                    val photo = currentPhoto!!
                    EditablePhotoHost(
                        photo = photo,
                        imageRevision = imageRevision,
                        allowSaveCopyFallback = false,
                        showSaveCopyButton = true,
                        repository = repository,
                        onSave = { result ->
                            viewModel.applySaved(result.photo, result.sizeBytes)
                            showToast(
                                message =
                                if (result.savedAsCopy) {
                                    context.getString(
                                        R.string.photo_editor_saved_as_copy,
                                        result.copyFolderLabel ?: savedAsCopyFallbackFolder,
                                    )
                                } else {
                                    savedMessage
                                },
                                long = result.savedAsCopy,
                            )
                        },
                        onDiscard = {
                            // Remount editor with a clean crop/rotation state.
                            imageRevision += 1
                        },
                        onError = { message -> showToast(message, long = true) },
                        modifier = Modifier.fillMaxSize(),
                    )
                }

                else -> {
                    Column(
                        modifier =
                        Modifier
                            .fillMaxSize()
                            .padding(24.dp),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally,
                    ) {
                        Icon(
                            imageVector = Icons.Filled.Crop,
                            contentDescription = null,
                            modifier = Modifier.size(56.dp),
                            tint = MaterialTheme.colorScheme.primary,
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = stringResource(R.string.photo_editor_empty_title),
                            style = MaterialTheme.typography.titleMedium,
                            textAlign = TextAlign.Center,
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = stringResource(R.string.photo_editor_empty_message),
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            textAlign = TextAlign.Center,
                        )
                        Spacer(modifier = Modifier.height(24.dp))
                        Button(onClick = { openPicker() }) {
                            AutoFitText(text = stringResource(R.string.photo_editor_open_photo), maxLines = 2)
                        }
                    }
                }
            }
        }
    }
}
