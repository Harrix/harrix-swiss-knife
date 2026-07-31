package dev.harrix.hsk.notes

/**
 * How folders and notes are shown in the Markdown Notes browser.
 */
enum class NotesBrowseLayout {
    List,
    Icons,
    ;

    companion object {
        val Default: NotesBrowseLayout = List

        fun fromStorageKey(key: String?): NotesBrowseLayout = entries.firstOrNull { it.name.equals(key, ignoreCase = true) } ?: Default
    }
}
