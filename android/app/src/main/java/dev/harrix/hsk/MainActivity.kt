package dev.harrix.hsk

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.ui.Modifier
import dev.harrix.hsk.ui.MainScreen
import dev.harrix.hsk.ui.theme.HskAndroidTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            HskAndroidTheme(darkTheme = false) {
                MainScreen(modifier = Modifier.fillMaxSize())
            }
        }
    }
}
