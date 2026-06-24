Convert or estimate from the data (text, nutrition label, and/or attached meal photo) into a food log table (csv) with tab-separated columns. Each row is one entry in the food diary.

Column format (all 5 columns are required):

```text
Name	Weight	Calories	Mode	Drink
```

- **Name** — product or dish name (first letter capitalized). Names must be in Russian.
- **Weight** — portion weight in grams (integer). In `portion` mode you may use `0` only if weight is still unknown **after** estimation.
- **Calories** — caloric value:
  - in `weight` mode — calories per 100 g (as with «Calculate by weight»);
  - in `portion` mode — calories for the entire portion (as with «Enter calories directly»).
  - If the source has no calorie numbers — **estimate** from product knowledge, nutrition references, or the attached photo.
- **Mode** — input mode:
  - `weight` — **default** for products, packages, snacks, ingredients, and most dishes: Calories column is **per 100 g**. Put portion weight in **Weight**.
  - `portion` — only if Calories is **already the total** for the portion (apple ~80 kcal, ready drink «85 kcal per 180 ml», dish «per portion» without conversion to per 100 g).
- **Important:** weight or volume in the name (**17г**, **50 g**, **180 ml**) does **not** automatically switch to `portion`. Package «toffee 17 g» is `weight`: the label usually shows **kcal/100 g** (e.g. 430), and 17 is portion weight in **Weight**.
- **Check before answering:** if you consider `portion` and **Weight > 0**, compute `(Calories / Weight) × 100`. If the result is **greater than ~900** — Calories were per 100 g; return **`weight`**, not `portion`.
- **Drink** — drink or not: `yes` or `no`.

Examples:

```text
Oatmeal	150	350	weight	no
Chicken breast	180	165	weight	no
Coffee	250	85	portion	yes
Green tea	200	5	portion	yes
Water	300	0	portion	yes
Apple	120	52	weight	no
Greek yogurt	150	59	weight	no
Protein bar	60	200	portion	no
```

If the source data specifies calories per 100 g and portion weight, use `weight` mode:

```text
Молоко 2.5% — 200 г, 52 ккал/100 г
```

→ `Молоко 2.5%	200	52	weight	yes`

If only calories per portion are given (or «порция», «portion», «за порцию»):

```text
Капучино 180 мл — 85 ккал
```

→ `Капучино	180	85	portion	yes`

If the source data contains **only a dish or product name** (no grams, kcal, or «ккал/100 г») — **estimate** typical portion weight and calories from nutrition references. Do **not** output `0` for Weight and Calories unless the item is truly zero-calorie (water, unsweetened tea).

```text
Паста с пармезаном и болоньезе
```

→ `Паста с пармезаном и болоньезе	350	180	weight	no` (estimated values)

```text
Борщ
```

→ `Борщ	300	50	weight	no` — **not** `Борщ	0	0	portion	no`

If a **meal photo** is attached — use it to estimate portion size and composition. User text clarifies the name but must **not** replace calorie estimation with zeros.

If **both text and photo** are provided — prioritize visual portion assessment from the photo; use the user's text for the dish name when appropriate.

If the product is clearly a drink (coffee, tea, juice, water, lemonade, etc.), set `Drink` = `yes`.

If it is food (porridge, meat, vegetables, non-liquid dessert, etc.), set `Drink` = `no`.

Do not add a date to the table — the date will be selected separately in the app.

Data to convert or estimate from:

```text
{{RAW_DATA}}
```

Return only table rows (no headers and no markdown wrappers).
