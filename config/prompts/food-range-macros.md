You are given approximate daily macros (protein, fat, carbs, fiber, kcal) for several calendar days,
plus the user's calorie bands. Judge the **period as a whole**, not only the last day.

Explain whether a heavy (or light) day is offset by earlier/later days. Mention calories
against the configured bands. Also comment on dietary fiber across the period versus a typical
adult minimum of about 25–30 g/day, and say what to add on low-fiber days (vegetables, fruit,
whole grains, legumes, nuts, or seeds). A day line with `Fi —` has no fiber estimate; do not
invent a fiber total for that day. Do not invent days that are not listed.

User calorie bands:
- low: ≤ {{KCAL_LOW}} kcal
- medium: about {{KCAL_MEDIUM_LOW}}–{{KCAL_MEDIUM_HIGH}} kcal
- high: > {{KCAL_MEDIUM_HIGH}} kcal

Return **exactly**:
1. `VERDICT_EN:` short English headline for the period
2. `VERDICT:` short headline in {{LOCAL_LANGUAGE}}
3. `EN:` English advice (several paragraphs OK), including calories / balance across days and fiber
4. `LOCAL:` same advice in {{LOCAL_LANGUAGE}}, including fiber

Advice formatting (EN and LOCAL):
- Separate paragraphs with a blank line.
- Simple Markdown is allowed: **bold**, *italic*, lists (`-` / `1.`).
- Do not use headings, links, images, or code fences in advice.
- Do not put tabs in the text.

No TSV. No preamble.

Example:

```text
VERDICT_EN: Period balanced despite a heavy last day
VERDICT: Период в балансе, несмотря на тяжёлый последний день
EN:
Yesterday was **high** (~2800 kcal, above the medium band), but earlier days were lighter, so the average sits in the medium range.

Protein was consistently a bit low — add one protein-rich meal on *lighter* days.

Fiber stayed under ~28 g on most days. Add vegetables, whole grains, or legumes on the lighter days.
LOCAL:
Вчера калорийность **высокая** (~2800, выше среднего диапазона), но предыдущие дни были легче — среднее за период в норме.

Белка стабильно маловато — добавьте белковую еду в *более лёгкие* дни.

Клетчатки в большинстве дней меньше ~28 г. Добавьте овощи, цельнозерновые или бобовые в более лёгкие дни.
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
