package dev.harrix.hsk.gallery

import android.content.Context

class GalleryCleanerPreferences(
    context: Context,
) {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun shouldShowIntro(): Boolean = prefs.getBoolean(KEY_SHOW_INTRO, true)

    fun setShowIntro(show: Boolean) {
        prefs.edit().putBoolean(KEY_SHOW_INTRO, show).apply()
    }

    fun shouldShowManageMediaPrompt(): Boolean = prefs.getBoolean(KEY_SHOW_MANAGE_MEDIA, true)

    fun setShowManageMediaPrompt(show: Boolean) {
        prefs.edit().putBoolean(KEY_SHOW_MANAGE_MEDIA, show).apply()
    }

    fun loadDateFilter(): GalleryDateFilter {
        val enabled = prefs.getBoolean(KEY_DATE_FILTER_ENABLED, false)
        val hasRange =
            prefs.contains(KEY_DATE_FILTER_START_SEC) && prefs.contains(KEY_DATE_FILTER_END_SEC)
        if (!hasRange) {
            return GalleryDateFilter(enabled = enabled)
        }
        val start = prefs.getLong(KEY_DATE_FILTER_START_SEC, 0L)
        val end = prefs.getLong(KEY_DATE_FILTER_END_SEC, 0L)
        return GalleryDateFilter(
            enabled = enabled,
            startEpochSecInclusive = start,
            endEpochSecInclusive = end,
        )
    }

    fun saveDateFilter(filter: GalleryDateFilter) {
        prefs
            .edit()
            .putBoolean(KEY_DATE_FILTER_ENABLED, filter.enabled)
            .putLong(KEY_DATE_FILTER_START_SEC, filter.startEpochSecInclusive)
            .putLong(KEY_DATE_FILTER_END_SEC, filter.endEpochSecInclusive)
            .apply()
    }

    fun isUnreviewedOnlyModeEnabled(): Boolean = prefs.getBoolean(KEY_UNREVIEWED_ONLY_MODE, false)

    fun setUnreviewedOnlyModeEnabled(enabled: Boolean) {
        prefs.edit().putBoolean(KEY_UNREVIEWED_ONLY_MODE, enabled).apply()
    }

    fun getReviewedPhotoIds(): Set<Long> = prefs
        .getStringSet(KEY_REVIEWED_PHOTO_IDS, emptySet())
        .orEmpty()
        .mapNotNull { it.toLongOrNull() }
        .toSet()

    fun markPhotoReviewed(photoId: Long) {
        val updated = HashSet(prefs.getStringSet(KEY_REVIEWED_PHOTO_IDS, emptySet()).orEmpty())
        if (updated.add(photoId.toString())) {
            prefs.edit().putStringSet(KEY_REVIEWED_PHOTO_IDS, updated).apply()
        }
    }

    fun unmarkPhotoReviewed(photoId: Long) {
        val updated = HashSet(prefs.getStringSet(KEY_REVIEWED_PHOTO_IDS, emptySet()).orEmpty())
        if (updated.remove(photoId.toString())) {
            prefs.edit().putStringSet(KEY_REVIEWED_PHOTO_IDS, updated).apply()
        }
    }

    fun clearReviewedPhotos() {
        prefs.edit().remove(KEY_REVIEWED_PHOTO_IDS).apply()
    }

    fun reviewedPhotoCount(): Int = getReviewedPhotoIds().size

    companion object {
        private const val PREFS_NAME = "gallery_cleaner"
        private const val KEY_SHOW_INTRO = "show_intro"
        private const val KEY_SHOW_MANAGE_MEDIA = "show_manage_media_v2"
        private const val KEY_DATE_FILTER_ENABLED = "date_filter_enabled"
        private const val KEY_DATE_FILTER_START_SEC = "date_filter_start_sec"
        private const val KEY_DATE_FILTER_END_SEC = "date_filter_end_sec"
        private const val KEY_UNREVIEWED_ONLY_MODE = "unreviewed_only_mode"
        private const val KEY_REVIEWED_PHOTO_IDS = "reviewed_photo_ids"
    }
}
