package dev.harrix.hsk.notes

/**
 * Vertical density for folder/note rows in the Markdown Notes browser.
 *
 * [verticalPaddingDp] is applied top and bottom of each list row.
 * [listRowHeightDp] keeps folder and note rows the same height.
 */
enum class NotesListDensity(
    val verticalPaddingDp: Int,
    val iconSizeDp: Int,
    val mergedButtonHeightDp: Int,
) {
    Compact(
        verticalPaddingDp = 2,
        iconSizeDp = 18,
        mergedButtonHeightDp = 28,
    ),
    Comfortable(
        verticalPaddingDp = 4,
        iconSizeDp = 20,
        mergedButtonHeightDp = 32,
    ),
    Spacious(
        verticalPaddingDp = 10,
        iconSizeDp = 24,
        mergedButtonHeightDp = 40,
    ),
    ;

    /** Fixed list-row height so folders and notes align. */
    val listRowHeightDp: Int
        get() = mergedButtonHeightDp + verticalPaddingDp * 2

    companion object {
        val Default: NotesListDensity = Comfortable

        fun fromStorageKey(key: String?): NotesListDensity = entries.firstOrNull { it.name.equals(key, ignoreCase = true) } ?: Default
    }
}
