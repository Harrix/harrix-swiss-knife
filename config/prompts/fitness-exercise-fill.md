Fill fields for a new fitness exercise in a personal tracker.

For this installation the local language is {{LOCAL_LANGUAGE}}.

You are given an English name and/or a local-language name (one may be empty). A media filename may also be provided. Infer the missing name and suggest a unit and calories burned per unit.

Return **one row** in TSV format (tab-separated columns, no headers, no markdown):

```text
Name	NameLocal	Unit	CaloriesPerUnit
```

- **Name** — short English exercise name suitable for the tracker.
- **NameLocal** — short natural label in {{LOCAL_LANGUAGE}}.
- **Unit** — measurement unit for one logged value. Prefer common tracker units such as `times`, `kg`, `m`, `km`, `min`, `sec`, `steps`. Use English unit labels.
- **CaloriesPerUnit** — estimated kcal burned **per one unit** (number, may use a decimal point). Examples: push-up ≈ `0.3`–`0.5` per time; 1 km run ≈ `60`–`80`; 1 min plank ≈ `3`–`5`. Use `0` only when calories are not meaningful.

Rules:

- One TSV row only; no quotes, no markdown fences, no explanations.
- If English Name is provided, keep it when already good; otherwise normalize lightly.
- If only NameLocal is provided, invent a clear English Name.
- If only Name is provided, translate to NameLocal.
- If a media filename is provided, treat it as a hint for the English name (ignore the extension, dates, counters, and underscores). Use it when names are empty or unclear.
- Unit and CaloriesPerUnit must always be filled with sensible estimates for an average adult.

English name (may be empty):

```text
{{NAME}}
```

Local name (may be empty):

```text
{{NAME_LOCAL}}
```

Media filename (may be empty):

```text
{{MEDIA_FILENAME}}
```

Return only one TSV row (4 columns), without explanations.
