package dev.harrix.hsk.ui.theme

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.PathBuilder
import androidx.compose.ui.graphics.vector.group
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.unit.dp

/** Custom app icons that are not in Material Icons. */
object HskIcons {
    private var saveCopyCached: ImageVector? = null

    /**
     * Save-copy: two overlapping floppy-disk (Save) glyphs.
     * Prefer this over Material SaveAs (floppy + pencil).
     */
    val SaveCopy: ImageVector
        get() {
            val cached = saveCopyCached
            if (cached != null) {
                return cached
            }
            val created =
                ImageVector
                    .Builder(
                        name = "Hsk.SaveCopy",
                        defaultWidth = 24.dp,
                        defaultHeight = 24.dp,
                        viewportWidth = 24f,
                        viewportHeight = 24f,
                    ).apply {
                        // Back floppy (slightly up-left, muted).
                        group(
                            translationX = -1.2f,
                            translationY = -1.2f,
                            scaleX = 0.78f,
                            scaleY = 0.78f,
                        ) {
                            path(
                                fill = SolidColor(Color.Black),
                                fillAlpha = 0.45f,
                            ) {
                                saveFloppyPath()
                            }
                        }
                        // Front floppy (slightly down-right).
                        group(
                            translationX = 3.6f,
                            translationY = 3.6f,
                            scaleX = 0.78f,
                            scaleY = 0.78f,
                        ) {
                            path(
                                fill = SolidColor(Color.Black),
                            ) {
                                saveFloppyPath()
                            }
                        }
                    }.build()
            saveCopyCached = created
            return created
        }
}

/** Material Filled Save path (24×24), shared by both disks in [HskIcons.SaveCopy]. */
private fun PathBuilder.saveFloppyPath() {
    moveTo(17.0f, 3.0f)
    horizontalLineTo(5.0f)
    curveToRelative(-1.11f, 0.0f, -2.0f, 0.9f, -2.0f, 2.0f)
    verticalLineToRelative(14.0f)
    curveToRelative(0.0f, 1.1f, 0.89f, 2.0f, 2.0f, 2.0f)
    horizontalLineToRelative(14.0f)
    curveToRelative(1.1f, 0.0f, 2.0f, -0.9f, 2.0f, -2.0f)
    verticalLineTo(7.0f)
    lineToRelative(-4.0f, -4.0f)
    close()
    moveTo(12.0f, 19.0f)
    curveToRelative(-1.66f, 0.0f, -3.0f, -1.34f, -3.0f, -3.0f)
    reflectiveCurveToRelative(1.34f, -3.0f, 3.0f, -3.0f)
    reflectiveCurveToRelative(3.0f, 1.34f, 3.0f, 3.0f)
    reflectiveCurveToRelative(-1.34f, 3.0f, -3.0f, 3.0f)
    close()
    moveTo(15.0f, 9.0f)
    horizontalLineTo(5.0f)
    verticalLineTo(5.0f)
    horizontalLineToRelative(10.0f)
    verticalLineToRelative(4.0f)
    close()
}
