package dev.harrix.hsk.dropboxsync

import org.junit.Assert.assertEquals
import org.junit.Test
import java.io.ByteArrayInputStream

class DropboxContentHasherTest {
    @Test
    fun emptyFileMatchesSha256OfEmpty() {
        val hash = DropboxContentHasher.hashBytes(ByteArray(0))
        assertEquals(
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            hash,
        )
    }

    @Test
    fun helloWorldMatchesKnownVector() {
        val hash = DropboxContentHasher.hashBytes("hello world".toByteArray())
        assertEquals(
            "bc62d4b80d9e36da29c16c5d4d9f11731f36052c72401a76c23c0fb5a9b74423",
            hash,
        )
    }

    @Test
    fun streamMatchesBytesForMultiBlockInput() {
        val data = ByteArray(DropboxContentHasher.BLOCK_SIZE + 123) { index ->
            (index % 251).toByte()
        }
        val fromBytes = DropboxContentHasher.hashBytes(data)
        val fromStream = DropboxContentHasher.hash(ByteArrayInputStream(data))
        assertEquals(fromBytes, fromStream)
    }
}
