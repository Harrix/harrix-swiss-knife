package dev.harrix.hsk.ui.speechtotext

import android.Manifest
import android.content.ActivityNotFoundException
import android.content.Intent
import android.content.pm.PackageManager
import android.widget.Toast
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.automirrored.filled.ShortText
import androidx.compose.material.icons.filled.AutoFixHigh
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Save
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material.icons.filled.TaskAlt
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
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
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import dev.harrix.hsk.R
import dev.harrix.hsk.speechtotext.AudioRecorder
import dev.harrix.hsk.speechtotext.SpeechMessageStatus
import dev.harrix.hsk.speechtotext.SpeechQueueItem
import dev.harrix.hsk.speechtotext.WaveformBucket
import dev.harrix.hsk.ui.AutoFitText
import dev.harrix.hsk.ui.CompactBottomActionButton
import dev.harrix.hsk.ui.theme.HskTopAppBarHeight
import dev.harrix.hsk.ui.theme.hskScaffoldContainerColor
import dev.harrix.hsk.ui.theme.hskScaffoldContentWindowInsets
import dev.harrix.hsk.ui.theme.hskTopAppBarColors
import dev.harrix.hsk.ui.theme.hskTopAppBarWindowInsets

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
private val DoneCardGreen = Color(0xFF2E7D32)
private val SlowWarningAmber = Color(0xFFFFA000)
private val RecordButtonRed = Color(0xFFE53935)
private val RecordButtonRedPressed = Color(0xFFC62828)
private val RecordButtonRedDisabled = Color(0xFFEF9A9A)
private const val TickTickPackage = "com.ticktick.task"
private val RecordButtonSize = 56.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SpeechToTextScreen(
    onClose: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: SpeechToTextViewModel = viewModel(),
) {
    val composerPhase by viewModel.composerPhase
    var errorMessage by viewModel.errorMessage
    var infoMessage by viewModel.infoMessage
    var hasApiKey by viewModel.hasApiKey
    val recordingDurationSeconds by viewModel.recordingDurationSeconds
    val averageRecognitionMs by viewModel.averageRecognitionMs
    val waveformBuckets = viewModel.waveformBuckets
    val items = viewModel.items
    val context = LocalContext.current
    val clipboard = LocalClipboardManager.current
    val copiedMessage = stringResource(R.string.speech_to_text_copied)
    val shareFailedMessage = stringResource(R.string.speech_to_text_share_failed)
    val shareChooserTitle = stringResource(R.string.speech_to_text_share)
    val tickTickUnavailableMessage = stringResource(R.string.speech_to_text_ticktick_unavailable)

    var pendingMicAction by remember { mutableStateOf<MicAction?>(null) }
    var saveTargetId by remember { mutableStateOf<String?>(null) }
    var selectedItemId by remember { mutableStateOf<String?>(null) }
    val selectedItem = items.firstOrNull { it.id == selectedItemId }

    fun leaveUtility() {
        viewModel.leaveScreen()
        onClose()
    }

    fun closeDetail() {
        selectedItemId = null
    }

    fun showToast(message: String) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }

    fun shareResultText(text: String) {
        val payload = text.trim()
        if (payload.isEmpty()) {
            return
        }
        val shareIntent =
            Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(Intent.EXTRA_TEXT, payload)
            }
        try {
            context.startActivity(Intent.createChooser(shareIntent, shareChooserTitle))
        } catch (_: ActivityNotFoundException) {
            showToast(shareFailedMessage)
        }
    }

    fun sendResultToTickTick(text: String) {
        val payload = text.trim()
        if (payload.isEmpty()) {
            return
        }
        val tickTickIntent =
            Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                setPackage(TickTickPackage)
                putExtra(Intent.EXTRA_TEXT, payload)
            }
        try {
            context.startActivity(tickTickIntent)
        } catch (_: ActivityNotFoundException) {
            showToast(tickTickUnavailableMessage)
        }
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

    val saveAudioLauncher =
        rememberLauncherForActivityResult(
            ActivityResultContracts.CreateDocument(AudioRecorder.MIME_M4A),
        ) { uri ->
            if (uri != null) {
                val id = saveTargetId
                if (id != null) {
                    viewModel.saveItemAudio(id, uri)
                } else {
                    viewModel.saveDraftAudio(uri)
                }
            }
            saveTargetId = null
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

    LaunchedEffect(selectedItemId, items.size) {
        if (selectedItemId != null && items.none { it.id == selectedItemId }) {
            selectedItemId = null
        }
    }

    BackHandler {
        if (selectedItemId != null) {
            closeDetail()
        } else {
            leaveUtility()
        }
    }

    LaunchedEffect(infoMessage) {
        val message = infoMessage ?: return@LaunchedEffect
        showToast(message)
        viewModel.clearInfo()
    }

    Scaffold(
        modifier = modifier.fillMaxSize(),
        containerColor = hskScaffoldContainerColor(),
        contentWindowInsets = hskScaffoldContentWindowInsets(),
        topBar = {
            TopAppBar(
                title = {
                    AutoFitText(
                        text = stringResource(R.string.speech_to_text_title),
                        maxLines = 1,
                    )
                },
                colors = hskTopAppBarColors(),
                windowInsets = hskTopAppBarWindowInsets(),
                expandedHeight = HskTopAppBarHeight,
                navigationIcon = {
                    if (selectedItem != null) {
                        IconButton(onClick = { closeDetail() }) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                                contentDescription = stringResource(R.string.speech_to_text_back),
                            )
                        }
                    } else {
                        IconButton(onClick = { leaveUtility() }) {
                            Icon(
                                imageVector = Icons.Filled.Close,
                                contentDescription = stringResource(R.string.speech_to_text_close),
                            )
                        }
                    }
                },
            )
        },
    ) { innerPadding ->
        if (selectedItem != null) {
            SpeechMessageDetail(
                item = selectedItem,
                averageRecognitionMs = averageRecognitionMs,
                hasApiKey = hasApiKey,
                modifier =
                Modifier
                    .padding(innerPadding)
                    .fillMaxSize()
                    .padding(horizontal = 16.dp, vertical = 12.dp),
                onRecognize = { viewModel.recognize(selectedItem.id) },
                onCancel = { viewModel.cancelRecognition(selectedItem.id) },
                onDelete = {
                    viewModel.deleteItem(selectedItem.id)
                    closeDetail()
                },
                onTextChange = { viewModel.updateItemText(selectedItem.id, it) },
                onCopy = {
                    clipboard.setText(AnnotatedString(selectedItem.text))
                    showToast(copiedMessage)
                },
                onShare = { shareResultText(selectedItem.text) },
                onSendToTickTick = { sendResultToTickTick(selectedItem.text) },
                onRewrite = { viewModel.rewriteItem(selectedItem.id) },
                onSingleLine = { viewModel.collapseItemToSingleLine(selectedItem.id) },
                onSave = {
                    saveTargetId = selectedItem.id
                    saveAudioLauncher.launch(viewModel.suggestedAudioFileName(selectedItem.id))
                },
            )
        } else {
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

                Column(
                    modifier =
                    Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState()),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    if (items.isEmpty()) {
                        Text(
                            text = stringResource(R.string.speech_to_text_empty_queue),
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.fillMaxWidth().padding(vertical = 24.dp),
                        )
                    }
                    items.asReversed().forEach { item ->
                        SpeechMessageRow(
                            item = item,
                            averageRecognitionMs = averageRecognitionMs,
                            onClick = { selectedItemId = item.id },
                        )
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))
                ComposerBar(
                    phase = composerPhase,
                    hasApiKey = hasApiKey,
                    buckets = waveformBuckets,
                    durationLabel = AudioRecorder.formatDuration(recordingDurationSeconds),
                    onStart = { startOrRequestMic(MicAction.Start) },
                    onStop = { viewModel.stopRecording() },
                    onCancelRecording = { viewModel.cancelRecording() },
                    onContinue = { startOrRequestMic(MicAction.Continue) },
                    onRerecord = { startOrRequestMic(MicAction.Rerecord) },
                    onRecognize = { viewModel.enqueueDraftAndRecognize() },
                    onRecordNew = { viewModel.enqueueDraftAndRecordNew() },
                    onSaveDraft = {
                        saveTargetId = null
                        saveAudioLauncher.launch(viewModel.suggestedAudioFileName())
                    },
                    onDiscard = { viewModel.discardDraft() },
                )
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
private fun SpeechMessageRow(
    item: SpeechQueueItem,
    averageRecognitionMs: Long,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val isSlow =
        item.status == SpeechMessageStatus.Processing &&
            averageRecognitionMs > 0L &&
            item.recognitionElapsedMs > averageRecognitionMs
    val containerColor =
        when {
            item.status == SpeechMessageStatus.Done -> DoneCardGreen.copy(alpha = 0.18f)
            isSlow -> SlowWarningAmber.copy(alpha = 0.22f)
            item.status == SpeechMessageStatus.Error -> MaterialTheme.colorScheme.errorContainer
            else -> MaterialTheme.colorScheme.surfaceVariant
        }
    val preview =
        when (item.status) {
            SpeechMessageStatus.Done ->
                item.text.ifBlank { stringResource(R.string.speech_to_text_result_label) }

            SpeechMessageStatus.Processing ->
                stringResource(R.string.speech_to_text_recognizing) +
                    " · " +
                    formatElapsed(item.recognitionElapsedMs)

            SpeechMessageStatus.Cancelled -> stringResource(R.string.speech_to_text_status_cancelled)

            SpeechMessageStatus.Error ->
                item.errorMessage.ifBlank {
                    stringResource(R.string.speech_to_text_status_error)
                }

            SpeechMessageStatus.Recorded -> stringResource(R.string.speech_to_text_status_recorded)
        }
    Surface(
        modifier =
        modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(12.dp),
        color = containerColor,
    ) {
        Row(
            modifier =
            Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 10.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = AudioRecorder.formatDuration(item.audioDurationSeconds),
                style = MaterialTheme.typography.labelLarge,
            )
            if (item.status == SpeechMessageStatus.Processing) {
                CircularProgressIndicator(
                    modifier = Modifier.size(18.dp),
                    strokeWidth = 2.dp,
                    color = if (isSlow) SlowWarningAmber else MaterialTheme.colorScheme.primary,
                )
            }
            Text(
                text = preview,
                style = MaterialTheme.typography.bodyMedium,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                modifier = Modifier.weight(1f),
                color =
                when {
                    item.status == SpeechMessageStatus.Error -> MaterialTheme.colorScheme.error
                    isSlow -> SlowWarningAmber
                    else -> MaterialTheme.colorScheme.onSurface
                },
            )
            Icon(
                imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun SpeechMessageDetail(
    item: SpeechQueueItem,
    averageRecognitionMs: Long,
    hasApiKey: Boolean,
    onRecognize: () -> Unit,
    onCancel: () -> Unit,
    onDelete: () -> Unit,
    onTextChange: (String) -> Unit,
    onCopy: () -> Unit,
    onShare: () -> Unit,
    onSendToTickTick: () -> Unit,
    onRewrite: () -> Unit,
    onSingleLine: () -> Unit,
    onSave: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val isSlow =
        item.status == SpeechMessageStatus.Processing &&
            averageRecognitionMs > 0L &&
            item.recognitionElapsedMs > averageRecognitionMs
    Column(
        modifier = modifier.verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = AudioRecorder.formatDuration(item.audioDurationSeconds),
                style = MaterialTheme.typography.titleMedium,
            )
            IconButton(onClick = onDelete) {
                Icon(
                    imageVector = Icons.Filled.Delete,
                    contentDescription = stringResource(R.string.speech_to_text_delete_message),
                )
            }
        }

        when (item.status) {
            SpeechMessageStatus.Processing -> {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    CircularProgressIndicator(
                        color = if (isSlow) SlowWarningAmber else MaterialTheme.colorScheme.primary,
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = formatElapsed(item.recognitionElapsedMs),
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(
                        text = stringResource(R.string.speech_to_text_recognizing),
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    if (isSlow) {
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = stringResource(R.string.speech_to_text_slow_warning),
                            style = MaterialTheme.typography.bodySmall,
                            color = SlowWarningAmber,
                        )
                    }
                }
                OutlinedButton(onClick = onCancel, modifier = Modifier.fillMaxWidth()) {
                    Text(stringResource(R.string.speech_to_text_cancel_recognition))
                }
            }

            SpeechMessageStatus.Done -> {
                OutlinedTextField(
                    value = item.text,
                    onValueChange = onTextChange,
                    modifier = Modifier.fillMaxWidth().height(180.dp),
                    textStyle = MaterialTheme.typography.bodyMedium,
                    label = { Text(stringResource(R.string.speech_to_text_result_label)) },
                )
                if (item.lastRecognitionDurationMs > 0L) {
                    Text(
                        text = formatElapsed(item.lastRecognitionDurationMs),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    CompactBottomActionButton(
                        onClick = onCopy,
                        icon = Icons.Filled.ContentCopy,
                        label = stringResource(R.string.speech_to_text_copy),
                    )
                    CompactBottomActionButton(
                        onClick = onShare,
                        icon = Icons.Filled.Share,
                        label = stringResource(R.string.speech_to_text_share),
                        outlined = true,
                    )
                }
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    CompactBottomActionButton(
                        onClick = onRewrite,
                        icon = Icons.Filled.AutoFixHigh,
                        label = stringResource(R.string.speech_to_text_rewrite),
                        outlined = true,
                        enabled = hasApiKey,
                    )
                    CompactBottomActionButton(
                        onClick = onSingleLine,
                        icon = Icons.AutoMirrored.Filled.ShortText,
                        label = stringResource(R.string.speech_to_text_single_line),
                        outlined = true,
                    )
                }
                OutlinedButton(onClick = onSendToTickTick, modifier = Modifier.fillMaxWidth()) {
                    Icon(
                        imageVector = Icons.Filled.TaskAlt,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp),
                    )
                    Spacer(modifier = Modifier.size(6.dp))
                    Text(stringResource(R.string.speech_to_text_send_to_ticktick))
                }
                OutlinedButton(onClick = onSave, modifier = Modifier.fillMaxWidth()) {
                    Icon(
                        imageVector = Icons.Filled.Save,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp),
                    )
                    Spacer(modifier = Modifier.size(6.dp))
                    Text(stringResource(R.string.speech_to_text_save_audio))
                }
            }

            SpeechMessageStatus.Recorded,
            SpeechMessageStatus.Cancelled,
            SpeechMessageStatus.Error,
            -> {
                val statusText =
                    when (item.status) {
                        SpeechMessageStatus.Cancelled ->
                            stringResource(R.string.speech_to_text_status_cancelled)

                        SpeechMessageStatus.Error ->
                            item.errorMessage.ifBlank {
                                stringResource(R.string.speech_to_text_status_error)
                            }

                        else -> stringResource(R.string.speech_to_text_status_recorded)
                    }
                Text(
                    text = statusText,
                    style = MaterialTheme.typography.bodyMedium,
                    color =
                    if (item.status == SpeechMessageStatus.Error) {
                        MaterialTheme.colorScheme.error
                    } else {
                        MaterialTheme.colorScheme.onSurfaceVariant
                    },
                )
                Button(
                    onClick = onRecognize,
                    enabled = hasApiKey,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(stringResource(R.string.speech_to_text_recognize))
                }
                OutlinedButton(onClick = onSave, modifier = Modifier.fillMaxWidth()) {
                    Icon(
                        imageVector = Icons.Filled.Save,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp),
                    )
                    Spacer(modifier = Modifier.size(6.dp))
                    Text(stringResource(R.string.speech_to_text_save_audio))
                }
            }
        }
    }
}

@Composable
private fun ComposerBar(
    phase: ComposerPhase,
    hasApiKey: Boolean,
    buckets: List<WaveformBucket>,
    durationLabel: String,
    onStart: () -> Unit,
    onStop: () -> Unit,
    onCancelRecording: () -> Unit,
    onContinue: () -> Unit,
    onRerecord: () -> Unit,
    onRecognize: () -> Unit,
    onRecordNew: () -> Unit,
    onSaveDraft: () -> Unit,
    onDiscard: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        tonalElevation = 2.dp,
    ) {
        Column(
            modifier =
            Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            when (phase) {
                ComposerPhase.Idle -> {
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(12.dp),
                    ) {
                        RecordStartButton(
                            enabled = hasApiKey,
                            onClick = onStart,
                        )
                        Text(
                            text = stringResource(R.string.speech_to_text_idle_message),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.fillMaxWidth(),
                        )
                    }
                }

                ComposerPhase.Recording -> {
                    Text(
                        text = stringResource(R.string.speech_to_text_recording),
                        style = MaterialTheme.typography.titleSmall,
                        color = MaterialTheme.colorScheme.error,
                    )
                    Text(
                        text = durationLabel,
                        style = MaterialTheme.typography.headlineSmall,
                    )
                    WaveformView(
                        buckets = buckets,
                        live = true,
                        modifier =
                        Modifier
                            .fillMaxWidth()
                            .height(72.dp),
                    )
                    Button(onClick = onStop, modifier = Modifier.fillMaxWidth()) {
                        Icon(
                            imageVector = Icons.Filled.Stop,
                            contentDescription = null,
                            modifier = Modifier.size(20.dp),
                        )
                        Spacer(modifier = Modifier.size(8.dp))
                        Text(stringResource(R.string.speech_to_text_stop))
                    }
                    OutlinedButton(onClick = onCancelRecording, modifier = Modifier.fillMaxWidth()) {
                        Text(stringResource(R.string.speech_to_text_cancel_recording))
                    }
                }

                ComposerPhase.Recorded -> {
                    Text(
                        text = stringResource(R.string.speech_to_text_recorded_ready),
                        style = MaterialTheme.typography.titleSmall,
                    )
                    Text(
                        text = durationLabel,
                        style = MaterialTheme.typography.headlineSmall,
                    )
                    WaveformView(
                        buckets = buckets,
                        live = false,
                        modifier =
                        Modifier
                            .fillMaxWidth()
                            .height(72.dp),
                    )
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Button(
                            onClick = onRecognize,
                            enabled = hasApiKey,
                            modifier = Modifier.weight(1f),
                        ) {
                            Text(stringResource(R.string.speech_to_text_recognize))
                        }
                        OutlinedButton(
                            onClick = onRecordNew,
                            modifier = Modifier.weight(1f),
                        ) {
                            Icon(
                                imageVector = Icons.Filled.Mic,
                                contentDescription = null,
                                modifier = Modifier.size(18.dp),
                            )
                            Spacer(modifier = Modifier.size(6.dp))
                            Text(stringResource(R.string.speech_to_text_record_new))
                        }
                    }
                    OutlinedButton(onClick = onSaveDraft, modifier = Modifier.fillMaxWidth()) {
                        Icon(
                            imageVector = Icons.Filled.Save,
                            contentDescription = null,
                            modifier = Modifier.size(20.dp),
                        )
                        Spacer(modifier = Modifier.size(8.dp))
                        Text(stringResource(R.string.speech_to_text_save_audio))
                    }
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        CompactBottomActionButton(
                            onClick = onContinue,
                            icon = Icons.Filled.PlayArrow,
                            label = stringResource(R.string.speech_to_text_continue),
                        )
                        CompactBottomActionButton(
                            onClick = onRerecord,
                            icon = Icons.Filled.Refresh,
                            label = stringResource(R.string.speech_to_text_rerecord),
                            outlined = true,
                        )
                        CompactBottomActionButton(
                            onClick = onDiscard,
                            icon = Icons.Filled.Delete,
                            label = stringResource(R.string.speech_to_text_discard_recording),
                            outlined = true,
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun RecordStartButton(
    enabled: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val interactionSource = remember { MutableInteractionSource() }
    val pressed by interactionSource.collectIsPressedAsState()
    val red =
        when {
            !enabled -> RecordButtonRedDisabled
            pressed -> RecordButtonRedPressed
            else -> RecordButtonRed
        }
    val label = stringResource(R.string.speech_to_text_start_recording)
    Box(
        modifier =
        modifier
            .size(RecordButtonSize)
            .clickable(
                enabled = enabled,
                interactionSource = interactionSource,
                indication = null,
                role = Role.Button,
                onClickLabel = label,
                onClick = onClick,
            ),
        contentAlignment = Alignment.Center,
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val center = Offset(size.width / 2f, size.height / 2f)
            val scale = size.minDimension / 56f
            val outerRadius = 23f * scale
            val ringWidth = 2.5f * scale
            val innerRadius = 16f * scale
            drawCircle(
                color = red,
                radius = outerRadius,
                center = center,
                style = Stroke(width = ringWidth),
            )
            drawCircle(
                color = red,
                radius = innerRadius,
                center = center,
            )
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

private fun formatElapsed(elapsedMs: Long): String {
    val totalSeconds = (elapsedMs / 1000L).coerceAtLeast(0L).toInt()
    val minutes = totalSeconds / 60
    val seconds = totalSeconds % 60
    return "%d:%02d".format(minutes, seconds)
}
