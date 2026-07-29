package dev.harrix.hsk.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val AppBackground = Color(0xFFE5E6EA)
val ContentSurface = Color(0xFFFFFFFF)

private val DarkColorScheme = darkColorScheme()
private val LightColorScheme =
    lightColorScheme(
        background = AppBackground,
        surface = ContentSurface,
        surfaceContainer = AppBackground,
        surfaceContainerLow = AppBackground,
        surfaceContainerHigh = AppBackground,
        surfaceContainerHighest = ContentSurface,
    )

@Composable
fun HskAndroidTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    MaterialTheme(
        colorScheme = colorScheme,
        content = content,
    )
}
