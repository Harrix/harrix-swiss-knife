Convert written workout notes into a sets table (csv) with tab-separated columns. Each row is one set in the fitness tracker.

Column format (all 3 columns are required; Type may be empty):

```text
Exercise	Type	Value
```

- **Exercise** — must be an **exact English name** from the catalog below. If the user wrote a local-language name, map it to that English name. Do **not** invent exercises that are not in the catalog.
- **Type** — exercise type from the catalog for that exercise (exact English type name). Leave empty when the user did not specify a type and the catalog marks type as optional, or when the exercise has no types. If type is **required**, you **must** pick one catalog type (use the selected type below when it fits, otherwise the most likely type).
- **Value** — numeric quantity only (reps, kg, steps, minutes, and so on). No unit suffix. Integers preferred (`12`, not `12.0`).

The user may list several sets in one note. Output **one row per set**. Repeated numbers for the same exercise are separate sets:

```text
подтягивания 12 10 8 и приседания 20
```

→

```text
Pull-up		12
Pull-up		10
Pull-up		8
Squat		20
```

If the note is only a number (or several numbers) with no exercise name, use the **currently selected exercise and type**:

```text
15
```

with selected exercise `Pull-up` → `Pull-up		15`

If the user names a type in local language, map it to the English type from the catalog.

Do not add a date to the table — the date will be selected separately in the app.

Currently selected exercise (may be `(none)`):

```text
{{SELECTED_EXERCISE}}
```

Currently selected type (may be `(none)`):

```text
{{SELECTED_TYPE}}
```

Exercise catalog (use only these names and types):

```text
{{EXERCISES}}
```

Data to convert:

```text
{{RAW_DATA}}
```

Return only table rows (no headers and no markdown wrappers).
