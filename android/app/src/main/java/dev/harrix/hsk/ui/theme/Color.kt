package dev.harrix.hsk.ui.theme

import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

/** Brand seed: main / primary actions. */
val BluePrimary = Color(0xFF2E86B7)

/** Brand seed: Keep / positive actions. */
val GreenKeep = Color(0xFF35965F)

/** Brand seed: Delete / error actions. */
val RedError = Color(0xFFCC584C)

val LightColorScheme =
    lightColorScheme(
        primary = BluePrimary,
        onPrimary = Color.White,
        primaryContainer = Color(0xFFD0E8F5),
        onPrimaryContainer = Color(0xFF00344D),
        secondary = GreenKeep,
        onSecondary = Color.White,
        secondaryContainer = Color(0xFFC6EBD7),
        onSecondaryContainer = Color(0xFF002113),
        tertiary = Color(0xFF5B6B7A),
        onTertiary = Color.White,
        tertiaryContainer = Color(0xFFDEE3EA),
        onTertiaryContainer = Color(0xFF181E25),
        error = RedError,
        onError = Color.White,
        errorContainer = Color(0xFFFFDAD6),
        onErrorContainer = Color(0xFF410002),
        background = Color(0xFFF5F8FB),
        onBackground = Color(0xFF171C20),
        surface = Color(0xFFF5F8FB),
        onSurface = Color(0xFF171C20),
        surfaceVariant = Color(0xFFDAE3EC),
        onSurfaceVariant = Color(0xFF3F4850),
        outline = Color(0xFF6F7881),
        outlineVariant = Color(0xFFBEC7D0),
        scrim = Color(0xFF000000),
        inverseSurface = Color(0xFF2C3135),
        inverseOnSurface = Color(0xFFEDF1F5),
        inversePrimary = Color(0xFF8FCEF0),
        surfaceTint = BluePrimary,
        surfaceBright = Color(0xFFF5F8FB),
        surfaceDim = Color(0xFFD6DADE),
        surfaceContainerLowest = Color.White,
        surfaceContainerLow = Color(0xFFEFF3F7),
        surfaceContainer = Color(0xFFE9EEF3),
        surfaceContainerHigh = Color(0xFFE3E8ED),
        surfaceContainerHighest = Color(0xFFDDE3E8),
    )

val DarkColorScheme =
    darkColorScheme(
        primary = Color(0xFF8FCEF0),
        onPrimary = Color(0xFF00344D),
        primaryContainer = Color(0xFF0B6A97),
        onPrimaryContainer = Color(0xFFD0E8F5),
        secondary = Color(0xFF8AD4AE),
        onSecondary = Color(0xFF003822),
        secondaryContainer = Color(0xFF1B7348),
        onSecondaryContainer = Color(0xFFC6EBD7),
        tertiary = Color(0xFFB8C2CC),
        onTertiary = Color(0xFF24303A),
        tertiaryContainer = Color(0xFF3A4650),
        onTertiaryContainer = Color(0xFFDEE3EA),
        error = Color(0xFFFFB4AB),
        onError = Color(0xFF690005),
        errorContainer = Color(0xFF93000A),
        onErrorContainer = Color(0xFFFFDAD6),
        background = Color(0xFF0F1418),
        onBackground = Color(0xFFDDE3E8),
        surface = Color(0xFF0F1418),
        onSurface = Color(0xFFDDE3E8),
        surfaceVariant = Color(0xFF3F4850),
        onSurfaceVariant = Color(0xFFBEC7D0),
        outline = Color(0xFF88919A),
        outlineVariant = Color(0xFF3F4850),
        scrim = Color(0xFF000000),
        inverseSurface = Color(0xFFDDE3E8),
        inverseOnSurface = Color(0xFF2C3135),
        inversePrimary = BluePrimary,
        surfaceTint = Color(0xFF8FCEF0),
        surfaceBright = Color(0xFF353A3E),
        surfaceDim = Color(0xFF0F1418),
        surfaceContainerLowest = Color(0xFF0A0F12),
        surfaceContainerLow = Color(0xFF171C20),
        surfaceContainer = Color(0xFF1B2024),
        surfaceContainerHigh = Color(0xFF252A2E),
        surfaceContainerHighest = Color(0xFF30353A),
    )
