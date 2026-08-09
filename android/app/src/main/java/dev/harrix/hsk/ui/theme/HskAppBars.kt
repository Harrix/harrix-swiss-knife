package dev.harrix.hsk.ui.theme

import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.WindowInsetsSides
import androidx.compose.foundation.layout.only
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.TopAppBarColors
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable

/**
 * Scaffold content insets that leave the status bar to [androidx.compose.material3.TopAppBar].
 *
 * Using full [WindowInsets.safeDrawing] on Scaffold pushes the app bar below the status bar, so
 * the clock strip keeps the window/background color while the bar uses a different surface.
 */
@Composable
fun hskScaffoldContentWindowInsets(): WindowInsets = WindowInsets.safeDrawing.only(WindowInsetsSides.Horizontal + WindowInsetsSides.Bottom)

/** Top app bar colors matching the status-bar strip under edge-to-edge. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun hskTopAppBarColors(): TopAppBarColors = TopAppBarDefaults.topAppBarColors(
    containerColor = MaterialTheme.colorScheme.surface,
    scrolledContainerColor = MaterialTheme.colorScheme.surface,
)
