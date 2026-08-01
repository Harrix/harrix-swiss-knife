package dev.harrix.hsk.gallery

/**
 * Order used when picking the next photo to review in Gallery Cleaner.
 */
enum class GalleryReviewOrder(
    val storageValue: String,
) {
    /** Default: any remaining photo at random. */
    Random("random"),

    /** Oldest [CameraPhoto.dateTakenEpochMs] first. */
    OldestFirst("oldest_first"),

    /** Newest [CameraPhoto.dateTakenEpochMs] first. */
    NewestFirst("newest_first"),
    ;

    companion object {
        fun fromStorage(value: String?): GalleryReviewOrder = entries.firstOrNull { it.storageValue == value } ?: Random
    }
}
