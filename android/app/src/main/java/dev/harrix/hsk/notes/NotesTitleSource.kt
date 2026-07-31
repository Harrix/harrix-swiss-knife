package dev.harrix.hsk.notes

/**
 * Where note titles in lists, tree, and tabs come from.
 */
enum class NotesTitleSource {
    /** YAML `title:` or first `#` heading, falling back to file stem. */
    Content,

    /** File name without `.md` / `.g.md`. */
    FileName,
    ;

    companion object {
        val Default: NotesTitleSource = Content

        fun fromStorageKey(key: String?): NotesTitleSource = entries.firstOrNull { it.name.equals(key, ignoreCase = true) } ?: Default
    }
}
