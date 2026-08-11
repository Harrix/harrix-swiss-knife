package dev.harrix.hsk.ui.gallery

import androidx.compose.foundation.gestures.detectDragGesturesAfterLongPress
import androidx.compose.foundation.gestures.scrollBy
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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.round
import androidx.compose.ui.unit.toIntRect
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive

/**
 * Gallery-style multi-select: long-press an item, then drag across the grid.
 * Each time the finger enters a cell (including returning to the start cell), that
 * item toggles. Near the top/bottom edges the grid auto-scrolls while selection continues.
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
        detectDragGesturesAfterLongPress(
            onDragStart = { offset ->
                val ids = itemIdsState.value
                val hitIndex =
                    lazyGridState.itemIndexAtOffset(offset, ids)
                        ?: return@detectDragGesturesAfterLongPress
                val hitId = ids[hitIndex]
                haptics.performHapticFeedback(HapticFeedbackType.LongPress)
                dragCurrentIndex = hitIndex
                lastDragPosition = offset
                onSelectedIdsChangeState.value(selectedIdsState.value.toggleId(hitId))
            },
            onDragCancel = {
                autoScrollSpeed = 0f
                dragCurrentIndex = null
                lastDragPosition = null
            },
            onDragEnd = {
                autoScrollSpeed = 0f
                dragCurrentIndex = null
                lastDragPosition = null
            },
            onDrag = { change, _ ->
                if (dragCurrentIndex == null) {
                    return@detectDragGesturesAfterLongPress
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
            },
        )
    }
}

private fun LazyGridState.itemIndexAtOffset(
    hitPoint: Offset,
    itemIds: List<Long>,
): Int? {
    val key =
        layoutInfo.visibleItemsInfo
            .find { itemInfo ->
                itemInfo.size.toIntRect().contains(hitPoint.round() - itemInfo.offset)
            }?.key as? Long
            ?: return null
    val index = itemIds.indexOf(key)
    return index.takeIf { it >= 0 }
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
