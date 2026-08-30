package dev.harrix.hsk.movies

/**
 * Groups watches of the same film or season and builds year / rating indexes.
 */
object MoviesCatalogBuilder {
    fun build(watches: List<MovieWatch>): MoviesCatalog {
        val titles =
            watches
                .groupBy { it.identityKey }
                .map { (id, group) -> toTitle(id, group) }
                .sortedWith(compareByDescending<MovieTitle> { dateSortKey(it.latestDate) }.thenBy { it.title.lowercase() })
        val years =
            titles
                .flatMap { title -> title.yearFolders.map { year -> year to title.id } }
                .groupBy({ it.first }, { it.second })
                .map { (label, ids) -> MoviesYearGroup(label = label, count = ids.distinct().size) }
                .sortedWith(compareBy({ it.label.toIntOrNull() == null }, { -(it.label.toIntOrNull() ?: 0) }, { it.label }))
        val ratings =
            MovieRatingBucket.entries
                .filter { it != MovieRatingBucket.Unrated }
                .map { bucket ->
                    MoviesRatingGroup(
                        bucket = bucket,
                        count = titles.count { it.ratingBucket == bucket },
                    )
                }.filter { it.count > 0 }
        return MoviesCatalog(titles = titles, years = years, ratings = ratings)
    }

    fun filter(
        catalog: MoviesCatalog,
        query: String,
        section: MoviesNavSection,
        year: String?,
        bucket: MovieRatingBucket?,
    ): List<MovieTitle> {
        val needle = query.trim().lowercase()
        return catalog.titles.filter { title ->
            matchesQuery(title, needle) &&
                when (section) {
                    MoviesNavSection.All -> true
                    MoviesNavSection.Years -> year.isNullOrBlank() || year in title.yearFolders
                    MoviesNavSection.Ratings -> bucket == null || title.ratingBucket == bucket
                }
        }
    }

    private fun matchesQuery(
        title: MovieTitle,
        needle: String,
    ): Boolean {
        if (needle.isEmpty()) {
            return true
        }
        if (title.title.lowercase().contains(needle)) {
            return true
        }
        if (title.originalTitle?.lowercase()?.contains(needle) == true) {
            return true
        }
        return title.watches.any { watch ->
            watch.review?.lowercase()?.contains(needle) == true ||
                watch.dateWatching?.lowercase()?.contains(needle) == true ||
                watch.yearFolder.lowercase().contains(needle) ||
                watch.extraFields.any { (key, value) ->
                    key.lowercase().contains(needle) || value.lowercase().contains(needle)
                }
        }
    }

    private fun toTitle(
        id: String,
        group: List<MovieWatch>,
    ): MovieTitle {
        val watches = group.sortedByDescending { dateSortKey(it.dateWatching) }
        val latest = watches.first()
        return MovieTitle(
            id = id,
            title = latest.title,
            originalTitle = watches.firstNotNullOfOrNull { it.originalTitle },
            latestRating = latest.rating,
            latestDate = latest.dateWatching,
            yearFolders =
            watches
                .map { it.yearFolder }
                .filter { it.isNotBlank() }
                .distinct(),
            watches = watches,
            imdbUrl = watches.firstNotNullOfOrNull { it.imdbUrl },
            kinopoiskUrl = watches.firstNotNullOfOrNull { it.kinopoiskUrl },
        )
    }

    private fun dateSortKey(raw: String?): String {
        val value = raw?.trim().orEmpty()
        if (value.isEmpty()) {
            return ""
        }
        return value
    }
}
