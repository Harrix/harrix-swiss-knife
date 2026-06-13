From the input data, estimate portion mass (in grams) and clarify whether it is a drink or food.

Given:

- Name: {{FOOD_NAME}}
- Calories (for the entire portion): {{CALORIES_TOTAL}} kcal
- Currently marked as drink: {{DRINK}}

Return **one row** in TSV format (tab-separated columns, no headers, no markdown):

```text
Drink	Weight
```

- **Drink** — `yes` for drinks (coffee, tea, juice, water, milk, lemonade, etc.), otherwise `no`.
- **Weight** — portion mass in grams (integer, ≥0). If mass cannot be determined — `0`.

Rules:

- «Calories» means the **entire portion**, not «per 100 g».
- If it is a drink and volume (ml) is typical for the name/type, treat \(1 ml \approx 1 g\).
- If the name contains grams or milliliters — use that value.
- If the value seems unreasonable (e.g. too little/too much for a typical portion) — return `0`.

Return only one TSV row (2 columns), without explanations.
