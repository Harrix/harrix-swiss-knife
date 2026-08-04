Convert a spoken food diary transcription into a food log table (csv) with tab-separated columns. Each row is one entry in the food diary.

The input is **speech recognition text**. It may contain ASR mistakes, informal wording, approximate portions («тарелка», «чашка», «кусочек»), and several dishes in one utterance. Interpret intent generously and estimate missing numbers from typical portions.

Column format (all 5 columns are required):

```text
Name	Weight	Calories	Mode	Drink
```

- **Name** — product or dish name (first letter capitalized). Names must be in Russian.
- **Weight** — portion weight in grams (integer). In `portion` mode you may use `0` only if weight is still unknown **after** estimation.
- **Calories** — caloric value:
  - in `weight` mode — calories per 100 g (as with «Calculate by weight»);
  - in `portion` mode — calories for the entire portion (as with «Enter calories directly»).
  - If the speaker gave no calorie numbers — **estimate** from product knowledge and nutrition references.
- **Mode** — input mode:
  - `weight` — **default** for products, packages, snacks, ingredients, and most dishes: Calories column is **per 100 g**. Put portion weight in **Weight**.
  - `portion` — only if Calories is **already the total** for the portion (apple ~80 kcal, ready drink «85 kcal», dish «за порцию» without conversion to per 100 g).
- **Important:** spoken weight or volume (**«17 грамм»**, **«50 г»**, **«180 мл»**) does **not** automatically switch to `portion`. A package «ириска 17 г» is usually `weight` with kcal/100 g and 17 in **Weight**.
- **Check before answering:** if you consider `portion` and **Weight > 0**, compute `(Calories / Weight) × 100`. If the result is **greater than ~900** — Calories were per 100 g; return **`weight`**, not `portion`.
- **Drink** — drink or not: `yes` or `no`.

Spoken examples:

```text
съел овсянку грамм сто пятьдесят и куриную грудку
```

→

```text
Овсянка	150	350	weight	no
Куриная грудь	180	165	weight	no
```

```text
выпил капучино большой и яблоко
```

→

```text
Капучино	250	85	portion	yes
Яблоко	120	52	weight	no
```

```text
тарелка борща и чай без сахара
```

→

```text
Борщ	300	50	weight	no
Чай	200	5	portion	yes
```

If the transcript names only a dish with no grams or kcal — **estimate** typical portion weight and calories. Do **not** output `0` for Weight and Calories unless the item is truly zero-calorie (water, unsweetened tea).

If the product is clearly a drink (coffee, tea, juice, water, lemonade, etc.), set `Drink` = `yes`.

If it is food (porridge, meat, vegetables, non-liquid dessert, etc.), set `Drink` = `no`.

Do not add a date to the table — the date will be selected separately in the app.

Speech transcription to convert:

```text
{{RAW_DATA}}
```

Return only table rows (no headers and no markdown wrappers).
