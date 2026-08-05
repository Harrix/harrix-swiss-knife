Translate finance transaction descriptions into English.

Return **only rows** in TSV format (two tab-separated columns, no headers, no markdown):

```text
Description	English
```

- **Description** — exact copy of the source description (character for character, including case and spaces).
- **English** — concise, natural English translation.

Rules:

- One TSV row per unique description in the list.
- Do not skip descriptions and do not add extra rows.
- Preserve brand names, quantities, and other meaningful details.
- Do not add explanations, headers, or markdown wrappers.

List of descriptions (one per line):

```text
{{TRANSACTION_DESCRIPTIONS}}
```
