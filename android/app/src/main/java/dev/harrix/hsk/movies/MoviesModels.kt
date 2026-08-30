package dev.harrix.hsk.movies

/**
 * One `## Title: rating` block from a year Markdown file.
 */
data class MovieWatch(
    val title: String,
    val rating: Double?,
    val originalTitle: String?,
    val dateWatching: String?,
    val kinopoiskUrl: String?,
    val imdbUrl: String?,
    val review: String?,
    val extraFields: List<Pair<String, String>>,
    val yearFolder: String,
    val sourceFileName: String,
    val identityKey: String,
    val imdbTitleId: String?,
    val kinopoiskId: String?,
)

/**
 * All watches of the same film or season, newest first.
 */
data class MovieTitle(
    val id: String,
    val title: String,
    val originalTitle: String?,
    val latestRating: Double?,
    val latestDate: String?,
    val yearFolders: List<String>,
    val watches: List<MovieWatch>,
    val imdbUrl: String?,
    val kinopoiskUrl: String?,
) {
    val watchCount: Int
        get() = watches.size

    val ratingBucket: MovieRatingBucket
        get() = MovieRatingBucket.from(latestRating)
}

enum class MovieRatingBucket {
    Exceptional,
    Excellent,
    AlmostTen,
    Good,
    OneTime,
    Disliked,
    Bad,
    Unrated,
    ;

    companion object {
        fun from(rating: Double?): MovieRatingBucket {
            if (rating == null) {
                return Unrated
            }
            return when {
                rating >= 11.0 -> Exceptional
                rating >= 10.0 -> Excellent
                rating >= 9.0 -> AlmostTen
                rating >= 8.0 -> Good
                rating >= 7.0 -> OneTime
                rating >= 6.0 -> Disliked
                else -> Bad
            }
        }
    }
}

enum class MoviesNavSection {
    All,
    Years,
    Ratings,
}

data class MoviesYearGroup(
    val label: String,
    val count: Int,
)

data class MoviesRatingGroup(
    val bucket: MovieRatingBucket,
    val count: Int,
)

data class MoviesCatalog(
    val titles: List<MovieTitle>,
    val years: List<MoviesYearGroup>,
    val ratings: List<MoviesRatingGroup>,
)
