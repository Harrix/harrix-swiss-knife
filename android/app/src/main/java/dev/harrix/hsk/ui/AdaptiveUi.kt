package dev.harrix.hsk.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.wrapContentWidth
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonColors
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import dev.harrix.hsk.ui.theme.ActionButtonShape

/** Compact phone width where icon+label-in-a-row buttons tend to wrap mid-word. */
const val CompactScreenWidthDp = 400

private const val MediumScreenWidthDp = 600

private const val ExpandedScreenWidthDp = 840

private val AdaptiveBottomBarMaxWidth = 720.dp

private val AdaptiveContentMaxWidth = 840.dp

@Composable
fun isCompactWidth(): Boolean = LocalConfiguration.current.screenWidthDp < CompactScreenWidthDp

@Composable
fun screenWidthDp(): Int = LocalConfiguration.current.screenWidthDp

@Composable
fun homeGridColumnCount(): Int {
    val configuration = LocalConfiguration.current
    val width = configuration.screenWidthDp
    val height = configuration.screenHeightDp
    return when {
        width >= ExpandedScreenWidthDp -> 3

        // Landscape phones: one column so cards stay readable above the nav bar.
        height < CompactScreenWidthDp && width >= MediumScreenWidthDp -> 1

        else -> 2
    }
}

@Composable
fun isCompactHeight(): Boolean = LocalConfiguration.current.screenHeightDp < CompactScreenWidthDp

/** True for tablets / large foldables (sw ≥ 600dp), orientation-independent. */
@Composable
fun isTablet(): Boolean = LocalConfiguration.current.smallestScreenWidthDp >= MediumScreenWidthDp

@Composable
fun videoGridColumnCount(): Int {
    val width = screenWidthDp()
    return when {
        width >= ExpandedScreenWidthDp -> 5
        width >= MediumScreenWidthDp -> 4
        else -> 3
    }
}

/**
 * Bottom-bar action: icon and label on one row. Short labels (Delete / Skip / Keep)
 * fit on narrow phones; longer translations wrap up to two lines, then shrink/ellipsis.
 * Grows evenly in a [RowScope].
 */
@Composable
fun RowScope.CompactBottomActionButton(
    onClick: () -> Unit,
    icon: ImageVector,
    label: String,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    outlined: Boolean = false,
    colors: ButtonColors =
        if (outlined) {
            ButtonDefaults.outlinedButtonColors()
        } else {
            ButtonDefaults.buttonColors()
        },
) {
    val content: @Composable () -> Unit = {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center,
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(18.dp),
            )
            Spacer(modifier = Modifier.width(6.dp))
            AutoFitText(
                text = label,
                modifier = Modifier.weight(1f, fill = false),
                style = MaterialTheme.typography.labelLarge,
                maxLines = 2,
                textAlign = TextAlign.Center,
            )
        }
    }
    val buttonModifier =
        modifier
            .weight(1f)
            .heightIn(min = 56.dp)
    val padding = PaddingValues(horizontal = 8.dp, vertical = 10.dp)
    if (outlined) {
        OutlinedButton(
            onClick = onClick,
            enabled = enabled,
            modifier = buttonModifier,
            shape = ActionButtonShape,
            contentPadding = padding,
            colors = colors,
            content = { content() },
        )
    } else {
        Button(
            onClick = onClick,
            enabled = enabled,
            modifier = buttonModifier,
            shape = ActionButtonShape,
            contentPadding = padding,
            colors = colors,
            content = { content() },
        )
    }
}

/** Limits bottom-bar width on tablets while staying full-width on phones. */
@Composable
fun Modifier.adaptiveBottomBarWidth(): Modifier = this
    .fillMaxWidth()
    .widthIn(max = AdaptiveBottomBarMaxWidth)

/** Limits settings / about content width on tablets and centers it. */
@Composable
fun Modifier.adaptiveContentWidth(): Modifier = this
    .fillMaxWidth()
    .wrapContentWidth(Alignment.CenterHorizontally)
    .widthIn(max = AdaptiveContentMaxWidth)

/**
 * Full-width primary action (e.g. Video Cleaner delete): on narrow phones stacks icon
 * above label; long labels wrap up to two lines, then shrink/ellipsis.
 */
@Composable
fun CompactWideActionButton(
    onClick: () -> Unit,
    icon: ImageVector,
    label: String,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    colors: ButtonColors = ButtonDefaults.buttonColors(),
) {
    val compact = isCompactWidth()
    Button(
        onClick = onClick,
        enabled = enabled,
        modifier = modifier
            .fillMaxWidth()
            .heightIn(min = if (compact) 64.dp else 56.dp),
        shape = ActionButtonShape,
        contentPadding =
        PaddingValues(
            horizontal = if (compact) 12.dp else 16.dp,
            vertical = 10.dp,
        ),
        colors = colors,
    ) {
        if (compact) {
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(2.dp),
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    modifier = Modifier.size(20.dp),
                )
                AutoFitText(
                    text = label,
                    style = MaterialTheme.typography.labelLarge,
                    maxLines = 2,
                    textAlign = TextAlign.Center,
                )
            }
        } else {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center,
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp),
                )
                Spacer(modifier = Modifier.width(8.dp))
                AutoFitText(
                    text = label,
                    modifier = Modifier.weight(1f, fill = false),
                    style = MaterialTheme.typography.labelLarge,
                    maxLines = 2,
                    textAlign = TextAlign.Center,
                )
            }
        }
    }
}
