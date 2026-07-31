package dev.harrix.hsk.notes

import android.net.Uri
import org.json.JSONArray
import org.json.JSONObject

/** Persisted open-tab session for Markdown Notes. */
data class NotesOpenTabsSession(
    val treeUri: String,
    val selectedDocumentId: String?,
    val tabs: List<OpenNoteTab>,
) {
    fun toJson(): String {
        val root = JSONObject()
        root.put(KEY_TREE_URI, treeUri)
        if (selectedDocumentId != null) {
            root.put(KEY_SELECTED_DOCUMENT_ID, selectedDocumentId)
        } else {
            root.put(KEY_SELECTED_DOCUMENT_ID, JSONObject.NULL)
        }
        val tabsJson = JSONArray()
        tabs.forEach { tab ->
            tabsJson.put(tab.toJson())
        }
        root.put(KEY_TABS, tabsJson)
        return root.toString()
    }

    companion object {
        private const val KEY_TREE_URI = "treeUri"
        private const val KEY_SELECTED_DOCUMENT_ID = "selectedDocumentId"
        private const val KEY_TABS = "tabs"
        private const val KEY_DOCUMENT_ID = "documentId"
        private const val KEY_URI = "uri"
        private const val KEY_TITLE = "title"
        private const val KEY_FILE_NAME = "fileName"
        private const val KEY_FOLDER_PATH = "folderPath"
        private const val KEY_NAME = "name"

        fun fromJson(raw: String): NotesOpenTabsSession? = runCatching {
            val root = JSONObject(raw)
            val treeUri = root.getString(KEY_TREE_URI).takeIf { it.isNotBlank() } ?: return null
            val selected =
                if (root.isNull(KEY_SELECTED_DOCUMENT_ID)) {
                    null
                } else {
                    root.optString(KEY_SELECTED_DOCUMENT_ID).takeIf { it.isNotBlank() }
                }
            val tabsJson = root.optJSONArray(KEY_TABS) ?: JSONArray()
            val tabs =
                buildList {
                    for (index in 0 until tabsJson.length()) {
                        val tabJson = tabsJson.optJSONObject(index) ?: continue
                        parseTab(tabJson)?.let(::add)
                    }
                }
            NotesOpenTabsSession(
                treeUri = treeUri,
                selectedDocumentId = selected,
                tabs = tabs,
            )
        }.getOrNull()

        private fun parseTab(json: JSONObject): OpenNoteTab? {
            val documentId = json.optString(KEY_DOCUMENT_ID).takeIf { it.isNotBlank() } ?: return null
            val uriString = json.optString(KEY_URI).takeIf { it.isNotBlank() } ?: return null
            val title = json.optString(KEY_TITLE).ifBlank { documentId }
            val fileName = json.optString(KEY_FILE_NAME)
            val pathJson = json.optJSONArray(KEY_FOLDER_PATH) ?: JSONArray()
            val folderPath =
                buildList {
                    for (index in 0 until pathJson.length()) {
                        val segmentJson = pathJson.optJSONObject(index) ?: continue
                        parseSegment(segmentJson)?.let(::add)
                    }
                }
            return OpenNoteTab(
                documentId = documentId,
                uri = Uri.parse(uriString),
                title = title,
                fileName = fileName,
                folderPath = folderPath,
            )
        }

        private fun parseSegment(json: JSONObject): NotesPathSegment? {
            val documentId = json.optString(KEY_DOCUMENT_ID).takeIf { it.isNotBlank() } ?: return null
            val name = json.optString(KEY_NAME).ifBlank { documentId }
            val uriString = json.optString(KEY_URI).takeIf { it.isNotBlank() } ?: return null
            return NotesPathSegment(
                documentId = documentId,
                name = name,
                uri = Uri.parse(uriString),
            )
        }

        private fun OpenNoteTab.toJson(): JSONObject {
            val json = JSONObject()
            json.put(KEY_DOCUMENT_ID, documentId)
            json.put(KEY_URI, uri.toString())
            json.put(KEY_TITLE, title)
            json.put(KEY_FILE_NAME, fileName)
            val pathJson = JSONArray()
            folderPath.forEach { segment ->
                pathJson.put(segment.toJson())
            }
            json.put(KEY_FOLDER_PATH, pathJson)
            return json
        }

        private fun NotesPathSegment.toJson(): JSONObject {
            val json = JSONObject()
            json.put(KEY_DOCUMENT_ID, documentId)
            json.put(KEY_NAME, name)
            json.put(KEY_URI, uri.toString())
            return json
        }
    }
}
