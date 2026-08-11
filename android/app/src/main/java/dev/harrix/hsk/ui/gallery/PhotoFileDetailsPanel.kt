package dev.harrix.hsk.ui.gallery

import android.content.Intent
import android.graphics.Bitmap
import android.widget.Toast
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.Map
import androidx.compose.material.icons.filled.Place
import androidx.compose.material3.CircularProgressIndicator
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
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
import dev.harrix.hsk.gallery.CameraPhoto
import dev.harrix.hsk.gallery.OsmStaticMapPreview
import dev.harrix.hsk.gallery.PhotoCaptureMode
import dev.harrix.hsk.gallery.PhotoFileDetails
import dev.harrix.hsk.gallery.PhotoFileDetailsLoader
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.text.DateFormat
import java.util.Date

@Composable
fun rememberPhotoFileDetails(photo: CameraPhoto): PhotoFileDetails? {
    val context = LocalContext.current
    var details by remember(photo.id, photo.uri, photo.sizeBytes) {
        mutableStateOf<PhotoFileDetails?>(null)
    }
    LaunchedEffect(photo.id, photo.uri, photo.sizeBytes) {
        details =
            withContext(Dispatchers.IO) {
                PhotoFileDetailsLoader.load(context, photo)
            }
    }
    return details
}

/**
 * Samsung Gallery–like file summary. [dateLabel] is prepared by the caller so existing
 * date/time formatting stays unchanged.
 */
@Composable
fun PhotoFileDetailsPanel(
    photo: CameraPhoto,
    dateLabel: String,
    modifier: Modifier = Modifier,
    compact: Boolean = false,
    endAligned: Boolean = false,
    showMap: Boolean = false,
    details: PhotoFileDetails? = rememberPhotoFileDetails(photo),
) {
    val context = LocalContext.current
    val clipboard = LocalClipboardManager.current
    val untitled = stringResource(R.string.gallery_cleaner_untitled)
    val copiedMessage = stringResource(R.string.photo_file_details_copied)
    val nameLabel =
        details?.displayName?.takeIf { it.isNotBlank() }
            ?: photo.displayName?.takeIf { it.isNotBlank() }
            ?: untitled
    val sizeFallback =
        remember(photo.sizeBytes) {
            CameraGalleryRepository.formatFileSize(photo.sizeBytes)
        }
    val pathLabel =
        details?.relativePath?.takeIf { it.isNotBlank() }?.let { relative ->
            stringResource(R.string.photo_file_details_path_format, relative.trimEnd('/'))
        }
    val statsLine =
        details?.fileStatsLine(CameraGalleryRepository::formatFileSize)
            ?: sizeFallback
    val settingsLine = details?.cameraSettingsLine()
    val coordinatesLabel = details?.coordinatesLabel()
    val modeLabel =
        when (details?.captureMode) {
            PhotoCaptureMode.Landscape -> stringResource(R.string.photo_file_details_mode_landscape)
            PhotoCaptureMode.Portrait -> stringResource(R.string.photo_file_details_mode_portrait)
            PhotoCaptureMode.Night -> stringResource(R.string.photo_file_details_mode_night)
            null -> null
        }
    val textAlign = if (endAligned) TextAlign.End else TextAlign.Start
    val horizontal = if (endAligned) Alignment.End else Alignment.Start

    fun copyText(value: String) {
        clipboard.setText(AnnotatedString(value))
        Toast.makeText(context, copiedMessage, Toast.LENGTH_SHORT).show()
    }

    if (compact) {
        Text(
            text = "$dateLabel · $statsLine",
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            maxLines = 2,
            overflow = TextOverflow.Ellipsis,
            textAlign = textAlign,
            modifier = modifier.then(if (endAligned) Modifier.fillMaxWidth() else Modifier),
        )
        return
    }

    val device = details?.deviceLabel
    val deviceLine =
        listOfNotNull(device, modeLabel)
            .joinToString(" · ")
            .takeIf { it.isNotEmpty() }

    Column(
        modifier = modifier,
        horizontalAlignment = horizontal,
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        CopyableDetailRow(
            text = dateLabel,
            copyLabel = stringResource(R.string.photo_file_details_copy_date),
            onCopy = { copyText(dateLabel) },
            textStyle = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
            textColor = MaterialTheme.colorScheme.onSurface,
            endAligned = endAligned,
        )
        CopyableDetailRow(
            text = nameLabel,
            copyLabel = stringResource(R.string.photo_file_details_copy_name),
            onCopy = { copyText(nameLabel) },
            textStyle = MaterialTheme.typography.bodyMedium,
            textColor = MaterialTheme.colorScheme.onSurfaceVariant,
            endAligned = endAligned,
        )
        if (pathLabel != null) {
            CopyableDetailRow(
                text = pathLabel,
                copyLabel = stringResource(R.string.photo_file_details_copy_path),
                onCopy = { copyText(pathLabel) },
                textStyle = MaterialTheme.typography.bodySmall,
                textColor = MaterialTheme.colorScheme.onSurfaceVariant,
                endAligned = endAligned,
                maxLines = 3,
            )
        }
        if (deviceLine != null) {
            CopyableDetailRow(
                text = deviceLine,
                copyLabel = stringResource(R.string.photo_file_details_copy_device),
                onCopy = { copyText(deviceLine) },
                textStyle =
                MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.SemiBold),
                textColor = MaterialTheme.colorScheme.onSurface,
                endAligned = endAligned,
                maxLines = 1,
            )
        }
        CopyableDetailRow(
            text = statsLine,
            copyLabel = stringResource(R.string.photo_file_details_copy_stats),
            onCopy = { copyText(statsLine) },
            textStyle = MaterialTheme.typography.bodyMedium,
            textColor = MaterialTheme.colorScheme.onSurfaceVariant,
            endAligned = endAligned,
        )
        if (settingsLine != null) {
            CopyableDetailRow(
                text = settingsLine,
                copyLabel = stringResource(R.string.photo_file_details_copy_settings),
                onCopy = { copyText(settingsLine) },
                textStyle = MaterialTheme.typography.bodyMedium,
                textColor = MaterialTheme.colorScheme.onSurfaceVariant,
                endAligned = endAligned,
            )
        }
        val location = details?.locationLabel
        if (location != null) {
            CopyableDetailRow(
                text = location,
                copyLabel = stringResource(R.string.photo_file_details_copy_location),
                onCopy = { copyText(location) },
                textStyle = MaterialTheme.typography.bodyMedium,
                textColor = MaterialTheme.colorScheme.onSurface,
                endAligned = endAligned,
                maxLines = 3,
                modifier = Modifier.padding(top = 4.dp),
            )
        }
        if (coordinatesLabel != null) {
            CopyableDetailRow(
                text = coordinatesLabel,
                copyLabel = stringResource(R.string.photo_file_details_copy_coordinates),
                onCopy = { copyText(coordinatesLabel) },
                textStyle = MaterialTheme.typography.bodyMedium,
                textColor = MaterialTheme.colorScheme.onSurface,
                endAligned = endAligned,
                modifier = Modifier.padding(top = 2.dp),
            )
        }
        if (showMap && details != null && details.hasMapLocation) {
            PhotoLocationMapPreview(
                details = details,
                modifier =
                Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp),
            )
        }
    }
}

/** Bottom sheet with full EXIF summary and optional Google Maps preview. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PhotoFileDetailsSheet(
    photo: CameraPhoto,
    onDismissRequest: () -> Unit,
) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
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
            PhotoFileDetailsPanel(
                photo = photo,
                dateLabel = galleryPhotoDateTimeLabel(photo),
                showMap = true,
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}

@Composable
private fun CopyableDetailRow(
    text: String,
    copyLabel: String,
    onCopy: () -> Unit,
    textStyle: TextStyle,
    textColor: Color,
    endAligned: Boolean,
    modifier: Modifier = Modifier,
    maxLines: Int = 2,
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement =
        if (endAligned) {
            Arrangement.spacedBy(4.dp, Alignment.End)
        } else {
            Arrangement.spacedBy(4.dp)
        },
    ) {
        Text(
            text = text,
            style = textStyle,
            color = textColor,
            maxLines = maxLines,
            overflow = TextOverflow.Ellipsis,
            textAlign = if (endAligned) TextAlign.End else TextAlign.Start,
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

@Composable
private fun PhotoLocationMapPreview(
    details: PhotoFileDetails,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val mapsUri = details.googleMapsUri() ?: return
    val latitude = details.latitude ?: return
    val longitude = details.longitude ?: return
    val mapLabel = stringResource(R.string.photo_file_details_map)
    val openMapLabel = stringResource(R.string.photo_file_details_open_map)
    var previewBitmap by remember(latitude, longitude) { mutableStateOf<Bitmap?>(null) }
    var loading by remember(latitude, longitude) { mutableStateOf(true) }

    LaunchedEffect(latitude, longitude) {
        loading = true
        previewBitmap = null
        previewBitmap =
            OsmStaticMapPreview.render(
                latitude = latitude,
                longitude = longitude,
            )
        loading = false
    }

    fun openMaps() {
        runCatching {
            context.startActivity(Intent(Intent.ACTION_VIEW, mapsUri))
        }
    }

    Column(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Text(
            text = mapLabel,
            style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.SemiBold),
            color = MaterialTheme.colorScheme.onSurface,
        )
        Box(
            modifier =
            Modifier
                .fillMaxWidth()
                .height(180.dp)
                .clip(RoundedCornerShape(12.dp))
                .background(MaterialTheme.colorScheme.surfaceVariant)
                .clickable(onClickLabel = openMapLabel) { openMaps() },
            contentAlignment = Alignment.Center,
        ) {
            val bitmap = previewBitmap
            when {
                loading ->
                    CircularProgressIndicator(
                        modifier = Modifier.size(36.dp),
                        strokeWidth = 3.dp,
                    )

                bitmap != null && !bitmap.isRecycled ->
                    Image(
                        bitmap = bitmap.asImageBitmap(),
                        contentDescription = mapLabel,
                        contentScale = ContentScale.Crop,
                        modifier = Modifier.fillMaxSize(),
                    )

                else ->
                    Column(
                        modifier =
                        Modifier
                            .fillMaxSize()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally,
                    ) {
                        Icon(
                            imageVector = Icons.Filled.Place,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.error,
                            modifier = Modifier.size(40.dp),
                        )
                        Text(
                            text = details.coordinatesLabel().orEmpty(),
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.padding(top = 8.dp),
                        )
                    }
            }
            if (!loading) {
                Row(
                    modifier =
                    Modifier
                        .align(Alignment.BottomStart)
                        .padding(8.dp)
                        .background(
                            MaterialTheme.colorScheme.surface.copy(alpha = 0.92f),
                            RoundedCornerShape(8.dp),
                        )
                        .padding(horizontal = 10.dp, vertical = 6.dp),
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Icon(
                        imageVector = Icons.Filled.Map,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                    )
                    Text(
                        text = openMapLabel,
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.onSurface,
                    )
                }
            }
        }
    }
}

/** Date/time label matching Gallery Cleaner’s current formatting. */
fun galleryPhotoDateTimeLabel(photo: CameraPhoto): String = DateFormat
    .getDateTimeInstance(DateFormat.MEDIUM, DateFormat.SHORT)
    .format(Date(photo.dateTakenEpochMs))
