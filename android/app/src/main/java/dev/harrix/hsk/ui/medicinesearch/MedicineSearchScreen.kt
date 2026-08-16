package dev.harrix.hsk.ui.medicinesearch

import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AddAPhoto
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.Medication
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.UploadFile
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import coil.request.ImageRequest
import coil.size.Size
import dev.harrix.hsk.R
import dev.harrix.hsk.ui.AutoFitText
import dev.harrix.hsk.ui.SimpleMarkdownText
import dev.harrix.hsk.ui.adaptiveContentWidth
import dev.harrix.hsk.ui.theme.HskTopAppBarHeight
import dev.harrix.hsk.ui.theme.hskScaffoldContainerColor
import dev.harrix.hsk.ui.theme.hskScaffoldContentWindowInsets
import dev.harrix.hsk.ui.theme.hskTopAppBarColors
import dev.harrix.hsk.ui.theme.hskTopAppBarWindowInsets
import kotlinx.coroutines.delay

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MedicineSearchScreen(
    onClose: () -> Unit,
    onOpenSettings: () -> Unit,
    settingsRevision: Int,
    modifier: Modifier = Modifier,
    viewModel: MedicineSearchViewModel = viewModel(),
) {
    var phase by viewModel.phase
    var queryText by viewModel.queryText
    val attachedPhotos by viewModel.attachedPhotos
    val resultText by viewModel.resultText
    var hasMedicinesFile by viewModel.hasMedicinesFile
    var errorMessage by viewModel.errorMessage
    var hasApiKey by viewModel.hasApiKey
    val context = LocalContext.current
    val clipboard = LocalClipboardManager.current
    val keyboard = LocalSoftwareKeyboardController.current
    val queryFocusRequester = remember { FocusRequester() }
    val scrollState = rememberScrollState()
    val copiedMessage = stringResource(R.string.medicine_search_copied)
    val isSearching = phase == MedicineSearchPhase.Searching
    val isLoadingFile = phase == MedicineSearchPhase.LoadingFile
    val busy = isSearching || isLoadingFile
    val showResult = resultText.isNotBlank()
    val canAsk = hasApiKey && !isLoadingFile && (queryText.isNotBlank() || attachedPhotos.isNotEmpty())

    fun leave() {
        viewModel.resetSession()
        onClose()
    }

    fun askBotHub() {
        keyboard?.hide()
        viewModel.search()
    }

    BackHandler(onBack = { leave() })

    LaunchedEffect(Unit) {
        // Wait a frame after navigation so the field can accept focus reliably.
        delay(100)
        queryFocusRequester.requestFocus()
        keyboard?.show()
    }

    LaunchedEffect(settingsRevision) {
        viewModel.reloadFromPreferences()
    }

    LaunchedEffect(phase, showResult) {
        if (phase == MedicineSearchPhase.Searching ||
            phase == MedicineSearchPhase.LoadingFile ||
            showResult
        ) {
            scrollState.animateScrollTo(scrollState.maxValue)
        }
    }

    val openDocument =
        rememberLauncherForActivityResult(
            ActivityResultContracts.OpenDocument(),
        ) { uri ->
            if (uri != null) {
                viewModel.onMedicinesFilePicked(uri)
            }
        }

    val pickPhotos =
        rememberLauncherForActivityResult(
            ActivityResultContracts.PickMultipleVisualMedia(MedicineSearchViewModel.MAX_PHOTOS),
        ) { uris ->
            if (uris.isNotEmpty()) {
                viewModel.addPhotos(uris)
            }
        }

    fun pickMedicinesFile() {
        openDocument.launch(arrayOf("text/markdown", "text/plain", "*/*"))
    }

    fun pickAttachedPhotos() {
        pickPhotos.launch(
            PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly),
        )
    }

    Scaffold(
        modifier = modifier.fillMaxSize(),
        containerColor = hskScaffoldContainerColor(),
        contentWindowInsets = hskScaffoldContentWindowInsets(),
        topBar = {
            TopAppBar(
                title = {
                    AutoFitText(
                        text = stringResource(R.string.medicine_search_title),
                        maxLines = 1,
                    )
                },
                colors = hskTopAppBarColors(),
                windowInsets = hskTopAppBarWindowInsets(),
                expandedHeight = HskTopAppBarHeight,
                navigationIcon = {
                    IconButton(onClick = { leave() }) {
                        Icon(
                            imageVector = Icons.Filled.Close,
                            contentDescription = stringResource(R.string.medicine_search_close),
                        )
                    }
                },
                actions = {
                    IconButton(onClick = onOpenSettings, enabled = !busy) {
                        Icon(
                            imageVector = Icons.Filled.Settings,
                            contentDescription =
                            stringResource(R.string.medicine_search_settings),
                        )
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
            Column(
                modifier =
                Modifier
                    .fillMaxSize()
                    .verticalScroll(scrollState)
                    .adaptiveContentWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                if (!hasApiKey) {
                    Text(
                        text = stringResource(R.string.medicine_search_missing_api_key),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.error,
                    )
                }

                if (!hasMedicinesFile) {
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Icon(
                            imageVector = Icons.Filled.Medication,
                            contentDescription = null,
                            modifier = Modifier.size(48.dp),
                            tint = MaterialTheme.colorScheme.primary,
                        )
                        Text(
                            text = stringResource(R.string.medicine_search_empty_title),
                            style = MaterialTheme.typography.titleMedium,
                            textAlign = TextAlign.Center,
                        )
                        Text(
                            text = stringResource(R.string.medicine_search_empty_message),
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            textAlign = TextAlign.Center,
                        )
                        Button(
                            onClick = { pickMedicinesFile() },
                            enabled = !busy,
                        ) {
                            Icon(
                                imageVector = Icons.Filled.UploadFile,
                                contentDescription = null,
                                modifier = Modifier.size(18.dp),
                            )
                            Spacer(modifier = Modifier.size(8.dp))
                            AutoFitText(
                                text = stringResource(R.string.medicine_search_pick_file),
                                maxLines = 2,
                            )
                        }
                        TextButton(
                            onClick = onOpenSettings,
                            enabled = !busy,
                        ) {
                            AutoFitText(
                                text = stringResource(R.string.medicine_search_settings),
                                maxLines = 2,
                            )
                        }
                    }
                }

                val hintColor = MaterialTheme.colorScheme.outlineVariant
                OutlinedTextField(
                    value = queryText,
                    onValueChange = { viewModel.onQueryChange(it) },
                    modifier =
                    Modifier
                        .fillMaxWidth()
                        .focusRequester(queryFocusRequester),
                    enabled = !busy,
                    minLines = 3,
                    maxLines = 6,
                    label = {
                        Text(stringResource(R.string.medicine_search_query_label))
                    },
                    placeholder = {
                        Text(
                            text = stringResource(R.string.medicine_search_query_hint),
                            color = hintColor,
                        )
                    },
                    colors =
                    OutlinedTextFieldDefaults.colors(
                        focusedPlaceholderColor = hintColor,
                        unfocusedPlaceholderColor = hintColor,
                        disabledPlaceholderColor = hintColor.copy(alpha = 0.7f),
                    ),
                )

                AttachedPhotosRow(
                    photos = attachedPhotos,
                    enabled = !busy,
                    canAddMore = attachedPhotos.size < MedicineSearchViewModel.MAX_PHOTOS,
                    onAdd = { pickAttachedPhotos() },
                    onRemove = { viewModel.removePhoto(it) },
                )

                Button(
                    onClick = {
                        if (!isSearching) {
                            askBotHub()
                        }
                    },
                    enabled = canAsk,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    if (isSearching) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(18.dp),
                            strokeWidth = 2.dp,
                            color = MaterialTheme.colorScheme.onPrimary,
                        )
                    } else {
                        Icon(
                            imageVector = Icons.Filled.Search,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp),
                        )
                    }
                    Spacer(modifier = Modifier.size(8.dp))
                    AutoFitText(
                        text =
                        stringResource(
                            if (isSearching) {
                                R.string.medicine_search_searching
                            } else {
                                R.string.medicine_search_search
                            },
                        ),
                        maxLines = 1,
                    )
                }

                if (isLoadingFile) {
                    BusyRow(text = stringResource(R.string.medicine_search_loading_file))
                }

                if (!hasMedicinesFile && phase == MedicineSearchPhase.Idle && !showResult) {
                    Text(
                        text = stringResource(R.string.medicine_search_works_without_file),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                if (showResult) {
                    Text(
                        text = stringResource(R.string.medicine_search_result_label),
                        style = MaterialTheme.typography.titleSmall,
                    )
                    SimpleMarkdownText(
                        markdown = resultText,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    FilledTonalButton(
                        onClick = {
                            clipboard.setText(AnnotatedString(resultText))
                            Toast
                                .makeText(context, copiedMessage, Toast.LENGTH_SHORT)
                                .show()
                        },
                        enabled = !busy,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Icon(
                            imageVector = Icons.Filled.ContentCopy,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp),
                        )
                        Spacer(modifier = Modifier.size(8.dp))
                        AutoFitText(
                            text = stringResource(R.string.medicine_search_copy),
                            maxLines = 1,
                        )
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))
            }
        }
    }

    errorMessage?.let { message ->
        AlertDialog(
            onDismissRequest = { viewModel.clearError() },
            title = { Text(stringResource(R.string.medicine_search_error_title)) },
            text = {
                Text(
                    text = message,
                    modifier = Modifier.verticalScroll(rememberScrollState()),
                )
            },
            confirmButton = {
                TextButton(onClick = { viewModel.clearError() }) {
                    Text(stringResource(R.string.medicine_search_error_ok))
                }
            },
        )
    }
}

@Composable
private fun AttachedPhotosRow(
    photos: List<Uri>,
    enabled: Boolean,
    canAddMore: Boolean,
    onAdd: () -> Unit,
    onRemove: (Uri) -> Unit,
) {
    val context = LocalContext.current
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(
            text = stringResource(R.string.medicine_search_photos_label),
            style = MaterialTheme.typography.titleSmall,
        )
        if (photos.isNotEmpty()) {
            Row(
                modifier =
                Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                photos.forEach { uri ->
                    Box(modifier = Modifier.size(72.dp)) {
                        AsyncImage(
                            model =
                            ImageRequest
                                .Builder(context)
                                .data(uri)
                                .size(Size(144, 144))
                                .crossfade(true)
                                .build(),
                            contentDescription = null,
                            modifier =
                            Modifier
                                .fillMaxSize()
                                .clip(RoundedCornerShape(8.dp)),
                            contentScale = ContentScale.Crop,
                        )
                        IconButton(
                            onClick = { onRemove(uri) },
                            enabled = enabled,
                            modifier =
                            Modifier
                                .align(Alignment.TopEnd)
                                .size(24.dp)
                                .background(
                                    color = MaterialTheme.colorScheme.surface.copy(alpha = 0.85f),
                                    shape = CircleShape,
                                ),
                        ) {
                            Icon(
                                imageVector = Icons.Filled.Close,
                                contentDescription =
                                stringResource(R.string.medicine_search_remove_photo),
                                modifier = Modifier.size(16.dp),
                            )
                        }
                    }
                }
            }
        }
        OutlinedButton(
            onClick = onAdd,
            enabled = enabled && canAddMore,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Icon(
                imageVector = Icons.Filled.AddAPhoto,
                contentDescription = null,
                modifier = Modifier.size(18.dp),
            )
            Spacer(modifier = Modifier.size(8.dp))
            AutoFitText(
                text = stringResource(R.string.medicine_search_add_photo),
                maxLines = 1,
            )
        }
    }
}

@Composable
private fun BusyRow(text: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        CircularProgressIndicator(modifier = Modifier.size(24.dp))
        Text(text = text, style = MaterialTheme.typography.bodyMedium)
    }
}
