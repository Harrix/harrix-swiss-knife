package dev.harrix.hsk.ui.gallery

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectDragGestures
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
    rotationQuarterTurns: Int,
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
    val handleHitSlopPx = with(density) { 28.dp.toPx() }
    val cropRectState = rememberUpdatedState(cropRect)
    val onCropRectChangeState = rememberUpdatedState(onCropRectChange)
    val turns = PhotoEditSaver.positiveMod(rotationQuarterTurns, 4)

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
            val fitted =
                remember(viewportW, viewportH, imageWidth, imageHeight, turns) {
                    if (imageWidth > 0 && imageHeight > 0) {
                        PhotoEditSaver.fittedImageRect(
                            viewportW,
                            viewportH,
                            imageWidth,
                            imageHeight,
                            turns,
                        )
                    } else {
                        PhotoEditSaver.FittedRect(0f, 0f, 0f, 0f)
                    }
                }

            if (fitted.width > 0f && fitted.height > 0f) {
                val preRotateW = if (turns % 2 == 0) fitted.width else fitted.height
                val preRotateH = if (turns % 2 == 0) fitted.height else fitted.width

                Box(
                    modifier =
                    Modifier
                        .size(
                            width = with(density) { fitted.width.toDp() },
                            height = with(density) { fitted.height.toDp() },
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
                                width = with(density) { preRotateW.toDp() },
                                height = with(density) { preRotateH.toDp() },
                            )
                            .graphicsLayer {
                                rotationZ = turns * 90f
                            },
                    )
                }

                val cropPx =
                    Rect(
                        left = fitted.left + cropRect.left * fitted.width,
                        top = fitted.top + cropRect.top * fitted.height,
                        right = fitted.left + cropRect.right * fitted.width,
                        bottom = fitted.top + cropRect.bottom * fitted.height,
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
                    val thirdW = cropPx.width / 3f
                    val thirdH = cropPx.height / 3f
                    for (i in 1..2) {
                        val x = cropPx.left + thirdW * i
                        drawLine(
                            color = Color.White.copy(alpha = 0.7f),
                            start = Offset(x, cropPx.top),
                            end = Offset(x, cropPx.bottom),
                            strokeWidth = 1.dp.toPx(),
                        )
                        val y = cropPx.top + thirdH * i
                        drawLine(
                            color = Color.White.copy(alpha = 0.7f),
                            start = Offset(cropPx.left, y),
                            end = Offset(cropPx.right, y),
                            strokeWidth = 1.dp.toPx(),
                        )
                    }
                    val handle = 14.dp.toPx()
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
                        .pointerInput(fitted, handleHitSlopPx, isSaving, turns) {
                            if (isSaving) {
                                return@pointerInput
                            }
                            var mode = CropDragMode.Move
                            detectDragGestures(
                                onDragStart = { start ->
                                    val currentCrop = cropRectState.value
                                    val currentCropPx =
                                        Rect(
                                            left = fitted.left + currentCrop.left * fitted.width,
                                            top = fitted.top + currentCrop.top * fitted.height,
                                            right = fitted.left + currentCrop.right * fitted.width,
                                            bottom = fitted.top + currentCrop.bottom * fitted.height,
                                        )
                                    mode = hitTestCropHandle(start, currentCropPx, handleHitSlopPx)
                                },
                                onDrag = { change, dragAmount ->
                                    change.consume()
                                    val next =
                                        applyCropDrag(
                                            cropRect = cropRectState.value,
                                            mode = mode,
                                            dragX = dragAmount.x / fitted.width,
                                            dragY = dragAmount.y / fitted.height,
                                            imageAspect = fitted.width / fitted.height,
                                        )
                                    onCropRectChangeState.value(PhotoEditSaver.clampCropRect(next))
                                },
                            )
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

private fun hitTestCropHandle(
    point: Offset,
    cropPx: Rect,
    slop: Float,
): CropDragMode {
    val corners =
        listOf(
            CropDragMode.ResizeTopLeft to Offset(cropPx.left, cropPx.top),
            CropDragMode.ResizeTopRight to Offset(cropPx.right, cropPx.top),
            CropDragMode.ResizeBottomLeft to Offset(cropPx.left, cropPx.bottom),
            CropDragMode.ResizeBottomRight to Offset(cropPx.right, cropPx.bottom),
        )
    for ((mode, corner) in corners) {
        if (abs(point.x - corner.x) <= slop && abs(point.y - corner.y) <= slop) {
            return mode
        }
    }
    return CropDragMode.Move
}

/**
 * Resize keeps the crop aspect equal to the displayed (rotated) image aspect.
 */
private fun applyCropDrag(
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
    if (width / max(height, 1e-6f) > imageAspect) {
        height = width / imageAspect
    } else {
        width = height * imageAspect
    }
    width = min(width, if (clampedX >= anchorX) 1f - anchorX else anchorX)
    height = width / imageAspect
    height = min(height, if (clampedY >= anchorY) 1f - anchorY else anchorY)
    width = height * imageAspect

    val left = if (clampedX >= anchorX) anchorX else anchorX - width
    val top = if (clampedY >= anchorY) anchorY else anchorY - height
    return NormalizedCropRect(
        left = left.coerceIn(0f, 1f),
        top = top.coerceIn(0f, 1f),
        right = (left + width).coerceIn(0f, 1f),
        bottom = (top + height).coerceIn(0f, 1f),
    )
}
