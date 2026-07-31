package dev.harrix.hsk.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.CleaningServices
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Description
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.VideoLibrary
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.NavigationDrawerItemColors
import androidx.compose.material3.NavigationDrawerItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import dev.harrix.hsk.R
import dev.harrix.hsk.ui.gallery.GalleryCleanerScreen
import dev.harrix.hsk.ui.gallery.VideoCleanerScreen
import dev.harrix.hsk.ui.notes.NotesViewerScreen
import dev.harrix.hsk.ui.settings.SettingsScreen
import dev.harrix.hsk.ui.settings.SettingsSection
import dev.harrix.hsk.ui.theme.HskAndroidTheme
import dev.harrix.hsk.ui.theme.ThemeMode
import kotlinx.coroutines.launch

private const val HomeGridColumns = 2
private val BottomBarMinHeight = 56.dp
private val BottomIconSize = 22.dp
private val BottomLabelFontSize = 10.sp
private val DrawerItemHeight = 40.dp
private val DrawerItemCornerRadius = 8.dp
private val DrawerItemVerticalGap = 2.dp
private val UtilityCardCornerRadius = 8.dp
private val UtilityCardMinHeight = 104.dp
private val UtilityCardIconSize = 40.dp

private enum class AppDestination {
    Home,
    GalleryCleaner,
    VideoCleaner,
    MarkdownNotes,
}

private data class UtilityCardItem(
    val titleRes: Int,
    val descriptionRes: Int,
    val icon: ImageVector,
    val destination: AppDestination,
)

private data class BottomNavItem(
    val destination: AppDestination,
    val icon: ImageVector,
    val labelRes: Int,
)

/** Bottom bar slots; add entries here to show more destinations. */
private val BottomNavItems =
    listOf(
        BottomNavItem(
            destination = AppDestination.Home,
            icon = Icons.Filled.Home,
            labelRes = R.string.nav_bottom_home,
        ),
        BottomNavItem(
            destination = AppDestination.MarkdownNotes,
            icon = Icons.Filled.Description,
            labelRes = R.string.nav_bottom_notes,
        ),
    )

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
    themeMode: ThemeMode,
    onThemeModeChange: (ThemeMode) -> Unit,
    modifier: Modifier = Modifier,
) {
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val scope = rememberCoroutineScope()
    val colorScheme = MaterialTheme.colorScheme
    val appName = stringResource(R.string.app_name)
    var destination by remember { mutableStateOf(AppDestination.Home) }
    var settingsSection by remember { mutableStateOf<SettingsSection?>(null) }
    var settingsRevision by remember { mutableIntStateOf(0) }
    var settingsShootDayEpochMs by remember { mutableStateOf<Long?>(null) }
    var homeMenuExpanded by remember { mutableStateOf(false) }
    val drawerItemColors =
        NavigationDrawerItemDefaults.colors(
            selectedContainerColor = colorScheme.secondaryContainer,
        )
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
                titleRes = R.string.nav_drawer_markdown_notes,
                descriptionRes = R.string.markdown_notes_card_description,
                icon = Icons.Filled.Description,
                destination = AppDestination.MarkdownNotes,
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

            AppDestination.Home,
            AppDestination.MarkdownNotes,
            -> {
                Scaffold(
                    containerColor = colorScheme.background,
                    contentWindowInsets = WindowInsets(0, 0, 0, 0),
                    bottomBar = {
                        BottomActionBar(
                            items = BottomNavItems,
                            selected = destination,
                            onSelect = { destination = it },
                            showClose = destination == AppDestination.MarkdownNotes,
                            onClose = { destination = AppDestination.Home },
                        )
                    },
                ) { bottomNavPadding ->
                    Box(
                        modifier =
                        Modifier
                            .padding(bottomNavPadding)
                            .fillMaxSize(),
                    ) {
                        when (destination) {
                            AppDestination.MarkdownNotes -> {
                                NotesViewerScreen(
                                    onClose = { destination = AppDestination.Home },
                                    onOpenSettings = {
                                        settingsSection = SettingsSection.MarkdownNotes
                                    },
                                    settingsRevision = settingsRevision,
                                    modifier = Modifier.fillMaxSize(),
                                )
                            }

                            else -> {
                                ModalNavigationDrawer(
                                    drawerState = drawerState,
                                    modifier = Modifier.fillMaxSize(),
                                    drawerContent = {
                                        AppNavigationDrawerContent(
                                            appName = appName,
                                            selected = destination,
                                            colors = drawerItemColors,
                                            onNavigate = { target ->
                                                scope.launch {
                                                    drawerState.close()
                                                    destination = target
                                                }
                                            },
                                            onAbout = {
                                                scope.launch { drawerState.close() }
                                            },
                                        )
                                    },
                                ) {
                                    Scaffold(
                                        containerColor = colorScheme.background,
                                        contentWindowInsets = WindowInsets(0, 0, 0, 0),
                                        topBar = {
                                            TopAppBar(
                                                title = { Text(appName) },
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
                                                            DropdownMenuItem(
                                                                text = {
                                                                    Text(
                                                                        stringResource(
                                                                            R.string.nav_settings,
                                                                        ),
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
                                                colors =
                                                TopAppBarDefaults.topAppBarColors(
                                                    containerColor = colorScheme.background,
                                                    scrolledContainerColor =
                                                    colorScheme.background,
                                                ),
                                            )
                                        },
                                    ) { innerPadding ->
                                        Surface(
                                            modifier =
                                            Modifier
                                                .padding(innerPadding)
                                                .fillMaxSize(),
                                            color = colorScheme.surface,
                                            shadowElevation = 0.dp,
                                            tonalElevation = 0.dp,
                                        ) {
                                            HomeUtilitiesGrid(
                                                utilities = utilities,
                                                onUtilityClick = { item ->
                                                    destination = item.destination
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
        }

        settingsSection?.let { section ->
            SettingsScreen(
                section = section,
                themeMode = themeMode,
                onThemeModeChange = onThemeModeChange,
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
    }
}

@Composable
private fun HomeUtilitiesGrid(
    utilities: List<UtilityCardItem>,
    onUtilityClick: (UtilityCardItem) -> Unit,
    modifier: Modifier = Modifier,
) {
    LazyVerticalGrid(
        columns = GridCells.Fixed(HomeGridColumns),
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        item(span = { GridItemSpan(HomeGridColumns) }) {
            Text(
                text = stringResource(R.string.home_utilities_title),
                style =
                MaterialTheme.typography.titleMedium.copy(
                    fontWeight = FontWeight.Bold,
                ),
                modifier = Modifier.padding(bottom = 4.dp),
            )
        }
        items(utilities) { utility ->
            UtilityCard(
                title = stringResource(utility.titleRes),
                description = stringResource(utility.descriptionRes),
                icon = utility.icon,
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
) {
    val colorScheme = MaterialTheme.colorScheme
    Row(
        modifier =
        modifier
            .fillMaxWidth()
            .height(UtilityCardMinHeight)
            .border(1.dp, colorScheme.outline, RoundedCornerShape(UtilityCardCornerRadius))
            .background(colorScheme.surface, RoundedCornerShape(UtilityCardCornerRadius))
            .clickable(onClick = onClick)
            .padding(horizontal = 12.dp, vertical = 10.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = colorScheme.onSurfaceVariant,
            modifier = Modifier.size(UtilityCardIconSize),
        )
        Spacer(modifier = Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style =
                MaterialTheme.typography.titleSmall.copy(
                    fontWeight = FontWeight.Bold,
                    fontSize = 14.sp,
                    lineHeight = 18.sp,
                ),
                color = colorScheme.onSurface,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
            )
            Spacer(modifier = Modifier.height(4.dp))
            AutoFitDescription(
                text = description,
                color = colorScheme.onSurfaceVariant,
                maxLines = 3,
                minFontSize = 9.sp,
                maxFontSize = 11.sp,
            )
        }
    }
}

@Composable
private fun AutoFitDescription(
    text: String,
    color: Color,
    maxLines: Int,
    minFontSize: TextUnit,
    maxFontSize: TextUnit,
    modifier: Modifier = Modifier,
) {
    var textStyle by remember(text) {
        mutableStateOf(
            TextStyle(
                fontSize = maxFontSize,
                lineHeight = maxFontSize * 1.3f,
            ),
        )
    }
    var readyToDraw by remember(text) { mutableStateOf(false) }

    Text(
        text = text,
        color = color,
        style = MaterialTheme.typography.bodySmall.merge(textStyle),
        maxLines = maxLines,
        overflow = TextOverflow.Clip,
        softWrap = true,
        modifier =
        modifier.drawWithContent {
            if (readyToDraw) {
                drawContent()
            }
        },
        onTextLayout = { result ->
            if (result.hasVisualOverflow && textStyle.fontSize > minFontSize) {
                val nextSize = (textStyle.fontSize.value - 0.5f).coerceAtLeast(minFontSize.value).sp
                textStyle =
                    textStyle.copy(
                        fontSize = nextSize,
                        lineHeight = nextSize * 1.3f,
                    )
            } else {
                readyToDraw = true
            }
        },
    )
}

@Composable
private fun AppNavigationDrawerContent(
    appName: String,
    selected: AppDestination,
    colors: NavigationDrawerItemColors,
    onNavigate: (AppDestination) -> Unit,
    onAbout: () -> Unit,
) {
    ModalDrawerSheet {
        Text(
            text = appName,
            style = MaterialTheme.typography.titleLarge,
            modifier =
            Modifier.padding(
                horizontal = 28.dp,
                vertical = 24.dp,
            ),
        )
        HorizontalDivider(
            modifier = Modifier.padding(bottom = 8.dp),
        )
        CompactNavigationDrawerItem(
            label = stringResource(R.string.nav_drawer_home),
            selected = selected == AppDestination.Home,
            onClick = { onNavigate(AppDestination.Home) },
            icon = Icons.AutoMirrored.Filled.List,
            colors = colors,
        )
        CompactNavigationDrawerItem(
            label = stringResource(R.string.nav_drawer_gallery_cleaner),
            selected = selected == AppDestination.GalleryCleaner,
            onClick = { onNavigate(AppDestination.GalleryCleaner) },
            icon = Icons.Filled.CleaningServices,
            colors = colors,
        )
        CompactNavigationDrawerItem(
            label = stringResource(R.string.nav_drawer_video_cleaner),
            selected = selected == AppDestination.VideoCleaner,
            onClick = { onNavigate(AppDestination.VideoCleaner) },
            icon = Icons.Filled.VideoLibrary,
            colors = colors,
        )
        CompactNavigationDrawerItem(
            label = stringResource(R.string.nav_drawer_markdown_notes),
            selected = selected == AppDestination.MarkdownNotes,
            onClick = { onNavigate(AppDestination.MarkdownNotes) },
            icon = Icons.Filled.Description,
            colors = colors,
        )
        CompactNavigationDrawerItem(
            label = stringResource(R.string.nav_drawer_about),
            selected = false,
            onClick = onAbout,
            icon = Icons.Filled.Info,
            colors = colors,
        )
    }
}

@Composable
private fun CompactNavigationDrawerItem(
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
    icon: ImageVector,
    colors: NavigationDrawerItemColors,
    modifier: Modifier = Modifier,
) {
    Surface(
        selected = selected,
        onClick = onClick,
        modifier =
        modifier
            .padding(horizontal = 12.dp, vertical = DrawerItemVerticalGap)
            .fillMaxWidth()
            .height(DrawerItemHeight),
        shape = RoundedCornerShape(DrawerItemCornerRadius),
        color = colors.containerColor(selected).value,
    ) {
        Row(
            modifier =
            Modifier
                .fillMaxSize()
                .padding(horizontal = 16.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = colors.iconColor(selected).value,
                modifier = Modifier.size(20.dp),
            )
            Spacer(modifier = Modifier.width(12.dp))
            Text(
                text = label,
                color = colors.textColor(selected).value,
                style = MaterialTheme.typography.labelLarge,
            )
        }
    }
}

@Composable
private fun BottomActionBar(
    items: List<BottomNavItem>,
    selected: AppDestination,
    onSelect: (AppDestination) -> Unit,
    modifier: Modifier = Modifier,
    showClose: Boolean = false,
    onClose: (() -> Unit)? = null,
) {
    val colorScheme = MaterialTheme.colorScheme

    Column(
        modifier =
        modifier
            .fillMaxWidth()
            .background(colorScheme.background)
            .windowInsetsPadding(WindowInsets.navigationBars),
    ) {
        HorizontalDivider(color = colorScheme.outlineVariant, thickness = 1.dp)
        Row(
            modifier =
            Modifier
                .fillMaxWidth()
                .heightIn(min = BottomBarMinHeight)
                .padding(horizontal = 4.dp, vertical = 4.dp),
            horizontalArrangement = Arrangement.SpaceEvenly,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            items.forEach { item ->
                val isSelected = item.destination == selected
                BottomBarLabeledButton(
                    icon = item.icon,
                    label = stringResource(item.labelRes),
                    selected = isSelected,
                    onClick = { onSelect(item.destination) },
                    modifier = Modifier.weight(1f),
                )
            }
            if (showClose && onClose != null) {
                BottomBarLabeledButton(
                    icon = Icons.Filled.Close,
                    label = stringResource(R.string.nav_bottom_close),
                    selected = false,
                    onClick = onClose,
                    modifier = Modifier.weight(1f),
                )
            }
        }
    }
}

@Composable
private fun BottomBarLabeledButton(
    icon: ImageVector,
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val colorScheme = MaterialTheme.colorScheme
    val tint =
        if (selected) {
            colorScheme.primary
        } else {
            colorScheme.onSurfaceVariant
        }
    Column(
        modifier =
        modifier
            .clickable(onClick = onClick)
            .padding(vertical = 2.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Icon(
            imageVector = icon,
            contentDescription = label,
            tint = tint,
            modifier = Modifier.size(BottomIconSize),
        )
        Text(
            text = label,
            color = tint,
            style = MaterialTheme.typography.labelSmall,
            fontSize = BottomLabelFontSize,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
        )
    }
}

@Preview(showBackground = true, backgroundColor = 0xFFE5E6EA)
@Composable
private fun MainScreenPreview() {
    HskAndroidTheme(darkTheme = false) {
        MainScreen(
            themeMode = ThemeMode.Light,
            onThemeModeChange = {},
        )
    }
}
