package dev.harrix.hsk.ui.gallery

import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.awaitLongPressOrCancellation
import androidx.compose.foundation.gestures.drag
import androidx.compose.foundation.gestures.scrollBy
import androidx.compose.foundation.lazy.grid.LazyGridItemInfo
import androidx.compose.foundation.lazy.grid.LazyGridState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.round
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive

/**
 * Gallery-style multi-select on a lazy grid:
 * - short tap toggles the cell under the finger
 * - long-press toggles that cell, then drag toggles each newly entered cell
 * - near the top/bottom edges the grid auto-scrolls while selection continues
 *
 * Gestures are handled on the grid itself (not per-item clickable) so long-press
 * works on every cell, not only the first.
 */
@Composable
fun Modifier.lazyGridDragSelect(
    lazyGridState: LazyGridState,
    itemIds: List<Long>,
    selectedIds: Set<Long>,
    onSelectedIdsChange: (Set<Long>) -> Unit,
): Modifier {
    val haptics = LocalHapticFeedback.current
    val autoScrollThresholdPx = with(LocalDensity.current) { 56.dp.toPx() }
    var autoScrollSpeed by remember { mutableFloatStateOf(0f) }
    var lastDragPosition by remember { mutableStateOf<Offset?>(null) }
    var dragCurrentIndex by remember { mutableStateOf<Int?>(null) }

    val itemIdsState = rememberUpdatedState(itemIds)
    val selectedIdsState = rememberUpdatedState(selectedIds)
    val onSelectedIdsChangeState = rememberUpdatedState(onSelectedIdsChange)

    fun toggleIndex(index: Int) {
        val id = itemIdsState.value.getOrNull(index) ?: return
        onSelectedIdsChangeState.value(selectedIdsState.value.toggleId(id))
    }

    fun applySelectionAt(position: Offset) {
        val previousIndex = dragCurrentIndex ?: return
        val ids = itemIdsState.value
        val hitIndex = lazyGridState.itemIndexAtOffset(position, ids) ?: return
        if (hitIndex == previousIndex) {
            return
        }
        onSelectedIdsChangeState.value(
            selectedIdsState.value.toggleDragPath(
                itemIds = ids,
                fromIndex = previousIndex,
                toIndex = hitIndex,
            ),
        )
        dragCurrentIndex = hitIndex
    }

    fun resetDrag() {
        autoScrollSpeed = 0f
        dragCurrentIndex = null
        lastDragPosition = null
    }

    LaunchedEffect(autoScrollSpeed) {
        if (autoScrollSpeed == 0f) {
            return@LaunchedEffect
        }
        while (isActive) {
            lazyGridState.scrollBy(autoScrollSpeed)
            lastDragPosition?.let { applySelectionAt(it) }
            delay(10)
        }
    }

    return this.pointerInput(itemIds, autoScrollThresholdPx) {
        awaitEachGesture {
            // Skip downs already taken by item controls (e.g. the ⋮ menu button).
            val down = awaitFirstDown(requireUnconsumed = true)
            val longPress = awaitLongPressOrCancellation(down.id)
            val ids = itemIdsState.value

            if (longPress == null) {
                // Released before long-press (tap), or cancelled by movement (scroll).
                val released =
                    currentEvent.changes.none { change ->
                        change.id == down.id && change.pressed
                    }
                if (released) {
                    val hitIndex =
                        lazyGridState.itemIndexAtOffset(down.position, ids)
                            ?: return@awaitEachGesture
                    toggleIndex(hitIndex)
                }
                return@awaitEachGesture
            }

            val hitIndex =
                lazyGridState.itemIndexAtOffset(longPress.position, ids)
                    ?: return@awaitEachGesture
            haptics.performHapticFeedback(HapticFeedbackType.LongPress)
            dragCurrentIndex = hitIndex
            lastDragPosition = longPress.position
            toggleIndex(hitIndex)

            drag(longPress.id) { change ->
                change.consume()
                if (dragCurrentIndex == null) {
                    return@drag
                }
                lastDragPosition = change.position
                val viewportHeight = lazyGridState.layoutInfo.viewportSize.height.toFloat()
                val distFromBottom = viewportHeight - change.position.y
                val distFromTop = change.position.y
                autoScrollSpeed =
                    when {
                        distFromBottom < autoScrollThresholdPx ->
                            autoScrollThresholdPx - distFromBottom

                        distFromTop < autoScrollThresholdPx ->
                            -(autoScrollThresholdPx - distFromTop)

                        else -> 0f
                    }
                applySelectionAt(change.position)
            }
            resetDrag()
        }
    }
}

private fun LazyGridState.itemIndexAtOffset(
    hitPoint: Offset,
    itemIds: List<Long>,
): Int? {
    if (itemIds.isEmpty()) {
        return null
    }
    val hit = hitPoint.round()
    // Prefer the topmost (last drawn) item when cells ever overlap in hit-testing.
    val itemInfo =
        layoutInfo.visibleItemsInfo
            .asReversed()
            .firstOrNull { info -> info.contains(hit) }
            ?: return null

    resolveItemIndex(itemInfo.key, itemInfo.index, itemIds)?.let { return it }
    return itemInfo.index.takeIf { it in itemIds.indices }
}

private fun resolveItemIndex(
    key: Any,
    layoutIndex: Int,
    itemIds: List<Long>,
): Int? {
    when (key) {
        is Long -> {
            val byKey = itemIds.indexOf(key)
            if (byKey >= 0) {
                return byKey
            }
        }

        is Int -> {
            if (key in itemIds.indices) {
                return key
            }
            val byKey = itemIds.indexOf(key.toLong())
            if (byKey >= 0) {
                return byKey
            }
        }
    }
    return layoutIndex.takeIf { it in itemIds.indices }
}

private fun LazyGridItemInfo.contains(hit: IntOffset): Boolean {
    val left = offset.x
    val top = offset.y
    val right = left + size.width
    val bottom = top + size.height
    return hit.x >= left && hit.x < right && hit.y >= top && hit.y < bottom
}

private fun Set<Long>.toggleId(id: Long): Set<Long> = if (id in this) {
    this - id
} else {
    this + id
}

/**
 * Toggle every item the finger newly enters while moving from [fromIndex] to [toIndex]
 * (the cell being left is not toggled again).
 */
private fun Set<Long>.toggleDragPath(
    itemIds: List<Long>,
    fromIndex: Int,
    toIndex: Int,
): Set<Long> {
    if (itemIds.isEmpty() || fromIndex == toIndex) {
        return this
    }
    if (fromIndex !in itemIds.indices || toIndex !in itemIds.indices) {
        return this
    }
    val step = if (toIndex > fromIndex) 1 else -1
    var result = this
    var index = fromIndex + step
    while (true) {
        result = result.toggleId(itemIds[index])
        if (index == toIndex) {
            break
        }
        index += step
    }
    return result
}
