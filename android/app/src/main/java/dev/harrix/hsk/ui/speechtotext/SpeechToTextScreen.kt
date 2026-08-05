package dev.harrix.hsk.ui.speechtotext

import android.Manifest
import android.content.pm.PackageManager
import android.widget.Toast
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Refresh
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
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import dev.harrix.hsk.R
import dev.harrix.hsk.speechtotext.AudioRecorder
import dev.harrix.hsk.speechtotext.WaveformBucket
import dev.harrix.hsk.ui.AutoFitText

private enum class MicAction {
    Start,
    Continue,
    Rerecord,
}

private val WaveformBg = Color(0xFF1E1E1E)
private val WaveformGrid = Color(0xFF3A3A3A)
private val WaveformCenter = Color(0xFF616161)
private val WaveformFill = Color(0xC84CAF50)
private val WaveformLiveFill = Color(0xD266BB6A)
private val WaveformOutline = Color(0xFF81C784)

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
    val recordingDurationSeconds by viewModel.recordingDurationSeconds
    val waveformBuckets = viewModel.waveformBuckets
    val context = LocalContext.current
    val clipboard = LocalClipboardManager.current
    val copiedMessage = stringResource(R.string.speech_to_text_copied)

    var pendingMicAction by remember { mutableStateOf<MicAction?>(null) }

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
            val action = pendingMicAction
            pendingMicAction = null
            if (granted) {
                when (action) {
                    MicAction.Continue -> viewModel.continueRecording()
                    MicAction.Rerecord -> viewModel.rerecord()
                    MicAction.Start, null -> viewModel.startRecording()
                }
            } else {
                viewModel.errorMessage.value =
                    context.getString(R.string.speech_to_text_permission_denied)
            }
        }

    fun startOrRequestMic(action: MicAction = MicAction.Start) {
        val granted =
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.RECORD_AUDIO,
            ) == PackageManager.PERMISSION_GRANTED
        if (granted) {
            when (action) {
                MicAction.Continue -> viewModel.continueRecording()
                MicAction.Rerecord -> viewModel.rerecord()
                MicAction.Start -> viewModel.startRecording()
            }
        } else {
            pendingMicAction = action
            permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
        }
    }

    BackHandler {
        when (phase) {
            SpeechToTextPhase.Recording -> viewModel.cancelRecording()

            SpeechToTextPhase.Recorded -> viewModel.discardRecording()

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
                        onRecord = { startOrRequestMic(MicAction.Start) },
                        enabled = hasApiKey,
                    )
                }

                SpeechToTextPhase.Recording -> {
                    RecordingContent(
                        buckets = waveformBuckets,
                        durationLabel = AudioRecorder.formatDuration(recordingDurationSeconds),
                        live = true,
                        onStop = { viewModel.stopRecording() },
                        onCancel = { viewModel.cancelRecording() },
                    )
                }

                SpeechToTextPhase.Recorded -> {
                    RecordedContent(
                        buckets = waveformBuckets,
                        durationLabel = AudioRecorder.formatDuration(recordingDurationSeconds),
                        onContinue = { startOrRequestMic(MicAction.Continue) },
                        onRerecord = { startOrRequestMic(MicAction.Rerecord) },
                        onRecognize = { viewModel.recognizeRecording() },
                        onDiscard = { viewModel.discardRecording() },
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
                        onRecordNew = { startOrRequestMic(MicAction.Start) },
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
    buckets: List<WaveformBucket>,
    durationLabel: String,
    live: Boolean,
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
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = durationLabel,
            style = MaterialTheme.typography.headlineMedium,
        )
        Spacer(modifier = Modifier.height(16.dp))
        WaveformView(
            buckets = buckets,
            live = live,
            modifier =
            Modifier
                .fillMaxWidth()
                .height(96.dp),
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

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun RecordedContent(
    buckets: List<WaveformBucket>,
    durationLabel: String,
    onContinue: () -> Unit,
    onRerecord: () -> Unit,
    onRecognize: () -> Unit,
    onDiscard: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = stringResource(R.string.speech_to_text_recorded_ready),
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center,
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = durationLabel,
            style = MaterialTheme.typography.headlineMedium,
        )
        Spacer(modifier = Modifier.height(16.dp))
        WaveformView(
            buckets = buckets,
            live = false,
            modifier =
            Modifier
                .fillMaxWidth()
                .height(96.dp),
        )
        Spacer(modifier = Modifier.height(24.dp))
        Button(
            onClick = onRecognize,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.speech_to_text_recognize))
        }
        Spacer(modifier = Modifier.height(12.dp))
        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.fillMaxWidth(),
        ) {
            FilledTonalButton(onClick = onContinue) {
                Icon(
                    imageVector = Icons.Filled.PlayArrow,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp),
                )
                Spacer(modifier = Modifier.size(6.dp))
                Text(stringResource(R.string.speech_to_text_continue))
            }
            OutlinedButton(onClick = onRerecord) {
                Icon(
                    imageVector = Icons.Filled.Refresh,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp),
                )
                Spacer(modifier = Modifier.size(6.dp))
                Text(stringResource(R.string.speech_to_text_rerecord))
            }
            OutlinedButton(onClick = onDiscard) {
                Text(stringResource(R.string.speech_to_text_discard_recording))
            }
        }
    }
}

@Composable
private fun WaveformView(
    buckets: List<WaveformBucket>,
    live: Boolean,
    modifier: Modifier = Modifier,
) {
    val displayBuckets =
        if (live && buckets.size > AudioRecorder.LIVE_BUCKET_COUNT) {
            buckets.takeLast(AudioRecorder.LIVE_BUCKET_COUNT)
        } else {
            buckets
        }
    val fill = if (live) WaveformLiveFill else WaveformFill
    Canvas(
        modifier =
        modifier
            .background(WaveformBg, RoundedCornerShape(8.dp))
            .padding(4.dp),
    ) {
        val width = size.width
        val height = size.height
        if (width <= 0f || height <= 0f) {
            return@Canvas
        }
        val margin = 8.dp.toPx()
        val centerY = height / 2f
        val halfHeight = maxOf(4f, (height - margin * 2f) / 2f)

        for (ratio in listOf(0.25f, 0.75f)) {
            val gridY = margin + ratio * (height - margin * 2f)
            drawLine(
                color = WaveformGrid,
                start = Offset(0f, gridY),
                end = Offset(width, gridY),
                strokeWidth = 1f,
            )
        }
        drawLine(
            color = WaveformCenter,
            start = Offset(0f, centerY),
            end = Offset(width, centerY),
            strokeWidth = 1f,
        )

        if (displayBuckets.isEmpty()) {
            return@Canvas
        }

        val bucketWidth = width / displayBuckets.size
        val path = Path()
        path.moveTo(0f, centerY)
        displayBuckets.forEachIndexed { index, bucket ->
            val x = index * bucketWidth + bucketWidth / 2f
            path.lineTo(x, centerY - bucket.peakPos * halfHeight)
        }
        val lastX = (displayBuckets.size - 1) * bucketWidth + bucketWidth / 2f
        path.lineTo(lastX, centerY)
        for (index in displayBuckets.lastIndex downTo 0) {
            val bucket = displayBuckets[index]
            val x = index * bucketWidth + bucketWidth / 2f
            path.lineTo(x, centerY - bucket.peakNeg * halfHeight)
        }
        path.close()
        drawPath(path = path, color = fill)
        drawPath(path = path, color = WaveformOutline, style = Stroke(width = 1.5f))
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
