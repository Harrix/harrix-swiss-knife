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

    fun clearDateFilter() {
        saveDateFilter(GalleryDateFilter(enabled = false))
    }

    fun isUnreviewedOnlyModeEnabled(): Boolean = prefs.getBoolean(KEY_UNREVIEWED_ONLY_MODE, false)

    fun setUnreviewedOnlyModeEnabled(enabled: Boolean) {
        prefs.edit().putBoolean(KEY_UNREVIEWED_ONLY_MODE, enabled).apply()
    }

    fun getReviewOrder(): GalleryReviewOrder = GalleryReviewOrder.fromStorage(prefs.getString(KEY_REVIEW_ORDER, null))

    fun setReviewOrder(order: GalleryReviewOrder) {
        prefs.edit().putString(KEY_REVIEW_ORDER, order.storageValue).apply()
    }

    /**
     * Custom images folder as MediaStore relative path (e.g. `DCIM/Screenshots/`).
     * `null` means the default Camera folder.
     */
    fun getImagesRelativePath(): String? {
        val stored = prefs.getString(KEY_IMAGES_RELATIVE_PATH, null)?.trim().orEmpty()
        return stored.takeIf { it.isNotEmpty() }?.let(MediaFolderPaths::normalizeRelativePath)
    }

    fun setImagesRelativePath(relativePath: String?) {
        val normalized =
            relativePath
                ?.trim()
                ?.takeIf { it.isNotEmpty() }
                ?.let(MediaFolderPaths::normalizeRelativePath)
        prefs
            .edit()
            .apply {
                if (normalized == null) {
                    remove(KEY_IMAGES_RELATIVE_PATH)
                } else {
                    putString(KEY_IMAGES_RELATIVE_PATH, normalized)
                }
            }.apply()
    }

    fun isDefaultImagesFolder(): Boolean = getImagesRelativePath() == null

    fun resetImagesFolderToDefault() {
        setImagesRelativePath(null)
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

    /**
     * Restores Gallery Cleaner options to defaults. Reviewed-photo history is kept;
     * use [clearReviewedPhotos] to reset that separately.
     */
    fun resetSettingsToDefaults() {
        prefs
            .edit()
            .putBoolean(KEY_SHOW_INTRO, true)
            .putBoolean(KEY_SHOW_MANAGE_MEDIA, true)
            .putBoolean(KEY_DATE_FILTER_ENABLED, false)
            .remove(KEY_DATE_FILTER_START_SEC)
            .remove(KEY_DATE_FILTER_END_SEC)
            .putBoolean(KEY_UNREVIEWED_ONLY_MODE, false)
            .putString(KEY_REVIEW_ORDER, GalleryReviewOrder.Random.storageValue)
            .remove(KEY_IMAGES_RELATIVE_PATH)
            .apply()
    }

    companion object {
        private const val PREFS_NAME = "gallery_cleaner"
        private const val KEY_SHOW_INTRO = "show_intro"
        private const val KEY_SHOW_MANAGE_MEDIA = "show_manage_media_v2"
        private const val KEY_DATE_FILTER_ENABLED = "date_filter_enabled"
        private const val KEY_DATE_FILTER_START_SEC = "date_filter_start_sec"
        private const val KEY_DATE_FILTER_END_SEC = "date_filter_end_sec"
        private const val KEY_UNREVIEWED_ONLY_MODE = "unreviewed_only_mode"
        private const val KEY_REVIEW_ORDER = "review_order"
        private const val KEY_IMAGES_RELATIVE_PATH = "images_relative_path"
        private const val KEY_REVIEWED_PHOTO_IDS = "reviewed_photo_ids"
    }
}
