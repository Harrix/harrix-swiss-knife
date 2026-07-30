package dev.harrix.hsk.ui.notes

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.InsertDriveFile
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material.icons.filled.Folder
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import dev.harrix.hsk.R
import dev.harrix.hsk.notes.NotesEntry
import dev.harrix.hsk.notes.NotesPathSegment

data class NotesTreeRow(
    val entry: NotesEntry,
    val depth: Int,
    /** Path from notes root through the parent folder (excludes the entry itself). */
    val parentPath: List<NotesPathSegment>,
)

@Composable
fun NotesTreeDrawerContent(
    rootLabel: String,
    rows: List<NotesTreeRow>,
    expandedFolderIds: Set<String>,
    selectedNoteDocumentId: String?,
    isLoadingRoot: Boolean,
    onToggleFolder: (NotesEntry.Folder) -> Unit,
    onOpenFolder: (NotesEntry.Folder, List<NotesPathSegment>) -> Unit,
    onOpenNote: (NotesEntry.Note, List<NotesPathSegment>) -> Unit,
    modifier: Modifier = Modifier,
) {
    ModalDrawerSheet(modifier = modifier) {
        Column(modifier = Modifier.fillMaxHeight()) {
            Text(
                text = rootLabel,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                modifier = Modifier.padding(horizontal = 20.dp, vertical = 16.dp),
            )
            HorizontalDivider()
            when {
                isLoadingRoot && rows.isEmpty() -> {
                    Column(
                        modifier =
                        Modifier
                            .fillMaxWidth()
                            .padding(24.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                    ) {
                        CircularProgressIndicator(modifier = Modifier.size(28.dp))
                    }
                }

                rows.isEmpty() -> {
                    Text(
                        text = stringResource(R.string.markdown_notes_folder_empty),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(20.dp),
                    )
                }

                else -> {
                    LazyColumn(modifier = Modifier.fillMaxSize()) {
                        items(
                            items = rows,
                            key = { row -> "${row.entry.documentId}-${row.depth}" },
                        ) { row ->
                            when (val entry = row.entry) {
                                is NotesEntry.Folder -> {
                                    NotesTreeFolderRow(
                                        folder = entry,
                                        depth = row.depth,
                                        expanded = entry.documentId in expandedFolderIds,
                                        onToggle = { onToggleFolder(entry) },
                                        onOpen = { onOpenFolder(entry, row.parentPath) },
                                    )
                                }

                                is NotesEntry.Note -> {
                                    NotesTreeNoteRow(
                                        note = entry,
                                        depth = row.depth,
                                        selected = entry.documentId == selectedNoteDocumentId,
                                        onOpen = { onOpenNote(entry, row.parentPath) },
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun NotesTreeFolderRow(
    folder: NotesEntry.Folder,
    depth: Int,
    expanded: Boolean,
    onToggle: () -> Unit,
    onOpen: () -> Unit,
) {
    Row(
        modifier =
        Modifier
            .fillMaxWidth()
            .height(40.dp)
            .clickable(onClick = onOpen)
            .padding(start = (8 + depth * 12).dp, end = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        IconButton(
            onClick = onToggle,
            modifier = Modifier.size(32.dp),
        ) {
            Icon(
                imageVector =
                if (expanded) {
                    Icons.Filled.ExpandMore
                } else {
                    Icons.AutoMirrored.Filled.KeyboardArrowRight
                },
                contentDescription = null,
                modifier = Modifier.size(18.dp),
            )
        }
        Icon(
            imageVector = Icons.Filled.Folder,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(18.dp),
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = folder.name,
            style = MaterialTheme.typography.bodyMedium,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            modifier = Modifier.weight(1f),
        )
    }
}

@Composable
private fun NotesTreeNoteRow(
    note: NotesEntry.Note,
    depth: Int,
    selected: Boolean,
    onOpen: () -> Unit,
) {
    Surface(
        selected = selected,
        onClick = onOpen,
        color =
        if (selected) {
            MaterialTheme.colorScheme.secondaryContainer
        } else {
            MaterialTheme.colorScheme.surface
        },
        modifier = Modifier.fillMaxWidth(),
    ) {
        Row(
            modifier =
            Modifier
                .fillMaxWidth()
                .height(40.dp)
                .padding(start = (40 + depth * 12).dp, end = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                imageVector = Icons.AutoMirrored.Filled.InsertDriveFile,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(18.dp),
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = note.displayLabel,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                modifier = Modifier.weight(1f),
            )
        }
    }
}

/** Flattens loaded children into visible rows according to [expandedFolderIds]. */
fun buildVisibleNotesTreeRows(
    root: NotesPathSegment,
    childrenByFolderId: Map<String, List<NotesEntry>>,
    expandedFolderIds: Set<String>,
): List<NotesTreeRow> {
    val result = ArrayList<NotesTreeRow>()

    fun walk(
        dir: NotesPathSegment,
        pathToDir: List<NotesPathSegment>,
        depth: Int,
    ) {
        val children = childrenByFolderId[dir.documentId].orEmpty()
        for (entry in children) {
            result +=
                NotesTreeRow(
                    entry = entry,
                    depth = depth,
                    parentPath = pathToDir,
                )
            if (entry is NotesEntry.Folder && entry.documentId in expandedFolderIds) {
                val folderSegment =
                    NotesPathSegment(
                        documentId = entry.documentId,
                        name = entry.name,
                        uri = entry.uri,
                    )
                walk(
                    dir = folderSegment,
                    pathToDir = pathToDir + folderSegment,
                    depth = depth + 1,
                )
            }
        }
    }

    walk(dir = root, pathToDir = listOf(root), depth = 0)
    return result
}
