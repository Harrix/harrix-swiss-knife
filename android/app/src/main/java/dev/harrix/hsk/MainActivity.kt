package dev.harrix.hsk

import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import androidx.activity.SystemBarStyle
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import dev.harrix.hsk.speechtotext.SpeechToTextWidgetProvider
import dev.harrix.hsk.ui.MainScreen
import dev.harrix.hsk.ui.theme.HskAndroidTheme

class MainActivity : AppCompatActivity() {
    private var pendingImageUriState = mutableStateOf<Uri?>(null)
    private var pendingOpenSpeechToTextState = mutableStateOf(false)

    override fun onCreate(savedInstanceState: Bundle?) {
        val preferences = AppPreferences(this)
        preferences.loadAppLanguage().apply()
        super.onCreate(savedInstanceState)
        enableEdgeToEdge(
            statusBarStyle =
            SystemBarStyle.auto(
                lightScrim = Color.TRANSPARENT,
                darkScrim = Color.TRANSPARENT,
            ),
            navigationBarStyle =
            SystemBarStyle.auto(
                lightScrim = Color.TRANSPARENT,
                darkScrim = Color.TRANSPARENT,
            ),
        )
        PhotoEditorShareShortcuts.publish(this)
        consumeIncomingIntent(intent)
        setContent {
            var themeMode by remember { mutableStateOf(preferences.loadThemeMode()) }
            var appLanguage by remember { mutableStateOf(preferences.loadAppLanguage()) }
            val darkTheme = themeMode.resolveDarkTheme(isSystemInDarkTheme())
            var pendingImageUri by pendingImageUriState
            var pendingOpenSpeechToText by pendingOpenSpeechToTextState
            HskAndroidTheme(darkTheme = darkTheme) {
                MainScreen(
                    themeMode = themeMode,
                    onThemeModeChange = { mode ->
                        preferences.saveThemeMode(mode)
                        themeMode = mode
                    },
                    appLanguage = appLanguage,
                    onAppLanguageChange = { language ->
                        preferences.saveAppLanguage(language)
                        appLanguage = language
                        language.apply()
                    },
                    pendingImageUri = pendingImageUri,
                    onPendingImageUriConsume = { pendingImageUriState.value = null },
                    pendingOpenSpeechToText = pendingOpenSpeechToText,
                    onPendingOpenSpeechToTextConsume = {
                        pendingOpenSpeechToTextState.value = false
                    },
                    modifier = Modifier.fillMaxSize(),
                )
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        consumeIncomingIntent(intent)
    }

    private fun consumeIncomingIntent(intent: Intent?) {
        if (intent == null) {
            return
        }
        if (intent.action == SpeechToTextWidgetProvider.ACTION_OPEN_SPEECH_TO_TEXT) {
            pendingOpenSpeechToTextState.value = true
            return
        }
        val uri = IncomingImageIntents.extractImageUri(intent) ?: return
        tryTakePersistableReadPermission(uri, intent.flags)
        pendingImageUriState.value = uri
    }

    private fun tryTakePersistableReadPermission(
        uri: Uri,
        intentFlags: Int,
    ) {
        val persistable = intentFlags and Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION != 0
        val read = intentFlags and Intent.FLAG_GRANT_READ_URI_PERMISSION != 0
        if (!persistable || !read) {
            return
        }
        runCatching {
            contentResolver.takePersistableUriPermission(
                uri,
                Intent.FLAG_GRANT_READ_URI_PERMISSION,
            )
        }
    }
}
