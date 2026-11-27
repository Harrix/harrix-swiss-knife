package dev.harrix.hsk.speechtotext

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class TickTickShareTest {
    @Test
    fun partsFor_shortText_staysInTitleOnly() {
        val parts = TickTickShare.partsFor("Buy milk")
        assertEquals("Buy milk", parts.title)
        assertNull(parts.content)
    }

    @Test
    fun partsFor_longText_truncatesTitleAndKeepsFullContent() {
        val payload = "word ".repeat(200).trim()
        val parts = TickTickShare.partsFor(payload)
        assertTrue(parts.title.length <= TickTickShare.TITLE_MAX_CHARS)
        assertTrue(parts.title.endsWith("…"))
        assertEquals(payload, parts.content)
    }

    @Test
    fun partsFor_empty_returnsEmptyTitle() {
        val parts = TickTickShare.partsFor("   ")
        assertEquals("", parts.title)
        assertNull(parts.content)
    }
}
