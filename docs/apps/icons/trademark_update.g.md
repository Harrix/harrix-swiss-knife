---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `trademark_update.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TrademarkUpdateWorker`](#%EF%B8%8F-class-trademarkupdateworker)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `run`](#%EF%B8%8F-method-run)
- [🔧 Function `update_trademark_files`](#-function-update_trademark_files)

</details>

## 🏛️ Class `TrademarkUpdateWorker`

```python
class TrademarkUpdateWorker(QObject)
```

Write one trademark change outside the GUI thread.

<details>
<summary>Code:</summary>

```python
class TrademarkUpdateWorker(QObject):

    succeeded = Signal(str, bool)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        *,
        md_path: Path,
        catalog_path: Path,
        family_id: str,
        enabled: bool,
    ) -> None:
        """Store paths and the requested trademark state."""
        super().__init__()
        self._md_path = md_path
        self._catalog_path = catalog_path
        self._family_id = family_id
        self._enabled = enabled

    @Slot()
    def run(self) -> None:
        """Update both files and report completion."""
        try:
            update_trademark_files(
                md_path=self._md_path,
                catalog_path=self._catalog_path,
                family_id=self._family_id,
                enabled=self._enabled,
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            self.failed.emit(str(exc))
        else:
            self.succeeded.emit(self._family_id, self._enabled)
        finally:
            self.finished.emit()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, *, md_path: Path, catalog_path: Path, family_id: str, enabled: bool) -> None
```

Store paths and the requested trademark state.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        *,
        md_path: Path,
        catalog_path: Path,
        family_id: str,
        enabled: bool,
    ) -> None:
        super().__init__()
        self._md_path = md_path
        self._catalog_path = catalog_path
        self._family_id = family_id
        self._enabled = enabled
```

</details>

### ⚙️ Method `run`

```python
def run(self) -> None
```

Update both files and report completion.

<details>
<summary>Code:</summary>

```python
def run(self) -> None:
        try:
            update_trademark_files(
                md_path=self._md_path,
                catalog_path=self._catalog_path,
                family_id=self._family_id,
                enabled=self._enabled,
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            self.failed.emit(str(exc))
        else:
            self.succeeded.emit(self._family_id, self._enabled)
        finally:
            self.finished.emit()
```

</details>

## 🔧 Function `update_trademark_files`

```python
def update_trademark_files(*, md_path: Path, catalog_path: Path, family_id: str, enabled: bool) -> None
```

Update the Markdown warning and corresponding `catalog.json` entry.

<details>
<summary>Code:</summary>

```python
def update_trademark_files(
    *,
    md_path: Path,
    catalog_path: Path,
    family_id: str,
    enabled: bool,
) -> None:
    text = md_path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        msg = f"YAML frontmatter not found in {md_path}"
        raise ValueError(msg)

    frontmatter = match.group(1)
    body = text[match.end() :].lstrip()
    frontmatter_lines = [line for line in frontmatter.splitlines() if not line.startswith("trademark:")]
    if enabled:
        frontmatter_lines.append("trademark: true")
        if TRADEMARK_WARNING not in body:
            h1_match = _H1_RE.search(body)
            if h1_match:
                body = body[: h1_match.end()] + f"\n\n{TRADEMARK_WARNING}" + body[h1_match.end() :]
            else:
                body = f"{TRADEMARK_WARNING}\n\n{body}"
    else:
        body = body.replace(TRADEMARK_WARNING, "").strip()
        body = re.sub(r"\n{3,}", "\n\n", body)

    new_frontmatter = "\n".join(frontmatter_lines)
    new_markdown = f"---\n{new_frontmatter}\n---\n\n{body.lstrip()}\n"

    catalog_text: str | None = None
    new_catalog_text: str | None = None
    if catalog_path.is_file():
        catalog_text = catalog_path.read_text(encoding="utf-8")
        raw = json.loads(catalog_text)
        icons = raw.get("icons") if isinstance(raw, dict) else None
        if not isinstance(icons, list):
            msg = f"Invalid icons list in {catalog_path}"
            raise ValueError(msg)
        matching = [item for item in icons if isinstance(item, dict) and item.get("id") == family_id]
        if not matching:
            msg = f"Icon {family_id!r} not found in {catalog_path}"
            raise ValueError(msg)
        matching[0]["trademark"] = enabled
        new_catalog_text = json.dumps(raw, ensure_ascii=False, indent=2) + "\n"

    old_markdown = text
    try:
        md_path.write_text(new_markdown, encoding="utf-8")
        if new_catalog_text is not None:
            catalog_path.write_text(new_catalog_text, encoding="utf-8")
    except OSError:
        md_path.write_text(old_markdown, encoding="utf-8")
        if catalog_text is not None:
            catalog_path.write_text(catalog_text, encoding="utf-8")
        raise
```

</details>
