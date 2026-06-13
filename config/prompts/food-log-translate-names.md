Translate product and dish names from Russian to English.

Return **only rows** in TSV format (two tab-separated columns, no headers, no markdown):

```text
Name	EnglishName
```

- **Name** — exact copy of the source name from the list (character for character, including case and spaces).
- **EnglishName** — English translation (Latin script). First letter capitalized, as for a product name.

Rules:

- One TSV row per unique name in the list.
- Do not skip names and do not add extra rows.
- Do not add explanations, headers, or markdown wrappers.

List of names (one per line):

```text
{{FOOD_NAMES}}
```
