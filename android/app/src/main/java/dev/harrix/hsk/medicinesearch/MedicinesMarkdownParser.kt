package dev.harrix.hsk.medicinesearch

/**
 * Extracts medicine names from a Markdown inventory for on-screen listing.
 * Full raw Markdown is still sent to Bot Hub unchanged.
 */
object MedicinesMarkdownParser {
    private val headingRegex = Regex("""^#{1,6}\s+(.+)$""")
    private val bulletRegex = Regex("""^\s*[-*+]\s+(.+)$""")
    private val numberedRegex = Regex("""^\s*\d+[.)]\s+(.+)$""")
    private val horizontalRuleRegex = Regex("""^\s*(-{3,}|\*{3,}|_{3,})\s*$""")

    fun parseNames(markdown: String): List<String> {
        val structured = linkedSetOf<String>()
        val plainLines = linkedSetOf<String>()
        for (raw in markdown.lineSequence()) {
            val line = raw.trimEnd()
            val trimmed = line.trim()
            if (trimmed.isEmpty() || horizontalRuleRegex.matches(trimmed)) {
                continue
            }
            val structuredName =
                matchGroup(headingRegex, trimmed)
                    ?: matchGroup(bulletRegex, trimmed)
                    ?: matchGroup(numberedRegex, trimmed)
            if (structuredName != null) {
                cleanName(structuredName)?.let { structured.add(it) }
            } else {
                cleanName(trimmed)?.let { plainLines.add(it) }
            }
        }
        return if (structured.isNotEmpty()) {
            structured.toList()
        } else {
            plainLines.toList()
        }
    }

    private fun matchGroup(
        regex: Regex,
        line: String,
    ): String? = regex.matchEntire(line)?.groupValues?.getOrNull(1)

    private fun cleanName(raw: String): String? {
        val cleaned =
            raw
                .trim()
                .removeSurrounding("**")
                .removeSurrounding("__")
                .removeSurrounding("*")
                .removeSurrounding("_")
                .removeSurrounding("`")
                .trim()
                .trimStart('#', '-', '*', '+')
                .trim()
        return cleaned.takeIf { it.isNotEmpty() }
    }
}
