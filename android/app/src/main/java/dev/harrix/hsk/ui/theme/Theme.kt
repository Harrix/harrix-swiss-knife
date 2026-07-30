package dev.harrix.hsk.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

val AppGreen = Color(0xFF4CAF50)
val AppRed = Color(0xFFCC584C)

private val LightBackground = Color(0xFFE5E6EA)
private val LightSurface = Color(0xFFFFFFFF)
private val LightDrawerSelected = Color(0xFFCDCED0)

private val DarkBackground = Color(0xFF121316)
private val DarkSurface = Color(0xFF1E1F24)
private val DarkDrawerSelected = Color(0xFF3A3B41)

enum class ThemeMode {
    System,
    Light,
    Dark,
    ;

    fun resolveDarkTheme(isSystemDark: Boolean): Boolean = when (this) {
        System -> isSystemDark
        Light -> false
        Dark -> true
    }

    companion object {
        fun fromStorage(value: String?): ThemeMode = entries.firstOrNull { it.name == value } ?: System
    }
}

private val DarkColorScheme =
    darkColorScheme(
        primary = AppGreen,
        onPrimary = Color.White,
        error = AppRed,
        onError = Color.White,
        background = DarkBackground,
        onBackground = Color(0xFFE8EAED),
        surface = DarkSurface,
        onSurface = Color(0xFFE8EAED),
        onSurfaceVariant = Color(0xFF9AA0A6),
        surfaceContainer = DarkBackground,
        surfaceContainerLow = DarkBackground,
        surfaceContainerHigh = Color(0xFF2A2B30),
        surfaceContainerHighest = DarkSurface,
        secondaryContainer = DarkDrawerSelected,
        onSecondaryContainer = Color(0xFFE8EAED),
        outline = Color(0xFF5F6368),
        outlineVariant = Color(0xFF3C4043),
    )

private val LightColorScheme =
    lightColorScheme(
        primary = AppGreen,
        onPrimary = Color.White,
        error = AppRed,
        onError = Color.White,
        background = LightBackground,
        onBackground = Color(0xFF1C1B1F),
        surface = LightSurface,
        onSurface = Color(0xFF1C1B1F),
        onSurfaceVariant = Color(0xFF5F6368),
        surfaceContainer = LightBackground,
        surfaceContainerLow = LightBackground,
        surfaceContainerHigh = LightBackground,
        surfaceContainerHighest = LightSurface,
        secondaryContainer = LightDrawerSelected,
        onSecondaryContainer = Color(0xFF1C1B1F),
        outline = Color(0xFFC0C0C0),
        outlineVariant = Color(0xFFD0D2D7),
    )

@Composable
fun HskAndroidTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            WindowCompat.getInsetsController(window, view).apply {
                isAppearanceLightStatusBars = !darkTheme
                isAppearanceLightNavigationBars = !darkTheme
            }
        }
    }
    MaterialTheme(
        colorScheme = colorScheme,
        content = content,
    )
}
