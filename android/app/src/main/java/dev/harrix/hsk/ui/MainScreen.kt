package dev.harrix.hsk.ui

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Image
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
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
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
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Settings
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
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.NavigationDrawerItemDefaults
import androidx.compose.material3.OutlinedCard
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import dev.harrix.hsk.R
import dev.harrix.hsk.ui.about.AboutScreen
import dev.harrix.hsk.ui.gallery.GalleryCleanerScreen
import dev.harrix.hsk.ui.gallery.VideoCleanerScreen
import dev.harrix.hsk.ui.settings.SettingsScreen
import dev.harrix.hsk.ui.settings.SettingsSection
import dev.harrix.hsk.ui.theme.HskAndroidTheme
import dev.harrix.hsk.ui.theme.ThemeMode
import kotlinx.coroutines.launch

private val UtilityCardMinHeight = 104.dp
private val UtilityCardCompactMinHeight = 88.dp
private val UtilityCardIconSize = 40.dp
private val UtilityCardCompactIconSize = 36.dp
private val TopBarLogoSize = 28.dp
private val DrawerLogoSize = 40.dp
private val DrawerMaxWidth = 320.dp
private val DrawerItemShape = RoundedCornerShape(8.dp)
private val DrawerItemPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp)

private enum class AppDestination {
    Home,
    GalleryCleaner,
    VideoCleaner,
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
    modifier: Modifier = Modifier,
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
                        contentWindowInsets = WindowInsets.safeDrawing,
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
                                                        text =
                                                        stringResource(
                                                            R.string.nav_settings,
                                                        ),
                                                        maxLines = 1,
                                                        overflow = TextOverflow.Ellipsis,
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
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleSmall,
                    color = colorScheme.onSurface,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodySmall,
                    color = colorScheme.onSurfaceVariant,
                    maxLines = if (compact) 2 else 3,
                    overflow = TextOverflow.Ellipsis,
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
        Text(
            text = appName,
            style = textStyle,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
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
            label = stringResource(R.string.nav_drawer_about),
            selected = false,
            onClick = onAbout,
            icon = Icons.Filled.Info,
        )
    }
}

@Composable
private fun DrawerNavItem(
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
    icon: ImageVector,
) {
    val colorScheme = MaterialTheme.colorScheme
    NavigationDrawerItem(
        label = {
            Text(
                text = label,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
        },
        selected = selected,
        onClick = onClick,
        icon = {
            Icon(
                imageVector = icon,
                contentDescription = null,
            )
        },
        shape = DrawerItemShape,
        colors =
        NavigationDrawerItemDefaults.colors(
            selectedContainerColor = colorScheme.surfaceVariant,
            selectedIconColor = colorScheme.onSurface,
            selectedTextColor = colorScheme.onSurface,
            unselectedContainerColor = colorScheme.surface,
            unselectedIconColor = colorScheme.onSurfaceVariant,
            unselectedTextColor = colorScheme.onSurfaceVariant,
        ),
        modifier = Modifier.padding(DrawerItemPadding),
    )
}

@Preview(showBackground = true)
@Composable
private fun MainScreenPreview() {
    HskAndroidTheme(darkTheme = false) {
        MainScreen(
            themeMode = ThemeMode.Light,
            onThemeModeChange = {},
        )
    }
}
