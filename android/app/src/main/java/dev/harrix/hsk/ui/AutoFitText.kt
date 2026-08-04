package dev.harrix.hsk.ui

import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.LocalTextStyle
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Constraints
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.isSpecified
import androidx.compose.ui.unit.sp

/** Smallest font size before ellipsis when auto-fitting translated labels. */
val AutoFitTextMinFontSize = 10.sp

/**
 * Label text that shrinks to fit the available space, then ellipsizes at [minFontSize].
 *
 * Use for buttons, chips, top-bar titles, and other fixed-width chrome where
 * translations may be longer than the English source.
 */
@Composable
fun AutoFitText(
    text: String,
    modifier: Modifier = Modifier,
    color: Color = Color.Unspecified,
    style: TextStyle = LocalTextStyle.current,
    textAlign: TextAlign? = null,
    maxLines: Int = 1,
    softWrap: Boolean = maxLines > 1,
    minFontSize: TextUnit = AutoFitTextMinFontSize,
    fillMaxWidth: Boolean = false,
) {
    val mergedStyle = LocalTextStyle.current.merge(style)
    val baseFontSize =
        if (mergedStyle.fontSize.isSpecified) {
            mergedStyle.fontSize
        } else {
            14.sp
        }
    val minSp = minFontSize.value.coerceAtLeast(1f)
    val maxSp = baseFontSize.value.coerceAtLeast(minSp)

    BoxWithConstraints(modifier = modifier) {
        val textMeasurer = rememberTextMeasurer()
        val maxWidthPx =
            if (constraints.hasBoundedWidth) {
                constraints.maxWidth.coerceAtLeast(0)
            } else {
                Constraints.Infinity
            }
        val maxHeightPx =
            if (constraints.hasBoundedHeight) {
                constraints.maxHeight.coerceAtLeast(0)
            } else {
                Constraints.Infinity
            }

        val fontSize =
            remember(
                text,
                maxWidthPx,
                maxHeightPx,
                maxSp,
                minSp,
                maxLines,
                softWrap,
                mergedStyle,
                color,
            ) {
                if (maxWidthPx == Constraints.Infinity && maxHeightPx == Constraints.Infinity) {
                    return@remember maxSp.sp
                }

                fun fits(sizeSp: Float): Boolean {
                    val candidate = mergedStyle.withAutoFitFontSize(sizeSp.sp, color)
                    val result =
                        textMeasurer.measure(
                            text = text,
                            style = candidate,
                            overflow = TextOverflow.Clip,
                            softWrap = softWrap,
                            maxLines = maxLines,
                            constraints =
                            Constraints(
                                maxWidth = maxWidthPx,
                                maxHeight = maxHeightPx,
                            ),
                        )
                    return !result.hasVisualOverflow
                }

                if (fits(maxSp)) {
                    return@remember maxSp.sp
                }
                if (!fits(minSp)) {
                    return@remember minSp.sp
                }
                var low = minSp
                var high = maxSp
                var best = minSp
                repeat(14) {
                    val mid = (low + high) / 2f
                    if (fits(mid)) {
                        best = mid
                        low = mid
                    } else {
                        high = mid
                    }
                }
                best.sp
            }

        Text(
            text = text,
            modifier = if (fillMaxWidth) Modifier.fillMaxWidth() else Modifier,
            color = color,
            style = mergedStyle.withAutoFitFontSize(fontSize, color),
            textAlign = textAlign,
            overflow = TextOverflow.Ellipsis,
            softWrap = softWrap,
            maxLines = maxLines,
        )
    }
}

private fun TextStyle.withAutoFitFontSize(
    size: TextUnit,
    color: Color,
): TextStyle {
    val scaledLineHeight =
        if (fontSize.isSpecified && lineHeight.isSpecified && fontSize.value > 0f) {
            (lineHeight.value * size.value / fontSize.value).sp
        } else {
            TextUnit.Unspecified
        }
    return copy(
        fontSize = size,
        lineHeight = scaledLineHeight,
        color = if (color != Color.Unspecified) color else this.color,
    )
}
