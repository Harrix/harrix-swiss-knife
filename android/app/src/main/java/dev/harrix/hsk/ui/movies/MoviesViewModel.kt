package dev.harrix.hsk.ui.movies

import android.app.Application
import android.content.Intent
import android.net.Uri
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import dev.harrix.hsk.movies.MovieRatingBucket
import dev.harrix.hsk.movies.MovieTitle
import dev.harrix.hsk.movies.MoviesCatalog
import dev.harrix.hsk.movies.MoviesCatalogBuilder
import dev.harrix.hsk.movies.MoviesNavSection
import dev.harrix.hsk.movies.MoviesPreferences
import dev.harrix.hsk.movies.MoviesRepository
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.withContext

enum class MoviesPhase {
    Idle,
    Loading,
    Ready,
}

class MoviesViewModel(
    application: Application,
) : AndroidViewModel(application) {
    private val preferences = MoviesPreferences(application.applicationContext)
    private val repository = MoviesRepository(application.applicationContext)
    private val posterJobs = mutableSetOf<String>()
    private val posterSemaphore = Semaphore(3)

    val phase = mutableStateOf(MoviesPhase.Idle)
    val queryText = mutableStateOf("")
    val section = mutableStateOf(MoviesNavSection.All)
    val selectedYear = mutableStateOf<String?>(null)
    val selectedRating = mutableStateOf<MovieRatingBucket?>(null)
    val selectedMovieId = mutableStateOf<String?>(null)
    val folderUri = mutableStateOf<Uri?>(null)
    val folderLabel = mutableStateOf<String?>(null)
    val errorMessage = mutableStateOf<String?>(null)
    val posters = mutableStateOf<Map<String, String>>(emptyMap())

    private var catalog = MoviesCatalog(emptyList(), emptyList(), emptyList())
    private var loadJob: Job? = null

    val visibleTitles: List<MovieTitle>
        get() =
            MoviesCatalogBuilder.filter(
                catalog = catalog,
                query = queryText.value,
                section = section.value,
                year = selectedYear.value,
                bucket = selectedRating.value,
            )

    val years get() = catalog.years

    val ratings get() = catalog.ratings

    val selectedMovie: MovieTitle?
        get() = selectedMovieId.value?.let { id -> catalog.titles.firstOrNull { it.id == id } }

    val hasFolder: Boolean
        get() = folderUri.value != null

    init {
        reloadFromPreferences()
    }

    fun reloadFromPreferences() {
        val uri = preferences.getFolderUri()
        if (uri == null) {
            clearFolderState()
            return
        }
        loadUri(uri, persist = false)
    }

    fun onFolderPicked(uri: Uri) {
        val previous = preferences.getFolderUri()
        takePersistableReadPermission(uri)
        preferences.setFolderUri(uri)
        if (previous != null && previous != uri) {
            releasePersistableReadPermission(previous)
        }
        loadUri(uri, persist = false)
    }

    fun onQueryChange(value: String) {
        queryText.value = value
    }

    fun onSectionChange(value: MoviesNavSection) {
        section.value = value
        selectedMovieId.value = null
        when (value) {
            MoviesNavSection.All -> Unit

            MoviesNavSection.Years -> {
                if (selectedYear.value == null || years.none { it.label == selectedYear.value }) {
                    selectedYear.value = years.firstOrNull()?.label
                }
            }

            MoviesNavSection.Ratings -> {
                if (selectedRating.value == null || ratings.none { it.bucket == selectedRating.value }) {
                    selectedRating.value = ratings.firstOrNull()?.bucket
                }
            }
        }
    }

    fun onYearSelected(year: String) {
        selectedYear.value = year
        selectedMovieId.value = null
    }

    fun onRatingSelected(bucket: MovieRatingBucket) {
        selectedRating.value = bucket
        selectedMovieId.value = null
    }

    fun onMovieSelected(movie: MovieTitle) {
        selectedMovieId.value = movie.id
        ensurePoster(movie)
    }

    fun closeMovie() {
        selectedMovieId.value = null
    }

    fun ensurePoster(movie: MovieTitle) {
        if (posters.value.containsKey(movie.id) || posterJobs.contains(movie.id)) {
            return
        }
        val cached = repository.cachedPoster(movie)
        if (cached != null) {
            posters.value = posters.value + (movie.id to cached.absolutePath)
            return
        }
        posterJobs += movie.id
        viewModelScope.launch {
            val file =
                withContext(Dispatchers.IO) {
                    posterSemaphore.withPermit { repository.fetchPoster(movie) }
                }
            posterJobs.remove(movie.id)
            if (file != null) {
                posters.value = posters.value + (movie.id to file.absolutePath)
            }
        }
    }

    private fun loadUri(
        uri: Uri,
        persist: Boolean,
    ) {
        if (persist) {
            preferences.setFolderUri(uri)
        }
        loadJob?.cancel()
        loadJob =
            viewModelScope.launch {
                phase.value = MoviesPhase.Loading
                errorMessage.value = null
                folderUri.value = uri
                folderLabel.value = repository.folderLabel(uri)
                val outcome =
                    withContext(Dispatchers.IO) {
                        runCatching { repository.loadCatalog(uri) }
                    }
                ensureActive()
                outcome
                    .onSuccess { loaded ->
                        catalog = loaded
                        selectedMovieId.value = null
                        if (selectedYear.value == null || loaded.years.none { it.label == selectedYear.value }) {
                            selectedYear.value = loaded.years.firstOrNull()?.label
                        }
                        if (selectedRating.value == null ||
                            loaded.ratings.none { it.bucket == selectedRating.value }
                        ) {
                            selectedRating.value = loaded.ratings.firstOrNull()?.bucket
                        }
                        seedCachedPosters(loaded.titles)
                        phase.value = MoviesPhase.Ready
                    }.onFailure { error ->
                        if (error is CancellationException) {
                            throw error
                        }
                        catalog = MoviesCatalog(emptyList(), emptyList(), emptyList())
                        errorMessage.value =
                            error.message?.takeIf { it.isNotBlank() } ?: error.toString()
                        phase.value = MoviesPhase.Idle
                    }
            }
    }

    private fun seedCachedPosters(titles: List<MovieTitle>) {
        val found = mutableMapOf<String, String>()
        for (title in titles) {
            val file = repository.cachedPoster(title) ?: continue
            found[title.id] = file.absolutePath
        }
        if (found.isNotEmpty()) {
            posters.value = posters.value + found
        }
    }

    private fun clearFolderState() {
        loadJob?.cancel()
        catalog = MoviesCatalog(emptyList(), emptyList(), emptyList())
        folderUri.value = null
        folderLabel.value = null
        selectedMovieId.value = null
        errorMessage.value = null
        phase.value = MoviesPhase.Idle
    }

    private fun takePersistableReadPermission(uri: Uri) {
        val resolver = getApplication<Application>().contentResolver
        val read = Intent.FLAG_GRANT_READ_URI_PERMISSION
        val readWrite = read or Intent.FLAG_GRANT_WRITE_URI_PERMISSION
        val taken =
            runCatching {
                resolver.takePersistableUriPermission(uri, read)
            }.isSuccess
        if (!taken) {
            runCatching { resolver.takePersistableUriPermission(uri, readWrite) }
        }
    }

    private fun releasePersistableReadPermission(uri: Uri) {
        runCatching {
            getApplication<Application>().contentResolver.releasePersistableUriPermission(
                uri,
                Intent.FLAG_GRANT_READ_URI_PERMISSION,
            )
        }
    }

    override fun onCleared() {
        loadJob?.cancel()
        super.onCleared()
    }
}
