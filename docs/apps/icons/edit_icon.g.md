---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `edit_icon.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `UpdateIconReport`](#%EF%B8%8F-class-updateiconreport)
- [🔧 Function `replace_family_id_in_name`](#-function-replace_family_id_in_name)
- [🔧 Function `update_icon_note`](#-function-update_icon_note)

</details>

## 🏛️ Class `UpdateIconReport`

```python
class UpdateIconReport
```

Outcome of applying edited icon metadata.

<details>
<summary>Code:</summary>

```python
class UpdateIconReport:

    old_family_id: str
    new_family_id: str
    dest_dir: Path
    moved: bool
    renamed_files: list[str]
```

</details>

## 🔧 Function `replace_family_id_in_name`

```python
def replace_family_id_in_name(name: str, old_id: str, new_id: str) -> str
```

Rename a file that is the family note or a prefixed variant.

<details>
<summary>Code:</summary>

```python
def replace_family_id_in_name(name: str, old_id: str, new_id: str) -> str:
    if name == old_id or name.startswith((f"{old_id}.", f"{old_id}_")):
        return f"{new_id}{name[len(old_id) :]}"
    return name
```

</details>

## 🔧 Function `update_icon_note`

```python
def update_icon_note(*, repo_root: Path, family: IconFamily, meta: NoteMeta, rebuild: bool = True) -> UpdateIconReport
```

Rewrite note YAML and, when needed, rename files and move the note folder.

<details>
<summary>Code:</summary>

```python
def update_icon_note(
    *,
    repo_root: Path,
    family: IconFamily,
    meta: NoteMeta,
    rebuild: bool = True,
) -> UpdateIconReport:
    root = Path(repo_root).expanduser().resolve()
    current_dir = _note_dir_for_family(family, root)
    icons_root = (root / "icons").resolve()
    old_id = family.id
    new_id = sync_family_id_category(meta.family_id.strip(), meta.category.strip()) or meta.family_id.strip()
    if not new_id:
        msg = "Filename is empty"
        raise ValueError(msg)

    if "__" in old_id:
        old_category = category_from_family_id(old_id)
    elif family.categories:
        old_category = family.categories[0]
    else:
        old_category = ""
    category_changed = meta.category.strip() != old_category
    id_changed = new_id != old_id
    dest_dir = current_dir
    if category_changed or id_changed:
        dest_dir = note_dir_for_meta(root, family_id=new_id, category=meta.category).resolve()
        if dest_dir != current_dir and dest_dir.exists():
            msg = f"Destination already exists: {dest_dir}"
            raise FileExistsError(msg)

    md_path = current_dir / f"{old_id}.md"
    if not md_path.is_file():
        md_path = current_dir / f"{new_id}.md"
    if not md_path.is_file():
        msg = f"Markdown note not found in `{current_dir}`"
        raise FileNotFoundError(msg)

    existing_frontmatter = parse_note_frontmatter(md_path.read_text(encoding="utf-8"))
    renamed = _rename_family_prefixed_files(current_dir, old_id, new_id) if id_changed else []
    md_path = current_dir / f"{new_id}.md"
    if not md_path.is_file():
        msg = f"Markdown note not found after rename in `{current_dir}`"
        raise FileNotFoundError(msg)

    extras = extra_categories_for_family(family.categories, old_id)
    extras = extra_categories_for_family(extras, new_id)
    applied = NoteMeta(
        family_id=new_id,
        title=meta.title,
        date=meta.date,
        category=meta.category,
        tags=list(meta.tags),
        author=meta.author,
        author_email=meta.author_email,
        license=meta.license,
        license_url=meta.license_url,
        permalink=meta.permalink,
        permalink_source=meta.permalink_source,
        lang=meta.lang,
        featured_name=meta.featured_name or family.featured or "featured-image.svg",
    )
    _rewrite_note_markdown(
        md_path,
        meta=applied,
        extra_categories=extras,
        trademark=family.trademark,
        old_family_id=old_id,
        new_family_id=new_id,
        extra_frontmatter=existing_frontmatter,
    )

    moved = False
    if dest_dir != current_dir:
        dest_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(current_dir), str(dest_dir))
        remove_empty_parents(current_dir.parent, icons_root)
        moved = True

    if rebuild:
        rebuild_catalog(root)
    return UpdateIconReport(
        old_family_id=old_id,
        new_family_id=new_id,
        dest_dir=dest_dir,
        moved=moved,
        renamed_files=renamed,
    )
```

</details>
