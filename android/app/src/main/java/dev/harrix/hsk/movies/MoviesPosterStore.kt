package dev.harrix.hsk.movies

import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.File
import java.util.concurrent.TimeUnit

/**
 * Loads a poster from the IMDb title page (`og:image`), then Kinopoisk.
 * Successful images and recent failures are cached under the app files dir.
 */
class MoviesPosterStore(
    private val cacheDir: File,
    private val client: OkHttpClient = defaultClient(),
) {
    fun cachedFile(movie: MovieTitle): File? {
        val key = cacheKey(movie) ?: return null
        val file = File(cacheDir, "$key.jpg")
        return file.takeIf { it.isFile && it.length() > 0L }
    }

    fun fetch(movie: MovieTitle): File? {
        val key = cacheKey(movie) ?: return null
        val file = File(cacheDir, "$key.jpg")
        if (file.isFile && file.length() > 0L) {
            return file
        }
        if (failedRecently(key)) {
            return null
        }
        cacheDir.mkdirs()
        val pageUrls = pageUrls(movie)
        for (pageUrl in pageUrls) {
            val imageUrl = scrapeOgImage(pageUrl) ?: continue
            if (downloadImage(imageUrl, file)) {
                failMarker(key).delete()
                return file
            }
        }
        markFailed(key)
        return null
    }

    private fun pageUrls(movie: MovieTitle): List<String> {
        val urls = mutableListOf<String>()
        val imdbId = MoviesMarkdownParser.imdbTitleId(movie.imdbUrl)
        if (imdbId != null) {
            urls += "https://www.imdb.com/title/$imdbId/"
        }
        val kinopoisk = movie.kinopoiskUrl?.trim()
        if (!kinopoisk.isNullOrEmpty()) {
            urls += kinopoisk
        }
        return urls
    }

    private fun scrapeOgImage(pageUrl: String): String? {
        val html = fetchText(pageUrl) ?: return null
        val tag =
            OG_IMAGE_TAG.find(html)?.value
                ?: OG_IMAGE_NAME_TAG.find(html)?.value
                ?: return null
        val content = CONTENT_ATTR.find(tag)?.groupValues?.get(1) ?: return null
        val resolved = resolveUrl(pageUrl, content.trim())
        return resolved.takeIf { it.startsWith("http://") || it.startsWith("https://") }
    }

    private fun fetchText(url: String): String? {
        val request =
            Request
                .Builder()
                .url(url)
                .header("User-Agent", USER_AGENT)
                .header("Accept", "text/html,application/xhtml+xml")
                .header("Accept-Language", "en-US,en;q=0.9,ru;q=0.8")
                .build()
        return runCatching {
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    return@use null
                }
                val body = response.body?.string().orEmpty()
                body.takeIf { it.isNotBlank() }
            }
        }.getOrNull()
    }

    private fun downloadImage(
        url: String,
        dest: File,
    ): Boolean {
        val request =
            Request
                .Builder()
                .url(url)
                .header("User-Agent", USER_AGENT)
                .header("Accept", "image/avif,image/webp,image/apng,image/*,*/*;q=0.8")
                .build()
        return runCatching {
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    return@use false
                }
                val bytes = response.body?.bytes() ?: return@use false
                if (bytes.isEmpty() || bytes.size > MAX_IMAGE_BYTES) {
                    return@use false
                }
                val contentType = response.header("Content-Type").orEmpty()
                if (contentType.isNotEmpty() && !contentType.startsWith("image/")) {
                    return@use false
                }
                dest.outputStream().use { output -> output.write(bytes) }
                dest.isFile && dest.length() > 0L
            }
        }.getOrDefault(false)
    }

    private fun cacheKey(movie: MovieTitle): String? {
        val imdb = MoviesMarkdownParser.imdbTitleId(movie.imdbUrl)
        if (imdb != null) {
            return imdb
        }
        val kinopoisk = MoviesMarkdownParser.kinopoiskId(movie.kinopoiskUrl)
        if (kinopoisk != null) {
            return "kp$kinopoisk"
        }
        return null
    }

    private fun failedRecently(key: String): Boolean {
        val marker = failMarker(key)
        if (!marker.isFile) {
            return false
        }
        val ageMs = System.currentTimeMillis() - marker.lastModified()
        return ageMs in 0 until FAIL_TTL_MS
    }

    private fun markFailed(key: String) {
        runCatching { failMarker(key).writeText("1") }
    }

    private fun failMarker(key: String): File = File(cacheDir, "$key.fail")

    companion object {
        private const val MAX_IMAGE_BYTES = 2 * 1024 * 1024
        private const val FAIL_TTL_MS = 7L * 24 * 60 * 60 * 1000
        private const val USER_AGENT =
            "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) " +
                "Chrome/120.0.0.0 Mobile Safari/537.36"
        private val OG_IMAGE_TAG =
            Regex(
                """<meta\s+[^>]*property=["']og:image["'][^>]*>""",
                RegexOption.IGNORE_CASE,
            )
        private val OG_IMAGE_NAME_TAG =
            Regex(
                """<meta\s+[^>]*name=["']og:image["'][^>]*>""",
                RegexOption.IGNORE_CASE,
            )
        private val CONTENT_ATTR =
            Regex(
                """content=["']([^"']+)["']""",
                RegexOption.IGNORE_CASE,
            )

        fun defaultClient(): OkHttpClient = OkHttpClient
            .Builder()
            .followRedirects(true)
            .followSslRedirects(true)
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(20, TimeUnit.SECONDS)
            .build()

        private fun resolveUrl(
            pageUrl: String,
            raw: String,
        ): String {
            val value = raw.trim()
            if (value.startsWith("//")) {
                return "https:$value"
            }
            if (value.startsWith("http://") || value.startsWith("https://")) {
                return value
            }
            return runCatching {
                java.net.URI(pageUrl).resolve(value).toString()
            }.getOrDefault(value)
        }
    }
}
