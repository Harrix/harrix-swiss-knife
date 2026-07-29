package dev.harrix.hsk.ui

import android.os.Build
import android.view.HapticFeedbackConstants
import android.view.View

/** Short system haptic for confirmed keep / delete actions. */
fun View.performLightActionHaptic() {
    val feedbackConstant =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            HapticFeedbackConstants.CONFIRM
        } else {
            HapticFeedbackConstants.CONTEXT_CLICK
        }
    performHapticFeedback(feedbackConstant)
}
