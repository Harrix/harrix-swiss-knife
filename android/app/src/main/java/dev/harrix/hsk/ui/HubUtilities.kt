package dev.harrix.hsk.ui

import androidx.annotation.StringRes
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.dp
import dev.harrix.hsk.R
import dev.harrix.hsk.ui.icons.LucideIcons

/**
 * Shared Lucide icons for hub utilities (home cards, drawer, top app bars).
 */
object HubUtilityIcons {
    val GalleryCleaner: ImageVector = LucideIcons.Broom
    val VideoCleaner: ImageVector = LucideIcons.VideoLibrary
    val PhotoEditor: ImageVector = LucideIcons.Crop
    val SpeechToText: ImageVector = LucideIcons.Mic
    val MedicineSearch: ImageVector = LucideIcons.Medication
    val Movies: ImageVector = LucideIcons.Movie
    val HealthConnect: ImageVector = LucideIcons.FitnessCenter
}

/**
 * Catalog entry for home grid / drawer utility rows.
 */
data class HubUtilityItem(
    @StringRes val titleRes: Int,
    @StringRes val descriptionRes: Int,
    val icon: ImageVector,
)

/** Home-card / drawer utilities in display order (without Home / About). */
val HubUtilities: List<HubUtilityItem> =
    listOf(
        HubUtilityItem(
            titleRes = R.string.nav_drawer_gallery_cleaner,
            descriptionRes = R.string.gallery_cleaner_card_description,
            icon = HubUtilityIcons.GalleryCleaner,
        ),
        HubUtilityItem(
            titleRes = R.string.nav_drawer_video_cleaner,
            descriptionRes = R.string.video_cleaner_card_description,
            icon = HubUtilityIcons.VideoCleaner,
        ),
        HubUtilityItem(
            titleRes = R.string.nav_drawer_photo_editor,
            descriptionRes = R.string.photo_editor_card_description,
            icon = HubUtilityIcons.PhotoEditor,
        ),
        HubUtilityItem(
            titleRes = R.string.nav_drawer_speech_to_text,
            descriptionRes = R.string.speech_to_text_card_description,
            icon = HubUtilityIcons.SpeechToText,
        ),
        HubUtilityItem(
            titleRes = R.string.nav_drawer_medicine_search,
            descriptionRes = R.string.medicine_search_card_description,
            icon = HubUtilityIcons.MedicineSearch,
        ),
        HubUtilityItem(
            titleRes = R.string.nav_drawer_movies,
            descriptionRes = R.string.movies_card_description,
            icon = HubUtilityIcons.Movies,
        ),
        HubUtilityItem(
            titleRes = R.string.nav_drawer_health_connect,
            descriptionRes = R.string.health_connect_card_description,
            icon = HubUtilityIcons.HealthConnect,
        ),
    )

/**
 * Top-app-bar title with the same utility Lucide icon used on home cards / drawer.
 */
@Composable
fun UtilityTopBarTitle(
    icon: ImageVector,
    title: String,
    modifier: Modifier = Modifier,
    subtitle: String? = null,
    titleStyle: TextStyle = MaterialTheme.typography.titleLarge,
) {
    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.Start,
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(22.dp),
            tint = MaterialTheme.colorScheme.onSurface,
        )
        Spacer(modifier = Modifier.width(10.dp))
        Column(modifier = Modifier.weight(1f, fill = false)) {
            AutoFitText(
                text = title,
                style = titleStyle,
                maxLines = 1,
            )
            if (!subtitle.isNullOrBlank()) {
                AutoFitText(
                    text = subtitle,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 1,
                )
            }
        }
    }
}
