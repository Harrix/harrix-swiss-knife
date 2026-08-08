Translate fitness exercise and exercise-type names into the local language used in this fitness app.

For this installation the local language is {{LOCAL_LANGUAGE}}.

Return **only rows** in TSV format (two tab-separated columns, no headers, no markdown):

```text
Name	LocalName
```

- **Name** — exact copy of the source name from the list (character for character, including case and spaces).
- **LocalName** — translation into the local language.

Rules:

- One TSV row per unique name in the list.
- Do not skip names and do not add extra rows.
- Do not add explanations, headers, or markdown wrappers.
- Use natural short labels suitable for a personal fitness tracker.

List of names (one per line):

```text
{{NAMES}}
```
