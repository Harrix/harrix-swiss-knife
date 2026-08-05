package dev.harrix.hsk.ui.gallery

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.calculatePan
import androidx.compose.foundation.gestures.calculateRotation
import androidx.compose.foundation.gestures.calculateZoom
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Crop
import androidx.compose.material.icons.filled.CropFree
import androidx.compose.material.icons.filled.CropRotate
import androidx.compose.material.icons.filled.Done
import androidx.compose.material.icons.filled.FileCopy
import androidx.compose.material.icons.filled.FitScreen
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.RestartAlt
import androidx.compose.material.icons.filled.Rotate90DegreesCcw
import androidx.compose.material.icons.filled.Rotate90DegreesCw
import androidx.compose.material.icons.filled.Transform
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.FilledIconButton
import androidx.compose.material3.FilledTonalIconButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedIconButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
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
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.input.pointer.positionChanged
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import coil.request.ImageRequest
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.CameraPhoto
import dev.harrix.hsk.gallery.NormalizedCropRect
import dev.harrix.hsk.gallery.NormalizedPerspectiveQuad
import dev.harrix.hsk.gallery.PhotoEditSaver
import dev.harrix.hsk.ui.OverflowTextTooltipBox
import dev.harrix.hsk.ui.adaptiveBottomBarWidth
import dev.harrix.hsk.ui.isCompactHeight
import dev.harrix.hsk.ui.isCompactWidth
import kotlinx.coroutines.delay
import kotlin.math.abs
import kotlin.math.hypot
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt
import coil.size.Size as CoilSize

private const val CropViewMinZoom = 0.5f
private const val CropViewMaxZoom = 5f
private const val CropViewZoomEpsilon = 0.02f

private enum class CropDragMode {
    Move,
    ResizeTopLeft,
    ResizeTopRight,
    ResizeBottomLeft,
    ResizeBottomRight,
}

/** Drag modes for perspective-crop corners (indices match [NormalizedPerspectiveQuad.corners]). */
private enum class PerspectiveDragMode {
    Move,
    Corner0,
    Corner1,
    Corner2,
    Corner3,
}

/** Accent color for the perspective frame (distinct from the white AABB crop). */
private val PerspectiveFrameColor = Color(0xFFFFB74D)

/** Locked crop aspect relative to the square workspace, or free resize. */
private const val AspectThreeFour = 3f / 4f
private const val AspectMatchEpsilon = 0.02f

private fun nearAspect(
    aspect: Float,
    target: Float,
): Boolean = abs(aspect - target) < AspectMatchEpsilon

private fun isThreeFourFamily(aspect: Float): Boolean = nearAspect(aspect, AspectThreeFour) ||
    nearAspect(aspect, 1f / AspectThreeFour)

@Composable
fun PhotoCropEditor(
    photo: CameraPhoto,
    rotationDegrees: Float,
    onRotationDegreesChange: (Float) -> Unit,
    cropRect: NormalizedCropRect,
    onCropRectChange: (NormalizedCropRect) -> Unit,
    perspectiveQuad: NormalizedPerspectiveQuad?,
    onPerspectiveQuadChange: (NormalizedPerspectiveQuad?) -> Unit,
    imageRevision: Int,
    isSaving: Boolean,
    onSave: () -> Unit,
    onDiscard: () -> Unit,
    modifier: Modifier = Modifier,
    onSaveCopy: (() -> Unit)? = null,
) {
    val context = LocalContext.current
    val density = LocalDensity.current
    val photoEditSaver = remember { PhotoEditSaver(context.applicationContext) }
    var imageWidth by remember(photo.id, imageRevision) { mutableIntStateOf(0) }
    var imageHeight by remember(photo.id, imageRevision) { mutableIntStateOf(0) }
    // Large hit targets: corners sit near the phone bezel and are hard to grab otherwise.
    val handleHitSlopPx = with(density) { 52.dp.toPx() }
    val handleVisualPx = with(density) { 24.dp.toPx() }
    val cropRectState = rememberUpdatedState(cropRect)
    val onCropRectChangeState = rememberUpdatedState(onCropRectChange)
    val perspectiveQuadState = rememberUpdatedState(perspectiveQuad)
    val onPerspectiveQuadChangeState = rememberUpdatedState(onPerspectiveQuadChange)
    val rotationState = rememberUpdatedState(rotationDegrees)
    val onRotationDegreesChangeState = rememberUpdatedState(onRotationDegreesChange)
    var isRotatingHint by remember { mutableStateOf(false) }
    var didInitCrop by remember(photo.id, imageRevision) { mutableStateOf(false) }
    val isPerspective = perspectiveQuad != null

    /** `null` = free aspect; otherwise width/height lock for the crop frame. */
    var lockedAspect by remember(photo.id, imageRevision) { mutableStateOf<Float?>(null) }
    val lockedAspectState = rememberUpdatedState(lockedAspect)
    var viewScale by remember(photo.id, imageRevision) { mutableFloatStateOf(1f) }
    var viewOffset by remember(photo.id, imageRevision) { mutableStateOf(Offset.Zero) }
    val viewScaleState = rememberUpdatedState(viewScale)
    val viewOffsetState = rememberUpdatedState(viewOffset)
    var lastViewportW by remember(photo.id, imageRevision) { mutableFloatStateOf(0f) }
    var lastViewportH by remember(photo.id, imageRevision) { mutableFloatStateOf(0f) }
    var lastWorkspaceSide by remember(photo.id, imageRevision) { mutableFloatStateOf(0f) }
    var trimSuggestion by remember(photo.id, imageRevision) {
        mutableStateOf<NormalizedCropRect?>(null)
    }
    val showTrimBars = trimSuggestion != null && !isPerspective
    val isViewTransformed =
        abs(viewScale - 1f) > CropViewZoomEpsilon ||
            hypot(viewOffset.x.toDouble(), viewOffset.y.toDouble()) > 1.0

    fun trimEmptyZones() {
        val suggestion = trimSuggestion ?: return
        if (isSaving || isPerspective) {
            return
        }
        lockedAspect = null
        onCropRectChange(suggestion)
        trimSuggestion = null
    }

    fun togglePerspectiveMode() {
        if (isSaving || imageWidth <= 0) {
            return
        }
        val currentQuad = perspectiveQuad
        if (currentQuad == null) {
            lockedAspect = null
            trimSuggestion = null
            onPerspectiveQuadChange(
                PhotoEditSaver.clampPerspectiveQuad(
                    NormalizedPerspectiveQuad.fromRect(cropRect),
                ),
            )
        } else {
            onCropRectChange(currentQuad.boundingRect())
            onPerspectiveQuadChange(null)
        }
    }

    LaunchedEffect(imageWidth, imageHeight, didInitCrop) {
        if (!didInitCrop && imageWidth > 0 && imageHeight > 0) {
            onCropRectChangeState.value(PhotoEditSaver.imageContentCrop(imageWidth, imageHeight))
            lockedAspect = imageWidth.toFloat() / imageHeight.toFloat()
            didInitCrop = true
        }
    }

    LaunchedEffect(
        photo.id,
        imageRevision,
        rotationDegrees,
        cropRect,
        perspectiveQuad,
        imageWidth,
        imageHeight,
        didInitCrop,
    ) {
        if (!didInitCrop || isSaving || perspectiveQuad != null) {
            trimSuggestion = null
            return@LaunchedEffect
        }
        if (imageWidth <= 0 || imageHeight <= 0) {
            trimSuggestion = null
            return@LaunchedEffect
        }
        trimSuggestion = null
        delay(280)
        val analysis =
            photoEditSaver.analyzeCropEmptyZones(
                imageWidth = imageWidth,
                imageHeight = imageHeight,
                rotationDegrees = rotationDegrees,
                crop = cropRect,
            )
        trimSuggestion =
            if (analysis.hasEmptyZones) {
                analysis.suggestedCrop
            } else {
                null
            }
    }

    val originalAspect =
        remember(imageWidth, imageHeight) {
            if (imageWidth > 0 && imageHeight > 0) {
                imageWidth.toFloat() / imageHeight.toFloat()
            } else {
                1f
            }
        }
    val showThreeFourChip =
        imageWidth > 0 && imageHeight > 0 && !nearAspect(originalAspect, AspectThreeFour)

    fun applyLockedAspect(aspect: Float) {
        if (imageWidth <= 0 || imageHeight <= 0) {
            return
        }
        lockedAspect = aspect
        val base = PhotoEditSaver.imageContentCrop(imageWidth, imageHeight)
        onCropRectChange(PhotoEditSaver.fitCropToAspect(base, aspect))
    }

    fun rotateCropAspect90() {
        if (imageWidth <= 0 || imageHeight <= 0) {
            return
        }
        val swapped = PhotoEditSaver.swapCropDimensions(cropRect)
        onCropRectChange(swapped)
        val currentLock = lockedAspect
        if (currentLock != null) {
            lockedAspect = 1f / currentLock.coerceAtLeast(1e-6f)
        }
    }

    fun toggleFreeAspect() {
        if (imageWidth <= 0 || imageHeight <= 0) {
            return
        }
        if (lockedAspect == null) {
            applyLockedAspect(originalAspect)
        } else {
            lockedAspect = null
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
            SideEffect {
                lastViewportW = viewportW
                lastViewportH = viewportH
                lastWorkspaceSide = workspace.width
            }
            val imageDrawSize =
                remember(imageWidth, imageHeight, workspace) {
                    PhotoEditSaver.imageDrawSizeInWorkspace(imageWidth, imageHeight, workspace)
                }

            if (workspace.width > 0f && imageDrawSize.first > 0f) {
                // All crop math is local to this square (0..side). The photo is smaller and
                // centered; black letterbox around it is valid crop space (saved as black).
                // Pinch zoom/pan scales the whole square (image + crop frame together).
                Box(
                    modifier =
                    Modifier
                        .size(
                            width = with(density) { workspace.width.toDp() },
                            height = with(density) { workspace.height.toDp() },
                        )
                        .graphicsLayer {
                            scaleX = viewScale
                            scaleY = viewScale
                            translationX = viewOffset.x
                            translationY = viewOffset.y
                        }
                        .background(Color.Black),
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

                    val side = workspace.width
                    val activeQuad = perspectiveQuad
                    val cropPx =
                        Rect(
                            left = cropRect.left * side,
                            top = cropRect.top * side,
                            right = cropRect.right * side,
                            bottom = cropRect.bottom * side,
                        )
                    val quadCornersPx =
                        activeQuad?.corners()?.map { corner ->
                            Offset(corner.x * side, corner.y * side)
                        }

                    Canvas(modifier = Modifier.fillMaxSize()) {
                        // Canvas lives inside zoomed graphicsLayer — divide by scale so
                        // strokes and corner handles stay constant on screen.
                        val invScale = 1f / viewScale.coerceAtLeast(1e-6f)
                        val cropStroke = 2.dp.toPx() * invScale
                        val guideStroke = 1.dp.toPx() * invScale
                        val handle = handleVisualPx * invScale
                        if (quadCornersPx != null && quadCornersPx.size == 4) {
                            val framePath =
                                Path().apply {
                                    moveTo(quadCornersPx[0].x, quadCornersPx[0].y)
                                    lineTo(quadCornersPx[1].x, quadCornersPx[1].y)
                                    lineTo(quadCornersPx[2].x, quadCornersPx[2].y)
                                    lineTo(quadCornersPx[3].x, quadCornersPx[3].y)
                                    close()
                                }
                            val dimPath =
                                Path().apply {
                                    fillType = PathFillType.EvenOdd
                                    addRect(Rect(0f, 0f, size.width, size.height))
                                    addPath(framePath)
                                }
                            drawPath(dimPath, Color.Black.copy(alpha = 0.55f))
                            drawPath(
                                path = framePath,
                                color = PerspectiveFrameColor,
                                style = Stroke(width = cropStroke),
                            )
                            // Diagonals help align poster/document corners.
                            drawLine(
                                color = PerspectiveFrameColor.copy(alpha = 0.55f),
                                start = quadCornersPx[0],
                                end = quadCornersPx[2],
                                strokeWidth = guideStroke,
                            )
                            drawLine(
                                color = PerspectiveFrameColor.copy(alpha = 0.55f),
                                start = quadCornersPx[1],
                                end = quadCornersPx[3],
                                strokeWidth = guideStroke,
                            )
                            quadCornersPx.forEach { corner ->
                                drawRect(
                                    color = PerspectiveFrameColor.copy(alpha = 0.85f),
                                    topLeft = Offset(corner.x - handle / 2f, corner.y - handle / 2f),
                                    size = Size(handle, handle),
                                )
                            }
                        } else {
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
                                style = Stroke(width = cropStroke),
                            )
                            val guideColor = Color.White.copy(alpha = 0.7f)
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
                            val corners =
                                listOf(
                                    Offset(cropPx.left, cropPx.top),
                                    Offset(cropPx.right, cropPx.top),
                                    Offset(cropPx.left, cropPx.bottom),
                                    Offset(cropPx.right, cropPx.bottom),
                                )
                            corners.forEach { corner ->
                                drawRect(
                                    color = Color.White.copy(alpha = 0.55f),
                                    topLeft = Offset(corner.x - handle / 2f, corner.y - handle / 2f),
                                    size = Size(handle, handle),
                                )
                            }
                        }
                    }

                    Box(
                        modifier =
                        Modifier
                            .fillMaxSize()
                            .pointerInput(
                                side,
                                handleHitSlopPx,
                                isSaving,
                                imageWidth,
                                imageHeight,
                                lockedAspect,
                                isPerspective,
                                viewportW,
                                viewportH,
                            ) {
                                if (isSaving) {
                                    return@pointerInput
                                }
                                awaitEachGesture {
                                    awaitFirstDown(requireUnconsumed = false)
                                    var multiTouch = false
                                    var cropMode: CropDragMode? = null
                                    var perspectiveMode: PerspectiveDragMode? = null
                                    var gestureActive = true
                                    var gestureScale = viewScaleState.value
                                    var gestureOffset = viewOffsetState.value
                                    isRotatingHint = false

                                    while (gestureActive) {
                                        val event = awaitPointerEvent()
                                        val pressed = event.changes.filter { it.pressed }
                                        if (pressed.isEmpty()) {
                                            gestureActive = false
                                        } else if (pressed.size >= 2) {
                                            multiTouch = true
                                            cropMode = null
                                            perspectiveMode = null
                                            val rotationDelta = event.calculateRotation()
                                            val zoomChange = event.calculateZoom()
                                            val panChange = event.calculatePan()
                                            if (rotationDelta != 0f) {
                                                isRotatingHint = true
                                                onRotationDegreesChangeState.value(
                                                    rotationState.value + rotationDelta,
                                                )
                                            }
                                            if (zoomChange != 1f || panChange != Offset.Zero) {
                                                gestureScale =
                                                    (gestureScale * zoomChange)
                                                        .coerceIn(CropViewMinZoom, CropViewMaxZoom)
                                                gestureOffset =
                                                    clampCropViewOffset(
                                                        offset = gestureOffset + panChange,
                                                        scale = gestureScale,
                                                        side = side,
                                                        viewportW = viewportW,
                                                        viewportH = viewportH,
                                                    )
                                                viewScale = gestureScale
                                                viewOffset = gestureOffset
                                            }
                                            pressed.forEach { change ->
                                                if (change.positionChanged()) {
                                                    change.consume()
                                                }
                                            }
                                        } else if (!multiTouch && pressed.size == 1) {
                                            val change = pressed[0]
                                            val currentPerspective = perspectiveQuadState.value
                                            if (currentPerspective != null) {
                                                val activeMode = perspectiveMode
                                                if (activeMode == null) {
                                                    val hitSlop =
                                                        handleHitSlopPx /
                                                            viewScaleState.value.coerceAtLeast(1e-6f)
                                                    val cornersPx =
                                                        currentPerspective.corners().map { corner ->
                                                            Offset(corner.x * side, corner.y * side)
                                                        }
                                                    perspectiveMode =
                                                        hitTestPerspectiveHandle(
                                                            change.position,
                                                            cornersPx,
                                                            hitSlop,
                                                        )
                                                } else if (side > 0f) {
                                                    val drag =
                                                        change.position - change.previousPosition
                                                    if (drag != Offset.Zero) {
                                                        val next =
                                                            when (activeMode) {
                                                                PerspectiveDragMode.Move ->
                                                                    PhotoEditSaver.movePerspectiveQuad(
                                                                        currentPerspective,
                                                                        drag.x / side,
                                                                        drag.y / side,
                                                                    )

                                                                PerspectiveDragMode.Corner0 ->
                                                                    PhotoEditSaver.dragPerspectiveCorner(
                                                                        currentPerspective,
                                                                        0,
                                                                        drag.x / side,
                                                                        drag.y / side,
                                                                    )

                                                                PerspectiveDragMode.Corner1 ->
                                                                    PhotoEditSaver.dragPerspectiveCorner(
                                                                        currentPerspective,
                                                                        1,
                                                                        drag.x / side,
                                                                        drag.y / side,
                                                                    )

                                                                PerspectiveDragMode.Corner2 ->
                                                                    PhotoEditSaver.dragPerspectiveCorner(
                                                                        currentPerspective,
                                                                        2,
                                                                        drag.x / side,
                                                                        drag.y / side,
                                                                    )

                                                                PerspectiveDragMode.Corner3 ->
                                                                    PhotoEditSaver.dragPerspectiveCorner(
                                                                        currentPerspective,
                                                                        3,
                                                                        drag.x / side,
                                                                        drag.y / side,
                                                                    )
                                                            }
                                                        onPerspectiveQuadChangeState.value(next)
                                                        change.consume()
                                                    }
                                                }
                                            } else {
                                                val activeMode = cropMode
                                                if (activeMode == null) {
                                                    val currentCrop = cropRectState.value
                                                    val currentCropPx =
                                                        Rect(
                                                            left = currentCrop.left * side,
                                                            top = currentCrop.top * side,
                                                            right = currentCrop.right * side,
                                                            bottom = currentCrop.bottom * side,
                                                        )
                                                    val hitSlop =
                                                        handleHitSlopPx /
                                                            viewScaleState.value.coerceAtLeast(1e-6f)
                                                    cropMode =
                                                        hitTestCropHandle(
                                                            change.position,
                                                            currentCropPx,
                                                            hitSlop,
                                                        )
                                                } else if (
                                                    imageHeight > 0 &&
                                                    side > 0f
                                                ) {
                                                    val drag =
                                                        change.position - change.previousPosition
                                                    if (drag != Offset.Zero) {
                                                        val aspectLock = lockedAspectState.value
                                                        val next =
                                                            if (aspectLock == null) {
                                                                applyFreeCropDrag(
                                                                    cropRect = cropRectState.value,
                                                                    mode = activeMode,
                                                                    dragX = drag.x / side,
                                                                    dragY = drag.y / side,
                                                                )
                                                            } else {
                                                                applyAspectCropDrag(
                                                                    cropRect = cropRectState.value,
                                                                    mode = activeMode,
                                                                    dragX = drag.x / side,
                                                                    dragY = drag.y / side,
                                                                    imageAspect = aspectLock,
                                                                )
                                                            }
                                                        onCropRectChangeState.value(
                                                            if (aspectLock == null) {
                                                                PhotoEditSaver.clampCropRectFree(next)
                                                            } else {
                                                                PhotoEditSaver.clampCropRect(
                                                                    rect = next,
                                                                    imageAspect = aspectLock,
                                                                )
                                                            },
                                                        )
                                                        change.consume()
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    isRotatingHint = false
                                }
                            },
                    )
                }
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

            if (!isSaving && workspace.width > 0f && imageWidth > 0) {
                Row(
                    modifier =
                    Modifier
                        .align(Alignment.TopEnd)
                        .padding(12.dp),
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    if (showTrimBars) {
                        EditToolbarIconButton(
                            onClick = { trimEmptyZones() },
                            icon = Icons.Filled.Crop,
                            label = stringResource(R.string.gallery_cleaner_edit_trim_empty),
                            tonal = true,
                        )
                    }
                    if (isViewTransformed && !isPerspective) {
                        EditToolbarIconButton(
                            onClick = {
                                val visible =
                                    visibleWorkspaceNormalized(
                                        viewportW = viewportW,
                                        viewportH = viewportH,
                                        side = workspace.width,
                                        scale = viewScale,
                                        offset = viewOffset,
                                    )
                                onCropRectChange(
                                    PhotoEditSaver.fitCropIntoBounds(
                                        rect = cropRect,
                                        bounds = visible,
                                    ),
                                )
                            },
                            icon = Icons.Filled.FitScreen,
                            label = stringResource(R.string.gallery_cleaner_edit_fit_frame),
                            tonal = true,
                        )
                    }
                }
            }

            if (isSaving) {
                CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.Center),
                    color = Color.White,
                )
            }
        }

        val compactChrome = isCompactWidth() || isCompactHeight()
        val aspectRotateLabel = stringResource(R.string.gallery_cleaner_edit_aspect_rotate)
        val aspectThreeFourLabel = stringResource(R.string.gallery_cleaner_edit_aspect_3_4)
        val aspectFreeLabel = stringResource(R.string.gallery_cleaner_edit_aspect_free)
        val perspectiveLabel = stringResource(R.string.gallery_cleaner_edit_perspective)
        val rotateCcwLabel = stringResource(R.string.gallery_cleaner_edit_rotate_ccw)
        val resetRotationLabel = stringResource(R.string.gallery_cleaner_edit_reset_rotation)
        val rotateCwLabel = stringResource(R.string.gallery_cleaner_edit_rotate_cw)
        val trimEmptyLabel = stringResource(R.string.gallery_cleaner_edit_trim_empty)
        val fitFrameLabel = stringResource(R.string.gallery_cleaner_edit_fit_frame)
        val discardLabel = stringResource(R.string.gallery_cleaner_edit_discard)
        val saveCopyLabel = stringResource(R.string.photo_editor_save_copy)
        val saveLabel = stringResource(R.string.gallery_cleaner_edit_save)
        val moreLabel = stringResource(R.string.gallery_cleaner_edit_more)
        val locked = lockedAspect
        val threeFourSelected = locked != null && isThreeFourFamily(locked)
        val freeAspectSelected = lockedAspect == null && !isPerspective
        val canEditAspect = !isSaving && imageWidth > 0 && !isPerspective
        val canTogglePerspective = !isSaving && imageWidth > 0
        val canResetRotation = !isSaving && abs(displayDegrees) >= 0.5f
        val canFitFrame = isViewTransformed && !isPerspective && imageWidth > 0
        var moreMenuExpanded by remember { mutableStateOf(false) }

        fun applyFitFrame() {
            if (!canFitFrame || lastWorkspaceSide <= 0f) {
                return
            }
            val visible =
                visibleWorkspaceNormalized(
                    viewportW = lastViewportW,
                    viewportH = lastViewportH,
                    side = lastWorkspaceSide,
                    scale = viewScale,
                    offset = viewOffset,
                )
            onCropRectChange(
                PhotoEditSaver.fitCropIntoBounds(
                    rect = cropRect,
                    bounds = visible,
                ),
            )
        }

        Box(
            modifier =
            Modifier
                .fillMaxWidth()
                .background(MaterialTheme.colorScheme.background),
            contentAlignment = Alignment.Center,
        ) {
            Column(
                modifier =
                Modifier
                    .adaptiveBottomBarWidth()
                    .padding(
                        horizontal = if (compactChrome) 4.dp else 8.dp,
                        vertical = if (compactChrome) 4.dp else 8.dp,
                    ),
                verticalArrangement = Arrangement.spacedBy(if (compactChrome) 2.dp else 4.dp),
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    EditToolbarIconButton(
                        onClick = { rotateCropAspect90() },
                        icon = Icons.Filled.CropRotate,
                        label = aspectRotateLabel,
                        enabled = canEditAspect,
                    )
                    if (showThreeFourChip) {
                        EditToolbarIconButton(
                            onClick = {
                                if (threeFourSelected) {
                                    applyLockedAspect(originalAspect)
                                } else {
                                    applyLockedAspect(AspectThreeFour)
                                }
                            },
                            icon = Icons.Filled.Crop,
                            label = aspectThreeFourLabel,
                            enabled = canEditAspect,
                            selected = threeFourSelected,
                        )
                    }
                    EditToolbarIconButton(
                        onClick = { toggleFreeAspect() },
                        icon = Icons.Filled.CropFree,
                        label = aspectFreeLabel,
                        enabled = canEditAspect,
                        selected = freeAspectSelected,
                    )
                    EditToolbarIconButton(
                        onClick = { togglePerspectiveMode() },
                        icon = Icons.Filled.Transform,
                        label = perspectiveLabel,
                        enabled = canTogglePerspective,
                        selected = isPerspective,
                    )
                    EditToolbarIconButton(
                        onClick = { onRotationDegreesChange(rotationDegrees - 90f) },
                        icon = Icons.Filled.Rotate90DegreesCcw,
                        label = rotateCcwLabel,
                        enabled = !isSaving,
                    )
                    EditToolbarIconButton(
                        onClick = { onRotationDegreesChange(0f) },
                        icon = Icons.Filled.RestartAlt,
                        label = resetRotationLabel,
                        enabled = canResetRotation,
                    )
                    EditToolbarIconButton(
                        onClick = { onRotationDegreesChange(rotationDegrees + 90f) },
                        icon = Icons.Filled.Rotate90DegreesCw,
                        label = rotateCwLabel,
                        enabled = !isSaving,
                    )
                    Box {
                        EditToolbarIconButton(
                            onClick = { moreMenuExpanded = true },
                            icon = Icons.Filled.MoreVert,
                            label = moreLabel,
                            enabled = !isSaving,
                        )
                        DropdownMenu(
                            expanded = moreMenuExpanded,
                            onDismissRequest = { moreMenuExpanded = false },
                        ) {
                            EditOverflowMenuItem(
                                icon = Icons.Filled.CropRotate,
                                label = aspectRotateLabel,
                                enabled = canEditAspect,
                                onClick = {
                                    moreMenuExpanded = false
                                    rotateCropAspect90()
                                },
                            )
                            if (showThreeFourChip) {
                                EditOverflowMenuItem(
                                    icon = Icons.Filled.Crop,
                                    label = aspectThreeFourLabel,
                                    enabled = canEditAspect,
                                    onClick = {
                                        moreMenuExpanded = false
                                        if (threeFourSelected) {
                                            applyLockedAspect(originalAspect)
                                        } else {
                                            applyLockedAspect(AspectThreeFour)
                                        }
                                    },
                                )
                            }
                            EditOverflowMenuItem(
                                icon = Icons.Filled.CropFree,
                                label = aspectFreeLabel,
                                enabled = canEditAspect,
                                onClick = {
                                    moreMenuExpanded = false
                                    toggleFreeAspect()
                                },
                            )
                            EditOverflowMenuItem(
                                icon = Icons.Filled.Transform,
                                label = perspectiveLabel,
                                enabled = canTogglePerspective,
                                onClick = {
                                    moreMenuExpanded = false
                                    togglePerspectiveMode()
                                },
                            )
                            HorizontalDivider()
                            EditOverflowMenuItem(
                                icon = Icons.Filled.Rotate90DegreesCcw,
                                label = rotateCcwLabel,
                                enabled = !isSaving,
                                onClick = {
                                    moreMenuExpanded = false
                                    onRotationDegreesChange(rotationDegrees - 90f)
                                },
                            )
                            EditOverflowMenuItem(
                                icon = Icons.Filled.RestartAlt,
                                label = resetRotationLabel,
                                enabled = canResetRotation,
                                onClick = {
                                    moreMenuExpanded = false
                                    onRotationDegreesChange(0f)
                                },
                            )
                            EditOverflowMenuItem(
                                icon = Icons.Filled.Rotate90DegreesCw,
                                label = rotateCwLabel,
                                enabled = !isSaving,
                                onClick = {
                                    moreMenuExpanded = false
                                    onRotationDegreesChange(rotationDegrees + 90f)
                                },
                            )
                            HorizontalDivider()
                            EditOverflowMenuItem(
                                icon = Icons.Filled.Crop,
                                label = trimEmptyLabel,
                                enabled = showTrimBars && !isSaving,
                                onClick = {
                                    moreMenuExpanded = false
                                    trimEmptyZones()
                                },
                            )
                            EditOverflowMenuItem(
                                icon = Icons.Filled.FitScreen,
                                label = fitFrameLabel,
                                enabled = canFitFrame && !isSaving,
                                onClick = {
                                    moreMenuExpanded = false
                                    applyFitFrame()
                                },
                            )
                            HorizontalDivider()
                            EditOverflowMenuItem(
                                icon = Icons.Filled.Close,
                                label = discardLabel,
                                enabled = !isSaving,
                                onClick = {
                                    moreMenuExpanded = false
                                    onDiscard()
                                },
                            )
                            if (onSaveCopy != null) {
                                EditOverflowMenuItem(
                                    icon = Icons.Filled.FileCopy,
                                    label = saveCopyLabel,
                                    enabled = !isSaving,
                                    onClick = {
                                        moreMenuExpanded = false
                                        onSaveCopy()
                                    },
                                )
                            }
                            EditOverflowMenuItem(
                                icon = Icons.Filled.Done,
                                label = saveLabel,
                                enabled = !isSaving,
                                onClick = {
                                    moreMenuExpanded = false
                                    onSave()
                                },
                            )
                        }
                    }
                }
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    EditToolbarIconButton(
                        onClick = onDiscard,
                        icon = Icons.Filled.Close,
                        label = discardLabel,
                        enabled = !isSaving,
                        outlined = true,
                    )
                    if (onSaveCopy != null) {
                        EditToolbarIconButton(
                            onClick = onSaveCopy,
                            icon = Icons.Filled.FileCopy,
                            label = saveCopyLabel,
                            enabled = !isSaving,
                            outlined = true,
                        )
                    }
                    EditToolbarIconButton(
                        onClick = onSave,
                        icon = Icons.Filled.Done,
                        label = saveLabel,
                        enabled = !isSaving,
                        filled = true,
                    )
                }
            }
        }
    }
}

@Composable
private fun EditToolbarIconButton(
    onClick: () -> Unit,
    icon: ImageVector,
    label: String,
    enabled: Boolean = true,
    selected: Boolean = false,
    tonal: Boolean = false,
    outlined: Boolean = false,
    filled: Boolean = false,
) {
    OverflowTextTooltipBox(text = label, enabled = true) {
        val iconContent: @Composable () -> Unit = {
            Icon(
                imageVector = icon,
                contentDescription = label,
            )
        }
        when {
            filled ->
                FilledIconButton(
                    onClick = onClick,
                    enabled = enabled,
                    content = iconContent,
                )

            selected || tonal ->
                FilledTonalIconButton(
                    onClick = onClick,
                    enabled = enabled,
                    content = iconContent,
                )

            outlined ->
                OutlinedIconButton(
                    onClick = onClick,
                    enabled = enabled,
                    content = iconContent,
                )

            else ->
                IconButton(
                    onClick = onClick,
                    enabled = enabled,
                    content = iconContent,
                )
        }
    }
}

@Composable
private fun EditOverflowMenuItem(
    icon: ImageVector,
    label: String,
    onClick: () -> Unit,
    enabled: Boolean = true,
) {
    DropdownMenuItem(
        text = {
            Text(
                text = label,
                maxLines = Int.MAX_VALUE,
                overflow = TextOverflow.Clip,
            )
        },
        onClick = onClick,
        enabled = enabled,
        leadingIcon = {
            Icon(
                imageVector = icon,
                contentDescription = null,
            )
        },
    )
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
 * Clamp pan so a center-scaled square of [side] stays useful inside the viewport.
 */
private fun clampCropViewOffset(
    offset: Offset,
    scale: Float,
    side: Float,
    viewportW: Float,
    viewportH: Float,
): Offset {
    val scaled = side * scale.coerceAtLeast(1e-6f)
    val maxX = max(0f, (scaled - viewportW) / 2f)
    val maxY = max(0f, (scaled - viewportH) / 2f)
    return Offset(
        x = offset.x.coerceIn(-maxX, maxX),
        y = offset.y.coerceIn(-maxY, maxY),
    )
}

/**
 * Normalized region of the square workspace currently visible in the viewport.
 * Matches center-origin [graphicsLayer] scale + translation on a centered square.
 */
private fun visibleWorkspaceNormalized(
    viewportW: Float,
    viewportH: Float,
    side: Float,
    scale: Float,
    offset: Offset,
): NormalizedCropRect {
    val s = scale.coerceAtLeast(1e-6f)
    val centerX = viewportW / 2f
    val centerY = viewportH / 2f
    fun parentToNorm(
        px: Float,
        py: Float,
    ): Pair<Float, Float> {
        val lx = side / 2f + (px - centerX - offset.x) / s
        val ly = side / 2f + (py - centerY - offset.y) / s
        return (lx / side) to (ly / side)
    }
    val (nLeft, nTop) = parentToNorm(0f, 0f)
    val (nRight, nBottom) = parentToNorm(viewportW, viewportH)
    val left = min(nLeft, nRight).coerceIn(0f, 1f)
    val top = min(nTop, nBottom).coerceIn(0f, 1f)
    val right = max(nLeft, nRight).coerceIn(0f, 1f)
    val bottom = max(nTop, nBottom).coerceIn(0f, 1f)
    if (right - left < 0.06f || bottom - top < 0.06f) {
        return NormalizedCropRect.Full
    }
    return NormalizedCropRect(left, top, right, bottom)
}

/**
 * Prefer perspective corner handles; move when the press is inside the quad.
 */
private fun hitTestPerspectiveHandle(
    point: Offset,
    cornersPx: List<Offset>,
    slop: Float,
): PerspectiveDragMode? {
    if (cornersPx.size != 4) {
        return null
    }
    val cornerModes =
        listOf(
            PerspectiveDragMode.Corner0,
            PerspectiveDragMode.Corner1,
            PerspectiveDragMode.Corner2,
            PerspectiveDragMode.Corner3,
        )
    var bestMode: PerspectiveDragMode? = null
    var bestDistSq = Float.MAX_VALUE
    for (i in cornersPx.indices) {
        val corner = cornersPx[i]
        val dx = point.x - corner.x
        val dy = point.y - corner.y
        if (abs(dx) <= slop && abs(dy) <= slop) {
            val distSq = dx * dx + dy * dy
            if (distSq < bestDistSq) {
                bestDistSq = distSq
                bestMode = cornerModes[i]
            }
        }
    }
    if (bestMode != null) {
        return bestMode
    }
    return if (pointInConvexQuad(point, cornersPx)) {
        PerspectiveDragMode.Move
    } else {
        null
    }
}

/** Ray-crossing test for a convex quad (or any simple polygon). */
private fun pointInConvexQuad(
    point: Offset,
    corners: List<Offset>,
): Boolean {
    if (corners.size != 4) {
        return false
    }
    var inside = false
    var j = corners.lastIndex
    for (i in corners.indices) {
        val ci = corners[i]
        val cj = corners[j]
        val intersects =
            (ci.y > point.y) != (cj.y > point.y) &&
                point.x < (cj.x - ci.x) * (point.y - ci.y) / (cj.y - ci.y + 1e-6f) + ci.x
        if (intersects) {
            inside = !inside
        }
        j = i
    }
    return inside
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

/** Free resize/move on the square workspace (no aspect lock). */
private fun applyFreeCropDrag(
    cropRect: NormalizedCropRect,
    mode: CropDragMode,
    dragX: Float,
    dragY: Float,
): NormalizedCropRect {
    if (mode == CropDragMode.Move) {
        val width = cropRect.width
        val height = cropRect.height
        val left = (cropRect.left + dragX).coerceIn(0f, (1f - width).coerceAtLeast(0f))
        val top = (cropRect.top + dragY).coerceIn(0f, (1f - height).coerceAtLeast(0f))
        return NormalizedCropRect(left, top, left + width, top + height)
    }
    var left = cropRect.left
    var top = cropRect.top
    var right = cropRect.right
    var bottom = cropRect.bottom
    when (mode) {
        CropDragMode.ResizeTopLeft -> {
            left = (left + dragX).coerceIn(0f, right - 0.06f)
            top = (top + dragY).coerceIn(0f, bottom - 0.06f)
        }

        CropDragMode.ResizeTopRight -> {
            right = (right + dragX).coerceIn(left + 0.06f, 1f)
            top = (top + dragY).coerceIn(0f, bottom - 0.06f)
        }

        CropDragMode.ResizeBottomLeft -> {
            left = (left + dragX).coerceIn(0f, right - 0.06f)
            bottom = (bottom + dragY).coerceIn(top + 0.06f, 1f)
        }

        CropDragMode.ResizeBottomRight -> {
            right = (right + dragX).coerceIn(left + 0.06f, 1f)
            bottom = (bottom + dragY).coerceIn(top + 0.06f, 1f)
        }

        CropDragMode.Move -> Unit
    }
    return NormalizedCropRect(left, top, right, bottom)
}

/**
 * Keeps crop aspect equal to [imageAspect]. Workspace is the full square canvas
 * (not only the photo): move/resize may place the frame over black letterbox so the
 * saved result can be partly black.
 */
private fun applyAspectCropDrag(
    cropRect: NormalizedCropRect,
    mode: CropDragMode,
    dragX: Float,
    dragY: Float,
    imageAspect: Float,
): NormalizedCropRect {
    val aspect = imageAspect.coerceAtLeast(1e-6f)
    if (mode == CropDragMode.Move) {
        // Keep size; slide anywhere inside the square (including black letterbox).
        val width = cropRect.width
        val height = cropRect.height
        val left = (cropRect.left + dragX).coerceIn(0f, (1f - width).coerceAtLeast(0f))
        val top = (cropRect.top + dragY).coerceIn(0f, (1f - height).coerceAtLeast(0f))
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

    // Size from the dominant drag axis, then fit aspect; clamp to square from the anchor.
    val deltaX = abs(rawX - anchorX)
    val deltaY = abs(rawY - anchorY)
    var width: Float
    var height: Float
    if (deltaX / aspect >= deltaY) {
        width = deltaX
        height = width / aspect
    } else {
        height = deltaY
        width = height * aspect
    }
    val maxWidth = if (rawX >= anchorX) 1f - anchorX else anchorX
    val maxHeight = if (rawY >= anchorY) 1f - anchorY else anchorY
    width = min(width, maxWidth)
    height = width / aspect
    if (height > maxHeight) {
        height = maxHeight
        width = height * aspect
    }
    width = max(width, 0.06f)
    height = width / aspect
    if (height < 0.06f) {
        height = 0.06f
        width = height * aspect
    }

    val left = (if (rawX >= anchorX) anchorX else anchorX - width).coerceIn(0f, 1f - width)
    val top = (if (rawY >= anchorY) anchorY else anchorY - height).coerceIn(0f, 1f - height)
    return NormalizedCropRect(left, top, left + width, top + height)
}
