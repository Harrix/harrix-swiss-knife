package dev.harrix.hsk.ui.speechtotext

import android.Manifest
import android.content.pm.PackageManager
import android.widget.Toast
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Stop
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
import androidx.core.content.ContextCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import dev.harrix.hsk.R
import dev.harrix.hsk.ui.AutoFitText

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun SpeechToTextScreen(
    onClose: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: SpeechToTextViewModel = viewModel(),
) {
    var phase by viewModel.phase
    var resultText by viewModel.resultText
    var errorMessage by viewModel.errorMessage
    var infoMessage by viewModel.infoMessage
    var hasApiKey by viewModel.hasApiKey
    val context = LocalContext.current
    val clipboard = LocalClipboardManager.current
    val copiedMessage = stringResource(R.string.speech_to_text_copied)

    fun leave() {
        viewModel.resetSession()
        onClose()
    }

    fun showToast(message: String) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }

    val permissionLauncher =
        rememberLauncherForActivityResult(
            ActivityResultContracts.RequestPermission(),
        ) { granted ->
            if (granted) {
                viewModel.startRecording()
            } else {
                viewModel.errorMessage.value =
                    context.getString(R.string.speech_to_text_permission_denied)
            }
        }

    fun startOrRequestMic() {
        val granted =
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.RECORD_AUDIO,
            ) == PackageManager.PERMISSION_GRANTED
        if (granted) {
            viewModel.startRecording()
        } else {
            permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
        }
    }

    BackHandler {
        when (phase) {
            SpeechToTextPhase.Recording -> viewModel.cancelRecording()

            SpeechToTextPhase.Recognizing,
            SpeechToTextPhase.Fixing,
            SpeechToTextPhase.Rewriting,
            -> Unit

            else -> leave()
        }
    }

    LaunchedEffect(infoMessage) {
        val message = infoMessage ?: return@LaunchedEffect
        showToast(message)
        viewModel.clearInfo()
    }

    Scaffold(
        modifier = modifier.fillMaxSize(),
        contentWindowInsets = WindowInsets.safeDrawing,
        topBar = {
            TopAppBar(
                title = {
                    AutoFitText(
                        text = stringResource(R.string.speech_to_text_title),
                        maxLines = 1,
                    )
                },
                navigationIcon = {
                    IconButton(
                        onClick = { leave() },
                        enabled =
                        phase != SpeechToTextPhase.Recognizing &&
                            phase != SpeechToTextPhase.Fixing &&
                            phase != SpeechToTextPhase.Rewriting,
                    ) {
                        Icon(
                            imageVector = Icons.Filled.Close,
                            contentDescription = stringResource(R.string.speech_to_text_close),
                        )
                    }
                },
            )
        },
    ) { innerPadding ->
        Column(
            modifier =
            Modifier
                .padding(innerPadding)
                .fillMaxSize()
                .padding(horizontal = 16.dp, vertical = 12.dp),
        ) {
            if (!hasApiKey) {
                Text(
                    text = stringResource(R.string.speech_to_text_missing_api_key),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.error,
                    modifier = Modifier.fillMaxWidth(),
                )
                Spacer(modifier = Modifier.height(12.dp))
            }

            when (phase) {
                SpeechToTextPhase.Idle -> {
                    IdleContent(
                        onRecord = { startOrRequestMic() },
                        enabled = hasApiKey,
                    )
                }

                SpeechToTextPhase.Recording -> {
                    RecordingContent(
                        onStop = { viewModel.stopRecordingAndProcess() },
                        onCancel = { viewModel.cancelRecording() },
                    )
                }

                SpeechToTextPhase.Recognizing,
                SpeechToTextPhase.Fixing,
                SpeechToTextPhase.Rewriting,
                -> {
                    BusyContent(phase = phase)
                }

                SpeechToTextPhase.Result -> {
                    ResultContent(
                        text = resultText,
                        onTextChange = { resultText = it },
                        onCopy = {
                            clipboard.setText(AnnotatedString(resultText))
                            showToast(copiedMessage)
                        },
                        onRewrite = { viewModel.rewrite() },
                        onRecordNew = { startOrRequestMic() },
                        onSingleLine = { viewModel.collapseToSingleLine() },
                    )
                }
            }
        }
    }

    errorMessage?.let { message ->
        AlertDialog(
            onDismissRequest = { viewModel.clearError() },
            title = { Text(stringResource(R.string.speech_to_text_error_title)) },
            text = { Text(message) },
            confirmButton = {
                TextButton(onClick = { viewModel.clearError() }) {
                    Text(stringResource(R.string.speech_to_text_error_ok))
                }
            },
        )
    }
}

@Composable
private fun IdleContent(
    onRecord: () -> Unit,
    enabled: Boolean,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = stringResource(R.string.speech_to_text_idle_message),
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.fillMaxWidth(),
        )
        Spacer(modifier = Modifier.height(24.dp))
        Button(
            onClick = onRecord,
            enabled = enabled,
        ) {
            Icon(
                imageVector = Icons.Filled.Mic,
                contentDescription = null,
                modifier = Modifier.size(20.dp),
            )
            Spacer(modifier = Modifier.size(8.dp))
            Text(stringResource(R.string.speech_to_text_record))
        }
    }
}

@Composable
private fun RecordingContent(
    onStop: () -> Unit,
    onCancel: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = stringResource(R.string.speech_to_text_recording),
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.error,
        )
        Spacer(modifier = Modifier.height(24.dp))
        Button(onClick = onStop) {
            Icon(
                imageVector = Icons.Filled.Stop,
                contentDescription = null,
                modifier = Modifier.size(20.dp),
            )
            Spacer(modifier = Modifier.size(8.dp))
            Text(stringResource(R.string.speech_to_text_stop))
        }
        Spacer(modifier = Modifier.height(12.dp))
        OutlinedButton(onClick = onCancel) {
            Text(stringResource(R.string.speech_to_text_cancel_recording))
        }
    }
}

@Composable
private fun BusyContent(
    phase: SpeechToTextPhase,
    modifier: Modifier = Modifier,
) {
    val messageRes =
        when (phase) {
            SpeechToTextPhase.Recognizing -> R.string.speech_to_text_recognizing
            SpeechToTextPhase.Fixing -> R.string.speech_to_text_fixing
            SpeechToTextPhase.Rewriting -> R.string.speech_to_text_rewriting
            else -> R.string.speech_to_text_recognizing
        }
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.Center,
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            CircularProgressIndicator()
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = stringResource(messageRes),
                style = MaterialTheme.typography.bodyLarge,
            )
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun ResultContent(
    text: String,
    onTextChange: (String) -> Unit,
    onCopy: () -> Unit,
    onRewrite: () -> Unit,
    onRecordNew: () -> Unit,
    onSingleLine: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(modifier = modifier.fillMaxSize()) {
        OutlinedTextField(
            value = text,
            onValueChange = onTextChange,
            modifier =
            Modifier
                .weight(1f)
                .fillMaxWidth(),
            textStyle = MaterialTheme.typography.bodyLarge,
            label = { Text(stringResource(R.string.speech_to_text_result_label)) },
        )
        Spacer(modifier = Modifier.height(12.dp))
        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.fillMaxWidth(),
        ) {
            FilledTonalButton(onClick = onCopy) {
                Icon(
                    imageVector = Icons.Filled.ContentCopy,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp),
                )
                Spacer(modifier = Modifier.size(6.dp))
                Text(stringResource(R.string.speech_to_text_copy))
            }
            OutlinedButton(onClick = onRewrite) {
                Text(stringResource(R.string.speech_to_text_rewrite))
            }
            OutlinedButton(onClick = onSingleLine) {
                Text(stringResource(R.string.speech_to_text_single_line))
            }
            Button(onClick = onRecordNew) {
                Icon(
                    imageVector = Icons.Filled.Mic,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp),
                )
                Spacer(modifier = Modifier.size(6.dp))
                Text(stringResource(R.string.speech_to_text_record_new))
            }
        }
    }
}
