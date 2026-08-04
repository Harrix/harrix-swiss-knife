package dev.harrix.hsk

import android.content.Intent
import android.content.pm.ShortcutManager
import android.os.Build
import androidx.core.content.pm.ShortcutInfoCompat
import androidx.core.content.pm.ShortcutManagerCompat
import androidx.core.graphics.drawable.IconCompat

/** Publishes a Direct Share target so Photo Editor ranks higher in the share sheet. */
object PhotoEditorShareShortcuts {
    const val CategoryImageEdit = "dev.harrix.hsk.share.IMAGE_EDIT"
    private const val ShortcutId = "photo_editor_share"

    fun publish(activity: MainActivity) {
        val shortcut =
            ShortcutInfoCompat
                .Builder(activity, ShortcutId)
                .setShortLabel(activity.getString(R.string.photo_editor_share_label))
                .setLongLabel(activity.getString(R.string.photo_editor_card_description))
                .setIcon(IconCompat.createWithResource(activity, R.mipmap.ic_launcher))
                .setIntent(
                    Intent(Intent.ACTION_MAIN)
                        .setClass(activity, MainActivity::class.java)
                        .addCategory(Intent.CATEGORY_LAUNCHER),
                ).setCategories(setOf(CategoryImageEdit))
                .setLongLived(true)
                .build()
        ShortcutManagerCompat.pushDynamicShortcut(activity, shortcut)

        // Helps some OEM share sheets that still look at platform ShortcutManager.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N_MR1) {
            runCatching {
                activity.getSystemService(ShortcutManager::class.java)?.reportShortcutUsed(ShortcutId)
            }
        }
    }
}
