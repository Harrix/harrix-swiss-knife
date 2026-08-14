Suggest search keywords for a vector icon.

You receive a **raster preview** of the icon (not SVG), the current category, and the current tags.

Tasks:

1. Keep useful existing tags.
2. Translate English tags into Russian and Russian tags into English.
3. Add your own relevant keywords in **both** English and Russian (objects, actions, style, synonyms people would search for).

Return **only** keywords, one per line, no numbering, no markdown, no explanations.

Rules:

- Lowercase unless the word is a proper name.
- One keyword or short phrase per line (2–3 words max).
- Do not repeat the same word (case-insensitive).
- Do not include the category slug as a tag unless it is also a natural search word.
- Prefer concrete visual terms over abstract commentary.

Category:

```text
{{CATEGORY}}
```

Current tags (one per line, may be empty):

```text
{{TAGS}}
```
