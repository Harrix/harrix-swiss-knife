package dev.harrix.hsk.ui.gallery

import android.graphics.Bitmap
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
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
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Undo
import androidx.compose.material.icons.filled.BlurOn
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Crop
import androidx.compose.material.icons.filled.CropFree
import androidx.compose.material.icons.filled.CropRotate
import androidx.compose.material.icons.filled.Done
import androidx.compose.material.icons.filled.FilterCenterFocus
import androidx.compose.material.icons.filled.FitScreen
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.OpenWith
import androidx.compose.material.icons.filled.RestartAlt
import androidx.compose.material.icons.filled.Rotate90DegreesCcw
import androidx.compose.material.icons.filled.Rotate90DegreesCw
import androidx.compose.material.icons.filled.Save
import androidx.compose.material.icons.filled.SaveAs
import androidx.compose.material.icons.filled.ScreenLockRotation
import androidx.compose.material.icons.filled.Transform
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.FilledIconButton
import androidx.compose.material3.FilledTonalIconButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LocalMinimumInteractiveComponentSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedIconButton
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
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
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.input.pointer.positionChanged
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import coil.request.ImageRequest
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.CameraPhoto
import dev.harrix.hsk.gallery.EditableImageCache
import dev.harrix.hsk.gallery.NormalizedBlurStroke
import dev.harrix.hsk.gallery.NormalizedCropRect
import dev.harrix.hsk.gallery.NormalizedPerspectiveQuad
import dev.harrix.hsk.gallery.NormalizedPoint
import dev.harrix.hsk.gallery.PerspectiveQuadDetector
import dev.harrix.hsk.gallery.PhotoBlurRenderer
import dev.harrix.hsk.gallery.PhotoEditSaver
import dev.harrix.hsk.ui.AutoFitText
import dev.harrix.hsk.ui.HskDropdownMenuItem
import dev.harrix.hsk.ui.OverflowTextTooltipBox
import dev.harrix.hsk.ui.adaptiveBottomBarWidth
import dev.harrix.hsk.ui.isCompactHeight
import dev.harrix.hsk.ui.isCompactWidth
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlin.math.abs
import kotlin.math.hypot
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt
import coil.size.Size as CoilSize

private const val CropViewMinZoom = 0.5f
private const val CropViewMaxZoom = 5f
private const val CropViewZoomEpsilon = 0.02f

private val EditToolbarButtonSize = 48.dp
private val EditToolbarButtonMinSize = 32.dp
private val EditToolbarSpacing = 4.dp
private val EditToolbarMinSpacing = 0.dp

/** Shrinks every toolbar button (and gaps) uniformly when the row is too narrow. */
private fun editToolbarFitMetrics(
    availableWidth: Dp,
    buttonCount: Int,
): Pair<Dp, Dp> {
    if (buttonCount <= 0) {
        return EditToolbarButtonSize to EditToolbarSpacing
    }
    val preferredTotal =
        EditToolbarButtonSize * buttonCount + EditToolbarSpacing * (buttonCount - 1)
    if (availableWidth >= preferredTotal) {
        return EditToolbarButtonSize to EditToolbarSpacing
    }
    val scale =
        (availableWidth / preferredTotal).coerceAtLeast(
            EditToolbarButtonMinSize / EditToolbarButtonSize,
        )
    val buttonSize =
        (EditToolbarButtonSize * scale).coerceAtLeast(EditToolbarButtonMinSize)
    val remaining = availableWidth - buttonSize * buttonCount
    val spacing =
        if (buttonCount > 1) {
            (remaining / (buttonCount - 1)).coerceAtLeast(EditToolbarMinSpacing)
        } else {
            EditToolbarMinSpacing
        }
    return buttonSize to spacing
}

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

/** One-finger gesture: pan the zoomed view, or edit the crop/perspective frame. */
private sealed class OneFingerAction {
    data object PanView : OneFingerAction()

    data class Crop(
        val mode: CropDragMode,
    ) : OneFingerAction()

    data class Perspective(
        val mode: PerspectiveDragMode,
    ) : OneFingerAction()

    data object Blur : OneFingerAction()
}

/** Accent color for the perspective frame (distinct from the white AABB crop). */
private val PerspectiveFrameColor = Color(0xFFFFB74D)
private val BlurBrushColor = Color(0xFF64B5F6)

/** Locked crop aspect relative to the square workspace, or free resize. */
private const val AspectThreeFour = 3f / 4f
private const val AspectMatchEpsilon = 0.02f

private fun nearAspect(
    aspect: Float,
    target: Float,
): Boolean = abs(aspect - target) < AspectMatchEpsilon

private fun isThreeFourFamily(aspect: Float): Boolean = nearAspect(aspect, AspectThreeFour) ||
    nearAspect(aspect, 1f / AspectThreeFour)

/**
 * 3:4 for a portrait photo, 4:3 for landscape, using the current editor rotation
 * so the crop keeps the orientation of the photo being edited.
 */
private fun threeFourAspectMatchingOrientation(
    imageWidth: Int,
    imageHeight: Int,
    rotationDegrees: Float,
): Float {
    if (imageWidth <= 0 || imageHeight <= 0) {
        return AspectThreeFour
    }
    val normalized = ((rotationDegrees % 180f) + 180f) % 180f
    val axesSwapped = normalized > 45f && normalized < 135f
    val visualWidth = if (axesSwapped) imageHeight else imageWidth
    val visualHeight = if (axesSwapped) imageWidth else imageHeight
    return if (visualWidth >= visualHeight) {
        1f / AspectThreeFour
    } else {
        AspectThreeFour
    }
}

@Composable
fun PhotoCropEditor(
    photo: CameraPhoto,
    rotationDegrees: Float,
    onRotationDegreesChange: (Float) -> Unit,
    cropRect: NormalizedCropRect,
    onCropRectChange: (NormalizedCropRect) -> Unit,
    perspectiveQuad: NormalizedPerspectiveQuad?,
    onPerspectiveQuadChange: (NormalizedPerspectiveQuad?) -> Unit,
    blurStrokes: List<NormalizedBlurStroke>,
    onBlurStrokesChange: (List<NormalizedBlurStroke>) -> Unit,
    blurStrength: Float,
    onBlurStrengthChange: (Float) -> Unit,
    imageRevision: Int,
    isSaving: Boolean,
    onSave: () -> Unit,
    onDiscard: () -> Unit,
    modifier: Modifier = Modifier,
    onSaveCopy: (() -> Unit)? = null,
) {
    val context = LocalContext.current
    val density = LocalDensity.current
    val scope = rememberCoroutineScope()
    val photoEditSaver = remember { PhotoEditSaver(context.applicationContext) }
    var imageWidth by remember(photo.id, imageRevision) { mutableIntStateOf(0) }
    var imageHeight by remember(photo.id, imageRevision) { mutableIntStateOf(0) }
    var blurPreviewBase by remember(photo.id, imageRevision) {
        mutableStateOf<Bitmap?>(null)
    }
    var blurPreviewBitmap by remember(photo.id, imageRevision) {
        mutableStateOf<Bitmap?>(null)
    }
    // Large hit targets: corners sit near the phone bezel and are hard to grab otherwise.
    val handleHitSlopPx = with(density) { 52.dp.toPx() }
    val handleVisualPx = with(density) { 24.dp.toPx() }
    val cropRectState = rememberUpdatedState(cropRect)
    val onCropRectChangeState = rememberUpdatedState(onCropRectChange)
    val perspectiveQuadState = rememberUpdatedState(perspectiveQuad)
    val onPerspectiveQuadChangeState = rememberUpdatedState(onPerspectiveQuadChange)
    val blurStrokesState = rememberUpdatedState(blurStrokes)
    val onBlurStrokesChangeState = rememberUpdatedState(onBlurStrokesChange)
    val rotationState = rememberUpdatedState(rotationDegrees)
    val onRotationDegreesChangeState = rememberUpdatedState(onRotationDegreesChange)
    var isRotatingHint by remember { mutableStateOf(false) }
    var didInitCrop by remember(photo.id, imageRevision) { mutableStateOf(false) }
    val isPerspective = perspectiveQuad != null
    var isBlurMode by remember(photo.id, imageRevision) { mutableStateOf(false) }
    var blurBrushRadius by remember(photo.id, imageRevision) { mutableFloatStateOf(0.07f) }

    /** `null` = free aspect; otherwise width/height lock for the crop frame. */
    var lockedAspect by remember(photo.id, imageRevision) { mutableStateOf<Float?>(null) }
    val lockedAspectState = rememberUpdatedState(lockedAspect)
    var rotationLocked by remember(photo.id, imageRevision) { mutableStateOf(false) }
    var containCropInImage by remember(photo.id, imageRevision) { mutableStateOf(false) }
    var cropMoveLocked by remember(photo.id, imageRevision) { mutableStateOf(false) }
    val rotationLockedState = rememberUpdatedState(rotationLocked)
    val containCropInImageState = rememberUpdatedState(containCropInImage)
    val cropMoveLockedState = rememberUpdatedState(cropMoveLocked)
    var showFileDetails by remember { mutableStateOf(false) }
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
    val showTrimBars = trimSuggestion != null && !isPerspective && !isBlurMode
    val isViewTransformed =
        abs(viewScale - 1f) > CropViewZoomEpsilon ||
            hypot(viewOffset.x.toDouble(), viewOffset.y.toDouble()) > 1.0

    fun trimEmptyZones() {
        val suggestion = trimSuggestion ?: return
        if (isSaving || isPerspective || isBlurMode) {
            return
        }
        lockedAspect = null
        onCropRectChange(suggestion)
        trimSuggestion = null
    }

    fun exitPerspectiveMode() {
        val currentQuad = perspectiveQuad ?: return
        showFileDetails = false
        onCropRectChange(currentQuad.boundingRect())
        onPerspectiveQuadChange(null)
    }

    fun togglePerspectiveMode() {
        if (isSaving || imageWidth <= 0) {
            return
        }
        if (isBlurMode) {
            isBlurMode = false
            onBlurStrokesChange(emptyList())
        }
        val currentQuad = perspectiveQuad
        if (currentQuad == null) {
            showFileDetails = false
            lockedAspect = null
            containCropInImage = false
            trimSuggestion = null
            val fallback =
                PhotoEditSaver.clampPerspectiveQuad(
                    NormalizedPerspectiveQuad.fromRect(cropRect),
                )
            onPerspectiveQuadChange(fallback)
            val detectUri = photo.uri
            val detectWidth = imageWidth
            val detectHeight = imageHeight
            val detectRotation = rotationDegrees
            scope.launch {
                val detected =
                    withContext(Dispatchers.Default) {
                        PerspectiveQuadDetector.detect(
                            context = context.applicationContext,
                            uri = detectUri,
                            imageWidth = detectWidth,
                            imageHeight = detectHeight,
                            rotationDegrees = detectRotation,
                        )
                    }
                if (detected != null && perspectiveQuadState.value != null) {
                    onPerspectiveQuadChangeState.value(detected)
                }
            }
        } else {
            exitPerspectiveMode()
        }
    }

    fun exitBlurMode() {
        isBlurMode = false
        onBlurStrokesChange(emptyList())
    }

    fun toggleBlurMode() {
        if (isSaving || imageWidth <= 0) {
            return
        }
        if (isBlurMode) {
            exitBlurMode()
            return
        }
        if (perspectiveQuad != null) {
            exitPerspectiveMode()
        }
        showFileDetails = false
        trimSuggestion = null
        onBlurStrokesChange(emptyList())
        isBlurMode = true
    }

    BackHandler(enabled = showFileDetails) {
        showFileDetails = false
    }

    BackHandler(enabled = isPerspective && !isSaving && !showFileDetails) {
        exitPerspectiveMode()
    }

    BackHandler(enabled = isBlurMode && !isSaving && !showFileDetails) {
        exitBlurMode()
    }

    LaunchedEffect(isPerspective, isBlurMode) {
        if (isPerspective || isBlurMode) {
            showFileDetails = false
        }
    }

    LaunchedEffect(isBlurMode, photo.uri, rotationDegrees) {
        if (!isBlurMode) {
            blurPreviewBase = null
            blurPreviewBitmap = null
            return@LaunchedEffect
        }
        blurPreviewBase =
            withContext(Dispatchers.Default) {
                PhotoBlurRenderer.createPreviewBase(
                    context = context.applicationContext,
                    uri = photo.uri,
                    rotationDegrees = rotationDegrees,
                )
            }
    }

    LaunchedEffect(isBlurMode, blurPreviewBase, blurStrokes, blurStrength) {
        if (!isBlurMode) {
            blurPreviewBitmap = null
            return@LaunchedEffect
        }
        val base = blurPreviewBase ?: return@LaunchedEffect
        if (blurStrokes.isEmpty()) {
            blurPreviewBitmap = base
            return@LaunchedEffect
        }
        // Debounce continuous brush and slider events; stale renders are cancelled.
        delay(70)
        blurPreviewBitmap =
            withContext(Dispatchers.Default) {
                val rendered =
                    try {
                        base.copy(Bitmap.Config.ARGB_8888, true)
                    } catch (_: OutOfMemoryError) {
                        null
                    } ?: return@withContext null
                if (PhotoBlurRenderer.apply(rendered, blurStrokes, blurStrength)) {
                    rendered
                } else {
                    null
                }
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
        val skipTrimAnalysis = !didInitCrop || isSaving || perspectiveQuad != null || isBlurMode
        if (skipTrimAnalysis) {
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

    fun photoCropBounds(): NormalizedCropRect = photoEditSaver.photoInscribedBounds(
        imageWidth = imageWidth,
        imageHeight = imageHeight,
        rotationDegrees = rotationDegrees,
    )

    fun clampCropIfContained(rect: NormalizedCropRect): NormalizedCropRect {
        if (!containCropInImage || imageWidth <= 0 || imageHeight <= 0) {
            return rect
        }
        return PhotoEditSaver.clampCropRectInsideBounds(
            rect = rect,
            bounds = photoCropBounds(),
            imageAspect = lockedAspect,
        )
    }

    fun toggleContainCropInImage() {
        if (isPerspective || isBlurMode || isSaving) {
            return
        }
        val enabling = !containCropInImage
        containCropInImage = enabling
        if (enabling && imageWidth > 0 && imageHeight > 0) {
            onCropRectChange(clampCropIfContained(cropRect))
        }
    }

    // After discrete rotation (±90 / reset), keep the frame inside the photo when
    // contain-mode is on. Skip while a pinch-rotate gesture is active (isRotatingHint).
    LaunchedEffect(
        containCropInImage,
        rotationDegrees,
        imageWidth,
        imageHeight,
        isPerspective,
        isRotatingHint,
    ) {
        if (!containCropInImage || isPerspective || isRotatingHint) {
            return@LaunchedEffect
        }
        if (imageWidth <= 0 || imageHeight <= 0) {
            return@LaunchedEffect
        }
        val clamped = clampCropIfContained(cropRect)
        if (clamped != cropRect) {
            onCropRectChangeState.value(clamped)
        }
    }

    fun applyLockedAspect(aspect: Float) {
        if (imageWidth <= 0 || imageHeight <= 0) {
            return
        }
        lockedAspect = aspect
        val base = PhotoEditSaver.imageContentCrop(imageWidth, imageHeight)
        onCropRectChange(
            clampCropIfContained(PhotoEditSaver.fitCropToAspect(base, aspect)),
        )
    }

    fun applyOrResetThreeFourAspect() {
        val currentLock = lockedAspect
        val alreadyThreeFour = currentLock != null && isThreeFourFamily(currentLock)
        if (alreadyThreeFour) {
            applyLockedAspect(originalAspect)
            return
        }
        applyLockedAspect(
            threeFourAspectMatchingOrientation(
                imageWidth = imageWidth,
                imageHeight = imageHeight,
                rotationDegrees = rotationDegrees,
            ),
        )
    }

    fun rotateCropAspect90() {
        if (imageWidth <= 0 || imageHeight <= 0) {
            return
        }
        val swapped = PhotoEditSaver.swapCropDimensions(cropRect)
        onCropRectChange(clampCropIfContained(swapped))
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
                val side = workspace.width
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
                            .allowHardware(false)
                            .memoryCacheKey(
                                EditableImageCache.key(
                                    photo.uri,
                                    photo.sizeBytes,
                                    imageRevision,
                                ),
                            )
                            .diskCacheKey(
                                EditableImageCache.key(
                                    photo.uri,
                                    photo.sizeBytes,
                                    imageRevision,
                                ),
                            )
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
                    val activeBlurPreview =
                        blurPreviewBitmap?.takeIf { preview ->
                            isBlurMode && blurStrokes.isNotEmpty() && preview.width > 0
                        }
                    if (activeBlurPreview != null) {
                        Image(
                            bitmap = activeBlurPreview.asImageBitmap(),
                            contentDescription = null,
                            contentScale = ContentScale.FillBounds,
                            modifier = Modifier.fillMaxSize(),
                        )
                    }

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
                        if (isBlurMode) {
                            blurStrokes.forEach { stroke ->
                                val points =
                                    stroke.points.map { point ->
                                        Offset(point.x * side, point.y * side)
                                    }
                                if (points.size == 1) {
                                    drawCircle(
                                        color = BlurBrushColor.copy(alpha = 0.12f),
                                        radius = stroke.radius * side,
                                        center = points.first(),
                                    )
                                } else if (points.isNotEmpty()) {
                                    val brushPath =
                                        Path().apply {
                                            moveTo(points.first().x, points.first().y)
                                            points.drop(1).forEach { point ->
                                                lineTo(point.x, point.y)
                                            }
                                        }
                                    drawPath(
                                        path = brushPath,
                                        color = BlurBrushColor.copy(alpha = 0.12f),
                                        style =
                                        Stroke(
                                            width = stroke.radius * side * 2f,
                                            cap = StrokeCap.Round,
                                            join = StrokeJoin.Round,
                                        ),
                                    )
                                }
                            }
                        } else if (quadCornersPx != null && quadCornersPx.size == 4) {
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
                }

                // Full-viewport overlay so pinch/pan work on letterbox and rotated image edges.
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
                            isBlurMode,
                            blurBrushRadius,
                            viewportW,
                            viewportH,
                        ) {
                            if (isSaving) {
                                return@pointerInput
                            }
                            awaitEachGesture {
                                awaitFirstDown(requireUnconsumed = false)
                                var multiTouch = false
                                var oneFingerAction: OneFingerAction? = null
                                var gestureActive = true
                                var gestureScale = viewScaleState.value
                                var gestureOffset = viewOffsetState.value
                                var blurStrokeBase = emptyList<NormalizedBlurStroke>()
                                val activeBlurPoints = mutableListOf<NormalizedPoint>()
                                isRotatingHint = false

                                fun viewportToWorkspace(point: Offset): Offset = viewportToWorkspacePoint(
                                    point = point,
                                    side = side,
                                    scale = gestureScale,
                                    offset = gestureOffset,
                                    viewportW = viewportW,
                                    viewportH = viewportH,
                                )

                                fun finalizeCrop(rect: NormalizedCropRect): NormalizedCropRect {
                                    val aspectLock = lockedAspectState.value
                                    val workspaceClamped =
                                        if (aspectLock == null) {
                                            PhotoEditSaver.clampCropRectFree(rect)
                                        } else {
                                            PhotoEditSaver.clampCropRect(
                                                rect = rect,
                                                imageAspect = aspectLock,
                                            )
                                        }
                                    if (!containCropInImageState.value ||
                                        imageWidth <= 0 ||
                                        imageHeight <= 0
                                    ) {
                                        return workspaceClamped
                                    }
                                    return PhotoEditSaver.clampCropRectInsideBounds(
                                        rect = workspaceClamped,
                                        bounds =
                                        photoEditSaver.photoInscribedBounds(
                                            imageWidth = imageWidth,
                                            imageHeight = imageHeight,
                                            rotationDegrees = rotationState.value,
                                        ),
                                        imageAspect = aspectLock,
                                    )
                                }

                                while (gestureActive) {
                                    val event = awaitPointerEvent()
                                    val pressed = event.changes.filter { it.pressed }
                                    if (pressed.isEmpty()) {
                                        gestureActive = false
                                    } else if (pressed.size >= 2) {
                                        multiTouch = true
                                        oneFingerAction = null
                                        val rotationDelta = event.calculateRotation()
                                        val zoomChange = event.calculateZoom()
                                        val panChange = event.calculatePan()
                                        // Keep current rotation while adjusting a perspective quad.
                                        val rotationAllowed =
                                            perspectiveQuadState.value == null &&
                                                !isBlurMode &&
                                                !rotationLockedState.value
                                        if (rotationDelta != 0f && rotationAllowed) {
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
                                        val activeAction = oneFingerAction
                                        if (activeAction == null) {
                                            val local = viewportToWorkspace(change.position)
                                            val hitSlop =
                                                handleHitSlopPx /
                                                    gestureScale.coerceAtLeast(1e-6f)
                                            val currentPerspective = perspectiveQuadState.value
                                            oneFingerAction =
                                                if (isBlurMode) {
                                                    val point =
                                                        NormalizedPoint(
                                                            x = (local.x / side).coerceIn(0f, 1f),
                                                            y = (local.y / side).coerceIn(0f, 1f),
                                                        )
                                                    blurStrokeBase = blurStrokesState.value
                                                    activeBlurPoints += point
                                                    onBlurStrokesChangeState.value(
                                                        blurStrokeBase +
                                                            NormalizedBlurStroke(
                                                                points = activeBlurPoints.toList(),
                                                                radius = blurBrushRadius,
                                                            ),
                                                    )
                                                    OneFingerAction.Blur
                                                } else if (currentPerspective != null) {
                                                    val cornersPx =
                                                        currentPerspective.corners().map { corner ->
                                                            Offset(corner.x * side, corner.y * side)
                                                        }
                                                    val cornersVisible =
                                                        anyWorkspacePointsVisible(
                                                            points = cornersPx,
                                                            side = side,
                                                            scale = gestureScale,
                                                            offset = gestureOffset,
                                                            viewportW = viewportW,
                                                            viewportH = viewportH,
                                                        )
                                                    resolvePerspectiveOneFingerAction(
                                                        localPoint = local,
                                                        cornersPx = cornersPx,
                                                        slop = hitSlop,
                                                        cornersVisible = cornersVisible,
                                                    )
                                                } else {
                                                    val currentCrop = cropRectState.value
                                                    val currentCropPx =
                                                        Rect(
                                                            left = currentCrop.left * side,
                                                            top = currentCrop.top * side,
                                                            right = currentCrop.right * side,
                                                            bottom = currentCrop.bottom * side,
                                                        )
                                                    val cornersVisible =
                                                        anyWorkspacePointsVisible(
                                                            points =
                                                            listOf(
                                                                Offset(
                                                                    currentCropPx.left,
                                                                    currentCropPx.top,
                                                                ),
                                                                Offset(
                                                                    currentCropPx.right,
                                                                    currentCropPx.top,
                                                                ),
                                                                Offset(
                                                                    currentCropPx.left,
                                                                    currentCropPx.bottom,
                                                                ),
                                                                Offset(
                                                                    currentCropPx.right,
                                                                    currentCropPx.bottom,
                                                                ),
                                                            ),
                                                            side = side,
                                                            scale = gestureScale,
                                                            offset = gestureOffset,
                                                            viewportW = viewportW,
                                                            viewportH = viewportH,
                                                        )
                                                    resolveCropOneFingerAction(
                                                        localPoint = local,
                                                        cropPx = currentCropPx,
                                                        slop = hitSlop,
                                                        cornersVisible = cornersVisible,
                                                        allowMove = !cropMoveLockedState.value,
                                                    )
                                                }
                                        } else {
                                            val drag = change.position - change.previousPosition
                                            if (drag != Offset.Zero) {
                                                when (activeAction) {
                                                    OneFingerAction.PanView -> {
                                                        gestureOffset =
                                                            clampCropViewOffset(
                                                                offset = gestureOffset + drag,
                                                                scale = gestureScale,
                                                                side = side,
                                                                viewportW = viewportW,
                                                                viewportH = viewportH,
                                                            )
                                                        viewOffset = gestureOffset
                                                        change.consume()
                                                    }

                                                    is OneFingerAction.Crop -> {
                                                        if (imageHeight > 0 && side > 0f) {
                                                            val dragLocal = drag / gestureScale
                                                            val aspectLock =
                                                                lockedAspectState.value
                                                            val next =
                                                                if (aspectLock == null) {
                                                                    applyFreeCropDrag(
                                                                        cropRect =
                                                                        cropRectState.value,
                                                                        mode = activeAction.mode,
                                                                        dragX = dragLocal.x / side,
                                                                        dragY = dragLocal.y / side,
                                                                    )
                                                                } else {
                                                                    applyAspectCropDrag(
                                                                        cropRect =
                                                                        cropRectState.value,
                                                                        mode = activeAction.mode,
                                                                        dragX = dragLocal.x / side,
                                                                        dragY = dragLocal.y / side,
                                                                        imageAspect = aspectLock,
                                                                    )
                                                                }
                                                            onCropRectChangeState.value(
                                                                finalizeCrop(next),
                                                            )
                                                            change.consume()
                                                        }
                                                    }

                                                    is OneFingerAction.Perspective -> {
                                                        if (side > 0f) {
                                                            val currentPerspective =
                                                                perspectiveQuadState.value
                                                            if (currentPerspective != null) {
                                                                val dragLocal = drag / gestureScale
                                                                val next =
                                                                    when (activeAction.mode) {
                                                                        PerspectiveDragMode.Move ->
                                                                            PhotoEditSaver
                                                                                .movePerspectiveQuad(
                                                                                    currentPerspective,
                                                                                    dragLocal.x / side,
                                                                                    dragLocal.y / side,
                                                                                )

                                                                        PerspectiveDragMode.Corner0 ->
                                                                            PhotoEditSaver
                                                                                .dragPerspectiveCorner(
                                                                                    currentPerspective,
                                                                                    0,
                                                                                    dragLocal.x / side,
                                                                                    dragLocal.y / side,
                                                                                )

                                                                        PerspectiveDragMode.Corner1 ->
                                                                            PhotoEditSaver
                                                                                .dragPerspectiveCorner(
                                                                                    currentPerspective,
                                                                                    1,
                                                                                    dragLocal.x / side,
                                                                                    dragLocal.y / side,
                                                                                )

                                                                        PerspectiveDragMode.Corner2 ->
                                                                            PhotoEditSaver
                                                                                .dragPerspectiveCorner(
                                                                                    currentPerspective,
                                                                                    2,
                                                                                    dragLocal.x / side,
                                                                                    dragLocal.y / side,
                                                                                )

                                                                        PerspectiveDragMode.Corner3 ->
                                                                            PhotoEditSaver
                                                                                .dragPerspectiveCorner(
                                                                                    currentPerspective,
                                                                                    3,
                                                                                    dragLocal.x / side,
                                                                                    dragLocal.y / side,
                                                                                )
                                                                    }
                                                                onPerspectiveQuadChangeState.value(next)
                                                                change.consume()
                                                            }
                                                        }
                                                    }

                                                    OneFingerAction.Blur -> {
                                                        val local =
                                                            viewportToWorkspace(change.position)
                                                        val point =
                                                            NormalizedPoint(
                                                                x =
                                                                (local.x / side)
                                                                    .coerceIn(0f, 1f),
                                                                y =
                                                                (local.y / side)
                                                                    .coerceIn(0f, 1f),
                                                            )
                                                        val previous =
                                                            activeBlurPoints.lastOrNull()
                                                        val farEnough =
                                                            previous == null ||
                                                                hypot(
                                                                    (point.x - previous.x)
                                                                        .toDouble(),
                                                                    (point.y - previous.y)
                                                                        .toDouble(),
                                                                ) >= 0.002
                                                        if (farEnough) {
                                                            activeBlurPoints += point
                                                            onBlurStrokesChangeState.value(
                                                                blurStrokeBase +
                                                                    NormalizedBlurStroke(
                                                                        points =
                                                                        activeBlurPoints.toList(),
                                                                        radius = blurBrushRadius,
                                                                    ),
                                                            )
                                                        }
                                                        change.consume()
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                                val shouldReclampAfterPinch =
                                    multiTouch &&
                                        containCropInImageState.value &&
                                        perspectiveQuadState.value == null
                                if (shouldReclampAfterPinch && imageWidth > 0 && imageHeight > 0) {
                                    onCropRectChangeState.value(
                                        finalizeCrop(cropRectState.value),
                                    )
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
                        .memoryCacheKey(
                            EditableImageCache.key(
                                photo.uri,
                                photo.sizeBytes,
                                imageRevision,
                            ),
                        )
                        .diskCacheKey(
                            EditableImageCache.key(
                                photo.uri,
                                photo.sizeBytes,
                                imageRevision,
                            ),
                        )
                        .allowHardware(false)
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

            val workspaceReady = workspace.width > 0f && imageWidth > 0
            val showCropModeToggles =
                !isSaving && workspaceReady && !isPerspective && !isBlurMode
            if (showCropModeToggles) {
                Row(
                    modifier =
                    Modifier
                        .align(Alignment.TopStart)
                        .padding(12.dp),
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    EditToolbarIconButton(
                        onClick = { rotationLocked = !rotationLocked },
                        icon = Icons.Filled.ScreenLockRotation,
                        label =
                        stringResource(
                            if (rotationLocked) {
                                R.string.gallery_cleaner_edit_unlock_rotation
                            } else {
                                R.string.gallery_cleaner_edit_lock_rotation
                            },
                        ),
                        selected = rotationLocked,
                        tonal = true,
                    )
                    EditToolbarIconButton(
                        onClick = { toggleContainCropInImage() },
                        icon = Icons.Filled.FilterCenterFocus,
                        label =
                        stringResource(
                            if (containCropInImage) {
                                R.string.gallery_cleaner_edit_allow_crop_outside
                            } else {
                                R.string.gallery_cleaner_edit_contain_crop
                            },
                        ),
                        selected = containCropInImage,
                        tonal = true,
                    )
                    EditToolbarIconButton(
                        onClick = { cropMoveLocked = !cropMoveLocked },
                        icon = Icons.Filled.OpenWith,
                        label =
                        stringResource(
                            if (cropMoveLocked) {
                                R.string.gallery_cleaner_edit_unlock_crop_move
                            } else {
                                R.string.gallery_cleaner_edit_lock_crop_move
                            },
                        ),
                        selected = cropMoveLocked,
                        tonal = true,
                    )
                }
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
                    if (isViewTransformed && !isPerspective && !isBlurMode) {
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
                                    clampCropIfContained(
                                        PhotoEditSaver.fitCropIntoBounds(
                                            rect = cropRect,
                                            bounds = visible,
                                        ),
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
        val threeFourTargetAspect =
            threeFourAspectMatchingOrientation(
                imageWidth = imageWidth,
                imageHeight = imageHeight,
                rotationDegrees = rotationDegrees,
            )
        val aspectThreeFourLabel =
            if (threeFourTargetAspect > 1f) {
                "4:3"
            } else {
                stringResource(R.string.gallery_cleaner_edit_aspect_3_4)
            }
        val aspectFreeLabel = stringResource(R.string.gallery_cleaner_edit_aspect_free)
        val perspectiveLabel = stringResource(R.string.gallery_cleaner_edit_perspective)
        val blurLabel = stringResource(R.string.gallery_cleaner_edit_blur)
        val blurBrushSizeLabel = stringResource(R.string.gallery_cleaner_edit_blur_brush_size)
        val blurLevelLabel = stringResource(R.string.gallery_cleaner_edit_blur_level)
        val undoBlurStrokeLabel =
            stringResource(R.string.gallery_cleaner_edit_blur_undo_stroke)
        val rotateCcwLabel = stringResource(R.string.gallery_cleaner_edit_rotate_ccw)
        val resetRotationLabel = stringResource(R.string.gallery_cleaner_edit_reset_rotation)
        val rotateCwLabel = stringResource(R.string.gallery_cleaner_edit_rotate_cw)
        val trimEmptyLabel = stringResource(R.string.gallery_cleaner_edit_trim_empty)
        val fitFrameLabel = stringResource(R.string.gallery_cleaner_edit_fit_frame)
        val discardLabel = stringResource(R.string.gallery_cleaner_edit_discard)
        val saveCopyLabel = stringResource(R.string.photo_editor_save_copy)
        val saveLabel = stringResource(R.string.gallery_cleaner_edit_save)
        val applyPerspectiveLabel =
            stringResource(R.string.gallery_cleaner_edit_perspective_apply)
        val applyBlurLabel = stringResource(R.string.gallery_cleaner_edit_blur_apply)
        val moreLabel = stringResource(R.string.gallery_cleaner_edit_more)
        val fileDetailsLabel = stringResource(R.string.photo_file_details_title)
        val locked = lockedAspect
        val threeFourSelected = locked != null && isThreeFourFamily(locked)
        val freeAspectSelected = lockedAspect == null && !isPerspective && !isBlurMode
        val canEditAspect = !isSaving && imageWidth > 0 && !isPerspective && !isBlurMode
        val canTogglePerspective = !isSaving && imageWidth > 0 && !isBlurMode
        val canToggleBlur = !isSaving && imageWidth > 0 && !isPerspective
        val canRotate = !isSaving && !isPerspective && !isBlurMode && !rotationLocked
        val canResetRotation = canRotate && abs(displayDegrees) >= 0.5f
        val canFitFrame =
            isViewTransformed && !isPerspective && !isBlurMode && imageWidth > 0
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
                clampCropIfContained(
                    PhotoEditSaver.fitCropIntoBounds(
                        rect = cropRect,
                        bounds = visible,
                    ),
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
                if (isBlurMode) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = blurBrushSizeLabel,
                                style = MaterialTheme.typography.labelMedium,
                            )
                            Slider(
                                value = blurBrushRadius,
                                onValueChange = { blurBrushRadius = it },
                                valueRange =
                                PhotoEditSaver.MIN_BLUR_BRUSH_RADIUS..PhotoEditSaver.MAX_BLUR_BRUSH_RADIUS,
                                enabled = !isSaving,
                            )
                        }
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = blurLevelLabel,
                                style = MaterialTheme.typography.labelMedium,
                            )
                            Slider(
                                value = blurStrength,
                                onValueChange = onBlurStrengthChange,
                                valueRange = 0f..1f,
                                enabled = !isSaving,
                            )
                        }
                    }
                }
                val toolButtonCount =
                    when {
                        isPerspective -> 2
                        isBlurMode -> 3
                        showThreeFourChip -> 9
                        else -> 8
                    }
                BoxWithConstraints(modifier = Modifier.fillMaxWidth()) {
                    val (toolButtonSize, toolSpacing) =
                        remember(maxWidth, toolButtonCount) {
                            editToolbarFitMetrics(maxWidth, toolButtonCount)
                        }
                    val toolsArrangement =
                        if (toolButtonSize >= EditToolbarButtonSize) {
                            Arrangement.SpaceEvenly
                        } else {
                            Arrangement.spacedBy(
                                toolSpacing,
                                Alignment.CenterHorizontally,
                            )
                        }
                    CompositionLocalProvider(
                        LocalMinimumInteractiveComponentSize provides toolButtonSize,
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = toolsArrangement,
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            if (!isPerspective && !isBlurMode) {
                                EditToolbarIconButton(
                                    onClick = { rotateCropAspect90() },
                                    icon = Icons.Filled.CropRotate,
                                    label = aspectRotateLabel,
                                    enabled = canEditAspect,
                                    buttonSize = toolButtonSize,
                                )
                                if (showThreeFourChip) {
                                    EditToolbarIconButton(
                                        onClick = { applyOrResetThreeFourAspect() },
                                        icon = Icons.Filled.Crop,
                                        label = aspectThreeFourLabel,
                                        enabled = canEditAspect,
                                        selected = threeFourSelected,
                                        buttonSize = toolButtonSize,
                                    )
                                }
                                EditToolbarIconButton(
                                    onClick = { toggleFreeAspect() },
                                    icon = Icons.Filled.CropFree,
                                    label = aspectFreeLabel,
                                    enabled = canEditAspect,
                                    selected = freeAspectSelected,
                                    buttonSize = toolButtonSize,
                                )
                            }
                            if (!isBlurMode) {
                                EditToolbarIconButton(
                                    onClick = { togglePerspectiveMode() },
                                    icon = Icons.Filled.Transform,
                                    label = perspectiveLabel,
                                    enabled = canTogglePerspective,
                                    selected = isPerspective,
                                    buttonSize = toolButtonSize,
                                )
                            }
                            if (!isPerspective) {
                                EditToolbarIconButton(
                                    onClick = { toggleBlurMode() },
                                    icon = Icons.Filled.BlurOn,
                                    label = blurLabel,
                                    enabled = canToggleBlur,
                                    selected = isBlurMode,
                                    buttonSize = toolButtonSize,
                                )
                            }
                            if (isBlurMode) {
                                EditToolbarIconButton(
                                    onClick = {
                                        if (blurStrokes.isNotEmpty()) {
                                            onBlurStrokesChange(blurStrokes.dropLast(1))
                                        }
                                    },
                                    icon = Icons.AutoMirrored.Filled.Undo,
                                    label = undoBlurStrokeLabel,
                                    enabled = !isSaving && blurStrokes.isNotEmpty(),
                                    buttonSize = toolButtonSize,
                                )
                            }
                            if (!isPerspective && !isBlurMode) {
                                EditToolbarIconButton(
                                    onClick = { onRotationDegreesChange(rotationDegrees - 90f) },
                                    icon = Icons.Filled.Rotate90DegreesCcw,
                                    label = rotateCcwLabel,
                                    enabled = canRotate,
                                    buttonSize = toolButtonSize,
                                )
                                EditToolbarIconButton(
                                    onClick = { onRotationDegreesChange(0f) },
                                    icon = Icons.Filled.RestartAlt,
                                    label = resetRotationLabel,
                                    enabled = canResetRotation,
                                    buttonSize = toolButtonSize,
                                )
                                EditToolbarIconButton(
                                    onClick = { onRotationDegreesChange(rotationDegrees + 90f) },
                                    icon = Icons.Filled.Rotate90DegreesCw,
                                    label = rotateCwLabel,
                                    enabled = canRotate,
                                    buttonSize = toolButtonSize,
                                )
                            }
                            Box {
                                EditToolbarIconButton(
                                    onClick = { moreMenuExpanded = true },
                                    icon = Icons.Filled.MoreVert,
                                    label = moreLabel,
                                    enabled = !isSaving,
                                    buttonSize = toolButtonSize,
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
                                                applyOrResetThreeFourAspect()
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
                                    EditOverflowMenuItem(
                                        icon = Icons.Filled.BlurOn,
                                        label = blurLabel,
                                        enabled = canToggleBlur,
                                        onClick = {
                                            moreMenuExpanded = false
                                            toggleBlurMode()
                                        },
                                    )
                                    if (isBlurMode) {
                                        EditOverflowMenuItem(
                                            icon = Icons.AutoMirrored.Filled.Undo,
                                            label = undoBlurStrokeLabel,
                                            enabled = blurStrokes.isNotEmpty() && !isSaving,
                                            onClick = {
                                                moreMenuExpanded = false
                                                if (blurStrokes.isNotEmpty()) {
                                                    onBlurStrokesChange(
                                                        blurStrokes.dropLast(1),
                                                    )
                                                }
                                            },
                                        )
                                    }
                                    HorizontalDivider()
                                    EditOverflowMenuItem(
                                        icon = Icons.Filled.Rotate90DegreesCcw,
                                        label = rotateCcwLabel,
                                        enabled = canRotate,
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
                                        enabled = canRotate,
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
                                    if (onSaveCopy != null && !isPerspective && !isBlurMode) {
                                        EditOverflowMenuItem(
                                            icon = Icons.Filled.SaveAs,
                                            label = saveCopyLabel,
                                            enabled = !isSaving,
                                            onClick = {
                                                moreMenuExpanded = false
                                                onSaveCopy()
                                            },
                                        )
                                    }
                                    EditOverflowMenuItem(
                                        icon = Icons.Filled.Info,
                                        label = fileDetailsLabel,
                                        enabled = !isPerspective && !isBlurMode,
                                        onClick = {
                                            moreMenuExpanded = false
                                            showFileDetails = true
                                        },
                                    )
                                    EditOverflowMenuItem(
                                        icon =
                                        if (isPerspective || isBlurMode) {
                                            Icons.Filled.Done
                                        } else {
                                            Icons.Filled.Save
                                        },
                                        label =
                                        when {
                                            isPerspective -> applyPerspectiveLabel
                                            isBlurMode -> applyBlurLabel
                                            else -> saveLabel
                                        },
                                        enabled =
                                        !isSaving && (!isBlurMode || blurStrokes.isNotEmpty()),
                                        onClick = {
                                            moreMenuExpanded = false
                                            onSave()
                                        },
                                    )
                                }
                            }
                        }
                    }
                }
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    EditToolbarIconButton(
                        onClick = onDiscard,
                        icon = Icons.Filled.Close,
                        label = discardLabel,
                        enabled = !isSaving,
                        outlined = true,
                    )
                    Spacer(modifier = Modifier.weight(1f))
                    if (onSaveCopy != null && !isPerspective && !isBlurMode) {
                        EditToolbarIconButton(
                            onClick = onSaveCopy,
                            icon = Icons.Filled.SaveAs,
                            label = saveCopyLabel,
                            enabled = !isSaving,
                            outlined = true,
                        )
                    }
                    if (isPerspective || isBlurMode) {
                        Button(
                            onClick = onSave,
                            enabled =
                            !isSaving && (!isBlurMode || blurStrokes.isNotEmpty()),
                        ) {
                            Icon(
                                imageVector = Icons.Filled.Done,
                                contentDescription = null,
                                modifier = Modifier.size(18.dp),
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            AutoFitText(
                                text =
                                if (isBlurMode) {
                                    applyBlurLabel
                                } else {
                                    applyPerspectiveLabel
                                },
                                maxLines = 2,
                                textAlign = TextAlign.Center,
                            )
                        }
                    } else {
                        EditToolbarIconButton(
                            onClick = onSave,
                            icon = Icons.Filled.Save,
                            label = saveLabel,
                            enabled = !isSaving,
                            filled = true,
                        )
                    }
                }
            }
        }
    }

    if (showFileDetails && !isPerspective && !isBlurMode) {
        PhotoFileDetailsSheet(
            photo = photo,
            onDismissRequest = { showFileDetails = false },
        )
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
    buttonSize: Dp = EditToolbarButtonSize,
) {
    val iconSize = buttonSize * 0.5f
    OverflowTextTooltipBox(text = label, enabled = true) {
        val buttonModifier = Modifier.size(buttonSize)
        val iconContent: @Composable () -> Unit = {
            Icon(
                imageVector = icon,
                contentDescription = label,
                modifier = Modifier.size(iconSize),
            )
        }
        when {
            // Selected toggles use a solid filled button so on/off is obvious on the photo.
            filled || selected ->
                FilledIconButton(
                    onClick = onClick,
                    modifier = buttonModifier,
                    enabled = enabled,
                    content = iconContent,
                )

            tonal ->
                FilledTonalIconButton(
                    onClick = onClick,
                    modifier = buttonModifier,
                    enabled = enabled,
                    content = iconContent,
                )

            outlined ->
                OutlinedIconButton(
                    onClick = onClick,
                    modifier = buttonModifier,
                    enabled = enabled,
                    content = iconContent,
                )

            else ->
                IconButton(
                    onClick = onClick,
                    modifier = buttonModifier,
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
    HskDropdownMenuItem(
        text = {
            AutoFitText(
                text = label,
                maxLines = 1,
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
 * Map a viewport touch into the unscaled workspace square (same space as crop math).
 */
private fun viewportToWorkspacePoint(
    point: Offset,
    side: Float,
    scale: Float,
    offset: Offset,
    viewportW: Float,
    viewportH: Float,
): Offset {
    val s = scale.coerceAtLeast(1e-6f)
    return Offset(
        x = side / 2f + (point.x - viewportW / 2f - offset.x) / s,
        y = side / 2f + (point.y - viewportH / 2f - offset.y) / s,
    )
}

private fun workspaceToViewportPoint(
    point: Offset,
    side: Float,
    scale: Float,
    offset: Offset,
    viewportW: Float,
    viewportH: Float,
): Offset {
    val s = scale.coerceAtLeast(1e-6f)
    return Offset(
        x = viewportW / 2f + (point.x - side / 2f) * s + offset.x,
        y = viewportH / 2f + (point.y - side / 2f) * s + offset.y,
    )
}

private fun isViewportPointVisible(
    point: Offset,
    viewportW: Float,
    viewportH: Float,
    margin: Float = 0f,
): Boolean = point.x in -margin..(viewportW + margin) &&
    point.y in -margin..(viewportH + margin)

private fun anyWorkspacePointsVisible(
    points: List<Offset>,
    side: Float,
    scale: Float,
    offset: Offset,
    viewportW: Float,
    viewportH: Float,
): Boolean = points.any { point ->
    isViewportPointVisible(
        point =
        workspaceToViewportPoint(
            point = point,
            side = side,
            scale = scale,
            offset = offset,
            viewportW = viewportW,
            viewportH = viewportH,
        ),
        viewportW = viewportW,
        viewportH = viewportH,
    )
}

/**
 * Outside frame → pan view. Inside without visible corners → pan view.
 * Visible corners → resize near a handle, otherwise move the frame.
 */
private fun resolveCropOneFingerAction(
    localPoint: Offset,
    cropPx: Rect,
    slop: Float,
    cornersVisible: Boolean,
    allowMove: Boolean = true,
): OneFingerAction {
    val cornerHit = hitTestCropCornerOnly(localPoint, cropPx, slop)
    if (cornerHit != null) {
        return OneFingerAction.Crop(cornerHit)
    }
    val inside =
        localPoint.x in cropPx.left..cropPx.right &&
            localPoint.y in cropPx.top..cropPx.bottom
    if (!inside || !cornersVisible || !allowMove) {
        return OneFingerAction.PanView
    }
    return OneFingerAction.Crop(CropDragMode.Move)
}

/**
 * Perspective: only corner handles reshape the quad. Swipes inside or outside the frame
 * pan the view (same as zoomed pan) so the frame is not dragged as a whole.
 */
private fun resolvePerspectiveOneFingerAction(
    localPoint: Offset,
    cornersPx: List<Offset>,
    slop: Float,
    cornersVisible: Boolean,
): OneFingerAction {
    if (cornersVisible) {
        val cornerHit = hitTestPerspectiveCornerOnly(localPoint, cornersPx, slop)
        if (cornerHit != null) {
            return OneFingerAction.Perspective(cornerHit)
        }
    }
    return OneFingerAction.PanView
}

private fun hitTestCropCornerOnly(
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
    return bestMode
}

private fun hitTestPerspectiveCornerOnly(
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
    return bestMode
}

/**
 * Prefer perspective corner handles; move when the press is inside the quad.
 */
private fun hitTestPerspectiveHandle(
    point: Offset,
    cornersPx: List<Offset>,
    slop: Float,
): PerspectiveDragMode? {
    hitTestPerspectiveCornerOnly(point, cornersPx, slop)?.let { return it }
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
    hitTestCropCornerOnly(point, cropPx, slop)?.let { return it }
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
