Generate one workout as a tab-separated table from the athlete profile, exercise catalog, and recent sets.

First line (required):

```text
Title	<short English workout name>
```

Then one header row and one data row per set:

```text
Exercise	Type	Value
```

- **Exercise** — exact English name from the catalog. Do not invent exercises.
- **Type** — exact English type from the catalog for that exercise, or empty when type is optional / the exercise has no types. If type is required, you must pick one catalog type.
- **Value** — numeric quantity only (no unit suffix). Integers preferred.

Rules:

- Fit the plan into about `{{DURATION_MIN}}` minutes for a `{{GENDER}}` athlete.
- Honor the athlete preferences below when choosing exercises and writing the Title.
- The Title must briefly mention the session focus from preferences (e.g. dumbbells, cardio, stretching, yoga, strength, or notes).
- Prefer catalog exercises the person already does (see recent sets), but mix in variety so the session is not a copy of the last workout.
- Use realistic values for the listed units and recent history.
- Output only the Title line and the TSV table. No commentary.

Gender: {{GENDER}}
Duration minutes: {{DURATION_MIN}}

Athlete preferences:

{{WORKOUT_PREFERENCES}}

Exercise catalog (name | unit | kcal per unit | types with calorie modifiers):

```text
{{EXERCISES}}
```

Recent completed sets (newest first, limited by app config):

```text
{{RECENT_SETS}}
```
