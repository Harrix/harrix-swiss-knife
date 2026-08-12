package dev.harrix.hsk.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import dev.harrix.hsk.R

/** Exact confirmation token users must type (case-insensitive). */
const val TypeYesConfirmWord = "yes"

/**
 * Destructive-action confirm dialog: user must type [TypeYesConfirmWord] before Confirm
 * is enabled.
 */
@Composable
fun TypeYesConfirmDialog(
    title: String,
    message: String,
    confirmLabel: String,
    onConfirm: () -> Unit,
    onDismissRequest: () -> Unit,
) {
    var typed by rememberSaveable { mutableStateOf("") }
    val canConfirm = typed.trim().equals(TypeYesConfirmWord, ignoreCase = true)
    val focusRequester = remember { FocusRequester() }

    LaunchedEffect(Unit) {
        focusRequester.requestFocus()
    }

    fun tryConfirm() {
        if (canConfirm) {
            onConfirm()
        }
    }

    AlertDialog(
        onDismissRequest = onDismissRequest,
        title = { AutoFitText(text = title, maxLines = 2) },
        text = {
            Column(
                modifier =
                Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Text(
                    text = message,
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = stringResource(R.string.confirm_type_yes_hint),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                OutlinedTextField(
                    value = typed,
                    onValueChange = { typed = it },
                    modifier =
                    Modifier
                        .fillMaxWidth()
                        .focusRequester(focusRequester),
                    label = { Text(stringResource(R.string.confirm_type_yes_label)) },
                    placeholder = { Text(TypeYesConfirmWord) },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                    keyboardActions = KeyboardActions(onDone = { tryConfirm() }),
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = { tryConfirm() },
                enabled = canConfirm,
            ) {
                AutoFitText(text = confirmLabel, maxLines = 1)
            }
        },
        dismissButton = {
            TextButton(onClick = onDismissRequest) {
                AutoFitText(
                    text = stringResource(R.string.confirm_cancel),
                    maxLines = 1,
                )
            }
        },
    )
}
