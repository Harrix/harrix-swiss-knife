Estimate approximate daily macros (protein, fat, carbohydrates) from the eaten food list,
and suggest a typical balanced adult daily norm for comparison.

Values are approximate. Prefer consistency with the provided total kcal when possible
(protein×4 + fat×9 + carb×4 ≈ kcal), but do not invent foods that are not listed.
Do not ask for body weight or personal goals — use a general adult balanced-day reference.

Return **exactly**:
1. One TSV data line (tab-separated, no headers, no markdown fences) for **intake**:
```text
Protein_g	Fat_g	Carb_g	Kcal
```
2. One TSV data line for **suggested daily norms**:
```text
NormProtein_g	NormFat_g	NormCarb_g	NormKcal
```
3. One line starting with `VERDICT:` and a short headline (e.g. balanced / low protein).
4. Optionally more lines of advice (what is missing, what to fix). Russian is preferred.

Rules:
- All numeric fields are non-negative (floats allowed).
- Norms should be a sensible full-day reference, not a copy of intake.
- Do not put tabs in VERDICT or advice lines.

Example:

```text
95.0	62.5	210.0	1850
100	70	250	2100
VERDICT: Low protein relative to the day norm
Add a protein-rich meal (eggs, fish, or legumes). Carbs are fine; fats are moderate.
```

Date:

```text
{{DATE}}
```

Food log for the day:

```text
{{DAY_MENU}}
```

Return only the two TSV lines, VERDICT, and optional advice — no preamble.
