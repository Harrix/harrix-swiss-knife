---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `catalog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `catalog_summary`](#-function-catalog_summary)
- [🔧 Function `load_official_songs`](#-function-load_official_songs)
- [🔧 Function `load_official_songs_from_path`](#-function-load_official_songs_from_path)
- [🔧 Function `official_songs_as_rows`](#-function-official_songs_as_rows)

</details>

## 🔧 Function `catalog_summary`

```python
def catalog_summary(songs: list[dict[str, Any]] | None = None) -> str
```

Return a short human summary of catalog size.

<details>
<summary>Code:</summary>

```python
def catalog_summary(songs: list[dict[str, Any]] | None = None) -> str:
    items = songs if songs is not None else load_official_songs()
    packs = {str(item.get("pack") or "") for item in items}
    packs.discard("")
    return f"{len(items)} official songs across {len(packs)} packs"
```

</details>

## 🔧 Function `load_official_songs`

```python
def load_official_songs() -> list[dict[str, str]]
```

Return seeded official songs as `{level_id, title, pack}` dicts.

<details>
<summary>Code:</summary>

```python
def load_official_songs() -> list[dict[str, str]]:
    package = resources.files("harrix_swiss_knife.beat_saber_saves")
    data_file = package.joinpath("data/official_songs.json")
    raw = data_file.read_text(encoding="utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, list):
        return []
    songs: list[dict[str, str]] = []
    for entry in payload:
        if not isinstance(entry, dict):
            continue
        level_id = str(entry.get("level_id") or "").strip()
        if not level_id or level_id.startswith("custom_level_"):
            continue
        songs.append(
            {
                "level_id": level_id,
                "title": str(entry.get("title") or level_id).strip() or level_id,
                "pack": str(entry.get("pack") or "").strip(),
            }
        )
    return songs
```

</details>

## 🔧 Function `load_official_songs_from_path`

```python
def load_official_songs_from_path(path: Path) -> list[dict[str, str]]
```

Load official songs from an explicit JSON path (tests).

<details>
<summary>Code:</summary>

```python
def load_official_songs_from_path(path: Path) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        return []
    return [entry for entry in payload if isinstance(entry, dict) and str(entry.get("level_id") or "").strip()]
```

</details>

## 🔧 Function `official_songs_as_rows`

```python
def official_songs_as_rows() -> list[tuple[str, str, str]]
```

Return `(level_id, title, pack)` tuples for DB seeding.

<details>
<summary>Code:</summary>

```python
def official_songs_as_rows() -> list[tuple[str, str, str]]:
    return [(s["level_id"], s["title"], s["pack"]) for s in load_official_songs()]
```

</details>
