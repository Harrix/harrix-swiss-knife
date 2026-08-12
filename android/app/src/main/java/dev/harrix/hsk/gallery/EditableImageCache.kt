package dev.harrix.hsk.gallery

import android.content.Context
import android.net.Uri
import coil.annotation.ExperimentalCoilApi
import coil.imageLoader
import coil.memory.MemoryCache

/**
 * Coil cache keys / invalidation for gallery photos that can be overwritten in place.
 * Keys always include [sizeBytes] so a rewrite that changes length cannot reuse a stale entry
 * after process restart (when in-memory revision counters are lost).
 */
object EditableImageCache {
    fun key(
        uri: Uri,
        sizeBytes: Long,
        revision: Int,
    ): String = "$uri-$sizeBytes-$revision"

    /**
     * Drops memory/disk entries for common key shapes used before/after an overwrite.
     * Safe to call with approximate [knownRevision]; a small range around it is cleared.
     */
    @OptIn(ExperimentalCoilApi::class)
    fun invalidate(
        context: Context,
        uri: Uri,
        previousSizeBytes: Long,
        newSizeBytes: Long,
        knownRevision: Int,
    ) {
        val loader = context.imageLoader
        val maxRev = (knownRevision + 2).coerceAtLeast(2)
        val keys = LinkedHashSet<String>()
        for (rev in 0..maxRev) {
            // Legacy editor keys (uri-revision only).
            keys.add("$uri-$rev")
            // Current editor / card keys.
            keys.add(key(uri, previousSizeBytes, rev))
            keys.add(key(uri, newSizeBytes, rev))
            // Legacy Photo Editor gallery thumb keys (uri-revision-size).
            keys.add("$uri-$rev-$previousSizeBytes")
            keys.add("$uri-$rev-$newSizeBytes")
        }
        for (cacheKey in keys) {
            loader.memoryCache?.remove(MemoryCache.Key(cacheKey))
            runCatching { loader.diskCache?.remove(cacheKey) }
        }
    }
}
