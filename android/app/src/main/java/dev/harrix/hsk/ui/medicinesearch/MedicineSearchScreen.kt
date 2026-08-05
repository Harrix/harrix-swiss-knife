package dev.harrix.hsk.ui.medicinesearch

import android.widget.Toast
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.OpenInNew
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
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import dev.harrix.hsk.R
import dev.harrix.hsk.medicinesearch.MedicinesNoteOpener
import dev.harrix.hsk.ui.AutoFitText
import dev.harrix.hsk.ui.adaptiveContentWidth

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
    var resultText by viewModel.resultText
    var fileDisplayName by viewModel.fileDisplayName
    var medicinesUri by viewModel.medicinesUri
    var hasMedicinesFile by viewModel.hasMedicinesFile
    var errorMessage by viewModel.errorMessage
    var hasApiKey by viewModel.hasApiKey
    val context = LocalContext.current
    val clipboard = LocalClipboardManager.current
    val copiedMessage = stringResource(R.string.medicine_search_copied)
    val openFailedMessage = stringResource(R.string.medicine_search_open_failed)
    val busy =
        phase == MedicineSearchPhase.Searching ||
            phase == MedicineSearchPhase.LoadingFile

    fun leave() {
        viewModel.resetSession()
        onClose()
    }

    fun openMedicinesNote() {
        val uri = medicinesUri
        if (uri == null) {
            return
        }
        val opened = MedicinesNoteOpener.open(context, uri)
        if (!opened) {
            Toast.makeText(context, openFailedMessage, Toast.LENGTH_SHORT).show()
        }
    }

    BackHandler(onBack = { leave() })

    LaunchedEffect(settingsRevision) {
        viewModel.reloadFromPreferences()
    }

    val openDocument =
        rememberLauncherForActivityResult(
            ActivityResultContracts.OpenDocument(),
        ) { uri ->
            if (uri != null) {
                viewModel.onMedicinesFilePicked(uri)
            }
        }

    fun pickMedicinesFile() {
        openDocument.launch(arrayOf("text/markdown", "text/plain", "*/*"))
    }

    Scaffold(
        modifier = modifier.fillMaxSize(),
        contentWindowInsets = WindowInsets.safeDrawing,
        topBar = {
            TopAppBar(
                title = {
                    AutoFitText(
                        text = stringResource(R.string.medicine_search_title),
                        maxLines = 1,
                    )
                },
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
                    .verticalScroll(rememberScrollState())
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
                    }
                } else {
                    Text(
                        text =
                        stringResource(
                            R.string.medicine_search_file_label,
                            fileDisplayName
                                ?: stringResource(R.string.medicine_search_file_unnamed),
                        ),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    FilledTonalButton(
                        onClick = { openMedicinesNote() },
                        enabled = !busy && medicinesUri != null,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.OpenInNew,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp),
                        )
                        Spacer(modifier = Modifier.size(8.dp))
                        AutoFitText(
                            text = stringResource(R.string.medicine_search_open_note),
                            maxLines = 2,
                        )
                    }
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        OutlinedButton(
                            onClick = { pickMedicinesFile() },
                            enabled = !busy,
                            modifier = Modifier.weight(1f),
                        ) {
                            AutoFitText(
                                text = stringResource(R.string.medicine_search_change_file),
                                maxLines = 2,
                                textAlign = TextAlign.Center,
                            )
                        }
                        OutlinedButton(
                            onClick = { viewModel.clearMedicinesFile() },
                            enabled = !busy,
                            modifier = Modifier.weight(1f),
                        ) {
                            AutoFitText(
                                text = stringResource(R.string.medicine_search_clear_file),
                                maxLines = 2,
                                textAlign = TextAlign.Center,
                            )
                        }
                    }
                }

                OutlinedTextField(
                    value = queryText,
                    onValueChange = { viewModel.onQueryChange(it) },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !busy,
                    minLines = 3,
                    maxLines = 6,
                    label = {
                        Text(stringResource(R.string.medicine_search_query_label))
                    },
                    placeholder = {
                        Text(stringResource(R.string.medicine_search_query_hint))
                    },
                )

                Button(
                    onClick = { viewModel.search() },
                    enabled = !busy && queryText.isNotBlank() && hasApiKey,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Icon(
                        imageVector = Icons.Filled.Search,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp),
                    )
                    Spacer(modifier = Modifier.size(8.dp))
                    AutoFitText(
                        text = stringResource(R.string.medicine_search_search),
                        maxLines = 1,
                    )
                }

                when (phase) {
                    MedicineSearchPhase.LoadingFile -> {
                        BusyRow(text = stringResource(R.string.medicine_search_loading_file))
                    }

                    MedicineSearchPhase.Searching -> {
                        BusyRow(text = stringResource(R.string.medicine_search_searching))
                    }

                    MedicineSearchPhase.Result -> {
                        if (resultText.isNotBlank()) {
                            Text(
                                text = stringResource(R.string.medicine_search_result_label),
                                style = MaterialTheme.typography.titleSmall,
                            )
                            OutlinedTextField(
                                value = resultText,
                                onValueChange = { resultText = it },
                                modifier = Modifier.fillMaxWidth(),
                                minLines = 8,
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
                    }

                    MedicineSearchPhase.Idle -> {
                        if (!hasMedicinesFile) {
                            Text(
                                text = stringResource(R.string.medicine_search_works_without_file),
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }
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
