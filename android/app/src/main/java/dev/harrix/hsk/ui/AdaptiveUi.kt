package dev.harrix.hsk.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonColors
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp

/** Compact phone width where icon+label-in-a-row buttons tend to wrap mid-word. */
const val CompactScreenWidthDp = 400

private val AdaptiveBottomBarMaxWidth = 720.dp

@Composable
fun isCompactWidth(): Boolean = LocalConfiguration.current.screenWidthDp < CompactScreenWidthDp

/**
 * Bottom-bar action: icon above label so Delete / Skip / Keep fit on narrow phones
 * without mid-word wrapping. Grows evenly in a [RowScope].
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
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(20.dp),
            )
            Text(
                text = label,
                style = MaterialTheme.typography.labelLarge,
                maxLines = 1,
                softWrap = false,
                overflow = TextOverflow.Ellipsis,
                textAlign = TextAlign.Center,
            )
        }
    }
    val buttonModifier =
        modifier
            .weight(1f)
            .heightIn(min = 56.dp)
    val padding = PaddingValues(horizontal = 6.dp, vertical = 8.dp)
    if (outlined) {
        OutlinedButton(
            onClick = onClick,
            enabled = enabled,
            modifier = buttonModifier,
            contentPadding = padding,
            colors = colors,
            content = { content() },
        )
    } else {
        Button(
            onClick = onClick,
            enabled = enabled,
            modifier = buttonModifier,
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
