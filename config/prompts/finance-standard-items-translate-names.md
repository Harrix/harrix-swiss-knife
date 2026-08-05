Translate finance standard item names into English.

Return **only rows** in TSV format (two tab-separated columns, no headers, no markdown):

```text
Name	English
```

- **Name** — exact copy of the source name (character for character, including case and spaces).
- **English** — concise, natural English translation.

Rules:

- One TSV row per unique name in the list.
- Do not skip names and do not add extra rows.
- Preserve brand names, quantities, and other meaningful details.
- Do not add explanations, headers, or markdown wrappers.

List of names (one per line):

```text
{{STANDARD_ITEM_NAMES}}
```
