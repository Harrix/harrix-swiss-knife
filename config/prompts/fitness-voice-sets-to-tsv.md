Convert a spoken workout transcription into a sets table (csv) with tab-separated columns. Each row is one set in the fitness tracker.

The input is **speech recognition text**. It may contain ASR mistakes, informal wording, dropped numbers, and several exercises in one utterance. Interpret intent generously and map names to the catalog even when they are slightly misheard or in the local language.

Column format (all 3 columns are required; Type may be empty):

```text
Exercise	Type	Value
```

- **Exercise** — must be an **exact English name** from the catalog below. Map local names and near-misses («подтягивания», «подтяг», «пуллап») to the closest catalog exercise. Do **not** invent exercises that are not in the catalog. If nothing matches, skip that fragment.
- **Type** — exercise type from the catalog for that exercise (exact English type name). Leave empty when the speaker did not mention a type and the catalog marks type as optional, or when the exercise has no types. If type is **required**, you **must** pick one catalog type (use the selected type below when it fits).
- **Value** — numeric quantity only. Spoken numbers («двенадцать», «15», «десять») become digits. No unit suffix.

The speaker may list several sets. Output **one row per set**. A sequence of numbers after one exercise is several sets of that exercise:

```text
сделал подтягивания двенадцать десять и восемь и ещё двадцать приседаний
```

→

```text
Pull-up		12
Pull-up		10
Pull-up		8
Squat		20
```

If the transcript is only a number (or several numbers) with no exercise name, use the **currently selected exercise and type**.

If the speaker names a weight or variant that matches a catalog type («с блином 24», «80 килограмм»), put that type in **Type** and the reps (or the named quantity) in **Value**. If they logged the weight itself as the value (for exercises measured in kg), put the kilograms in **Value**.

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

Speech transcription to convert:

```text
{{RAW_DATA}}
```

Return only table rows (no headers and no markdown wrappers).
