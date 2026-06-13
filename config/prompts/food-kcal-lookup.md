From the product or dish name, estimate caloric value and determine whether it is a drink or food.

Return **one row** in TSV format (tab-separated columns, no headers, no markdown):

```text
Calories	Mode	Drink	Weight
```

- **Calories** — number (kcal):
  - when `Mode=weight` — calories **per 100 g** (as on the label «kcal/100 g», reference books, typical values for the product);
  - when `Mode=portion` — calories for the **entire portion** (the amount eaten at once), not per 100 g.
- **Mode** — input mode in the app:
  - `weight` — **default** for products, packages, snacks, ingredients: Calories column is **per 100 g**. Put portion weight in **Weight** if it can be extracted from the name (17 g, 50g, 200 ml ≈ g).
  - `portion` — only if Calories is **already the total** for the portion (apple ~80 kcal, ready drink «85 kcal per 180 ml», dish «per portion» without conversion to per 100 g).
- **Important:** weight or volume in the name (**17г**, **50 g**, **180 ml**) does **not** automatically switch to `portion`. Package «toffee 17 g» is `weight`: the label usually shows **kcal/100 g** (e.g. 430), and 17 is portion weight in **Weight**.
- **Check before answering:** if you consider `portion` and **Weight > 0**, compute `(Calories / Weight) × 100`. If the result is **greater than ~900** — Calories were per 100 g; return **`weight`**, not `portion`.
- **Drink** — `yes` for drinks (coffee, tea, juice, water, milk, lemonade, etc.), otherwise `no`.
- **Weight** — portion weight in grams (integer). If grams or milliliters can be extracted from the name — specify (ml ≈ g). If weight is unknown — `0`.

Examples:

```text
165	weight	no	0
85	portion	yes	180
350	weight	no	0
52	weight	yes	0
430	weight	no	17
80	portion	no	150
```

(«Chicken breast» → `165	weight	no	0`; «Cappuccino 180 ml» with ~85 kcal per cup → `85	portion	yes	180`; «Peanut toffee 17g» → `430	weight	no	17` — 430 kcal/100 g, portion 17 g.)

Product name:

```text
{{FOOD_NAME}}
```

Return only one TSV row (4 columns), without explanations.
