package dev.harrix.hsk.ui

import android.net.Uri
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.CleaningServices
import androidx.compose.material.icons.filled.Crop
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Medication
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.VideoLibrary
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.OutlinedCard
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import dev.harrix.hsk.R
import dev.harrix.hsk.ui.HskDropdownMenuItem
import dev.harrix.hsk.ui.about.AboutScreen
import dev.harrix.hsk.ui.gallery.GalleryCleanerScreen
import dev.harrix.hsk.ui.gallery.VideoCleanerScreen
import dev.harrix.hsk.ui.medicinesearch.MedicineSearchScreen
import dev.harrix.hsk.ui.photoeditor.PhotoEditorScreen
import dev.harrix.hsk.ui.settings.SettingsScreen
import dev.harrix.hsk.ui.settings.SettingsSection
import dev.harrix.hsk.ui.speechtotext.SpeechToTextScreen
import dev.harrix.hsk.ui.theme.AppLanguage
import dev.harrix.hsk.ui.theme.HskAndroidTheme
import dev.harrix.hsk.ui.theme.HskTopAppBarHeight
import dev.harrix.hsk.ui.theme.ThemeMode
import dev.harrix.hsk.ui.theme.hskScaffoldContainerColor
import dev.harrix.hsk.ui.theme.hskScaffoldContentWindowInsets
import dev.harrix.hsk.ui.theme.hskTopAppBarColors
import dev.harrix.hsk.ui.theme.hskTopAppBarWindowInsets
import kotlinx.coroutines.launch

private val UtilityCardMinHeight = 104.dp
private val UtilityCardCompactMinHeight = 88.dp
private val UtilityCardIconSize = 40.dp
private val UtilityCardCompactIconSize = 36.dp
private val TopBarLogoSize = 28.dp
private val DrawerLogoSize = 40.dp
private val DrawerMaxWidth = 320.dp
private val DrawerItemShape = RoundedCornerShape(12.dp)
private val DrawerItemOuterPadding = PaddingValues(horizontal = 8.dp, vertical = 1.dp)
private val DrawerItemContentPadding = PaddingValues(horizontal = 12.dp, vertical = 8.dp)

private enum class AppDestination {
    Home,
    GalleryCleaner,
    VideoCleaner,
    PhotoEditor,
    SpeechToText,
    MedicineSearch,
}

private data class UtilityCardItem(
    val titleRes: Int,
    val descriptionRes: Int,
    val icon: ImageVector,
    val destination: AppDestination,
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
    themeMode: ThemeMode,
    onThemeModeChange: (ThemeMode) -> Unit,
    appLanguage: AppLanguage,
    onAppLanguageChange: (AppLanguage) -> Unit,
    modifier: Modifier = Modifier,
    pendingImageUri: Uri? = null,
    onPendingImageUriConsume: () -> Unit = {},
    pendingOpenSpeechToText: Boolean = false,
    onPendingOpenSpeechToTextConsume: () -> Unit = {},
) {
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val scope = rememberCoroutineScope()
    val appName = stringResource(R.string.app_name)
    // Survive Activity recreation (e.g. landscape rotation); plain remember resets to Home.
    var destination by rememberSaveable { mutableStateOf(AppDestination.Home) }
    var settingsSection by rememberSaveable { mutableStateOf<SettingsSection?>(null) }
    var settingsRevision by rememberSaveable { mutableIntStateOf(0) }
    var settingsShootDayEpochMs by rememberSaveable { mutableStateOf<Long?>(null) }
    var showAbout by rememberSaveable { mutableStateOf(false) }
    var homeMenuExpanded by remember { mutableStateOf(false) }
    var photoEditorInitialUri by remember { mutableStateOf<Uri?>(null) }
    val onPendingImageUriConsumeState = rememberUpdatedState(onPendingImageUriConsume)
    val onPendingOpenSpeechToTextConsumeState =
        rememberUpdatedState(onPendingOpenSpeechToTextConsume)
    var autoStartSpeechRecording by remember { mutableStateOf(false) }

    LaunchedEffect(pendingImageUri) {
        val uri = pendingImageUri ?: return@LaunchedEffect
        photoEditorInitialUri = uri
        destination = AppDestination.PhotoEditor
        showAbout = false
        settingsSection = null
        onPendingImageUriConsumeState.value()
    }

    LaunchedEffect(pendingOpenSpeechToText) {
        if (!pendingOpenSpeechToText) {
            return@LaunchedEffect
        }
        destination = AppDestination.SpeechToText
        showAbout = false
        settingsSection = null
        autoStartSpeechRecording = true
        onPendingOpenSpeechToTextConsumeState.value()
    }

    BackHandler(enabled = drawerState.isOpen) {
        scope.launch { drawerState.close() }
    }

    val utilities =
        listOf(
            UtilityCardItem(
                titleRes = R.string.nav_drawer_gallery_cleaner,
                descriptionRes = R.string.gallery_cleaner_card_description,
                icon = Icons.Filled.CleaningServices,
                destination = AppDestination.GalleryCleaner,
            ),
            UtilityCardItem(
                titleRes = R.string.nav_drawer_video_cleaner,
                descriptionRes = R.string.video_cleaner_card_description,
                icon = Icons.Filled.VideoLibrary,
                destination = AppDestination.VideoCleaner,
            ),
            UtilityCardItem(
                titleRes = R.string.nav_drawer_photo_editor,
                descriptionRes = R.string.photo_editor_card_description,
                icon = Icons.Filled.Crop,
                destination = AppDestination.PhotoEditor,
            ),
            UtilityCardItem(
                titleRes = R.string.nav_drawer_speech_to_text,
                descriptionRes = R.string.speech_to_text_card_description,
                icon = Icons.Filled.Mic,
                destination = AppDestination.SpeechToText,
            ),
            UtilityCardItem(
                titleRes = R.string.nav_drawer_medicine_search,
                descriptionRes = R.string.medicine_search_card_description,
                icon = Icons.Filled.Medication,
                destination = AppDestination.MedicineSearch,
            ),
        )

    Box(modifier = modifier.fillMaxSize()) {
        when (destination) {
            AppDestination.GalleryCleaner -> {
                GalleryCleanerScreen(
                    onClose = { destination = AppDestination.Home },
                    onOpenSettings = { shootDayEpochMs ->
                        settingsShootDayEpochMs = shootDayEpochMs
                        settingsSection = SettingsSection.GalleryCleaner
                    },
                    settingsRevision = settingsRevision,
                    modifier = Modifier.fillMaxSize(),
                )
            }

            AppDestination.VideoCleaner -> {
                VideoCleanerScreen(
                    onClose = { destination = AppDestination.Home },
                    onOpenSettings = { settingsSection = SettingsSection.VideoCleaner },
                    settingsRevision = settingsRevision,
                    modifier = Modifier.fillMaxSize(),
                )
            }

            AppDestination.PhotoEditor -> {
                PhotoEditorScreen(
                    onClose = {
                        photoEditorInitialUri = null
                        destination = AppDestination.Home
                    },
                    initialUri = photoEditorInitialUri,
                    onInitialUriConsume = { photoEditorInitialUri = null },
                    settingsRevision = settingsRevision,
                    modifier = Modifier.fillMaxSize(),
                )
            }

            AppDestination.SpeechToText -> {
                SpeechToTextScreen(
                    onClose = {
                        autoStartSpeechRecording = false
                        destination = AppDestination.Home
                    },
                    autoStartRecording = autoStartSpeechRecording,
                    onAutoStartRecordingConsume = { autoStartSpeechRecording = false },
                    modifier = Modifier.fillMaxSize(),
                )
            }

            AppDestination.MedicineSearch -> {
                MedicineSearchScreen(
                    onClose = { destination = AppDestination.Home },
                    onOpenSettings = { settingsSection = SettingsSection.MedicineSearch },
                    settingsRevision = settingsRevision,
                    modifier = Modifier.fillMaxSize(),
                )
            }

            AppDestination.Home -> {
                ModalNavigationDrawer(
                    drawerState = drawerState,
                    modifier = Modifier.fillMaxSize(),
                    drawerContent = {
                        AppNavigationDrawerContent(
                            appName = appName,
                            selected = destination,
                            onNavigate = { target ->
                                scope.launch {
                                    drawerState.close()
                                    destination = target
                                }
                            },
                            onAbout = {
                                scope.launch {
                                    drawerState.close()
                                    showAbout = true
                                }
                            },
                            onOpenSettings = {
                                scope.launch {
                                    drawerState.close()
                                    settingsSection = SettingsSection.All
                                }
                            },
                        )
                    },
                ) {
                    Scaffold(
                        containerColor = hskScaffoldContainerColor(),
                        contentWindowInsets = hskScaffoldContentWindowInsets(),
                        topBar = {
                            TopAppBar(
                                title = {
                                    BrandTitle(
                                        appName = appName,
                                        logoSize = TopBarLogoSize,
                                        textStyle = MaterialTheme.typography.titleLarge,
                                        modifier = Modifier.fillMaxWidth(),
                                    )
                                },
                                colors = hskTopAppBarColors(),
                                windowInsets = hskTopAppBarWindowInsets(),
                                expandedHeight = HskTopAppBarHeight,
                                navigationIcon = {
                                    IconButton(
                                        onClick = {
                                            scope.launch { drawerState.open() }
                                        },
                                    ) {
                                        Icon(
                                            imageVector = Icons.Filled.Menu,
                                            contentDescription =
                                            stringResource(R.string.nav_open),
                                        )
                                    }
                                },
                                actions = {
                                    Box {
                                        IconButton(
                                            onClick = { homeMenuExpanded = true },
                                        ) {
                                            Icon(
                                                imageVector = Icons.Filled.MoreVert,
                                                contentDescription =
                                                stringResource(
                                                    R.string.nav_settings,
                                                ),
                                            )
                                        }
                                        DropdownMenu(
                                            expanded = homeMenuExpanded,
                                            onDismissRequest = {
                                                homeMenuExpanded = false
                                            },
                                        ) {
                                            HskDropdownMenuItem(
                                                text = {
                                                    AutoFitText(
                                                        text =
                                                        stringResource(
                                                            R.string.nav_settings,
                                                        ),
                                                        maxLines = 1,
                                                    )
                                                },
                                                leadingIcon = {
                                                    Icon(
                                                        imageVector = Icons.Filled.Settings,
                                                        contentDescription = null,
                                                    )
                                                },
                                                onClick = {
                                                    homeMenuExpanded = false
                                                    settingsSection =
                                                        SettingsSection.All
                                                },
                                            )
                                        }
                                    }
                                },
                            )
                        },
                    ) { innerPadding ->
                        HomeUtilitiesGrid(
                            utilities = utilities,
                            onUtilityClick = { item ->
                                destination = item.destination
                            },
                            modifier =
                            Modifier
                                .padding(innerPadding)
                                .fillMaxSize(),
                        )
                    }
                }
            }
        }

        settingsSection?.let { section ->
            SettingsScreen(
                section = section,
                themeMode = themeMode,
                onThemeModeChange = onThemeModeChange,
                appLanguage = appLanguage,
                onAppLanguageChange = onAppLanguageChange,
                onClose = {
                    settingsSection = null
                    settingsShootDayEpochMs = null
                    settingsRevision += 1
                },
                onOpenAllSettings =
                if (section == SettingsSection.All) {
                    null
                } else {
                    { settingsSection = SettingsSection.All }
                },
                currentShootDayEpochMs = settingsShootDayEpochMs,
                modifier = Modifier.fillMaxSize(),
            )
        }

        if (showAbout) {
            AboutScreen(
                onClose = { showAbout = false },
                modifier = Modifier.fillMaxSize(),
            )
        }
    }
}

@Composable
private fun HomeUtilitiesGrid(
    utilities: List<UtilityCardItem>,
    onUtilityClick: (UtilityCardItem) -> Unit,
    modifier: Modifier = Modifier,
) {
    val compact = isCompactWidth() || isCompactHeight()
    val contentPadding = if (compact) 12.dp else 16.dp
    val spacing = if (compact) 8.dp else 12.dp
    LazyVerticalGrid(
        columns = GridCells.Fixed(homeGridColumnCount()),
        modifier = modifier.adaptiveContentWidth(),
        contentPadding = PaddingValues(contentPadding),
        horizontalArrangement = Arrangement.spacedBy(spacing),
        verticalArrangement = Arrangement.spacedBy(spacing),
    ) {
        items(utilities) { utility ->
            UtilityCard(
                title = stringResource(utility.titleRes),
                description = stringResource(utility.descriptionRes),
                icon = utility.icon,
                compact = compact,
                onClick = { onUtilityClick(utility) },
            )
        }
    }
}

@Composable
private fun UtilityCard(
    title: String,
    description: String,
    icon: ImageVector,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    compact: Boolean = false,
) {
    val colorScheme = MaterialTheme.colorScheme
    val iconSize = if (compact) UtilityCardCompactIconSize else UtilityCardIconSize
    OutlinedCard(
        onClick = onClick,
        modifier =
        modifier
            .fillMaxWidth()
            .heightIn(min = if (compact) UtilityCardCompactMinHeight else UtilityCardMinHeight),
        shape = MaterialTheme.shapes.medium,
    ) {
        Row(
            modifier =
            Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = if (compact) 10.dp else 12.dp,
                    vertical = if (compact) 10.dp else 12.dp,
                ),
            verticalAlignment = Alignment.Top,
        ) {
            Surface(
                modifier = Modifier.size(iconSize),
                shape = CircleShape,
                color = colorScheme.primaryContainer,
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = icon,
                        contentDescription = null,
                        tint = colorScheme.onPrimaryContainer,
                        modifier = Modifier.size(if (compact) 20.dp else 22.dp),
                    )
                }
            }
            Spacer(modifier = Modifier.width(if (compact) 10.dp else 12.dp))
            Column(modifier = Modifier.weight(1f)) {
                AutoFitText(
                    text = title,
                    style = MaterialTheme.typography.titleSmall,
                    color = colorScheme.onSurface,
                    maxLines = 1,
                )
                Spacer(modifier = Modifier.height(4.dp))
                AutoFitText(
                    text = description,
                    style = MaterialTheme.typography.bodySmall,
                    color = colorScheme.onSurfaceVariant,
                    maxLines = if (compact) 2 else 3,
                )
            }
        }
    }
}

@Composable
private fun BrandTitle(
    appName: String,
    logoSize: Dp,
    textStyle: TextStyle,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Image(
            painter = painterResource(R.drawable.ic_app_logo),
            contentDescription = null,
            contentScale = ContentScale.Fit,
            modifier = Modifier.size(logoSize),
        )
        Spacer(modifier = Modifier.width(12.dp))
        AutoFitText(
            text = appName,
            style = textStyle,
            maxLines = 1,
            modifier = Modifier.weight(1f, fill = false),
        )
    }
}

@Composable
private fun AppNavigationDrawerContent(
    appName: String,
    selected: AppDestination,
    onNavigate: (AppDestination) -> Unit,
    onAbout: () -> Unit,
    onOpenSettings: () -> Unit,
) {
    ModalDrawerSheet(
        modifier = Modifier.widthIn(max = DrawerMaxWidth),
        drawerContainerColor = MaterialTheme.colorScheme.surface,
    ) {
        Row(
            modifier =
            Modifier
                .fillMaxWidth()
                .padding(start = 20.dp, end = 4.dp, top = 12.dp, bottom = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            BrandTitle(
                appName = appName,
                logoSize = DrawerLogoSize,
                textStyle = MaterialTheme.typography.titleLarge,
                modifier = Modifier.weight(1f),
            )
            IconButton(onClick = onOpenSettings) {
                Icon(
                    imageVector = Icons.Filled.Settings,
                    contentDescription = stringResource(R.string.nav_settings),
                )
            }
        }
        HorizontalDivider(
            modifier = Modifier.padding(bottom = 4.dp),
        )
        DrawerNavItem(
            label = stringResource(R.string.nav_drawer_home),
            selected = selected == AppDestination.Home,
            onClick = { onNavigate(AppDestination.Home) },
            icon = Icons.AutoMirrored.Filled.List,
        )
        DrawerNavItem(
            label = stringResource(R.string.nav_drawer_gallery_cleaner),
            selected = selected == AppDestination.GalleryCleaner,
            onClick = { onNavigate(AppDestination.GalleryCleaner) },
            icon = Icons.Filled.CleaningServices,
        )
        DrawerNavItem(
            label = stringResource(R.string.nav_drawer_video_cleaner),
            selected = selected == AppDestination.VideoCleaner,
            onClick = { onNavigate(AppDestination.VideoCleaner) },
            icon = Icons.Filled.VideoLibrary,
        )
        DrawerNavItem(
            label = stringResource(R.string.nav_drawer_photo_editor),
            selected = selected == AppDestination.PhotoEditor,
            onClick = { onNavigate(AppDestination.PhotoEditor) },
            icon = Icons.Filled.Crop,
        )
        DrawerNavItem(
            label = stringResource(R.string.nav_drawer_speech_to_text),
            selected = selected == AppDestination.SpeechToText,
            onClick = { onNavigate(AppDestination.SpeechToText) },
            icon = Icons.Filled.Mic,
        )
        DrawerNavItem(
            label = stringResource(R.string.nav_drawer_medicine_search),
            selected = selected == AppDestination.MedicineSearch,
            onClick = { onNavigate(AppDestination.MedicineSearch) },
            icon = Icons.Filled.Medication,
        )
        DrawerNavItem(
            label = stringResource(R.string.nav_drawer_about),
            selected = false,
            onClick = onAbout,
            icon = Icons.Filled.Info,
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun DrawerNavItem(
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
    icon: ImageVector,
) {
    val colorScheme = MaterialTheme.colorScheme
    val contentColor =
        if (selected) {
            colorScheme.onSurface
        } else {
            colorScheme.onSurfaceVariant
        }
    Surface(
        selected = selected,
        onClick = onClick,
        modifier =
        Modifier
            .fillMaxWidth()
            .padding(DrawerItemOuterPadding),
        shape = DrawerItemShape,
        color =
        if (selected) {
            colorScheme.surfaceVariant
        } else {
            Color.Transparent
        },
        contentColor = contentColor,
    ) {
        Row(
            modifier =
            Modifier
                .fillMaxWidth()
                .heightIn(min = 40.dp)
                .padding(DrawerItemContentPadding),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(22.dp),
            )
            Spacer(modifier = Modifier.width(10.dp))
            AutoFitText(
                text = label,
                style = MaterialTheme.typography.labelLarge,
                maxLines = 1,
            )
        }
    }
}

@Preview(showBackground = true)
@Composable
private fun MainScreenPreview() {
    HskAndroidTheme(darkTheme = false) {
        MainScreen(
            themeMode = ThemeMode.Light,
            onThemeModeChange = {},
            appLanguage = AppLanguage.System,
            onAppLanguageChange = {},
        )
    }
}
