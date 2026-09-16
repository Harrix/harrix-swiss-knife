You are given approximate daily macros (protein, fat, carbs, kcal) for several calendar days,
plus the user's calorie bands. Judge the **period as a whole**, not only the last day.

Explain whether a heavy (or light) day is offset by earlier/later days. Mention calories
against the configured bands. Do not invent days that are not listed.

User calorie bands:
- low: ≤ {{KCAL_LOW}} kcal
- medium: about {{KCAL_MEDIUM_LOW}}–{{KCAL_MEDIUM_HIGH}} kcal
- high: > {{KCAL_MEDIUM_HIGH}} kcal

Return **exactly**:
1. `VERDICT_EN:` short English headline for the period
2. `VERDICT:` short headline in {{LOCAL_LANGUAGE}}
3. `EN:` English advice (several lines OK), including calories / balance across days
4. `LOCAL:` same advice in {{LOCAL_LANGUAGE}}

Do not put tabs in the text. No TSV. No preamble.

Example:

```text
VERDICT_EN: Period balanced despite a heavy last day
VERDICT: Период в балансе, несмотря на тяжёлый последний день
EN:
Yesterday was high (~2800 kcal, above the medium band), but earlier days were lighter, so the average sits in the medium range.
Protein was consistently a bit low — add one protein-rich meal on lighter days.
LOCAL:
Вчера калорийность высокая (~2800, выше среднего диапазона), но предыдущие дни были легче — среднее за период в норме.
Белка стабильно маловато — добавьте белковую еду в более лёгкие дни.
```

Date range:

```text
{{DATE_FROM}} … {{DATE_TO}}
```

Per-day macros (intake / AI day-norm):

```text
{{DAYS_SUMMARY}}
```

Return only VERDICT_EN, VERDICT, EN, and LOCAL sections.
