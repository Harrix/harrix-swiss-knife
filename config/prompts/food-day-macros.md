Estimate approximate daily macros (protein, fat, carbohydrates) from the eaten food list,
and suggest a typical balanced adult daily norm for comparison.

Values are approximate. Prefer consistency with the provided total kcal when possible
(protein×4 + fat×9 + carb×4 ≈ kcal), but do not invent foods that are not listed.
Do not ask for body weight or personal goals.

User calorie bands from settings (use these when judging kcal and when choosing NormKcal):
- low: at or below {{KCAL_LOW}} kcal
- medium: about {{KCAL_MEDIUM_LOW}}–{{KCAL_MEDIUM_HIGH}} kcal
- high: above {{KCAL_MEDIUM_HIGH}} kcal

Prefer NormKcal near the middle of the medium band unless the day clearly differs.

Return **exactly**:
1. One TSV data line (tab-separated, no headers, no markdown fences) for **intake**:
```text
Protein_g	Fat_g	Carb_g	Kcal
```
2. One TSV data line for **suggested daily norms**:
```text
NormProtein_g	NormFat_g	NormCarb_g	NormKcal
```
3. `VERDICT_EN:` short English headline
4. `VERDICT:` short headline in {{LOCAL_LANGUAGE}}
5. A line exactly `EN:` then English advice (several lines OK). **Must comment on calories** vs the bands above.
6. A line exactly `LOCAL:` then the same advice in {{LOCAL_LANGUAGE}}, including calories.

Rules:
- All numeric fields are non-negative (floats allowed).
- Norms should be a sensible full-day reference, not a copy of intake.
- Do not put tabs in VERDICT or advice lines.

Example:

```text
95.0	62.5	210.0	1850
100	70	250	2100
VERDICT_EN: Low protein; calories in the medium-low band
VERDICT: Мало белка; калории в средней-нижней зоне
EN:
Add a protein-rich meal (eggs, fish, or legumes). Carbs are fine; fats are moderate.
Calories (~1850) sit near the low/medium boundary — fine for a light day, a bit low if this is a normal active day.
LOCAL:
Добавьте белковую еду (яйца, рыба или бобовые). Углеводы в норме, жиры умеренные.
Калории (~1850) у нижней границы среднего диапазона — нормально для лёгкого дня.
```

Date:

```text
{{DATE}}
```

Food log for the day:

```text
{{DAY_MENU}}
```

Return only the two TSV lines, VERDICT_EN, VERDICT, EN, and LOCAL sections — no preamble.
