package dev.harrix.hsk

import android.app.Application
import dev.harrix.hsk.ai.AiConfig

class HskApp : Application() {
    override fun onCreate() {
        super.onCreate()
        AiConfig.attach(this)
    }
}
