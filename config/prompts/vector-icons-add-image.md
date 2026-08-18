Suggest metadata for a new vector icon note.

You receive a **raster preview** of the icon (not SVG), the current form values,
and a list of existing variant filenames already in this icons repository.

Tasks:

1. Suggest a concise family `filename` using `category__slug` when possible
   (lowercase, double underscore between category and slug, hyphens inside tokens).
2. Suggest a human `name` (Title Case, no category prefix).
3. Suggest one `category` slug (lowercase).
4. Suggest bilingual EN/RU search `tags` (one per line), same style as keyword expansion.

Return **only** these fields in this exact shape (no markdown fences):

```text
filename: category__slug
name: Title Case Name
category: category
tags:
keyword one
keyword two
```

Current values (may be empty):

```text
FILENAME: {{FILENAME}}
NAME: {{NAME}}
CATEGORY: {{CATEGORY}}
TAGS:
{{TAGS}}
```

Existing variant filenames in the repository (one stem per line, may be truncated):

```text
{{EXISTING_FILES}}
```
