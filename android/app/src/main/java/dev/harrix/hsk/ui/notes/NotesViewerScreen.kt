package dev.harrix.hsk.ui.notes

import android.net.Uri
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.InsertDriveFile
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Folder
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Save
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.TextFieldDefaults
import androidx.compose.material3.rememberDrawerState
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
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Constraints
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import dev.harrix.hsk.R
import dev.harrix.hsk.notes.NotesBrowseLayout
import dev.harrix.hsk.notes.NotesEntry
import dev.harrix.hsk.notes.NotesListDensity
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
import kotlin.math.roundToInt

private val NotesIconsGridMinCellWidth = 96.dp
private val NotesIconsLabelMinFontSize = 9.sp
private val NotesIconsLabelMaxFontSize = 13.sp
private const val NotesIconsLabelMaxLines = 3
private const val NotesIconsLabelFontStepSp = 0.5f

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
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    var notesTreeUri by remember { mutableStateOf(preferences.loadNotesTreeUri()) }
    var menuExpanded by remember { mutableStateOf(false) }
    var folderPath by remember { mutableStateOf<List<NotesPathSegment>>(emptyList()) }
    var entries by remember { mutableStateOf<List<NotesEntry>>(emptyList()) }
    var isLoading by remember { mutableStateOf(false) }
    var statusMessage by remember { mutableStateOf<String?>(null) }
    var openTabs by remember { mutableStateOf<List<OpenNoteTab>>(emptyList()) }
    var selectedTabDocumentId by remember { mutableStateOf<String?>(null) }
    var sessionRestoredForTree by remember { mutableStateOf<String?>(null) }
    var noteContent by remember { mutableStateOf<String?>(null) }
    var noteLoading by remember { mutableStateOf(false) }
    var isEditing by remember { mutableStateOf(false) }
    var draftText by remember { mutableStateOf("") }
    var lastSavedText by remember { mutableStateOf<String?>(null) }
    var isSaving by remember { mutableStateOf(false) }
    var saveFeedback by remember { mutableStateOf<String?>(null) }
    var autosaveJob by remember { mutableStateOf<Job?>(null) }
    var folderListRequestId by remember { mutableIntStateOf(0) }
    var listDensity by remember { mutableStateOf(preferences.loadListDensity()) }
    var browseLayout by remember { mutableStateOf(preferences.loadBrowseLayout()) }
    var treeRoot by remember { mutableStateOf<NotesPathSegment?>(null) }
    var treeChildrenByFolderId by remember {
        mutableStateOf<Map<String, List<NotesEntry>>>(emptyMap())
    }
    var treeExpandedFolderIds by remember { mutableStateOf<Set<String>>(emptySet()) }
    var treeLoadingRoot by remember { mutableStateOf(false) }

    fun reloadPath() {
        notesTreeUri = preferences.loadNotesTreeUri()
        listDensity = preferences.loadListDensity()
        browseLayout = preferences.loadBrowseLayout()
    }

    fun clearTreeState() {
        treeRoot = null
        treeChildrenByFolderId = emptyMap()
        treeExpandedFolderIds = emptySet()
        treeLoadingRoot = false
    }

    fun putTreeChildren(
        dirDocumentId: String,
        children: List<NotesEntry>,
    ) {
        treeChildrenByFolderId = treeChildrenByFolderId + (dirDocumentId to children)
    }

    fun loadTreeFolder(
        treeUri: Uri,
        dir: NotesPathSegment,
        onLoaded: ((List<NotesEntry>) -> Unit)? = null,
    ) {
        val cached = repository.peekListing(treeUri, dir.documentId)
        if (cached != null) {
            val withTitles = repository.withCachedContentTitles(cached)
            putTreeChildren(dir.documentId, withTitles)
            onLoaded?.invoke(withTitles)
            scope.launch {
                val updates = repository.resolveMissingContentTitles(
                    withTitles.filterIsInstance<NotesEntry.Note>(),
                )
                if (updates.isNotEmpty()) {
                    putTreeChildren(
                        dir.documentId,
                        repository.withUpdatedNoteLabels(
                            treeChildrenByFolderId[dir.documentId].orEmpty(),
                            updates,
                        ),
                    )
                }
            }
            return
        }
        scope.launch {
            val listed =
                runCatching {
                    repository.listChildren(treeUri, dir.documentId, dir.name)
                }.getOrNull()
            if (listed == null) {
                onLoaded?.invoke(emptyList())
                return@launch
            }
            val withTitles = repository.withCachedContentTitles(listed)
            putTreeChildren(dir.documentId, withTitles)
            onLoaded?.invoke(withTitles)
            val updates =
                repository.resolveMissingContentTitles(
                    withTitles.filterIsInstance<NotesEntry.Note>(),
                )
            if (updates.isNotEmpty()) {
                putTreeChildren(
                    dir.documentId,
                    repository.withUpdatedNoteLabels(
                        treeChildrenByFolderId[dir.documentId].orEmpty(),
                        updates,
                    ),
                )
            }
        }
    }

    fun ensureTreeRootLoaded() {
        val tree = notesTreeUri ?: run {
            clearTreeState()
            return
        }
        val treeUri = Uri.parse(tree)
        val root = repository.rootSegment(treeUri)
        treeRoot = root
        if (treeChildrenByFolderId.containsKey(root.documentId)) {
            return
        }
        treeLoadingRoot = true
        loadTreeFolder(treeUri, root) {
            treeLoadingRoot = false
        }
    }

    fun expandPathToNote(tab: OpenNoteTab) {
        val tree = notesTreeUri ?: return
        val treeUri = Uri.parse(tree)
        val root = treeRoot ?: repository.rootSegment(treeUri).also { treeRoot = it }
        treeExpandedFolderIds = tab.folderPath.map { it.documentId }.toSet()
        val segmentsToLoad =
            if (tab.folderPath.isEmpty()) {
                listOf(root)
            } else {
                tab.folderPath
            }
        segmentsToLoad.forEach { segment ->
            loadTreeFolder(treeUri, segment)
        }
        // Also ensure root is loaded when path starts deeper.
        if (tab.folderPath.isNotEmpty()) {
            loadTreeFolder(treeUri, root)
        }
    }

    fun toggleTreeFolder(folder: NotesEntry.Folder) {
        val tree = notesTreeUri ?: return
        val treeUri = Uri.parse(tree)
        if (folder.documentId in treeExpandedFolderIds) {
            treeExpandedFolderIds = treeExpandedFolderIds - folder.documentId
            return
        }
        treeExpandedFolderIds = treeExpandedFolderIds + folder.documentId
        loadTreeFolder(
            treeUri,
            NotesPathSegment(
                documentId = folder.documentId,
                name = folder.name,
                uri = folder.uri,
            ),
        )
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
                val tab = openTabs.firstOrNull { it.documentId == selectedTabDocumentId }
                if (tab != null) {
                    val contentTitle = repository.rememberTitleFromContent(tab.documentId, text)
                    val fileStem =
                        entries
                            .filterIsInstance<NotesEntry.Note>()
                            .firstOrNull { note -> note.documentId == tab.documentId }
                            ?.let { note -> NotesTreeRepository.noteDisplayLabel(note.name) }
                    val label = contentTitle ?: fileStem ?: tab.title
                    openTabs =
                        openTabs.map { openTab ->
                            if (openTab.documentId == tab.documentId) {
                                openTab.copy(title = label)
                            } else {
                                openTab
                            }
                        }
                    val labels = mapOf(tab.documentId to label)
                    entries = repository.withUpdatedNoteLabels(entries, labels)
                    notesTreeUri?.let { tree ->
                        folderPath.lastOrNull()?.let { dir ->
                            repository.patchListingNoteLabels(
                                Uri.parse(tree),
                                dir.documentId,
                                labels,
                            )
                        }
                    }
                }
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

    fun enrichNoteTitles(
        treeUri: Uri,
        dirDocumentId: String,
        listed: List<NotesEntry>,
        requestId: Int,
    ) {
        val notes = listed.filterIsInstance<NotesEntry.Note>()
        if (notes.isEmpty()) {
            return
        }
        scope.launch {
            val updates = repository.resolveMissingContentTitles(notes)
            if (updates.isEmpty() || requestId != folderListRequestId) {
                return@launch
            }
            if (folderPath.lastOrNull()?.documentId != dirDocumentId) {
                repository.patchListingNoteLabels(treeUri, dirDocumentId, updates)
                return@launch
            }
            entries = repository.withUpdatedNoteLabels(entries, updates)
            putTreeChildren(
                dirDocumentId,
                repository.withUpdatedNoteLabels(
                    treeChildrenByFolderId[dirDocumentId] ?: entries,
                    updates,
                ),
            )
            repository.patchListingNoteLabels(treeUri, dirDocumentId, updates)
            openTabs =
                openTabs.map { tab ->
                    val label = updates[tab.documentId]
                    if (label != null) {
                        tab.copy(title = label)
                    } else {
                        tab
                    }
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

            folderListRequestId += 1
            val requestId = folderListRequestId

            val cached = repository.peekListing(treeUri, current.documentId)
            if (cached != null) {
                val withTitles = repository.withCachedContentTitles(cached)
                folderPath = path
                entries = withTitles
                putTreeChildren(current.documentId, withTitles)
                isLoading = false
                prefetchChildFolders(treeUri, withTitles)
                enrichNoteTitles(treeUri, current.documentId, withTitles, requestId)
                return@persistCurrentDraft
            }

            isLoading = true
            scope.launch {
                val shallow =
                    runCatching {
                        repository.listChildrenShallow(treeUri, current.documentId, current.name)
                    }.getOrNull()
                if (requestId == folderListRequestId && shallow != null) {
                    folderPath = path
                    entries = repository.withCachedContentTitles(shallow)
                    putTreeChildren(current.documentId, entries)
                    isLoading = false
                    enrichNoteTitles(treeUri, current.documentId, entries, requestId)
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
                        val withTitles = repository.withCachedContentTitles(listed)
                        folderPath = path
                        entries = withTitles
                        putTreeChildren(current.documentId, withTitles)
                        prefetchChildFolders(treeUri, withTitles)
                        enrichNoteTitles(treeUri, current.documentId, withTitles, requestId)
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
        if (selectedTabDocumentId != note.documentId) {
            noteLoading = true
            noteContent = null
            resetEditorState()
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
        if (selectedTabDocumentId != documentId) {
            noteLoading = true
            noteContent = null
            resetEditorState()
        }
        selectedTabDocumentId = documentId
    }

    fun closeTab(documentId: String) {
        val closingSelected = selectedTabDocumentId == documentId
        if (closingSelected) {
            persistCurrentDraft {
                openTabs = openTabs.filterNot { it.documentId == documentId }
                val nextId = openTabs.lastOrNull()?.documentId
                selectedTabDocumentId = nextId
                if (nextId == null) {
                    noteContent = null
                    noteLoading = false
                    resetEditorState()
                } else {
                    noteLoading = true
                    noteContent = null
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
                noteLoading = false
                resetEditorState()
            }

            folderPath.size > 1 -> {
                openFolderList(folderPath.dropLast(1))
            }

            else -> {
                onClose()
            }
        }
    }

    fun selectTab(documentId: String) {
        if (documentId == selectedTabDocumentId) {
            return
        }
        persistCurrentDraft {
            selectedTabDocumentId = documentId
            noteLoading = true
            noteContent = null
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
        clearTreeState()
        repository.prepareForTree(notesTreeUri)
        val root = ensureRootPath()
        if (root != null && notesTreeUri != null) {
            if (sessionRestoredForTree != notesTreeUri) {
                val session = preferences.loadOpenTabsSession(notesTreeUri)
                openTabs = session.tabs
                selectedTabDocumentId = session.selectedDocumentId
                if (session.selectedDocumentId != null) {
                    noteLoading = true
                    noteContent = null
                    resetEditorState()
                } else {
                    noteContent = null
                    noteLoading = false
                    resetEditorState()
                }
                sessionRestoredForTree = notesTreeUri
            }
            openFolderList(root)
            ensureTreeRootLoaded()
        } else {
            sessionRestoredForTree = null
            folderPath = emptyList()
            entries = emptyList()
            openTabs = emptyList()
            selectedTabDocumentId = null
            noteContent = null
            noteLoading = false
            resetEditorState()
            preferences.clearOpenTabsSession()
        }
    }

    LaunchedEffect(openTabs, selectedTabDocumentId, notesTreeUri, sessionRestoredForTree) {
        val tree = notesTreeUri
        if (tree == null) {
            return@LaunchedEffect
        }
        if (sessionRestoredForTree != tree) {
            return@LaunchedEffect
        }
        preferences.saveOpenTabsSession(
            treeUri = tree,
            tabs = openTabs,
            selectedDocumentId = selectedTabDocumentId,
        )
    }

    val selectedTab = openTabs.firstOrNull { it.documentId == selectedTabDocumentId }

    LaunchedEffect(selectedTabDocumentId, selectedTab?.folderPath) {
        val tab = selectedTab
        if (tab == null) {
            treeExpandedFolderIds = emptySet()
            ensureTreeRootLoaded()
        } else {
            expandPathToNote(tab)
        }
    }

    LaunchedEffect(drawerState.isOpen) {
        if (drawerState.isOpen) {
            ensureTreeRootLoaded()
        }
    }

    LaunchedEffect(selectedTabDocumentId, selectedTab?.uri) {
        val tab = selectedTab
        if (tab == null) {
            noteContent = null
            noteLoading = false
            resetEditorState()
            return@LaunchedEffect
        }
        noteLoading = true
        statusMessage = null
        saveFeedback = null
        noteContent = null
        val result =
            withContext(Dispatchers.IO) {
                runCatching { repository.readText(tab.uri) }
            }
        result
            .onSuccess { loaded ->
                noteContent = loaded
                draftText = loaded
                lastSavedText = loaded
                isEditing = false
                statusMessage = null
            }.onFailure { error ->
                noteContent = null
                draftText = ""
                lastSavedText = null
                isEditing = false
                statusMessage =
                    error.message ?: context.getString(R.string.markdown_notes_load_failed)
            }
        noteLoading = false
    }

    LaunchedEffect(saveFeedback) {
        if (saveFeedback != null) {
            delay(SaveFeedbackVisibleMs)
            saveFeedback = null
        }
    }

    BackHandler {
        if (drawerState.isOpen) {
            scope.launch { drawerState.close() }
        } else {
            navigateBack()
        }
    }

    val treeRows =
        remember(treeRoot, treeChildrenByFolderId, treeExpandedFolderIds) {
            val root = treeRoot ?: return@remember emptyList()
            buildVisibleNotesTreeRows(
                root = root,
                childrenByFolderId = treeChildrenByFolderId,
                expandedFolderIds = treeExpandedFolderIds,
            )
        }
    val drawerTitle =
        treeRoot?.name
            ?: notesTreeUri?.let { notesFolderDisplayName(context, it) }
            ?: stringResource(R.string.markdown_notes_title)

    ModalNavigationDrawer(
        drawerState = drawerState,
        modifier = modifier,
        gesturesEnabled = !notesTreeUri.isNullOrBlank(),
        drawerContent = {
            NotesTreeDrawerContent(
                rootLabel = drawerTitle,
                rows = treeRows,
                expandedFolderIds = treeExpandedFolderIds,
                selectedNoteDocumentId = selectedTabDocumentId,
                isLoadingRoot = treeLoadingRoot,
                onToggleFolder = { toggleTreeFolder(it) },
                onOpenFolder = { folder, parentPath ->
                    scope.launch { drawerState.close() }
                    openFolderList(
                        parentPath +
                            NotesPathSegment(
                                documentId = folder.documentId,
                                name = folder.name,
                                uri = folder.uri,
                            ),
                    )
                },
                onOpenNote = { note, parentPath ->
                    scope.launch { drawerState.close() }
                    openNote(note, parentPath)
                },
            )
        },
    ) {
        Scaffold(
            modifier = Modifier.fillMaxSize(),
            containerColor = MaterialTheme.colorScheme.background,
            contentWindowInsets = WindowInsets.statusBars,
        ) { innerPadding ->
            Column(
                modifier =
                Modifier
                    .padding(innerPadding)
                    .fillMaxSize(),
            ) {
                NotesTopChrome(
                    onOpenDrawer = {
                        scope.launch { drawerState.open() }
                    },
                    openTabs = openTabs,
                    selectedTabDocumentId = selectedTabDocumentId,
                    onSelectTab = { selectTab(it) },
                    onCloseTab = { closeTab(it) },
                    showEditActions = selectedTab != null && !noteLoading && noteContent != null,
                    isEditing = isEditing,
                    isSaving = isSaving,
                    onSave = { persistCurrentDraft() },
                    onEdit = {
                        isEditing = true
                        draftText = noteContent.orEmpty()
                        lastSavedText = noteContent
                        saveFeedback = null
                    },
                    menuExpanded = menuExpanded,
                    onMenuExpandedChange = { menuExpanded = it },
                    onOpenSettings = onOpenSettings,
                )
                if (notesTreeUri.isNullOrBlank()) {
                    Box(
                        modifier = Modifier.weight(1f).fillMaxWidth(),
                        contentAlignment = Alignment.Center,
                    ) {
                        NotesPathWelcomeContent(
                            onChooseFolder = { folderPicker.launch(null) },
                            modifier = Modifier.padding(24.dp),
                        )
                    }
                } else {
                    NotesNavigationRow(
                        onBack = { navigateBack() },
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
                    Box(
                        modifier =
                        Modifier
                            .weight(1f)
                            .fillMaxWidth()
                            .background(MaterialTheme.colorScheme.surface),
                    ) {
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
                                    density = listDensity,
                                    layout = browseLayout,
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
}

private const val AutosaveDelayMs = 800L
private const val SaveFeedbackVisibleMs = 1500L
private val NotesTabMaxWidth = 140.dp

@Composable
private fun NotesTopChrome(
    onOpenDrawer: () -> Unit,
    openTabs: List<OpenNoteTab>,
    selectedTabDocumentId: String?,
    onSelectTab: (String) -> Unit,
    onCloseTab: (String) -> Unit,
    showEditActions: Boolean,
    isEditing: Boolean,
    isSaving: Boolean,
    onSave: () -> Unit,
    onEdit: () -> Unit,
    menuExpanded: Boolean,
    onMenuExpandedChange: (Boolean) -> Unit,
    onOpenSettings: () -> Unit,
) {
    Row(
        modifier =
        Modifier
            .fillMaxWidth()
            .padding(start = 4.dp, end = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        IconButton(onClick = onOpenDrawer) {
            Icon(
                imageVector = Icons.Filled.Menu,
                contentDescription = stringResource(R.string.nav_open),
            )
        }
        if (openTabs.isNotEmpty()) {
            val tabsScrollState = rememberScrollState()
            LaunchedEffect(openTabs.size, selectedTabDocumentId, tabsScrollState.maxValue) {
                if (selectedTabDocumentId == openTabs.lastOrNull()?.documentId) {
                    tabsScrollState.animateScrollTo(tabsScrollState.maxValue)
                }
            }
            Row(
                modifier =
                Modifier
                    .weight(1f)
                    .horizontalScroll(tabsScrollState),
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
                                modifier = Modifier.widthIn(max = NotesTabMaxWidth),
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
            Text(
                text = stringResource(R.string.markdown_notes_title),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                modifier = Modifier.weight(1f),
            )
        }
        if (showEditActions) {
            if (isEditing) {
                IconButton(
                    onClick = onSave,
                    enabled = !isSaving,
                ) {
                    Icon(
                        imageVector = Icons.Filled.Save,
                        contentDescription = stringResource(R.string.markdown_notes_save),
                    )
                }
            } else {
                IconButton(onClick = onEdit) {
                    Icon(
                        imageVector = Icons.Filled.Edit,
                        contentDescription = stringResource(R.string.markdown_notes_edit),
                    )
                }
            }
        }
        Box {
            IconButton(onClick = { onMenuExpandedChange(true) }) {
                Icon(
                    imageVector = Icons.Filled.MoreVert,
                    contentDescription = stringResource(R.string.markdown_notes_menu),
                )
            }
            DropdownMenu(
                expanded = menuExpanded,
                onDismissRequest = { onMenuExpandedChange(false) },
            ) {
                DropdownMenuItem(
                    text = {
                        Text(stringResource(R.string.markdown_notes_settings))
                    },
                    onClick = {
                        onMenuExpandedChange(false)
                        onOpenSettings()
                    },
                )
            }
        }
    }
}

@Composable
private fun NotesNavigationRow(
    onBack: () -> Unit,
    segments: List<NotesPathSegment>,
    lastIsNote: Boolean,
    onSegmentClick: (Int) -> Unit,
) {
    Row(
        modifier =
        Modifier
            .fillMaxWidth()
            .padding(end = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        IconButton(onClick = onBack) {
            Icon(
                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                contentDescription = stringResource(R.string.markdown_notes_back),
            )
        }
        if (segments.isNotEmpty()) {
            NotesBreadcrumbs(
                segments = segments,
                lastIsNote = lastIsNote,
                onSegmentClick = onSegmentClick,
                modifier = Modifier.weight(1f),
            )
        }
    }
}

@Composable
private fun NotesBreadcrumbs(
    segments: List<NotesPathSegment>,
    lastIsNote: Boolean,
    onSegmentClick: (Int) -> Unit,
    modifier: Modifier = Modifier,
) {
    if (segments.isEmpty()) {
        return
    }
    Row(
        modifier =
        modifier
            .horizontalScroll(rememberScrollState())
            .padding(vertical = 6.dp),
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
            val color =
                if (clickable) {
                    MaterialTheme.colorScheme.primary
                } else {
                    MaterialTheme.colorScheme.onSurface
                }
            if (index == 0) {
                Icon(
                    imageVector = Icons.Filled.Home,
                    contentDescription = stringResource(R.string.nav_drawer_home),
                    tint = color,
                    modifier =
                    Modifier
                        .size(18.dp)
                        .then(
                            if (clickable) {
                                Modifier.clickable { onSegmentClick(index) }
                            } else {
                                Modifier
                            },
                        ),
                )
            } else {
                Text(
                    text = segment.name,
                    style = MaterialTheme.typography.labelLarge,
                    color = color,
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
}

@Composable
private fun NotesFolderList(
    entries: List<NotesEntry>,
    statusMessage: String?,
    density: NotesListDensity,
    layout: NotesBrowseLayout,
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

        layout == NotesBrowseLayout.Icons -> {
            LazyVerticalGrid(
                columns = GridCells.Adaptive(minSize = NotesIconsGridMinCellWidth),
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(4.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                items(entries, key = { it.documentId }) { entry ->
                    when (entry) {
                        is NotesEntry.Folder -> {
                            NotesFolderIconCell(
                                folder = entry,
                                density = density,
                                onOpen = { onOpenFolder(entry) },
                                onShowMergedNote = { onShowMergedNote(entry) },
                            )
                        }

                        is NotesEntry.Note -> {
                            NotesNoteIconCell(
                                note = entry,
                                density = density,
                                onOpen = { onOpenNote(entry) },
                            )
                        }
                    }
                }
            }
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
                                density = density,
                                onOpen = { onOpenFolder(entry) },
                                onShowMergedNote = { onShowMergedNote(entry) },
                            )
                        }

                        is NotesEntry.Note -> {
                            NotesNoteRow(
                                note = entry,
                                density = density,
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
    density: NotesListDensity,
    onOpen: () -> Unit,
    onShowMergedNote: () -> Unit,
) {
    var menuExpanded by remember { mutableStateOf(false) }
    val iconSize = density.iconSizeDp.dp
    val menuButtonSize = density.mergedButtonHeightDp.dp
    Row(
        modifier =
        Modifier
            .fillMaxWidth()
            .height(density.listRowHeightDp.dp)
            .clickable(onClick = onOpen)
            .padding(horizontal = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = Icons.Filled.Folder,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(iconSize),
        )
        Spacer(modifier = Modifier.width(10.dp))
        Text(
            text = folder.name,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.weight(1f),
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
        )
        if (folder.hasMergedNote) {
            Box(modifier = Modifier.size(menuButtonSize)) {
                IconButton(
                    onClick = { menuExpanded = true },
                    modifier = Modifier.fillMaxSize(),
                ) {
                    Icon(
                        imageVector = Icons.Filled.MoreVert,
                        contentDescription = stringResource(R.string.markdown_notes_folder_menu),
                    )
                }
                NotesFolderMergedMenu(
                    expanded = menuExpanded,
                    onDismiss = { menuExpanded = false },
                    onShowMergedNote = onShowMergedNote,
                )
            }
        }
    }
}

@Composable
private fun NotesNoteRow(
    note: NotesEntry.Note,
    density: NotesListDensity,
    onOpen: () -> Unit,
) {
    val iconSize = density.iconSizeDp.dp
    Row(
        modifier =
        Modifier
            .fillMaxWidth()
            .height(density.listRowHeightDp.dp)
            .clickable(onClick = onOpen)
            .padding(horizontal = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = Icons.AutoMirrored.Filled.InsertDriveFile,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.size(iconSize),
        )
        Spacer(modifier = Modifier.width(10.dp))
        Text(
            text = note.displayLabel,
            style = MaterialTheme.typography.bodyMedium,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            modifier = Modifier.weight(1f),
        )
    }
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun NotesFolderIconCell(
    folder: NotesEntry.Folder,
    density: NotesListDensity,
    onOpen: () -> Unit,
    onShowMergedNote: () -> Unit,
) {
    var menuExpanded by remember { mutableStateOf(false) }
    Box(modifier = Modifier.fillMaxWidth()) {
        NotesIconCell(
            label = folder.name,
            density = density,
            icon = {
                Icon(
                    imageVector = Icons.Filled.Folder,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(notesGridIconSize(density)),
                )
            },
            onOpen = onOpen,
            onLongClick =
            if (folder.hasMergedNote) {
                { menuExpanded = true }
            } else {
                null
            },
        )
        NotesFolderMergedMenu(
            expanded = menuExpanded,
            onDismiss = { menuExpanded = false },
            onShowMergedNote = onShowMergedNote,
        )
    }
}

@Composable
private fun NotesNoteIconCell(
    note: NotesEntry.Note,
    density: NotesListDensity,
    onOpen: () -> Unit,
) {
    NotesIconCell(
        label = note.displayLabel,
        density = density,
        icon = {
            Icon(
                imageVector = Icons.AutoMirrored.Filled.InsertDriveFile,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(notesGridIconSize(density)),
            )
        },
        onOpen = onOpen,
    )
}

@Composable
private fun NotesFolderMergedMenu(
    expanded: Boolean,
    onDismiss: () -> Unit,
    onShowMergedNote: () -> Unit,
) {
    DropdownMenu(
        expanded = expanded,
        onDismissRequest = onDismiss,
    ) {
        DropdownMenuItem(
            text = { Text(stringResource(R.string.markdown_notes_show_merged)) },
            onClick = {
                onDismiss()
                onShowMergedNote()
            },
        )
    }
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun NotesIconCell(
    label: String,
    density: NotesListDensity,
    icon: @Composable () -> Unit,
    onOpen: () -> Unit,
    onLongClick: (() -> Unit)? = null,
) {
    val verticalPadding = density.verticalPaddingDp.dp
    Column(
        modifier =
        Modifier
            .fillMaxWidth()
            .then(
                if (onLongClick != null) {
                    Modifier.combinedClickable(
                        onClick = onOpen,
                        onLongClick = onLongClick,
                    )
                } else {
                    Modifier.clickable(onClick = onOpen)
                },
            ).padding(horizontal = 4.dp, vertical = verticalPadding),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        icon()
        Spacer(modifier = Modifier.height(6.dp))
        NotesAutoSizeLabel(
            text = label,
            modifier =
            Modifier
                .fillMaxWidth()
                .heightIn(min = 36.dp),
        )
    }
}

@Composable
private fun NotesAutoSizeLabel(
    text: String,
    modifier: Modifier = Modifier,
) {
    val baseStyle = MaterialTheme.typography.labelMedium
    val textMeasurer = rememberTextMeasurer()
    var fontSize by remember(text) { mutableStateOf(NotesIconsLabelMaxFontSize) }

    BoxWithConstraints(modifier = modifier) {
        val maxWidthPx = constraints.maxWidth
        LaunchedEffect(text, maxWidthPx, baseStyle) {
            if (maxWidthPx <= 0) {
                return@LaunchedEffect
            }
            var candidate = NotesIconsLabelMaxFontSize
            while (candidate > NotesIconsLabelMinFontSize) {
                val layout =
                    textMeasurer.measure(
                        text = text,
                        style = baseStyle.copy(fontSize = candidate, lineHeight = candidate * 1.2f),
                        overflow = TextOverflow.Clip,
                        softWrap = true,
                        maxLines = NotesIconsLabelMaxLines,
                        constraints = Constraints(maxWidth = maxWidthPx),
                    )
                if (!layout.hasVisualOverflow) {
                    break
                }
                candidate = (candidate.value - NotesIconsLabelFontStepSp).coerceAtLeast(
                    NotesIconsLabelMinFontSize.value,
                ).sp
            }
            fontSize = candidate
        }
        Text(
            text = text,
            style = baseStyle.copy(fontSize = fontSize, lineHeight = fontSize * 1.2f),
            textAlign = TextAlign.Center,
            maxLines = NotesIconsLabelMaxLines,
            overflow = TextOverflow.Ellipsis,
            softWrap = true,
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

private fun notesGridIconSize(density: NotesListDensity) = (density.iconSizeDp * 2).dp

@Composable
private fun NotesPlainTextPane(
    isLoading: Boolean,
    content: String?,
    draftText: String,
    isEditing: Boolean,
    errorMessage: String?,
    onDraftChange: (String) -> Unit,
) {
    var viewLines by remember { mutableStateOf<List<String>?>(null) }
    var preparingView by remember { mutableStateOf(false) }

    LaunchedEffect(content, isEditing) {
        if (isEditing || content == null) {
            viewLines = null
            preparingView = false
            return@LaunchedEffect
        }
        preparingView = true
        viewLines =
            withContext(Dispatchers.IO) {
                content.lineSequence().toList()
            }
        preparingView = false
    }

    when {
        isLoading || preparingView -> {
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
            val lines = viewLines.orEmpty()
            val listState = rememberLazyListState()
            Surface(
                modifier = Modifier.fillMaxSize(),
                color = MaterialTheme.colorScheme.surface,
            ) {
                Box(modifier = Modifier.fillMaxSize()) {
                    LazyColumn(
                        state = listState,
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(16.dp),
                    ) {
                        items(
                            count = lines.size,
                            key = { index -> index },
                        ) { index ->
                            Text(
                                text = lines[index].ifEmpty { "\u00A0" },
                                style = MaterialTheme.typography.bodyMedium,
                            )
                        }
                    }
                    NotesVerticalScrollbar(
                        state = listState,
                        modifier =
                        Modifier
                            .align(Alignment.CenterEnd)
                            .padding(end = 2.dp, top = 8.dp, bottom = 8.dp),
                    )
                }
            }
        }
    }
}

@Composable
private fun NotesVerticalScrollbar(
    state: LazyListState,
    modifier: Modifier = Modifier,
) {
    val layoutInfo = state.layoutInfo
    val visibleItems = layoutInfo.visibleItemsInfo
    val totalItems = layoutInfo.totalItemsCount
    val viewportHeight = layoutInfo.viewportSize.height.toFloat()
    val canShow =
        visibleItems.isNotEmpty() &&
            totalItems > 0 &&
            viewportHeight > 0f

    if (!canShow) {
        return
    }

    val averageItemSize = visibleItems.sumOf { it.size }.toFloat() / visibleItems.size
    val estimatedContentHeight = averageItemSize * totalItems
    if (estimatedContentHeight <= viewportHeight + 1f) {
        return
    }

    val scrollOffset =
        visibleItems.first().index * averageItemSize + state.firstVisibleItemScrollOffset
    val maxScroll = (estimatedContentHeight - viewportHeight).coerceAtLeast(1f)
    val scrollFraction = (scrollOffset / maxScroll).coerceIn(0f, 1f)
    val thumbHeightPx =
        (viewportHeight * (viewportHeight / estimatedContentHeight))
            .coerceIn(viewportHeight * 0.08f, viewportHeight)
    val thumbOffsetPx = scrollFraction * (viewportHeight - thumbHeightPx)
    val density = LocalDensity.current

    Box(
        modifier =
        modifier
            .fillMaxHeight()
            .width(4.dp),
    ) {
        Box(
            modifier =
            Modifier
                .align(Alignment.TopCenter)
                .offset { IntOffset(0, thumbOffsetPx.roundToInt()) }
                .width(3.dp)
                .height(with(density) { thumbHeightPx.toDp() })
                .background(
                    color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.4f),
                    shape = RoundedCornerShape(2.dp),
                ),
        )
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
