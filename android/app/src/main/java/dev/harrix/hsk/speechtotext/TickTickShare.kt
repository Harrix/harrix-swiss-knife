package dev.harrix.hsk.speechtotext

import android.content.Intent
import android.net.Uri

/**
 * Builds TickTick share payloads so long transcripts fit the task title
 * and keep the full text in the task description/content.
 */
object TickTickShare {
    const val PACKAGE_NAME: String = "com.ticktick.task"

    /** Practical title length for TickTick task lists / create form. */
    const val TITLE_MAX_CHARS: Int = 512

    /** Avoid Binder / intent URI blow-ups for huge transcripts. */
    private const val MAX_ADD_TASK_URI_CHARS: Int = 200_000

    data class Parts(
        val title: String,
        /** Full text for description; null when the whole text fits in [title]. */
        val content: String?,
    )

    fun partsFor(text: String): Parts {
        val payload = text.trim()
        if (payload.isEmpty()) {
            return Parts(title = "", content = null)
        }
        if (payload.length <= TITLE_MAX_CHARS) {
            return Parts(title = payload, content = null)
        }
        val ellipsis = "…"
        val maxBody = (TITLE_MAX_CHARS - ellipsis.length).coerceAtLeast(1)
        val cut = payload.take(maxBody)
        val boundary =
            cut
                .lastIndexOfAny(charArrayOf(' ', '\n', '\t', '\r', '.', ',', '!', '?', '。', '…'))
                .takeIf { it >= maxBody / 2 }
                ?: maxBody
        val title = cut.take(boundary).trimEnd() + ellipsis
        return Parts(title = title, content = payload)
    }

    fun addTaskUri(
        title: String,
        content: String?,
    ): Uri? {
        if (title.isBlank()) {
            return null
        }
        val builder =
            Uri
                .Builder()
                .scheme("ticktick")
                .authority("x-callback-url")
                .appendPath("v1")
                .appendPath("add_task")
                .appendQueryParameter("title", title)
        if (!content.isNullOrEmpty()) {
            builder.appendQueryParameter("content", content)
        }
        val uri = builder.build()
        return uri.takeIf { it.toString().length <= MAX_ADD_TASK_URI_CHARS }
    }

    fun shareIntent(
        title: String,
        content: String?,
    ): Intent {
        val uri = addTaskUri(title, content)
        if (uri != null) {
            return Intent(Intent.ACTION_VIEW, uri).apply {
                setPackage(PACKAGE_NAME)
            }
        }
        return Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            setPackage(PACKAGE_NAME)
            putExtra(Intent.EXTRA_SUBJECT, title)
            putExtra(Intent.EXTRA_TEXT, content ?: title)
        }
    }
}
