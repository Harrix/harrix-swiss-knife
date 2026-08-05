package dev.harrix.hsk.medicinesearch

import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.net.Uri
import dev.harrix.hsk.R

/**
 * Opens the medicines Markdown note in Harrix Notes when installed,
 * otherwise shows the system “Open with” chooser for a normal `.md` file.
 */
object MedicinesNoteOpener {
    const val HARRIX_NOTES_PACKAGE = "dev.harrix.notes"

    fun open(
        context: Context,
        uri: Uri,
    ): Boolean {
        val mimeType =
            context.contentResolver
                .getType(uri)
                ?.takeIf { it.isNotBlank() && it != "application/octet-stream" }
                ?: "text/markdown"
        val viewIntent =
            Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(uri, mimeType)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
        val chooserTitle = context.getString(R.string.medicine_search_open_with)
        val harrixIntent =
            Intent(viewIntent).apply {
                setPackage(HARRIX_NOTES_PACKAGE)
            }
        if (harrixIntent.resolveActivity(context.packageManager) != null) {
            runCatching {
                context.grantUriPermission(
                    HARRIX_NOTES_PACKAGE,
                    uri,
                    Intent.FLAG_GRANT_READ_URI_PERMISSION,
                )
            }
            val started =
                runCatching {
                    context.startActivity(harrixIntent)
                    true
                }.getOrDefault(false)
            if (started) {
                return true
            }
        }
        return try {
            context.startActivity(Intent.createChooser(viewIntent, chooserTitle))
            true
        } catch (_: ActivityNotFoundException) {
            false
        } catch (_: SecurityException) {
            false
        }
    }
}
