Convert the data into a food log table (csv) with tab-separated columns. Each row is one entry in the food diary.

Column format (all 5 columns are required):

```text
Name	Weight	Calories	Mode	Drink
```

- **Name** — product or dish name (first letter capitalized). Names must be in Russian.
- **Weight** — portion weight in grams (integer). In `portion` mode you may use `0` if weight is unknown.
- **Calories** — value from the calories field:
  - in `weight` mode — calories per 100 g (as with «Calculate by weight»);
  - in `portion` mode — calories for the entire portion (as with «Enter calories directly»).
- **Mode** — input mode:
  - `weight` — calculated from weight and calories per 100 g;
  - `portion` — calories for the portion directly.
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

→ `Milk 2.5%	200	52	weight	yes`

If only calories per portion are given (or «порция», «portion», «за порцию»):

```text
Капучино 180 мл — 85 ккал
```

→ `Cappuccino	180	85	portion	yes`

If the product is clearly a drink (coffee, tea, juice, water, lemonade, etc.), set `Drink` = `yes`.

If it is food (porridge, meat, vegetables, non-liquid dessert, etc.), set `Drink` = `no`.

Do not add a date to the table — the date will be selected separately in the app.

Data to convert:

```text
{{RAW_DATA}}
```

Return only table rows (no headers and no markdown wrappers).
