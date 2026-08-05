package dev.harrix.hsk.ui

import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp

private val BulletLine = Regex("""^\s*[-*+]\s+(.*)$""")
private val NumberedLine = Regex("""^\s*(\d+)\.\s+(.*)$""")
private val BoldInline = Regex("""(\*\*|__)(.+?)\1""")

private sealed interface MarkdownBlock {
    data class Paragraph(
        val text: AnnotatedString,
    ) : MarkdownBlock

    data class Bullet(
        val text: AnnotatedString,
    ) : MarkdownBlock

    data class Numbered(
        val number: Int,
        val text: AnnotatedString,
    ) : MarkdownBlock
}

/**
 * Renders a small Markdown subset used in Medicine Search answers:
 * bold (`**…**` / `__…__`), unordered lists, and numbered lists.
 */
@Composable
fun SimpleMarkdownText(
    markdown: String,
    modifier: Modifier = Modifier,
) {
    val blocks = remember(markdown) { parseSimpleMarkdown(markdown) }
    SelectionContainer(modifier = modifier) {
        Column(
            modifier =
            Modifier
                .fillMaxWidth()
                .border(
                    width = 1.dp,
                    color = MaterialTheme.colorScheme.outline,
                    shape = RoundedCornerShape(4.dp),
                ).padding(horizontal = 16.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            blocks.forEach { block ->
                when (block) {
                    is MarkdownBlock.Paragraph -> {
                        Text(
                            text = block.text,
                            style = MaterialTheme.typography.bodyLarge,
                            color = MaterialTheme.colorScheme.onSurface,
                        )
                    }

                    is MarkdownBlock.Bullet -> {
                        MarkdownListRow(
                            marker = "•",
                            text = block.text,
                        )
                    }

                    is MarkdownBlock.Numbered -> {
                        MarkdownListRow(
                            marker = "${block.number}.",
                            text = block.text,
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun MarkdownListRow(
    marker: String,
    text: AnnotatedString,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(
            text = marker,
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurface,
            modifier = Modifier.widthIn(min = 20.dp),
        )
        Text(
            text = text,
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurface,
            modifier = Modifier.weight(1f),
        )
    }
}

private fun parseSimpleMarkdown(markdown: String): List<MarkdownBlock> {
    val normalized = markdown.replace("\r\n", "\n").trim()
    if (normalized.isEmpty()) {
        return emptyList()
    }
    val blocks = mutableListOf<MarkdownBlock>()
    val paragraph = StringBuilder()

    fun flushParagraph() {
        val text = paragraph.toString().trim()
        paragraph.clear()
        if (text.isNotEmpty()) {
            blocks += MarkdownBlock.Paragraph(annotateInlineMarkdown(text))
        }
    }

    for (line in normalized.lineSequence()) {
        val bullet = BulletLine.matchEntire(line)
        val numbered = NumberedLine.matchEntire(line)
        when {
            bullet != null -> {
                flushParagraph()
                blocks += MarkdownBlock.Bullet(annotateInlineMarkdown(bullet.groupValues[1].trim()))
            }

            numbered != null -> {
                flushParagraph()
                blocks +=
                    MarkdownBlock.Numbered(
                        number = numbered.groupValues[1].toInt(),
                        text = annotateInlineMarkdown(numbered.groupValues[2].trim()),
                    )
            }

            line.isBlank() -> flushParagraph()

            else -> {
                if (paragraph.isNotEmpty()) {
                    paragraph.append(' ')
                }
                paragraph.append(line.trim())
            }
        }
    }
    flushParagraph()
    return blocks
}

private fun annotateInlineMarkdown(text: String): AnnotatedString = buildAnnotatedString {
    var index = 0
    for (match in BoldInline.findAll(text)) {
        if (match.range.first > index) {
            append(text.substring(index, match.range.first))
        }
        withStyle(SpanStyle(fontWeight = FontWeight.Bold)) {
            append(match.groupValues[2])
        }
        index = match.range.last + 1
    }
    if (index < text.length) {
        append(text.substring(index))
    }
}
