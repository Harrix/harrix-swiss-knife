package dev.harrix.hsk.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.NavigationDrawerItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import dev.harrix.hsk.R
import dev.harrix.hsk.ui.theme.AppBackground
import dev.harrix.hsk.ui.theme.ContentSurface
import dev.harrix.hsk.ui.theme.DrawerSelectedContainer
import dev.harrix.hsk.ui.theme.HskAndroidTheme
import kotlinx.coroutines.launch

private const val BottomBarItemCount = 5
private val BottomBarHeight = 52.dp
private val BottomButtonSize = 40.dp
private val BottomIconSize = 20.dp
private val BottomIconTint = Color(0xFF5C5F66)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(modifier: Modifier = Modifier) {
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val scope = rememberCoroutineScope()
    val appName = stringResource(R.string.app_name)
    val drawerItemColors =
        NavigationDrawerItemDefaults.colors(
            selectedContainerColor = DrawerSelectedContainer,
        )

    ModalNavigationDrawer(
        drawerState = drawerState,
        modifier = modifier,
        drawerContent = {
            ModalDrawerSheet {
                Text(
                    text = appName,
                    style = MaterialTheme.typography.titleLarge,
                    modifier = Modifier.padding(horizontal = 28.dp, vertical = 24.dp),
                )
                HorizontalDivider(modifier = Modifier.padding(bottom = 8.dp))
                NavigationDrawerItem(
                    label = { Text(stringResource(R.string.nav_drawer_home)) },
                    selected = true,
                    onClick = { scope.launch { drawerState.close() } },
                    icon = {
                        Icon(Icons.AutoMirrored.Filled.List, contentDescription = null)
                    },
                    colors = drawerItemColors,
                    modifier = Modifier.padding(horizontal = 12.dp),
                )
                NavigationDrawerItem(
                    label = { Text(stringResource(R.string.nav_drawer_about)) },
                    selected = false,
                    onClick = { scope.launch { drawerState.close() } },
                    icon = {
                        Icon(Icons.Filled.Info, contentDescription = null)
                    },
                    colors = drawerItemColors,
                    modifier = Modifier.padding(horizontal = 12.dp),
                )
            }
        },
    ) {
        Scaffold(
            containerColor = AppBackground,
            contentWindowInsets = WindowInsets(0, 0, 0, 0),
            topBar = {
                TopAppBar(
                    title = { Text(appName) },
                    navigationIcon = {
                        IconButton(
                            onClick = { scope.launch { drawerState.open() } },
                        ) {
                            Icon(
                                imageVector = Icons.Filled.Menu,
                                contentDescription = stringResource(R.string.nav_open),
                            )
                        }
                    },
                    actions = {
                        IconButton(onClick = {}) {
                            Icon(
                                imageVector = Icons.Filled.MoreVert,
                                contentDescription = stringResource(R.string.nav_settings),
                            )
                        }
                    },
                    colors =
                        TopAppBarDefaults.topAppBarColors(
                            containerColor = AppBackground,
                            scrolledContainerColor = AppBackground,
                        ),
                )
            },
            bottomBar = { BottomActionBar() },
        ) { innerPadding ->
            Surface(
                modifier =
                    Modifier
                        .padding(innerPadding)
                        .fillMaxSize(),
                color = ContentSurface,
                shadowElevation = 0.dp,
                tonalElevation = 0.dp,
            ) {
                Column(
                    modifier =
                        Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState())
                            .padding(20.dp),
                ) {
                    Text(
                        text = stringResource(R.string.main_content_placeholder),
                        style = MaterialTheme.typography.bodyLarge,
                    )
                }
            }
        }
    }
}

@Composable
private fun BottomActionBar(modifier: Modifier = Modifier) {
    val contentDescription = stringResource(R.string.bottom_nav_item)

    Column(
        modifier =
            modifier
                .fillMaxWidth()
                .background(AppBackground)
                .windowInsetsPadding(WindowInsets.navigationBars),
    ) {
        HorizontalDivider(color = Color(0xFFD0D2D7), thickness = 1.dp)
        Row(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .height(BottomBarHeight)
                    .padding(horizontal = 8.dp),
            horizontalArrangement = Arrangement.SpaceEvenly,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            repeat(BottomBarItemCount) {
                IconButton(
                    onClick = {},
                    modifier = Modifier.size(BottomButtonSize),
                ) {
                    Icon(
                        imageVector = Icons.Filled.Menu,
                        contentDescription = contentDescription,
                        tint = BottomIconTint,
                        modifier = Modifier.size(BottomIconSize),
                    )
                }
            }
        }
    }
}

@Preview(showBackground = true, backgroundColor = 0xFFE5E6EA)
@Composable
private fun MainScreenPreview() {
    HskAndroidTheme(darkTheme = false) {
        MainScreen()
    }
}
