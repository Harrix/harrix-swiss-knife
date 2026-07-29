package dev.harrix.hsk.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val AppBackground = Color(0xFFE5E6EA)
val ContentSurface = Color(0xFFFFFFFF)
val DrawerSelectedContainer = Color(0xFFCDCED0)
val AppGreen = Color(0xFF4CAF50)
val AppRed = Color(0xFFCC584C)

private val DarkColorScheme =
    darkColorScheme(
        primary = AppGreen,
        onPrimary = Color.White,
        error = AppRed,
        onError = Color.White,
    )
private val LightColorScheme =
    lightColorScheme(
        primary = AppGreen,
        onPrimary = Color.White,
        error = AppRed,
        onError = Color.White,
        background = AppBackground,
        surface = ContentSurface,
        surfaceContainer = AppBackground,
        surfaceContainerLow = AppBackground,
        surfaceContainerHigh = AppBackground,
        surfaceContainerHighest = ContentSurface,
        secondaryContainer = DrawerSelectedContainer,
        onSecondaryContainer = Color(0xFF1C1B1F),
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
