package dev.harrix.hsk.notes

/**
 * Extracts a note display title from Markdown the same way as
 * `vscode/harrix-notes-explorer-hsk` (YAML `title:` or first `#` heading).
 */
object NoteTitleExtractor {
    private val FRONTMATTER_REGEX = Regex("^---\\r?\\n([\\s\\S]*?)\\r?\\n---\\r?\\n?")
    private val TITLE_LINE_REGEX = Regex("^title\\s*:\\s*(.*)$", RegexOption.IGNORE_CASE)
    private val H1_REGEX = Regex("^#\\s+(.+)$")

    fun extract(text: String): String {
        var src = text
        if (src.isNotEmpty() && src[0] == '\uFEFF') {
            src = src.substring(1)
        }
        val fmMatch = FRONTMATTER_REGEX.find(src)
        val title =
            if (fmMatch != null) {
                titleFromFrontmatterBlock(fmMatch.groupValues[1])
                    .ifEmpty { firstH1AfterFrontmatter(src.substring(fmMatch.range.last + 1)) }
            } else {
                firstH1AfterFrontmatter(src)
            }
        return stripHtmlComments(title)
    }

    private fun titleFromFrontmatterBlock(fmText: String): String {
        for (line in fmText.lineSequence()) {
            val match = TITLE_LINE_REGEX.find(line) ?: continue
            val title = unquoteYamlScalar(match.groupValues[1])
            if (title.isNotEmpty()) {
                return title
            }
        }
        return ""
    }

    private fun firstH1AfterFrontmatter(body: String): String {
        var inFence = false
        for (rawLine in body.lineSequence()) {
            val heading = headingCandidate(rawLine, inFence) ?: continue
            when {
                heading.isFence -> inFence = !inFence
                heading.h1Text != null -> return heading.h1Text
            }
        }
        return ""
    }

    private data class HeadingCandidate(
        val isFence: Boolean,
        val h1Text: String?,
    )

    private fun headingCandidate(
        rawLine: String,
        inFence: Boolean,
    ): HeadingCandidate? {
        val line = rawLine.trim()
        if (line.isEmpty()) {
            return null
        }
        if (line.startsWith("```")) {
            return HeadingCandidate(isFence = true, h1Text = null)
        }
        if (inFence || isHtmlCommentLine(line)) {
            return null
        }
        if (line.startsWith("##")) {
            return null
        }
        val h1 = H1_REGEX.find(line) ?: return null
        return HeadingCandidate(isFence = false, h1Text = h1.groupValues[1].trim())
    }

    private fun isHtmlCommentLine(line: String): Boolean = line.startsWith("<!--") && line.contains("-->")

    private fun unquoteYamlScalar(value: String): String {
        var v = value.trim()
        if (isQuotedScalar(v)) {
            v = v.substring(1, v.length - 1)
        }
        return v.trim()
    }

    private fun isQuotedScalar(value: String): Boolean {
        if (value.length < 2) {
            return false
        }
        val doubleQuoted = value.startsWith("\"") && value.endsWith("\"")
        val singleQuoted = value.startsWith("'") && value.endsWith("'")
        return doubleQuoted || singleQuoted
    }

    private fun stripHtmlComments(text: String): String = text.replace(Regex("<!--[\\s\\S]*?-->"), "").trim()
}
