package dev.harrix.hsk.ui.gallery

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.calculateRotation
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Done
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathFillType
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.input.pointer.positionChanged
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import coil.request.ImageRequest
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.CameraPhoto
import dev.harrix.hsk.gallery.NormalizedCropRect
import dev.harrix.hsk.gallery.PhotoEditSaver
import dev.harrix.hsk.ui.theme.AppGreen
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt
import coil.size.Size as CoilSize

private enum class CropDragMode {
    Move,
    ResizeTopLeft,
    ResizeTopRight,
    ResizeBottomLeft,
    ResizeBottomRight,
}

@Composable
fun PhotoCropEditor(
    photo: CameraPhoto,
    rotationDegrees: Float,
    onRotationDegreesChange: (Float) -> Unit,
    cropRect: NormalizedCropRect,
    onCropRectChange: (NormalizedCropRect) -> Unit,
    imageRevision: Int,
    isSaving: Boolean,
    onSave: () -> Unit,
    onDiscard: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val density = LocalDensity.current
    var imageWidth by remember(photo.id, imageRevision) { mutableIntStateOf(0) }
    var imageHeight by remember(photo.id, imageRevision) { mutableIntStateOf(0) }
    // Large hit targets: corners sit near the phone bezel and are hard to grab otherwise.
    val handleHitSlopPx = with(density) { 52.dp.toPx() }
    val handleVisualPx = with(density) { 24.dp.toPx() }
    val cropRectState = rememberUpdatedState(cropRect)
    val onCropRectChangeState = rememberUpdatedState(onCropRectChange)
    val rotationState = rememberUpdatedState(rotationDegrees)
    val onRotationDegreesChangeState = rememberUpdatedState(onRotationDegreesChange)
    var isRotatingHint by remember { mutableStateOf(false) }
    var didInitCrop by remember(photo.id, imageRevision) { mutableStateOf(false) }

    LaunchedEffect(imageWidth, imageHeight, didInitCrop) {
        if (!didInitCrop && imageWidth > 0 && imageHeight > 0) {
            onCropRectChangeState.value(PhotoEditSaver.imageContentCrop(imageWidth, imageHeight))
            didInitCrop = true
        }
    }

    val displayDegrees = ((rotationDegrees % 360f) + 360f) % 360f

    Column(modifier = modifier.fillMaxSize()) {
        BoxWithConstraints(
            modifier =
            Modifier
                .weight(1f)
                .fillMaxWidth()
                .background(Color.Black),
            contentAlignment = Alignment.Center,
        ) {
            val viewportW = constraints.maxWidth.toFloat()
            val viewportH = constraints.maxHeight.toFloat()
            val workspace =
                remember(viewportW, viewportH) {
                    PhotoEditSaver.fittedSquareInViewport(viewportW, viewportH)
                }
            val imageDrawSize =
                remember(imageWidth, imageHeight, workspace) {
                    PhotoEditSaver.imageDrawSizeInWorkspace(imageWidth, imageHeight, workspace)
                }

            if (workspace.width > 0f && imageDrawSize.first > 0f) {
                Box(
                    modifier =
                    Modifier
                        .size(
                            width = with(density) { workspace.width.toDp() },
                            height = with(density) { workspace.height.toDp() },
                        ),
                    contentAlignment = Alignment.Center,
                ) {
                    AsyncImage(
                        model =
                        ImageRequest
                            .Builder(context)
                            .data(photo.uri)
                            .size(CoilSize.ORIGINAL)
                            .memoryCacheKey("${photo.uri}-$imageRevision")
                            .diskCacheKey("${photo.uri}-$imageRevision")
                            .crossfade(false)
                            .build(),
                        contentDescription = photo.displayName,
                        contentScale = ContentScale.FillBounds,
                        onSuccess = { state ->
                            applyPainterSize(state.painter.intrinsicSize) { width, height ->
                                imageWidth = width
                                imageHeight = height
                            }
                        },
                        modifier =
                        Modifier
                            .size(
                                width = with(density) { imageDrawSize.first.toDp() },
                                height = with(density) { imageDrawSize.second.toDp() },
                            )
                            .graphicsLayer {
                                rotationZ = rotationDegrees
                                clip = false
                            },
                    )
                }

                val cropPx =
                    Rect(
                        left = workspace.left + cropRect.left * workspace.width,
                        top = workspace.top + cropRect.top * workspace.height,
                        right = workspace.left + cropRect.right * workspace.width,
                        bottom = workspace.top + cropRect.bottom * workspace.height,
                    )

                Canvas(modifier = Modifier.fillMaxSize()) {
                    val dimPath =
                        Path().apply {
                            fillType = PathFillType.EvenOdd
                            addRect(Rect(0f, 0f, size.width, size.height))
                            addRect(cropPx)
                        }
                    drawPath(dimPath, Color.Black.copy(alpha = 0.55f))
                    drawRect(
                        color = Color.White,
                        topLeft = Offset(cropPx.left, cropPx.top),
                        size = Size(cropPx.width, cropPx.height),
                        style = Stroke(width = 2.dp.toPx()),
                    )
                    val guideColor = Color.White.copy(alpha = 0.7f)
                    val guideStroke = 1.dp.toPx()
                    val thirdW = cropPx.width / 3f
                    val thirdH = cropPx.height / 3f
                    for (i in 1..2) {
                        val x = cropPx.left + thirdW * i
                        drawLine(
                            color = guideColor,
                            start = Offset(x, cropPx.top),
                            end = Offset(x, cropPx.bottom),
                            strokeWidth = guideStroke,
                        )
                        val y = cropPx.top + thirdH * i
                        drawLine(
                            color = guideColor,
                            start = Offset(cropPx.left, y),
                            end = Offset(cropPx.right, y),
                            strokeWidth = guideStroke,
                        )
                    }
                    val midX = cropPx.left + cropPx.width / 2f
                    val midY = cropPx.top + cropPx.height / 2f
                    drawLine(
                        color = guideColor,
                        start = Offset(midX, cropPx.top),
                        end = Offset(midX, cropPx.bottom),
                        strokeWidth = guideStroke,
                    )
                    drawLine(
                        color = guideColor,
                        start = Offset(cropPx.left, midY),
                        end = Offset(cropPx.right, midY),
                        strokeWidth = guideStroke,
                    )
                    val handle = handleVisualPx
                    val corners =
                        listOf(
                            Offset(cropPx.left, cropPx.top),
                            Offset(cropPx.right, cropPx.top),
                            Offset(cropPx.left, cropPx.bottom),
                            Offset(cropPx.right, cropPx.bottom),
                        )
                    corners.forEach { corner ->
                        drawRect(
                            color = Color.White,
                            topLeft = Offset(corner.x - handle / 2f, corner.y - handle / 2f),
                            size = Size(handle, handle),
                        )
                    }
                }

                Box(
                    modifier =
                    Modifier
                        .fillMaxSize()
                        .pointerInput(workspace, handleHitSlopPx, isSaving, imageWidth, imageHeight) {
                            if (isSaving) {
                                return@pointerInput
                            }
                            awaitEachGesture {
                                awaitFirstDown(requireUnconsumed = false)
                                var multiTouch = false
                                var cropMode: CropDragMode? = null
                                var gestureActive = true
                                isRotatingHint = false

                                while (gestureActive) {
                                    val event = awaitPointerEvent()
                                    val pressed = event.changes.filter { it.pressed }
                                    if (pressed.isEmpty()) {
                                        gestureActive = false
                                    } else if (pressed.size >= 2) {
                                        multiTouch = true
                                        cropMode = null
                                        isRotatingHint = true
                                        val rotationDelta = event.calculateRotation()
                                        if (rotationDelta != 0f) {
                                            onRotationDegreesChangeState.value(
                                                rotationState.value + rotationDelta,
                                            )
                                        }
                                        pressed.forEach { change ->
                                            if (change.positionChanged()) {
                                                change.consume()
                                            }
                                        }
                                    } else if (!multiTouch && pressed.size == 1) {
                                        val change = pressed[0]
                                        val activeMode = cropMode
                                        if (activeMode == null) {
                                            val currentCrop = cropRectState.value
                                            val currentCropPx =
                                                Rect(
                                                    left =
                                                    workspace.left +
                                                        currentCrop.left * workspace.width,
                                                    top =
                                                    workspace.top +
                                                        currentCrop.top * workspace.height,
                                                    right =
                                                    workspace.left +
                                                        currentCrop.right * workspace.width,
                                                    bottom =
                                                    workspace.top +
                                                        currentCrop.bottom * workspace.height,
                                                )
                                            cropMode =
                                                hitTestCropHandle(
                                                    change.position,
                                                    currentCropPx,
                                                    handleHitSlopPx,
                                                )
                                        } else {
                                            val drag = change.position - change.previousPosition
                                            if (drag != Offset.Zero && imageHeight > 0) {
                                                val imageAspect =
                                                    imageWidth.toFloat() / imageHeight.toFloat()
                                                val next =
                                                    applyAspectCropDrag(
                                                        cropRect = cropRectState.value,
                                                        mode = activeMode,
                                                        dragX = drag.x / workspace.width,
                                                        dragY = drag.y / workspace.height,
                                                        imageAspect = imageAspect,
                                                    )
                                                onCropRectChangeState.value(
                                                    PhotoEditSaver.clampCropRect(
                                                        rect = next,
                                                        imageAspect = imageAspect,
                                                    ),
                                                )
                                                change.consume()
                                            }
                                        }
                                    }
                                }
                                isRotatingHint = false
                            }
                        },
                )
            } else {
                AsyncImage(
                    model =
                    ImageRequest
                        .Builder(context)
                        .data(photo.uri)
                        .size(CoilSize.ORIGINAL)
                        .memoryCacheKey("${photo.uri}-$imageRevision")
                        .diskCacheKey("${photo.uri}-$imageRevision")
                        .crossfade(false)
                        .build(),
                    contentDescription = photo.displayName,
                    contentScale = ContentScale.Fit,
                    onSuccess = { state ->
                        applyPainterSize(state.painter.intrinsicSize) { width, height ->
                            imageWidth = width
                            imageHeight = height
                        }
                    },
                    modifier = Modifier.fillMaxSize(),
                )
            }

            if (isRotatingHint || abs(displayDegrees) >= 0.5f) {
                Text(
                    text =
                    stringResource(
                        R.string.gallery_cleaner_edit_rotation_degrees,
                        displayDegrees.roundToInt() % 360,
                    ),
                    color = Color.White,
                    style = MaterialTheme.typography.labelLarge,
                    modifier =
                    Modifier
                        .align(Alignment.TopCenter)
                        .padding(top = 16.dp)
                        .background(Color.Black.copy(alpha = 0.45f))
                        .padding(horizontal = 10.dp, vertical = 4.dp),
                )
            }

            if (isSaving) {
                CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.Center),
                    color = Color.White,
                )
            }
        }

        Row(
            modifier =
            Modifier
                .fillMaxWidth()
                .background(MaterialTheme.colorScheme.background)
                .windowInsetsPadding(WindowInsets.navigationBars)
                .padding(horizontal = 16.dp, vertical = 12.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            OutlinedButton(
                onClick = onDiscard,
                enabled = !isSaving,
                modifier = Modifier.weight(1f),
            ) {
                Icon(
                    imageVector = Icons.Filled.Close,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp),
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(stringResource(R.string.gallery_cleaner_edit_discard))
            }
            Button(
                onClick = onSave,
                enabled = !isSaving,
                modifier = Modifier.weight(1f),
                colors =
                ButtonDefaults.buttonColors(
                    containerColor = AppGreen,
                    contentColor = Color.White,
                ),
            ) {
                Icon(
                    imageVector = Icons.Filled.Done,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp),
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(stringResource(R.string.gallery_cleaner_edit_save))
            }
        }
    }
}

private fun applyPainterSize(
    size: Size,
    onSize: (width: Int, height: Int) -> Unit,
) {
    val validWidth = size.width > 0f && size.width.isFinite()
    val validHeight = size.height > 0f && size.height.isFinite()
    if (validWidth && validHeight) {
        onSize(size.width.toInt(), size.height.toInt())
    }
}

/**
 * Prefer corner handles (large slop, including outside the crop toward the bezel).
 * Move only when the press is inside the crop, away from corners.
 */
private fun hitTestCropHandle(
    point: Offset,
    cropPx: Rect,
    slop: Float,
): CropDragMode? {
    val corners =
        listOf(
            CropDragMode.ResizeTopLeft to Offset(cropPx.left, cropPx.top),
            CropDragMode.ResizeTopRight to Offset(cropPx.right, cropPx.top),
            CropDragMode.ResizeBottomLeft to Offset(cropPx.left, cropPx.bottom),
            CropDragMode.ResizeBottomRight to Offset(cropPx.right, cropPx.bottom),
        )
    var bestMode: CropDragMode? = null
    var bestDistSq = Float.MAX_VALUE
    for ((mode, corner) in corners) {
        val dx = point.x - corner.x
        val dy = point.y - corner.y
        if (abs(dx) <= slop && abs(dy) <= slop) {
            val distSq = dx * dx + dy * dy
            if (distSq < bestDistSq) {
                bestDistSq = distSq
                bestMode = mode
            }
        }
    }
    if (bestMode != null) {
        return bestMode
    }
    val insideCrop =
        point.x in cropPx.left..cropPx.right &&
            point.y in cropPx.top..cropPx.bottom
    return if (insideCrop) {
        CropDragMode.Move
    } else {
        null
    }
}

/**
 * Resize keeps the crop aspect equal to the source file (`width / height`).
 * Workspace is square, so normalized aspect matches pixel aspect. Crop may extend
 * into black letterbox areas around the photo.
 */
private fun applyAspectCropDrag(
    cropRect: NormalizedCropRect,
    mode: CropDragMode,
    dragX: Float,
    dragY: Float,
    imageAspect: Float,
): NormalizedCropRect {
    if (mode == CropDragMode.Move) {
        val width = cropRect.width
        val height = cropRect.height
        val left = (cropRect.left + dragX).coerceIn(0f, 1f - width)
        val top = (cropRect.top + dragY).coerceIn(0f, 1f - height)
        return NormalizedCropRect(left, top, left + width, top + height)
    }

    val aspect = imageAspect.coerceAtLeast(1e-6f)
    val (anchorX, anchorY) =
        when (mode) {
            CropDragMode.ResizeTopLeft -> cropRect.right to cropRect.bottom
            CropDragMode.ResizeTopRight -> cropRect.left to cropRect.bottom
            CropDragMode.ResizeBottomLeft -> cropRect.right to cropRect.top
            CropDragMode.ResizeBottomRight -> cropRect.left to cropRect.top
            CropDragMode.Move -> return cropRect
        }
    val (rawX, rawY) =
        when (mode) {
            CropDragMode.ResizeTopLeft -> (cropRect.left + dragX) to (cropRect.top + dragY)
            CropDragMode.ResizeTopRight -> (cropRect.right + dragX) to (cropRect.top + dragY)
            CropDragMode.ResizeBottomLeft -> (cropRect.left + dragX) to (cropRect.bottom + dragY)
            CropDragMode.ResizeBottomRight -> (cropRect.right + dragX) to (cropRect.bottom + dragY)
            CropDragMode.Move -> return cropRect
        }
    val clampedX = rawX.coerceIn(0f, 1f)
    val clampedY = rawY.coerceIn(0f, 1f)
    var width = abs(clampedX - anchorX)
    var height = abs(clampedY - anchorY)
    if (width / max(height, 1e-6f) > aspect) {
        height = width / aspect
    } else {
        width = height * aspect
    }
    width = min(width, if (clampedX >= anchorX) 1f - anchorX else anchorX)
    height = width / aspect
    height = min(height, if (clampedY >= anchorY) 1f - anchorY else anchorY)
    width = height * aspect

    val left = if (clampedX >= anchorX) anchorX else anchorX - width
    val top = if (clampedY >= anchorY) anchorY else anchorY - height
    return NormalizedCropRect(
        left = left.coerceIn(0f, 1f),
        top = top.coerceIn(0f, 1f),
        right = (left + width).coerceIn(0f, 1f),
        bottom = (top + height).coerceIn(0f, 1f),
    )
}
