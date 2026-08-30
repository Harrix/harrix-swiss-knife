package dev.harrix.hsk.movies

/**
 * Parses movie notes: `## Title: rating` sections and `**Field:**` lines.
 * TOC inside `<details>` is ignored.
 */
object MoviesMarkdownParser {
    private val headingRegex = Regex("""^##\s+(.+):\s*(\d+(?:\.\d+)?)\s*$""")
    private val fieldRegex = Regex("""^-\s+\*\*(.+?):\*\*\s*(.*)$""")
    private val detailsBlockRegex =
        Regex("""<details\b[^>]*>.*?</details>""", setOf(RegexOption.IGNORE_CASE, RegexOption.DOT_MATCHES_ALL))
    private val markdownLinkRegex = Regex("""<(https?://[^>\s]+)>""")
    private val bareUrlRegex = Regex("""https?://[^\s)>\]]+""")
    private val imdbIdRegex = Regex("""(?:imdb\.com/title/)(tt\d+)""", RegexOption.IGNORE_CASE)
    private val imdbSeasonRegex = Regex("""[?&]season=(\d+)""", RegexOption.IGNORE_CASE)
    private val kinopoiskIdRegex =
        Regex("""kinopoisk\.ru/(?:film|series)/(\d+)""", RegexOption.IGNORE_CASE)
    private val titleSeasonRegex =
        Regex("""\(\s*(?:сезон|season)\s+(\d+)\s*\)""", RegexOption.IGNORE_CASE)
    private val tocHeadings = setOf("содержание", "contents", "toc")

    fun parse(
        markdown: String,
        yearFolder: String,
        sourceFileName: String,
    ): List<MovieWatch> {
        val withoutToc = detailsBlockRegex.replace(markdown, "")
        val watches = mutableListOf<MovieWatch>()
        val lines = withoutToc.replace("\r\n", "\n").replace('\r', '\n').split('\n')
        var index = 0
        while (index < lines.size) {
            val heading = parseHeading(lines[index])
            if (heading == null) {
                index += 1
            } else {
                val section = readSectionFields(lines, index + 1)
                watches +=
                    buildWatch(
                        title = heading.first,
                        rating = heading.second,
                        fields = section.fields,
                        yearFolder = yearFolder,
                        sourceFileName = sourceFileName,
                    )
                index = section.nextIndex
            }
        }
        return watches
    }

    fun shouldReadFile(fileName: String): Boolean {
        val name = fileName.trim()
        if (!name.endsWith(".md", ignoreCase = true)) {
            return false
        }
        if (name.endsWith(".g.md", ignoreCase = true)) {
            return false
        }
        if (name.startsWith("_")) {
            return false
        }
        val stem = name.substringBeforeLast('.')
        if (stem.contains("Критерии-оценки", ignoreCase = true) ||
            stem.contains("criteria", ignoreCase = true)
        ) {
            return false
        }
        if (stem.contains("table.include", ignoreCase = true)) {
            return false
        }
        return true
    }

    fun identityKey(
        title: String,
        imdbUrl: String?,
        kinopoiskUrl: String?,
    ): String {
        val imdbId = imdbTitleId(imdbUrl)
        val kinopoiskId = kinopoiskId(kinopoiskUrl)
        val season = seasonNumber(title, imdbUrl)
        return when {
            imdbId != null && season != null -> "imdb:$imdbId:s$season"
            imdbId != null -> "imdb:$imdbId"
            kinopoiskId != null && season != null -> "kp:$kinopoiskId:s$season"
            kinopoiskId != null -> "kp:$kinopoiskId"
            else -> "title:${normalizeTitle(title)}"
        }
    }

    fun imdbTitleId(url: String?): String? {
        val raw = url?.trim().orEmpty()
        if (raw.isEmpty()) {
            return null
        }
        return imdbIdRegex.find(raw)?.groupValues?.get(1)?.lowercase()
    }

    fun kinopoiskId(url: String?): String? {
        val raw = url?.trim().orEmpty()
        if (raw.isEmpty()) {
            return null
        }
        return kinopoiskIdRegex.find(raw)?.groupValues?.get(1)
    }

    fun usableUrl(raw: String?): String? {
        val text = raw?.trim().orEmpty()
        if (text.isEmpty()) {
            return null
        }
        val fromAngle = markdownLinkRegex.find(text)?.groupValues?.get(1)
        val candidate = (fromAngle ?: bareUrlRegex.find(text)?.value ?: text).trimEnd('.', ',', ';')
        if (!candidate.startsWith("http://") && !candidate.startsWith("https://")) {
            return null
        }
        val kinopoiskId = kinopoiskId(candidate)
        if (candidate.contains("kinopoisk.ru", ignoreCase = true) && kinopoiskId == null) {
            return null
        }
        return candidate
    }

    fun formatRating(rating: Double?): String {
        if (rating == null) {
            return ""
        }
        val asInt = rating.toInt()
        return if (rating == asInt.toDouble()) {
            asInt.toString()
        } else {
            rating.toString()
        }
    }

    private data class SectionFields(
        val fields: Map<String, String>,
        val nextIndex: Int,
    )

    private fun readSectionFields(
        lines: List<String>,
        startIndex: Int,
    ): SectionFields {
        val fields = linkedMapOf<String, String>()
        var index = startIndex
        while (index < lines.size && !lines[index].startsWith("## ")) {
            val field = fieldRegex.find(lines[index])
            if (field == null) {
                index += 1
            } else {
                val value = readFieldValue(lines, index, field)
                fields[field.groupValues[1].trim()] = value.text
                index = value.nextIndex
            }
        }
        return SectionFields(fields = fields, nextIndex = index)
    }

    private data class FieldValue(
        val text: String,
        val nextIndex: Int,
    )

    private fun readFieldValue(
        lines: List<String>,
        startIndex: Int,
        field: MatchResult,
    ): FieldValue {
        val extra = mutableListOf<String>()
        val first = field.groupValues[2].trim()
        if (first.isNotEmpty()) {
            extra += first
        }
        var index = startIndex + 1
        while (index < lines.size &&
            !lines[index].startsWith("## ") &&
            !fieldRegex.containsMatchIn(lines[index])
        ) {
            if (lines[index].isNotBlank()) {
                extra += lines[index].trim()
            }
            index += 1
        }
        return FieldValue(text = extra.joinToString("\n").trim(), nextIndex = index)
    }

    private fun parseHeading(line: String): Pair<String, Double>? {
        val match = headingRegex.find(line.trim()) ?: return null
        val title = match.groupValues[1].trim()
        if (title.isEmpty() || title.lowercase() in tocHeadings) {
            return null
        }
        val rating = match.groupValues[2].toDoubleOrNull() ?: return null
        return title to rating
    }

    private fun buildWatch(
        title: String,
        rating: Double,
        fields: Map<String, String>,
        yearFolder: String,
        sourceFileName: String,
    ): MovieWatch {
        val knownKeys =
            setOf(
                "original or english title",
                "original title",
                "english title",
                "date watching",
                "kinopoisk",
                "imdb",
                "review",
            )
        val original = firstField(fields, "Original or English title", "Original title", "English title")
        val dateWatching = firstField(fields, "Date watching")
        val kinopoiskUrl = usableUrl(firstField(fields, "Kinopoisk"))
        val imdbUrl = usableUrl(firstField(fields, "IMDb", "IMDB"))
        val review = firstField(fields, "Review")
        val extra =
            fields
                .filterKeys { key -> key.lowercase() !in knownKeys }
                .map { it.key to it.value }
        return MovieWatch(
            title = title,
            rating = rating,
            originalTitle = original,
            dateWatching = dateWatching,
            kinopoiskUrl = kinopoiskUrl,
            imdbUrl = imdbUrl,
            review = review,
            extraFields = extra,
            yearFolder = yearFolder,
            sourceFileName = sourceFileName,
            identityKey = identityKey(title, imdbUrl, kinopoiskUrl),
            imdbTitleId = imdbTitleId(imdbUrl),
            kinopoiskId = kinopoiskId(kinopoiskUrl),
        )
    }

    private fun firstField(
        fields: Map<String, String>,
        vararg keys: String,
    ): String? {
        for (key in keys) {
            val value = fields.entries.firstOrNull { it.key.equals(key, ignoreCase = true) }?.value
            if (!value.isNullOrBlank()) {
                return value.trim()
            }
        }
        return null
    }

    private fun seasonNumber(
        title: String,
        imdbUrl: String?,
    ): Int? {
        val fromTitle = titleSeasonRegex.find(title)?.groupValues?.get(1)?.toIntOrNull()
        if (fromTitle != null) {
            return fromTitle
        }
        return imdbSeasonRegex.find(imdbUrl.orEmpty())?.groupValues?.get(1)?.toIntOrNull()
    }

    private fun normalizeTitle(title: String): String = title
        .lowercase()
        .replace('ё', 'е')
        .replace(Regex("""\s+"""), " ")
        .trim()
}
