package dev.harrix.hsk.dropboxsync

/**
 * Gitignore-style path matcher for sync exclusions.
 *
 * Supports:
 * - Exact segment names (`.git`, `node_modules`)
 * - Simple globs (`*.tmp`, `.Trash*`, `~$*`)
 * - Optional "ignore all hidden `.*`" toggle
 */
class SyncIgnoreMatcher(
    patterns: Collection<String>,
    private val ignoreHidden: Boolean = false,
) {
    private val compiled: List<IgnoreRule> =
        patterns
            .map { it.trim() }
            .filter { it.isNotEmpty() && !it.startsWith("#") }
            .map { IgnoreRule.parse(it) }

    fun ignores(relativePath: String): Boolean {
        val normalized = normalizeRelativePath(relativePath)
        if (normalized.isEmpty()) {
            return false
        }
        val segments = normalized.split('/')
        if (ignoreHidden && segments.any { it.startsWith('.') }) {
            return true
        }
        return segments.any { segment -> compiled.any { it.matchesSegment(segment) } } ||
            compiled.any { it.matchesPath(normalized) }
    }

    fun ignoresDirectory(relativePath: String): Boolean = ignores(relativePath)

    companion object {
        val DefaultPatterns: List<String> =
            listOf(
                ".git",
                ".hg",
                ".svn",
                ".venv",
                "venv",
                "node_modules",
                "__pycache__",
                ".pytest_cache",
                ".mypy_cache",
                ".ruff_cache",
                ".gradle",
                ".idea",
                ".cursor",
                ".DS_Store",
                "Thumbs.db",
                "desktop.ini",
                ".thumbnails",
                ".Trash*",
                "*.tmp",
                "*.part",
                "*.crdownload",
                "~$*",
                "*.hsksync.tmp",
            )

        fun fromText(
            text: String,
            ignoreHidden: Boolean = false,
        ): SyncIgnoreMatcher {
            val patterns =
                text
                    .lineSequence()
                    .map { it.trim() }
                    .filter { it.isNotEmpty() && !it.startsWith("#") }
                    .toList()
            return SyncIgnoreMatcher(patterns, ignoreHidden)
        }

        fun forPair(
            globalText: String,
            useGlobal: Boolean,
            customText: String,
            ignoreHidden: Boolean,
        ): SyncIgnoreMatcher {
            val patterns = mutableListOf<String>()
            if (useGlobal) {
                patterns +=
                    globalText
                        .lineSequence()
                        .map { it.trim() }
                        .filter { it.isNotEmpty() && !it.startsWith("#") }
            }
            patterns +=
                customText
                    .lineSequence()
                    .map { it.trim() }
                    .filter { it.isNotEmpty() && !it.startsWith("#") }
            return SyncIgnoreMatcher(patterns, ignoreHidden)
        }
    }

    private data class IgnoreRule(
        val raw: String,
        val regex: Regex,
        val pathScoped: Boolean,
    ) {
        fun matchesSegment(segment: String): Boolean = !pathScoped && regex.matches(segment)

        fun matchesPath(path: String): Boolean = pathScoped && regex.matches(path)

        companion object {
            fun parse(pattern: String): IgnoreRule {
                val trimmed = pattern.trim().trimStart('/')
                val pathScoped = trimmed.contains('/')
                val regex =
                    Regex(
                        "^" +
                            trimmed
                                .split('/')
                                .joinToString("/") { segmentToRegex(it) } +
                            "$",
                        RegexOption.IGNORE_CASE,
                    )
                return IgnoreRule(trimmed, regex, pathScoped)
            }

            private fun segmentToRegex(segment: String): String {
                val out = StringBuilder()
                var i = 0
                while (i < segment.length) {
                    when (val ch = segment[i]) {
                        '*' -> out.append(".*")

                        '?' -> out.append('.')

                        '.', '+', '(', ')', '[', ']', '{', '}', '^', '$', '|', '\\' -> {
                            out.append('\\').append(ch)
                        }

                        else -> out.append(ch)
                    }
                    i += 1
                }
                return out.toString()
            }
        }
    }
}
