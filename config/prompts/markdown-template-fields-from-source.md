Extract structured field values for a Markdown note template from the user text and/or attached images (screenshots of Kinopoisk, IMDb, book cards, maps, menus, etc.).

Return **only** a JSON object. Keys must be exact field names from the list below. Values must be strings.

Fields to fill (extract only these; omit a key if the value is unknown):

```text
{{FIELDS}}
```

Rules:

- Use only information present in the text and/or images. Do not invent facts.
- Do not include a `Review` field. Do not return image or file paths.
- Dates must be `yyyy-MM-dd`.
- Floats use a dot as the decimal separator (e.g. `"8.5"`). Integers as digit strings (e.g. `"3"`).
- URLs should be full `https://...` when visible.
- If a website address is visible on a screenshot or in the text (e.g. `https://yandex.ru/maps/org/erna/97485316407/?ll=37.618307%2C55.732873&z=15.81`), put the full URL into the `Web`, `Site`, or `Website` field (whichever exists in the field list). Prefer that over inventing or omitting the link.
- Prefer original titles/names as shown in the source when a field asks for English or original title.
- For `Address` (and similar address fields), return the **full** address including the city (e.g. `"Москва, ул. Тверская, 1"`), not street-only. If `City` is a separate field, still put the complete address with city in `Address`, and put the city alone in `City`.
- No markdown fences, no explanations, no extra keys.

Example shape (illustrative only):

```json
{"Title": "Song of the Sea", "Score": "8.5", "Date watching": "2019-10-28"}
```

User text (may be empty if only images were provided):

```text
{{RAW_DATA}}
```
