package dev.harrix.hsk.ui.movies

import android.content.ActivityNotFoundException
import android.content.Intent
import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.BackHandler
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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.FolderOpen
import androidx.compose.material.icons.filled.Movie
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import coil.request.ImageRequest
import dev.harrix.hsk.R
import dev.harrix.hsk.movies.MovieRatingBucket
import dev.harrix.hsk.movies.MovieTitle
import dev.harrix.hsk.movies.MovieWatch
import dev.harrix.hsk.movies.MoviesMarkdownParser
import dev.harrix.hsk.movies.MoviesNavSection
import dev.harrix.hsk.movies.MoviesRatingGroup
import dev.harrix.hsk.movies.MoviesYearGroup
import dev.harrix.hsk.ui.AutoFitText
import dev.harrix.hsk.ui.adaptiveContentWidth
import dev.harrix.hsk.ui.theme.HskTopAppBarHeight
import dev.harrix.hsk.ui.theme.hskScaffoldContainerColor
import dev.harrix.hsk.ui.theme.hskScaffoldContentWindowInsets
import dev.harrix.hsk.ui.theme.hskTopAppBarColors
import dev.harrix.hsk.ui.theme.hskTopAppBarWindowInsets
import java.io.File

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MoviesScreen(
    onClose: () -> Unit,
    onOpenSettings: () -> Unit,
    settingsRevision: Int,
    modifier: Modifier = Modifier,
    viewModel: MoviesViewModel = viewModel(),
) {
    val phase by viewModel.phase
    val queryText by viewModel.queryText
    val section by viewModel.section
    val selectedYear by viewModel.selectedYear
    val selectedRating by viewModel.selectedRating
    val folderLabel by viewModel.folderLabel
    val errorMessage by viewModel.errorMessage
    val posters by viewModel.posters
    val selectedMovie = viewModel.selectedMovie
    val titles = viewModel.visibleTitles
    val years = viewModel.years
    val ratings = viewModel.ratings
    val hasFolder = viewModel.hasFolder
    val context = LocalContext.current
    val keyboard = LocalSoftwareKeyboardController.current
    val openFailed = stringResource(R.string.movies_open_link_failed)

    val openTree =
        rememberLauncherForActivityResult(
            ActivityResultContracts.OpenDocumentTree(),
        ) { uri ->
            if (uri != null) {
                viewModel.onFolderPicked(uri)
            }
        }

    fun pickFolder() {
        openTree.launch(null)
    }

    fun openLink(url: String) {
        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
        try {
            context.startActivity(intent)
        } catch (_: ActivityNotFoundException) {
            Toast.makeText(context, openFailed, Toast.LENGTH_SHORT).show()
        } catch (_: SecurityException) {
            Toast.makeText(context, openFailed, Toast.LENGTH_SHORT).show()
        }
    }

    fun leave() {
        if (selectedMovie != null) {
            viewModel.closeMovie()
        } else {
            onClose()
        }
    }

    BackHandler(onBack = { leave() })

    LaunchedEffect(settingsRevision) {
        viewModel.reloadFromPreferences()
    }

    Scaffold(
        modifier = modifier.fillMaxSize(),
        containerColor = hskScaffoldContainerColor(),
        contentWindowInsets = hskScaffoldContentWindowInsets(),
        topBar = {
            TopAppBar(
                title = {
                    AutoFitText(
                        text =
                        if (selectedMovie != null) {
                            selectedMovie.title
                        } else {
                            stringResource(R.string.movies_title)
                        },
                        maxLines = 1,
                    )
                },
                colors = hskTopAppBarColors(),
                windowInsets = hskTopAppBarWindowInsets(),
                expandedHeight = HskTopAppBarHeight,
                navigationIcon = {
                    IconButton(onClick = { leave() }) {
                        Icon(
                            imageVector =
                            if (selectedMovie != null) {
                                Icons.AutoMirrored.Filled.ArrowBack
                            } else {
                                Icons.Filled.Close
                            },
                            contentDescription =
                            if (selectedMovie != null) {
                                stringResource(R.string.movies_back)
                            } else {
                                stringResource(R.string.movies_close)
                            },
                        )
                    }
                },
                actions = {
                    if (selectedMovie == null) {
                        IconButton(onClick = onOpenSettings) {
                            Icon(
                                imageVector = Icons.Filled.Settings,
                                contentDescription = stringResource(R.string.movies_settings),
                            )
                        }
                    }
                },
            )
        },
        bottomBar = {
            if (selectedMovie == null && hasFolder && phase == MoviesPhase.Ready) {
                MoviesNavigationBar(
                    section = section,
                    onSectionChange = viewModel::onSectionChange,
                )
            }
        },
    ) { innerPadding ->
        Box(
            modifier =
            Modifier
                .padding(innerPadding)
                .fillMaxSize(),
        ) {
            when {
                selectedMovie != null -> {
                    MovieDetailPane(
                        movie = selectedMovie,
                        posterPath = posters[selectedMovie.id],
                        onOpenLink = ::openLink,
                        modifier = Modifier.fillMaxSize(),
                    )
                    LaunchedEffect(selectedMovie.id) {
                        viewModel.ensurePoster(selectedMovie)
                    }
                }

                !hasFolder -> {
                    MoviesEmptyFolder(
                        onPickFolder = ::pickFolder,
                        modifier = Modifier.fillMaxSize(),
                    )
                }

                phase == MoviesPhase.Loading -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center,
                    ) {
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(12.dp),
                        ) {
                            CircularProgressIndicator()
                            Text(
                                text = stringResource(R.string.movies_loading),
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }

                else -> {
                    MoviesBrowsePane(
                        queryText = queryText,
                        onQueryChange = viewModel::onQueryChange,
                        onSearch = { keyboard?.hide() },
                        folderLabel = folderLabel,
                        errorMessage = errorMessage,
                        section = section,
                        years = years,
                        ratings = ratings,
                        selectedYear = selectedYear,
                        selectedRating = selectedRating,
                        onYearChange = viewModel::onYearSelected,
                        onRatingChange = viewModel::onRatingSelected,
                        titles = titles,
                        posters = posters,
                        onMovieOpen = viewModel::onMovieSelected,
                        onEnsurePoster = viewModel::ensurePoster,
                        onPickFolder = ::pickFolder,
                        modifier = Modifier.fillMaxSize(),
                    )
                }
            }
        }
    }
}

@Composable
private fun MoviesNavigationBar(
    section: MoviesNavSection,
    onSectionChange: (MoviesNavSection) -> Unit,
    modifier: Modifier = Modifier,
) {
    NavigationBar(modifier = modifier) {
        NavigationBarItem(
            selected = section == MoviesNavSection.All,
            onClick = { onSectionChange(MoviesNavSection.All) },
            icon = {
                Icon(
                    imageVector = Icons.Filled.Search,
                    contentDescription = null,
                )
            },
            label = { Text(text = stringResource(R.string.movies_nav_all)) },
        )
        NavigationBarItem(
            selected = section == MoviesNavSection.Years,
            onClick = { onSectionChange(MoviesNavSection.Years) },
            icon = {
                Icon(
                    imageVector = Icons.Filled.DateRange,
                    contentDescription = null,
                )
            },
            label = { Text(text = stringResource(R.string.movies_nav_years)) },
        )
        NavigationBarItem(
            selected = section == MoviesNavSection.Ratings,
            onClick = { onSectionChange(MoviesNavSection.Ratings) },
            icon = {
                Icon(
                    imageVector = Icons.Filled.Star,
                    contentDescription = null,
                )
            },
            label = { Text(text = stringResource(R.string.movies_nav_ratings)) },
        )
    }
}

@Composable
private fun MoviesEmptyFolder(
    onPickFolder: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier =
        modifier
            .adaptiveContentWidth()
            .padding(horizontal = 24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Icon(
            imageVector = Icons.Filled.Movie,
            contentDescription = null,
            modifier = Modifier.size(48.dp),
            tint = MaterialTheme.colorScheme.primary,
        )
        Spacer(modifier = Modifier.height(12.dp))
        Text(
            text = stringResource(R.string.movies_empty_title),
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center,
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = stringResource(R.string.movies_empty_message),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
        )
        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = onPickFolder) {
            Icon(
                imageVector = Icons.Filled.FolderOpen,
                contentDescription = null,
                modifier = Modifier.size(18.dp),
            )
            Spacer(modifier = Modifier.size(8.dp))
            Text(text = stringResource(R.string.movies_pick_folder))
        }
    }
}

@Composable
private fun MoviesBrowsePane(
    queryText: String,
    onQueryChange: (String) -> Unit,
    onSearch: () -> Unit,
    folderLabel: String?,
    errorMessage: String?,
    section: MoviesNavSection,
    years: List<MoviesYearGroup>,
    ratings: List<MoviesRatingGroup>,
    selectedYear: String?,
    selectedRating: MovieRatingBucket?,
    onYearChange: (String) -> Unit,
    onRatingChange: (MovieRatingBucket) -> Unit,
    titles: List<MovieTitle>,
    posters: Map<String, String>,
    onMovieOpen: (MovieTitle) -> Unit,
    onEnsurePoster: (MovieTitle) -> Unit,
    onPickFolder: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier =
        modifier
            .adaptiveContentWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        OutlinedTextField(
            value = queryText,
            onValueChange = onQueryChange,
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            leadingIcon = {
                Icon(
                    imageVector = Icons.Filled.Search,
                    contentDescription = null,
                )
            },
            placeholder = { Text(text = stringResource(R.string.movies_search_hint)) },
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
            keyboardActions = KeyboardActions(onSearch = { onSearch() }),
        )
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text =
                stringResource(
                    R.string.movies_folder_label,
                    folderLabel ?: stringResource(R.string.movies_folder_unnamed),
                ),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.weight(1f),
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            OutlinedButton(
                onClick = onPickFolder,
                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp),
            ) {
                Text(text = stringResource(R.string.movies_change_folder))
            }
        }
        if (!errorMessage.isNullOrBlank()) {
            Text(
                text = errorMessage,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.error,
            )
        }
        when (section) {
            MoviesNavSection.All -> Unit

            MoviesNavSection.Years -> {
                MoviesYearChips(
                    years = years,
                    selectedYear = selectedYear,
                    onYearChange = onYearChange,
                )
            }

            MoviesNavSection.Ratings -> {
                MoviesRatingChips(
                    ratings = ratings,
                    selectedRating = selectedRating,
                    onRatingChange = onRatingChange,
                )
            }
        }
        if (titles.isEmpty()) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = stringResource(R.string.movies_no_results),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center,
                )
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.spacedBy(8.dp),
                contentPadding = PaddingValues(bottom = 16.dp),
            ) {
                items(titles, key = { it.id }) { movie ->
                    MovieListRow(
                        movie = movie,
                        posterPath = posters[movie.id],
                        onClick = { onMovieOpen(movie) },
                        onVisible = { onEnsurePoster(movie) },
                    )
                }
            }
        }
    }
}

@Composable
private fun MoviesYearChips(
    years: List<MoviesYearGroup>,
    selectedYear: String?,
    onYearChange: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier.horizontalScroll(rememberScrollState()),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        years.forEach { year ->
            FilterChip(
                selected = year.label == selectedYear,
                onClick = { onYearChange(year.label) },
                label = {
                    Text(text = stringResource(R.string.movies_chip_count, year.label, year.count))
                },
            )
        }
    }
}

@Composable
private fun MoviesRatingChips(
    ratings: List<MoviesRatingGroup>,
    selectedRating: MovieRatingBucket?,
    onRatingChange: (MovieRatingBucket) -> Unit,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier.horizontalScroll(rememberScrollState()),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        ratings.forEach { group ->
            FilterChip(
                selected = group.bucket == selectedRating,
                onClick = { onRatingChange(group.bucket) },
                label = {
                    Text(
                        text =
                        stringResource(
                            R.string.movies_chip_count,
                            ratingBucketLabel(group.bucket),
                            group.count,
                        ),
                    )
                },
            )
        }
    }
}

@Composable
private fun MovieListRow(
    movie: MovieTitle,
    posterPath: String?,
    onClick: () -> Unit,
    onVisible: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val latestOnVisible by rememberUpdatedState(onVisible)
    LaunchedEffect(movie.id) {
        latestOnVisible()
    }
    Surface(
        modifier =
        modifier
            .fillMaxWidth()
            .clickable(role = Role.Button, onClick = onClick),
        shape = RoundedCornerShape(12.dp),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.45f),
    ) {
        Row(
            modifier = Modifier.padding(10.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            MoviePoster(
                posterPath = posterPath,
                contentDescription = stringResource(R.string.movies_poster),
                modifier = Modifier.size(width = 56.dp, height = 84.dp),
            )
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(2.dp),
            ) {
                Text(
                    text = movie.title,
                    style = MaterialTheme.typography.titleMedium,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                )
                movie.originalTitle?.let { original ->
                    Text(
                        text = original,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                    )
                }
                Text(
                    text = watchSummary(movie),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            movie.latestRating?.let { rating ->
                Text(
                    text = MoviesMarkdownParser.formatRating(rating),
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.primary,
                )
            }
        }
    }
}

@Composable
private fun MovieDetailPane(
    movie: MovieTitle,
    posterPath: String?,
    onOpenLink: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier =
        modifier
            .verticalScroll(rememberScrollState())
            .adaptiveContentWidth()
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Row(
            horizontalArrangement = Arrangement.spacedBy(16.dp),
            verticalAlignment = Alignment.Top,
        ) {
            MoviePoster(
                posterPath = posterPath,
                contentDescription = stringResource(R.string.movies_poster),
                modifier = Modifier.size(width = 120.dp, height = 180.dp),
            )
            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                movie.latestRating?.let { rating ->
                    Text(
                        text =
                        stringResource(
                            R.string.movies_rating_value,
                            MoviesMarkdownParser.formatRating(rating),
                        ),
                        style = MaterialTheme.typography.headlineSmall,
                        color = MaterialTheme.colorScheme.primary,
                    )
                    Text(
                        text = ratingBucketDescription(movie.ratingBucket),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                movie.originalTitle?.let { original ->
                    Text(
                        text = stringResource(R.string.movies_original_title, original),
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
                Text(
                    text = watchSummary(movie),
                    style = MaterialTheme.typography.bodyMedium,
                )
                movie.latestDate?.let { date ->
                    Text(
                        text = stringResource(R.string.movies_last_watched, date),
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            movie.imdbUrl?.let { url ->
                Button(onClick = { onOpenLink(url) }) {
                    Text(text = stringResource(R.string.movies_imdb))
                }
            }
            movie.kinopoiskUrl?.let { url ->
                OutlinedButton(onClick = { onOpenLink(url) }) {
                    Text(text = stringResource(R.string.movies_kinopoisk))
                }
            }
        }
        if (movie.watches.size > 1) {
            Text(
                text = stringResource(R.string.movies_watch_history),
                style = MaterialTheme.typography.titleSmall,
            )
            movie.watches.forEach { watch ->
                WatchHistoryRow(watch = watch)
            }
        } else {
            movie.watches.firstOrNull()?.let { watch ->
                WatchFields(watch = watch)
                watch.review?.takeIf { it.isNotBlank() }?.let { review ->
                    Text(
                        text = stringResource(R.string.movies_review),
                        style = MaterialTheme.typography.titleSmall,
                    )
                    Text(
                        text = review,
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }
        }
    }
}

@Composable
private fun WatchHistoryRow(
    watch: MovieWatch,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        val rating = MoviesMarkdownParser.formatRating(watch.rating)
        val date = watch.dateWatching ?: watch.yearFolder
        Text(
            text =
            if (rating.isEmpty()) {
                date
            } else {
                stringResource(R.string.movies_watch_line, date, rating)
            },
            style = MaterialTheme.typography.bodyMedium,
        )
        watch.review?.takeIf { it.isNotBlank() }?.let { review ->
            Text(
                text = review,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun WatchFields(
    watch: MovieWatch,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        watch.dateWatching?.let { date ->
            Text(
                text = stringResource(R.string.movies_date_watching, date),
                style = MaterialTheme.typography.bodyMedium,
            )
        }
        watch.extraFields.forEach { (key, value) ->
            Text(
                text = "$key: $value",
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
}

@Composable
private fun MoviePoster(
    posterPath: String?,
    contentDescription: String,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    Surface(
        modifier = modifier.clip(RoundedCornerShape(8.dp)),
        color = MaterialTheme.colorScheme.surfaceVariant,
    ) {
        if (posterPath.isNullOrBlank()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Icon(
                    imageVector = Icons.Filled.Movie,
                    contentDescription = contentDescription,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        } else {
            AsyncImage(
                model =
                ImageRequest
                    .Builder(context)
                    .data(File(posterPath))
                    .crossfade(true)
                    .build(),
                contentDescription = contentDescription,
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop,
            )
        }
    }
}

@Composable
private fun watchSummary(movie: MovieTitle): String = if (movie.watchCount <= 1) {
    stringResource(R.string.movies_watched_once)
} else {
    stringResource(R.string.movies_watched_times, movie.watchCount)
}

@Composable
private fun ratingBucketLabel(bucket: MovieRatingBucket): String = when (bucket) {
    MovieRatingBucket.Exceptional -> stringResource(R.string.movies_rating_11_label)
    MovieRatingBucket.Excellent -> stringResource(R.string.movies_rating_10_label)
    MovieRatingBucket.AlmostTen -> stringResource(R.string.movies_rating_9_label)
    MovieRatingBucket.Good -> stringResource(R.string.movies_rating_8_label)
    MovieRatingBucket.OneTime -> stringResource(R.string.movies_rating_7_label)
    MovieRatingBucket.Disliked -> stringResource(R.string.movies_rating_6_label)
    MovieRatingBucket.Bad -> stringResource(R.string.movies_rating_1_5_label)
    MovieRatingBucket.Unrated -> stringResource(R.string.movies_rating_other)
}

@Composable
private fun ratingBucketDescription(bucket: MovieRatingBucket): String = when (bucket) {
    MovieRatingBucket.Exceptional -> stringResource(R.string.movies_rating_11)
    MovieRatingBucket.Excellent -> stringResource(R.string.movies_rating_10)
    MovieRatingBucket.AlmostTen -> stringResource(R.string.movies_rating_9)
    MovieRatingBucket.Good -> stringResource(R.string.movies_rating_8)
    MovieRatingBucket.OneTime -> stringResource(R.string.movies_rating_7)
    MovieRatingBucket.Disliked -> stringResource(R.string.movies_rating_6)
    MovieRatingBucket.Bad -> stringResource(R.string.movies_rating_1_5)
    MovieRatingBucket.Unrated -> stringResource(R.string.movies_rating_other)
}
