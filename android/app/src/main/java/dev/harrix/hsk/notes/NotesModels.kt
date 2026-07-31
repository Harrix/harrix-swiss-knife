package dev.harrix.hsk.notes

import android.net.Uri

/** A folder or note row in the Markdown Notes browser. */
sealed class NotesEntry {
    abstract val documentId: String
    abstract val name: String
    abstract val uri: Uri
    abstract val sortLabel: String

    data class Folder(
        override val documentId: String,
        override val name: String,
        override val uri: Uri,
        val hasMergedNote: Boolean,
        val mergedNoteDocumentId: String?,
        val mergedNoteUri: Uri?,
    ) : NotesEntry() {
        override val sortLabel: String get() = name
    }

    data class Note(
        override val documentId: String,
        override val name: String,
        override val uri: Uri,
        val displayLabel: String,
    ) : NotesEntry() {
        override val sortLabel: String get() = displayLabel
    }
}

/** One segment in the folder navigation / breadcrumb path. */
data class NotesPathSegment(
    val documentId: String,
    val name: String,
    val uri: Uri,
)

/** An open note tab in the viewer. */
data class OpenNoteTab(
    val documentId: String,
    val uri: Uri,
    val title: String,
    /** Original document file name (e.g. `Note.md`), used when titles come from file names. */
    val fileName: String = "",
    /** Path from notes root through parent folders (excludes the note itself). */
    val folderPath: List<NotesPathSegment>,
)
