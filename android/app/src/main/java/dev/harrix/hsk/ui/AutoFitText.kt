package dev.harrix.hsk.ui

import androidx.compose.material3.LocalTextStyle
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
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
 * Implemented without [androidx.compose.foundation.layout.BoxWithConstraints] so it is safe
 * inside [androidx.compose.material3.ListItem], segmented buttons, and other layouts that
 * request intrinsic measurements.
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
    val textMeasurer = rememberTextMeasurer()
    var fontSizeSp by remember(text, maxSp, minSp, maxLines, softWrap, mergedStyle) {
        mutableFloatStateOf(maxSp)
    }

    Text(
        text = text,
        modifier = modifier,
        color = color,
        style = mergedStyle.withAutoFitFontSize(fontSizeSp.sp, color),
        textAlign = textAlign,
        overflow = TextOverflow.Ellipsis,
        softWrap = softWrap,
        maxLines = maxLines,
        onTextLayout = { result ->
            if (!result.hasVisualOverflow || fontSizeSp <= minSp + 0.01f) {
                return@Text
            }
            val constraints = result.layoutInput.constraints
            val maxWidth = constraints.maxWidth.coerceAtLeast(0)
            val maxHeight =
                if (constraints.hasBoundedHeight) {
                    constraints.maxHeight.coerceAtLeast(0)
                } else {
                    Constraints.Infinity
                }

            fun fits(sizeSp: Float): Boolean {
                val measured =
                    textMeasurer.measure(
                        text = text,
                        style = mergedStyle.withAutoFitFontSize(sizeSp.sp, color),
                        overflow = TextOverflow.Clip,
                        softWrap = softWrap,
                        maxLines = maxLines,
                        constraints =
                        Constraints(
                            maxWidth = maxWidth,
                            maxHeight = maxHeight,
                        ),
                    )
                return !measured.hasVisualOverflow
            }

            val best =
                if (!fits(minSp)) {
                    minSp
                } else {
                    var low = minSp
                    var high = fontSizeSp
                    var found = minSp
                    repeat(12) {
                        val mid = (low + high) / 2f
                        if (fits(mid)) {
                            found = mid
                            low = mid
                        } else {
                            high = mid
                        }
                    }
                    found
                }
            if (best < fontSizeSp - 0.05f) {
                fontSizeSp = best
            } else if (fontSizeSp > minSp) {
                // Still overflowing but binary search stalled — force the floor.
                fontSizeSp = minSp
            }
        },
    )
}

private fun TextStyle.withAutoFitFontSize(
    size: TextUnit,
    color: Color,
): TextStyle {
    val canScaleLineHeight =
        fontSize.isSpecified &&
            lineHeight.isSpecified &&
            fontSize.isSp &&
            lineHeight.isSp &&
            fontSize.value > 0f
    val scaledLineHeight =
        if (canScaleLineHeight) {
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
