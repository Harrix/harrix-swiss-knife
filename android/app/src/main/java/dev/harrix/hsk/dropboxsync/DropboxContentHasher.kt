package dev.harrix.hsk.dropboxsync

import java.io.InputStream
import java.security.MessageDigest

/**
 * Streaming Dropbox content_hash (SHA-256 over 4 MiB block digests).
 *
 * Uses a 64 KiB read buffer so multi-GB files stay memory-safe on 32-bit devices.
 */
object DropboxContentHasher {
    const val BLOCK_SIZE: Int = 4 * 1024 * 1024
    private const val READ_BUFFER_SIZE: Int = 64 * 1024

    @Suppress("NestedBlockDepth")
    fun hash(input: InputStream): String {
        val overall = MessageDigest.getInstance("SHA-256")
        val block = MessageDigest.getInstance("SHA-256")
        val buffer = ByteArray(READ_BUFFER_SIZE)
        var inBlock = 0
        var read = input.read(buffer)
        while (read >= 0) {
            if (read > 0) {
                var offset = 0
                while (offset < read) {
                    val space = BLOCK_SIZE - inBlock
                    val chunk = minOf(space, read - offset)
                    block.update(buffer, offset, chunk)
                    inBlock += chunk
                    offset += chunk
                    if (inBlock == BLOCK_SIZE) {
                        overall.update(block.digest())
                        block.reset()
                        inBlock = 0
                    }
                }
            }
            read = input.read(buffer)
        }
        if (inBlock > 0) {
            overall.update(block.digest())
        }
        return overall.digest().toHex()
    }

    fun hashBytes(data: ByteArray): String = hash(data.inputStream())

    private fun ByteArray.toHex(): String {
        val out = StringBuilder(size * 2)
        for (byte in this) {
            out.append("%02x".format(byte))
        }
        return out.toString()
    }
}
