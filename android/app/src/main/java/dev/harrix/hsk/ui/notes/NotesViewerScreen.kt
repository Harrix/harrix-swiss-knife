package dev.harrix.hsk.ui.notes

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.InsertDriveFile
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Folder
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Save
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TextField
import androidx.compose.material3.TextFieldDefaults
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import dev.harrix.hsk.R
import dev.harrix.hsk.notes.NotesEntry
import dev.harrix.hsk.notes.NotesPathSegment
import dev.harrix.hsk.notes.NotesTreeRepository
import dev.harrix.hsk.notes.NotesViewerPreferences
import dev.harrix.hsk.notes.OpenNoteTab
import dev.harrix.hsk.notes.notesFolderDisplayName
import dev.harrix.hsk.notes.takeNotesFolderPermission
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotesViewerScreen(
    onClose: () -> Unit,
    onOpenSettings: () -> Unit,
    modifier: Modifier = Modifier,
    settingsRevision: Int = 0,
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val preferences = remember { NotesViewerPreferences(context.applicationContext) }
    val repository = remember { NotesTreeRepository(context.applicationContext) }
    var notesTreeUri by remember { mutableStateOf(preferences.loadNotesTreeUri()) }
    var menuExpanded by remember { mutableStateOf(false) }
    var folderPath by remember { mutableStateOf<List<NotesPathSegment>>(emptyList()) }
    var entries by remember { mutableStateOf<List<NotesEntry>>(emptyList()) }
    var isLoading by remember { mutableStateOf(false) }
    var statusMessage by remember { mutableStateOf<String?>(null) }
    var openTabs by remember { mutableStateOf<List<OpenNoteTab>>(emptyList()) }
    var selectedTabDocumentId by remember { mutableStateOf<String?>(null) }
    var noteContent by remember { mutableStateOf<String?>(null) }
    var noteLoading by remember { mutableStateOf(false) }
    var isEditing by remember { mutableStateOf(false) }
    var draftText by remember { mutableStateOf("") }
    var lastSavedText by remember { mutableStateOf<String?>(null) }
    var isSaving by remember { mutableStateOf(false) }
    var saveFeedback by remember { mutableStateOf<String?>(null) }
    var autosaveJob by remember { mutableStateOf<Job?>(null) }
    var folderListRequestId by remember { mutableIntStateOf(0) }

    fun reloadPath() {
        notesTreeUri = preferences.loadNotesTreeUri()
    }

    fun resetEditorState() {
        isEditing = false
        draftText = ""
        lastSavedText = null
        saveFeedback = null
        autosaveJob?.cancel()
        autosaveJob = null
    }

    suspend fun saveNoteText(
        uri: Uri,
        text: String,
    ): Boolean {
        isSaving = true
        val result =
            withContext(Dispatchers.IO) {
                runCatching { repository.writeText(uri, text) }
            }
        isSaving = false
        return result
            .onSuccess {
                lastSavedText = text
                noteContent = text
                saveFeedback = context.getString(R.string.markdown_notes_saved)
                statusMessage = null
            }.onFailure { error ->
                statusMessage =
                    error.message ?: context.getString(R.string.markdown_notes_save_failed)
                saveFeedback = null
            }.isSuccess
    }

    fun persistCurrentDraft(after: (() -> Unit)? = null) {
        val tab = openTabs.firstOrNull { it.documentId == selectedTabDocumentId }
        if (tab == null || !isEditing) {
            after?.invoke()
            return
        }
        if (draftText == lastSavedText) {
            after?.invoke()
            return
        }
        scope.launch {
            saveNoteText(tab.uri, draftText)
            after?.invoke()
        }
    }

    fun scheduleAutosave() {
        val tab = openTabs.firstOrNull { it.documentId == selectedTabDocumentId } ?: return
        if (!isEditing || draftText == lastSavedText) {
            return
        }
        autosaveJob?.cancel()
        autosaveJob =
            scope.launch {
                delay(AutosaveDelayMs)
                if (isEditing && draftText != lastSavedText) {
                    saveNoteText(tab.uri, draftText)
                }
            }
    }

    fun prefetchChildFolders(
        treeUri: Uri,
        listed: List<NotesEntry>,
    ) {
        listed.filterIsInstance<NotesEntry.Folder>().forEach { folder ->
            scope.launch {
                repository.prefetchDirectory(treeUri, folder.documentId, folder.name)
            }
        }
    }

    fun openFolderList(path: List<NotesPathSegment>) {
        val tree = notesTreeUri ?: return
        val treeUri = Uri.parse(tree)
        val current = path.lastOrNull() ?: return
        persistCurrentDraft {
            statusMessage = null
            selectedTabDocumentId = null
            noteContent = null
            resetEditorState()

            val cached = repository.peekListing(treeUri, current.documentId)
            if (cached != null) {
                folderPath = path
                entries = cached
                isLoading = false
                prefetchChildFolders(treeUri, cached)
                return@persistCurrentDraft
            }

            folderListRequestId += 1
            val requestId = folderListRequestId
            isLoading = true
            scope.launch {
                val shallow =
                    runCatching {
                        repository.listChildrenShallow(treeUri, current.documentId, current.name)
                    }.getOrNull()
                if (requestId == folderListRequestId && shallow != null) {
                    folderPath = path
                    entries = shallow
                    isLoading = false
                }

                val result =
                    runCatching {
                        repository.listChildren(treeUri, current.documentId, current.name)
                    }
                if (requestId != folderListRequestId) {
                    return@launch
                }
                result
                    .onSuccess { listed ->
                        folderPath = path
                        entries = listed
                        prefetchChildFolders(treeUri, listed)
                    }.onFailure { error ->
                        if (shallow == null) {
                            statusMessage =
                                error.message
                                    ?: context.getString(R.string.markdown_notes_load_failed)
                            entries = emptyList()
                        }
                    }
                isLoading = false
            }
        }
    }

    fun ensureRootPath(): List<NotesPathSegment>? {
        val tree = notesTreeUri ?: return null
        val treeUri = Uri.parse(tree)
        return listOf(repository.rootSegment(treeUri))
    }

    fun openNote(
        note: NotesEntry.Note,
        pathForNote: List<NotesPathSegment>,
    ) {
        val existing = openTabs.firstOrNull { it.documentId == note.documentId }
        if (existing == null) {
            openTabs = openTabs +
                OpenNoteTab(
                    documentId = note.documentId,
                    uri = note.uri,
                    title = note.displayLabel,
                    folderPath = pathForNote,
                )
        }
        selectedTabDocumentId = note.documentId
    }

    fun openMergedNote(
        folder: NotesEntry.Folder,
        pathForFolder: List<NotesPathSegment>,
    ) {
        val uri = folder.mergedNoteUri ?: return
        val documentId = folder.mergedNoteDocumentId ?: return
        val title = "_${folder.name}.g"
        val existing = openTabs.firstOrNull { it.documentId == documentId }
        if (existing == null) {
            openTabs = openTabs +
                OpenNoteTab(
                    documentId = documentId,
                    uri = uri,
                    title = title,
                    folderPath = pathForFolder,
                )
        }
        selectedTabDocumentId = documentId
    }

    fun closeTab(documentId: String) {
        val closingSelected = selectedTabDocumentId == documentId
        if (closingSelected) {
            persistCurrentDraft {
                openTabs = openTabs.filterNot { it.documentId == documentId }
                selectedTabDocumentId = openTabs.lastOrNull()?.documentId
                if (selectedTabDocumentId == null) {
                    noteContent = null
                    resetEditorState()
                } else {
                    resetEditorState()
                }
            }
        } else {
            openTabs = openTabs.filterNot { it.documentId == documentId }
        }
    }

    fun navigateBack() {
        when {
            isEditing -> {
                persistCurrentDraft {
                    isEditing = false
                    draftText = noteContent.orEmpty()
                    lastSavedText = noteContent
                }
            }

            selectedTabDocumentId != null -> {
                selectedTabDocumentId = null
                noteContent = null
                resetEditorState()
            }

            folderPath.size > 1 -> {
                openFolderList(folderPath.dropLast(1))
            }
        }
    }

    fun selectTab(documentId: String) {
        if (documentId == selectedTabDocumentId) {
            return
        }
        persistCurrentDraft {
            selectedTabDocumentId = documentId
            resetEditorState()
        }
    }

    val folderPicker =
        rememberLauncherForActivityResult(
            ActivityResultContracts.OpenDocumentTree(),
        ) { uri: Uri? ->
            if (uri == null) {
                return@rememberLauncherForActivityResult
            }
            takeNotesFolderPermission(context, uri)
            preferences.saveNotesTreeUri(uri.toString())
            repository.clearCache()
            reloadPath()
        }

    LaunchedEffect(settingsRevision) {
        reloadPath()
    }

    LaunchedEffect(notesTreeUri) {
        repository.prepareForTree(notesTreeUri)
        val root = ensureRootPath()
        if (root != null) {
            openFolderList(root)
        } else {
            folderPath = emptyList()
            entries = emptyList()
            openTabs = emptyList()
            selectedTabDocumentId = null
            noteContent = null
            resetEditorState()
        }
    }

    val selectedTab = openTabs.firstOrNull { it.documentId == selectedTabDocumentId }

    LaunchedEffect(selectedTabDocumentId, selectedTab?.uri) {
        val tab = selectedTab
        if (tab == null) {
            noteContent = null
            resetEditorState()
            return@LaunchedEffect
        }
        noteLoading = true
        statusMessage = null
        saveFeedback = null
        val loaded =
            withContext(Dispatchers.IO) {
                runCatching { repository.readText(tab.uri) }
                    .onFailure { error ->
                        statusMessage =
                            error.message ?: context.getString(R.string.markdown_notes_load_failed)
                    }.getOrNull()
            }
        noteContent = loaded
        draftText = loaded.orEmpty()
        lastSavedText = loaded
        isEditing = false
        noteLoading = false
    }

    LaunchedEffect(saveFeedback) {
        if (saveFeedback != null) {
            delay(SaveFeedbackVisibleMs)
            saveFeedback = null
        }
    }

    val canGoBack = isEditing || selectedTabDocumentId != null || folderPath.size > 1

    Scaffold(
        modifier = modifier,
        containerColor = MaterialTheme.colorScheme.background,
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.markdown_notes_title)) },
                navigationIcon = {
                    IconButton(onClick = onClose) {
                        Icon(
                            imageVector = Icons.Filled.Close,
                            contentDescription = stringResource(R.string.markdown_notes_close),
                        )
                    }
                },
                actions = {
                    if (selectedTab != null && !noteLoading && noteContent != null) {
                        if (isEditing) {
                            IconButton(
                                onClick = { persistCurrentDraft() },
                                enabled = !isSaving,
                            ) {
                                Icon(
                                    imageVector = Icons.Filled.Save,
                                    contentDescription = stringResource(R.string.markdown_notes_save),
                                )
                            }
                        } else {
                            IconButton(
                                onClick = {
                                    isEditing = true
                                    draftText = noteContent.orEmpty()
                                    lastSavedText = noteContent
                                    saveFeedback = null
                                },
                            ) {
                                Icon(
                                    imageVector = Icons.Filled.Edit,
                                    contentDescription = stringResource(R.string.markdown_notes_edit),
                                )
                            }
                        }
                    }
                    Box {
                        IconButton(onClick = { menuExpanded = true }) {
                            Icon(
                                imageVector = Icons.Filled.MoreVert,
                                contentDescription = stringResource(R.string.markdown_notes_menu),
                            )
                        }
                        DropdownMenu(
                            expanded = menuExpanded,
                            onDismissRequest = { menuExpanded = false },
                        ) {
                            DropdownMenuItem(
                                text = {
                                    Text(stringResource(R.string.markdown_notes_settings))
                                },
                                onClick = {
                                    menuExpanded = false
                                    onOpenSettings()
                                },
                            )
                        }
                    }
                },
                colors =
                TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.background,
                    scrolledContainerColor = MaterialTheme.colorScheme.background,
                ),
            )
        },
    ) { innerPadding ->
        Column(
            modifier =
            Modifier
                .padding(innerPadding)
                .fillMaxSize(),
        ) {
            if (notesTreeUri.isNullOrBlank()) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center,
                ) {
                    NotesPathWelcomeContent(
                        onChooseFolder = { folderPicker.launch(null) },
                        modifier = Modifier.padding(24.dp),
                    )
                }
            } else {
                NotesChromeBar(
                    canGoBack = canGoBack,
                    onBack = { navigateBack() },
                    openTabs = openTabs,
                    selectedTabDocumentId = selectedTabDocumentId,
                    onSelectTab = { selectTab(it) },
                    onCloseTab = { closeTab(it) },
                )
                NotesBreadcrumbs(
                    segments =
                    if (selectedTab != null) {
                        selectedTab.folderPath +
                            NotesPathSegment(
                                documentId = selectedTab.documentId,
                                name = selectedTab.title,
                                uri = selectedTab.uri,
                            )
                    } else {
                        folderPath
                    },
                    lastIsNote = selectedTab != null,
                    onSegmentClick = { index ->
                        val path =
                            if (selectedTab != null) {
                                selectedTab.folderPath
                            } else {
                                folderPath
                            }
                        val targetIndex = index.coerceAtMost(path.lastIndex)
                        if (targetIndex >= 0) {
                            openFolderList(path.take(targetIndex + 1))
                        }
                    },
                )
                if (isEditing && (isSaving || saveFeedback != null)) {
                    Text(
                        text =
                        if (isSaving) {
                            stringResource(R.string.markdown_notes_save)
                        } else {
                            saveFeedback.orEmpty()
                        },
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 2.dp),
                    )
                }
                HorizontalDivider()
                Box(modifier = Modifier.fillMaxSize()) {
                    when {
                        selectedTab != null -> {
                            NotesPlainTextPane(
                                isLoading = noteLoading,
                                content = noteContent,
                                draftText = draftText,
                                isEditing = isEditing,
                                errorMessage = statusMessage,
                                onDraftChange = { value ->
                                    draftText = value
                                    scheduleAutosave()
                                },
                            )
                        }

                        isLoading -> {
                            CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
                        }

                        else -> {
                            NotesFolderList(
                                entries = entries,
                                statusMessage = statusMessage,
                                onOpenFolder = { folder ->
                                    openFolderList(
                                        folderPath +
                                            NotesPathSegment(
                                                documentId = folder.documentId,
                                                name = folder.name,
                                                uri = folder.uri,
                                            ),
                                    )
                                },
                                onOpenNote = { note ->
                                    openNote(note, folderPath)
                                },
                                onShowMergedNote = { folder ->
                                    openMergedNote(folder, folderPath)
                                },
                            )
                        }
                    }
                }
            }
        }
    }
}

private const val AutosaveDelayMs = 800L
private const val SaveFeedbackVisibleMs = 1500L

@Composable
private fun NotesChromeBar(
    canGoBack: Boolean,
    onBack: () -> Unit,
    openTabs: List<OpenNoteTab>,
    selectedTabDocumentId: String?,
    onSelectTab: (String) -> Unit,
    onCloseTab: (String) -> Unit,
) {
    Row(
        modifier =
        Modifier
            .fillMaxWidth()
            .padding(start = 4.dp, end = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        IconButton(
            onClick = onBack,
            enabled = canGoBack,
        ) {
            Icon(
                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                contentDescription = stringResource(R.string.markdown_notes_back),
            )
        }
        if (openTabs.isNotEmpty()) {
            Row(
                modifier =
                Modifier
                    .weight(1f)
                    .horizontalScroll(rememberScrollState()),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                openTabs.forEach { tab ->
                    val selected = tab.documentId == selectedTabDocumentId
                    Surface(
                        onClick = { onSelectTab(tab.documentId) },
                        shape = MaterialTheme.shapes.small,
                        color =
                        if (selected) {
                            MaterialTheme.colorScheme.secondaryContainer
                        } else {
                            MaterialTheme.colorScheme.surface
                        },
                        tonalElevation = if (selected) 2.dp else 0.dp,
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.padding(start = 10.dp, end = 2.dp),
                        ) {
                            Text(
                                text = tab.title,
                                style = MaterialTheme.typography.labelLarge,
                                fontWeight =
                                if (selected) {
                                    FontWeight.Bold
                                } else {
                                    FontWeight.Normal
                                },
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis,
                                modifier = Modifier.width(88.dp),
                            )
                            IconButton(
                                onClick = { onCloseTab(tab.documentId) },
                                modifier = Modifier.size(28.dp),
                            ) {
                                Icon(
                                    imageVector = Icons.Filled.Close,
                                    contentDescription =
                                    stringResource(R.string.markdown_notes_close_tab),
                                    modifier = Modifier.size(14.dp),
                                )
                            }
                        }
                    }
                }
            }
        } else {
            Spacer(modifier = Modifier.weight(1f))
        }
    }
}

@Composable
private fun NotesBreadcrumbs(
    segments: List<NotesPathSegment>,
    lastIsNote: Boolean,
    onSegmentClick: (Int) -> Unit,
) {
    if (segments.isEmpty()) {
        return
    }
    Row(
        modifier =
        Modifier
            .fillMaxWidth()
            .horizontalScroll(rememberScrollState())
            .padding(horizontal = 12.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        segments.forEachIndexed { index, segment ->
            if (index > 0) {
                Text(
                    text = " / ",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            val isLast = index == segments.lastIndex
            val clickable = !(isLast && lastIsNote)
            Text(
                text = segment.name,
                style = MaterialTheme.typography.labelLarge,
                color =
                if (clickable) {
                    MaterialTheme.colorScheme.primary
                } else {
                    MaterialTheme.colorScheme.onSurface
                },
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                modifier =
                if (clickable) {
                    Modifier.clickable { onSegmentClick(index) }
                } else {
                    Modifier
                },
            )
        }
    }
}

@Composable
private fun NotesFolderList(
    entries: List<NotesEntry>,
    statusMessage: String?,
    onOpenFolder: (NotesEntry.Folder) -> Unit,
    onOpenNote: (NotesEntry.Note) -> Unit,
    onShowMergedNote: (NotesEntry.Folder) -> Unit,
) {
    when {
        statusMessage != null && entries.isEmpty() -> {
            Text(
                text = statusMessage,
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier.padding(24.dp),
            )
        }

        entries.isEmpty() -> {
            Text(
                text = stringResource(R.string.markdown_notes_folder_empty),
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(24.dp),
            )
        }

        else -> {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(vertical = 4.dp),
            ) {
                items(entries, key = { it.documentId }) { entry ->
                    when (entry) {
                        is NotesEntry.Folder -> {
                            NotesFolderRow(
                                folder = entry,
                                onOpen = { onOpenFolder(entry) },
                                onShowMergedNote = { onShowMergedNote(entry) },
                            )
                        }

                        is NotesEntry.Note -> {
                            NotesNoteRow(
                                note = entry,
                                onOpen = { onOpenNote(entry) },
                            )
                        }
                    }
                    HorizontalDivider()
                }
            }
        }
    }
}

@Composable
private fun NotesFolderRow(
    folder: NotesEntry.Folder,
    onOpen: () -> Unit,
    onShowMergedNote: () -> Unit,
) {
    Row(
        modifier =
        Modifier
            .fillMaxWidth()
            .clickable(onClick = onOpen)
            .padding(horizontal = 12.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = Icons.Filled.Folder,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
        )
        Spacer(modifier = Modifier.width(12.dp))
        Text(
            text = folder.name,
            style = MaterialTheme.typography.bodyLarge,
            modifier = Modifier.weight(1f),
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
        )
        if (folder.hasMergedNote) {
            TextButton(onClick = onShowMergedNote) {
                Text(stringResource(R.string.markdown_notes_show_merged))
            }
        }
    }
}

@Composable
private fun NotesNoteRow(
    note: NotesEntry.Note,
    onOpen: () -> Unit,
) {
    Row(
        modifier =
        Modifier
            .fillMaxWidth()
            .clickable(onClick = onOpen)
            .padding(horizontal = 12.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = Icons.AutoMirrored.Filled.InsertDriveFile,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Spacer(modifier = Modifier.width(12.dp))
        Text(
            text = note.displayLabel,
            style = MaterialTheme.typography.bodyLarge,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
        )
    }
}

@Composable
private fun NotesPlainTextPane(
    isLoading: Boolean,
    content: String?,
    draftText: String,
    isEditing: Boolean,
    errorMessage: String?,
    onDraftChange: (String) -> Unit,
) {
    when {
        isLoading -> {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }

        errorMessage != null && content == null -> {
            Text(
                text = errorMessage,
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier.padding(24.dp),
            )
        }

        isEditing -> {
            TextField(
                value = draftText,
                onValueChange = onDraftChange,
                modifier = Modifier.fillMaxSize(),
                textStyle = MaterialTheme.typography.bodyMedium,
                colors =
                TextFieldDefaults.colors(
                    focusedContainerColor = MaterialTheme.colorScheme.surface,
                    unfocusedContainerColor = MaterialTheme.colorScheme.surface,
                    disabledContainerColor = MaterialTheme.colorScheme.surface,
                    focusedIndicatorColor = MaterialTheme.colorScheme.surface,
                    unfocusedIndicatorColor = MaterialTheme.colorScheme.surface,
                ),
            )
        }

        else -> {
            Surface(
                modifier = Modifier.fillMaxSize(),
                color = MaterialTheme.colorScheme.surface,
            ) {
                Text(
                    text = content.orEmpty(),
                    style = MaterialTheme.typography.bodyMedium,
                    modifier =
                    Modifier
                        .fillMaxSize()
                        .verticalScroll(rememberScrollState())
                        .padding(16.dp),
                )
            }
        }
    }
}

@Composable
private fun NotesPathWelcomeContent(
    onChooseFolder: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(
            text = stringResource(R.string.markdown_notes_welcome_title),
            style = MaterialTheme.typography.titleLarge,
            textAlign = TextAlign.Center,
        )
        Text(
            text = stringResource(R.string.markdown_notes_welcome_message),
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
        )
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = onChooseFolder) {
            Text(stringResource(R.string.markdown_notes_choose_folder))
        }
    }
}

/** Shared notes-folder picker + path summary for settings. */
@Composable
fun NotesFolderPathControls(
    treeUri: String?,
    onTreeUriChange: (String?) -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val preferences = remember { NotesViewerPreferences(context.applicationContext) }
    val folderPicker =
        rememberLauncherForActivityResult(
            ActivityResultContracts.OpenDocumentTree(),
        ) { uri: Uri? ->
            if (uri == null) {
                return@rememberLauncherForActivityResult
            }
            takeNotesFolderPermission(context, uri)
            val value = uri.toString()
            preferences.saveNotesTreeUri(value)
            onTreeUriChange(value)
        }

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(
            text = stringResource(R.string.settings_markdown_notes_path),
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(
            text =
            if (treeUri.isNullOrBlank()) {
                stringResource(R.string.settings_markdown_notes_path_none)
            } else {
                notesFolderDisplayName(context, treeUri)
            },
            style = MaterialTheme.typography.bodyMedium,
        )
        Button(
            onClick = { folderPicker.launch(null) },
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.markdown_notes_choose_folder))
        }
        OutlinedButton(
            onClick = {
                preferences.clearNotesTreeUri()
                onTreeUriChange(null)
            },
            enabled = !treeUri.isNullOrBlank(),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.settings_markdown_notes_path_clear))
        }
    }
}
