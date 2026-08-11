package dev.harrix.hsk.ui.gallery

import android.widget.Toast
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.CameraGalleryRepository
import dev.harrix.hsk.gallery.CameraVideo
import dev.harrix.hsk.gallery.VideoFileDetails
import dev.harrix.hsk.gallery.VideoFileDetailsLoader
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.text.DateFormat
import java.util.Date

@Composable
fun rememberVideoFileDetails(video: CameraVideo): VideoFileDetails? {
    val context = LocalContext.current
    var details by remember(video.id, video.uri, video.sizeBytes) {
        mutableStateOf<VideoFileDetails?>(null)
    }
    LaunchedEffect(video.id, video.uri, video.sizeBytes) {
        details =
            withContext(Dispatchers.IO) {
                VideoFileDetailsLoader.load(context, video)
            }
    }
    return details
}

@Composable
fun VideoFileDetailsPanel(
    video: CameraVideo,
    dateLabel: String,
    modifier: Modifier = Modifier,
    details: VideoFileDetails? = rememberVideoFileDetails(video),
) {
    val context = LocalContext.current
    val clipboard = LocalClipboardManager.current
    val untitled = stringResource(R.string.video_cleaner_untitled)
    val copiedMessage = stringResource(R.string.photo_file_details_copied)
    val nameLabel =
        details?.displayName?.takeIf { it.isNotBlank() }
            ?: video.displayName?.takeIf { it.isNotBlank() }
            ?: untitled
    val sizeFallback =
        remember(video.sizeBytes) {
            CameraGalleryRepository.formatFileSize(video.sizeBytes)
        }
    val pathLabel =
        details?.relativePath?.takeIf { it.isNotBlank() }?.let { relative ->
            stringResource(R.string.photo_file_details_path_format, relative.trimEnd('/'))
        }
    val statsLine =
        details?.fileStatsLine(CameraGalleryRepository::formatFileSize)
            ?: sizeFallback

    fun copyText(value: String) {
        clipboard.setText(AnnotatedString(value))
        Toast.makeText(context, copiedMessage, Toast.LENGTH_SHORT).show()
    }

    Column(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        VideoCopyableDetailRow(
            text = dateLabel,
            copyLabel = stringResource(R.string.photo_file_details_copy_date),
            onCopy = { copyText(dateLabel) },
            textStyle = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
            textColor = MaterialTheme.colorScheme.onSurface,
        )
        VideoCopyableDetailRow(
            text = nameLabel,
            copyLabel = stringResource(R.string.photo_file_details_copy_name),
            onCopy = { copyText(nameLabel) },
            textStyle = MaterialTheme.typography.bodyMedium,
            textColor = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        if (pathLabel != null) {
            VideoCopyableDetailRow(
                text = pathLabel,
                copyLabel = stringResource(R.string.photo_file_details_copy_path),
                onCopy = { copyText(pathLabel) },
                textStyle = MaterialTheme.typography.bodySmall,
                textColor = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 3,
            )
        }
        VideoCopyableDetailRow(
            text = statsLine,
            copyLabel = stringResource(R.string.photo_file_details_copy_stats),
            onCopy = { copyText(statsLine) },
            textStyle = MaterialTheme.typography.bodyMedium,
            textColor = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

/** Bottom sheet with video metadata summary (no location block — videos usually lack GPS). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VideoFileDetailsSheet(
    video: CameraVideo,
    onDismissRequest: () -> Unit,
) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    val details = rememberVideoFileDetails(video)
    val dateLabel =
        remember(video.id, video.dateAddedEpochSec, details?.dateTakenEpochMs) {
            galleryVideoDateTimeLabel(video, details)
        }

    ModalBottomSheet(
        onDismissRequest = onDismissRequest,
        sheetState = sheetState,
    ) {
        Column(
            modifier =
            Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 8.dp)
                .padding(bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = stringResource(R.string.photo_file_details_title),
                style = MaterialTheme.typography.titleLarge,
            )
            VideoFileDetailsPanel(
                video = video,
                dateLabel = dateLabel,
                details = details,
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}

private fun galleryVideoDateTimeLabel(
    video: CameraVideo,
    details: VideoFileDetails?,
): String {
    val epochMs =
        details?.dateTakenEpochMs
            ?: video.dateAddedEpochSec.takeIf { it > 0L }?.times(1000L)
            ?: System.currentTimeMillis()
    return DateFormat
        .getDateTimeInstance(DateFormat.MEDIUM, DateFormat.SHORT)
        .format(Date(epochMs))
}

@Composable
private fun VideoCopyableDetailRow(
    text: String,
    copyLabel: String,
    onCopy: () -> Unit,
    textStyle: TextStyle,
    textColor: Color,
    modifier: Modifier = Modifier,
    maxLines: Int = 2,
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Text(
            text = text,
            style = textStyle,
            color = textColor,
            maxLines = maxLines,
            overflow = TextOverflow.Ellipsis,
            textAlign = TextAlign.Start,
            modifier = Modifier.weight(1f),
        )
        IconButton(
            onClick = onCopy,
            modifier = Modifier.size(36.dp),
        ) {
            Icon(
                imageVector = Icons.Filled.ContentCopy,
                contentDescription = copyLabel,
                modifier = Modifier.size(18.dp),
                tint = MaterialTheme.colorScheme.primary,
            )
        }
    }
}
