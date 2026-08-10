package dev.harrix.hsk.ui.gallery

import android.annotation.SuppressLint
import android.content.Intent
import android.view.MotionEvent
import android.webkit.WebView
import android.webkit.WebViewClient
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Map
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.CameraGalleryRepository
import dev.harrix.hsk.gallery.CameraPhoto
import dev.harrix.hsk.gallery.PhotoCaptureMode
import dev.harrix.hsk.gallery.PhotoFileDetails
import dev.harrix.hsk.gallery.PhotoFileDetailsLoader
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.text.DateFormat
import java.util.Date
import java.util.Locale

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
    val untitled = stringResource(R.string.gallery_cleaner_untitled)
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
    val modeLabel =
        when (details?.captureMode) {
            PhotoCaptureMode.Landscape -> stringResource(R.string.photo_file_details_mode_landscape)
            PhotoCaptureMode.Portrait -> stringResource(R.string.photo_file_details_mode_portrait)
            PhotoCaptureMode.Night -> stringResource(R.string.photo_file_details_mode_night)
            null -> null
        }
    val textAlign = if (endAligned) TextAlign.End else TextAlign.Start
    val horizontal = if (endAligned) Alignment.End else Alignment.Start

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

    Column(
        modifier = modifier,
        horizontalAlignment = horizontal,
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Text(
            text = dateLabel,
            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
            color = MaterialTheme.colorScheme.onSurface,
            maxLines = 2,
            overflow = TextOverflow.Ellipsis,
            textAlign = textAlign,
            modifier = if (endAligned) Modifier.fillMaxWidth() else Modifier,
        )
        Text(
            text = nameLabel,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            textAlign = textAlign,
            modifier = if (endAligned) Modifier.fillMaxWidth() else Modifier,
        )
        if (pathLabel != null) {
            Text(
                text = pathLabel,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
                textAlign = textAlign,
                modifier = if (endAligned) Modifier.fillMaxWidth() else Modifier,
            )
        }

        val device = details?.deviceLabel
        if (device != null || modeLabel != null) {
            Row(
                modifier = if (endAligned) Modifier.fillMaxWidth() else Modifier,
                horizontalArrangement =
                if (endAligned) {
                    Arrangement.spacedBy(8.dp, Alignment.End)
                } else {
                    Arrangement.spacedBy(8.dp)
                },
                verticalAlignment = Alignment.CenterVertically,
            ) {
                if (device != null) {
                    Text(
                        text = device,
                        style =
                        MaterialTheme.typography.titleSmall.copy(
                            fontWeight = FontWeight.SemiBold,
                        ),
                        color = MaterialTheme.colorScheme.onSurface,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.weight(1f, fill = false),
                    )
                }
                if (modeLabel != null) {
                    Text(
                        text = modeLabel,
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier =
                        Modifier
                            .background(
                                MaterialTheme.colorScheme.surfaceVariant,
                                RoundedCornerShape(50),
                            )
                            .padding(horizontal = 8.dp, vertical = 2.dp),
                    )
                }
            }
        }

        Text(
            text = statsLine,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            maxLines = 2,
            overflow = TextOverflow.Ellipsis,
            textAlign = textAlign,
            modifier = if (endAligned) Modifier.fillMaxWidth() else Modifier,
        )
        if (settingsLine != null) {
            Text(
                text = settingsLine,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
                textAlign = textAlign,
                modifier = if (endAligned) Modifier.fillMaxWidth() else Modifier,
            )
        }
        val location = details?.locationLabel
        if (location != null) {
            Text(
                text = location,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface,
                maxLines = 3,
                overflow = TextOverflow.Ellipsis,
                textAlign = textAlign,
                modifier =
                Modifier
                    .padding(top = 4.dp)
                    .then(if (endAligned) Modifier.fillMaxWidth() else Modifier),
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
    val embedUrl =
        remember(latitude, longitude) {
            String.format(
                Locale.US,
                "https://www.google.com/maps?q=%f,%f&z=15&output=embed",
                latitude,
                longitude,
            )
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
                .background(MaterialTheme.colorScheme.surfaceVariant),
        ) {
            AndroidView(
                factory = { viewContext ->
                    createMapsWebView(viewContext, embedUrl)
                },
                update = { webView ->
                    if (webView.url != embedUrl) {
                        webView.loadUrl(embedUrl)
                    }
                },
                modifier = Modifier.fillMaxSize(),
            )
            // Capture taps so the map opens in the browser with a pin.
            Box(
                modifier =
                Modifier
                    .fillMaxSize()
                    .clickable(onClickLabel = openMapLabel) { openMaps() },
            )
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

@SuppressLint("SetJavaScriptEnabled")
private fun createMapsWebView(
    context: android.content.Context,
    embedUrl: String,
): WebView = WebView(context).apply {
    settings.javaScriptEnabled = true
    settings.domStorageEnabled = true
    // Preview only; taps are handled by the Compose overlay.
    setOnTouchListener { _, event -> event.action == MotionEvent.ACTION_MOVE }
    webViewClient = WebViewClient()
    loadUrl(embedUrl)
}

/** Date/time label matching Gallery Cleaner’s current formatting. */
fun galleryPhotoDateTimeLabel(photo: CameraPhoto): String = DateFormat
    .getDateTimeInstance(DateFormat.MEDIUM, DateFormat.SHORT)
    .format(Date(photo.dateTakenEpochMs))
