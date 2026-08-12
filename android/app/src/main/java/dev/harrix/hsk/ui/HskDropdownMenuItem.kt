package dev.harrix.hsk.ui

import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.heightIn
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.LocalMinimumInteractiveComponentSize
import androidx.compose.material3.MenuDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

private val HskMenuItemHorizontalPadding = 12.dp
private val HskMenuItemVerticalPadding = 4.dp
private val HskMenuItemMinHeight = 36.dp
private val HskMenuItemMaxHeight = 40.dp

/** Dense dropdown rows; Material defaults leave too much vertical gap. */
val HskMenuItemContentPadding =
    PaddingValues(
        horizontal = HskMenuItemHorizontalPadding,
        vertical = HskMenuItemVerticalPadding,
    )

@Composable
fun HskDropdownMenuItem(
    text: @Composable () -> Unit,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    leadingIcon: @Composable (() -> Unit)? = null,
    trailingIcon: @Composable (() -> Unit)? = null,
    enabled: Boolean = true,
) {
    CompositionLocalProvider(LocalMinimumInteractiveComponentSize provides Dp.Unspecified) {
        DropdownMenuItem(
            text = text,
            onClick = onClick,
            modifier =
            modifier.heightIn(
                min = HskMenuItemMinHeight,
                max = HskMenuItemMaxHeight,
            ),
            leadingIcon = leadingIcon,
            trailingIcon = trailingIcon,
            enabled = enabled,
            colors = MenuDefaults.itemColors(),
            contentPadding = HskMenuItemContentPadding,
        )
    }
}
