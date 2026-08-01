package dev.harrix.hsk.ui.theme

import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

/** Brand seed: Keep / primary actions. */
val GreenPrimary = Color(0xFF4CAF50)

/** Brand seed: Delete / error actions. */
val RedError = Color(0xFFCC584C)

val LightColorScheme =
    lightColorScheme(
        primary = GreenPrimary,
        onPrimary = Color.White,
        primaryContainer = Color(0xFFC8E6C9),
        onPrimaryContainer = Color(0xFF0D3B12),
        secondary = Color(0xFF52634F),
        onSecondary = Color.White,
        secondaryContainer = Color(0xFFD5E8D0),
        onSecondaryContainer = Color(0xFF101F0F),
        tertiary = Color(0xFF39656B),
        onTertiary = Color.White,
        tertiaryContainer = Color(0xFFBCEBF2),
        onTertiaryContainer = Color(0xFF001F23),
        error = RedError,
        onError = Color.White,
        errorContainer = Color(0xFFFFDAD6),
        onErrorContainer = Color(0xFF410002),
        background = Color(0xFFF7FBF2),
        onBackground = Color(0xFF191D17),
        surface = Color(0xFFF7FBF2),
        onSurface = Color(0xFF191D17),
        surfaceVariant = Color(0xFFDDE5D9),
        onSurfaceVariant = Color(0xFF414941),
        outline = Color(0xFF727970),
        outlineVariant = Color(0xFFC1C9BB),
        scrim = Color(0xFF000000),
        inverseSurface = Color(0xFF2D322B),
        inverseOnSurface = Color(0xFFEFF2E9),
        inversePrimary = Color(0xFFA3D69B),
        surfaceTint = GreenPrimary,
        surfaceBright = Color(0xFFF7FBF2),
        surfaceDim = Color(0xFFD8DBD3),
        surfaceContainerLowest = Color.White,
        surfaceContainerLow = Color(0xFFF1F5EC),
        surfaceContainer = Color(0xFFEBF0E6),
        surfaceContainerHigh = Color(0xFFE5EAE1),
        surfaceContainerHighest = Color(0xFFE0E4DB),
    )

val DarkColorScheme =
    darkColorScheme(
        primary = Color(0xFFA3D69B),
        onPrimary = Color(0xFF0D380F),
        primaryContainer = Color(0xFF1B5E20),
        onPrimaryContainer = Color(0xFFC8E6C9),
        secondary = Color(0xFFB9CCB5),
        onSecondary = Color(0xFF243425),
        secondaryContainer = Color(0xFF3A4B39),
        onSecondaryContainer = Color(0xFFD5E8D0),
        tertiary = Color(0xFFA0CFD5),
        onTertiary = Color(0xFF00363B),
        tertiaryContainer = Color(0xFF1F4D53),
        onTertiaryContainer = Color(0xFFBCEBF2),
        error = Color(0xFFFFB4AB),
        onError = Color(0xFF690005),
        errorContainer = Color(0xFF93000A),
        onErrorContainer = Color(0xFFFFDAD6),
        background = Color(0xFF10140F),
        onBackground = Color(0xFFE0E4DB),
        surface = Color(0xFF10140F),
        onSurface = Color(0xFFE0E4DB),
        surfaceVariant = Color(0xFF414941),
        onSurfaceVariant = Color(0xFFC1C9BB),
        outline = Color(0xFF8B9386),
        outlineVariant = Color(0xFF414941),
        scrim = Color(0xFF000000),
        inverseSurface = Color(0xFFE0E4DB),
        inverseOnSurface = Color(0xFF2D322B),
        inversePrimary = Color(0xFF2E6B28),
        surfaceTint = Color(0xFFA3D69B),
        surfaceBright = Color(0xFF363A34),
        surfaceDim = Color(0xFF10140F),
        surfaceContainerLowest = Color(0xFF0B0F0A),
        surfaceContainerLow = Color(0xFF191D17),
        surfaceContainer = Color(0xFF1D211B),
        surfaceContainerHigh = Color(0xFF272B25),
        surfaceContainerHighest = Color(0xFF323630),
    )
