"""Update an existing icon note: metadata, filenames, and category folder."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.icons.add_vector_meta import (
    NoteMeta,
    extra_categories_for_family,
    note_dir_for_meta,
    sync_family_id_category,
)
from harrix_swiss_knife.apps.icons.catalog import (
    parse_note_frontmatter,
    rebuild_catalog,
    remove_empty_parents,
)
from harrix_swiss_knife.apps.icons.family_id import category_from_family_id

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.icons.catalog import IconFamily

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_H1_RE = re.compile(r"^# .+$", re.MULTILINE)
_KNOWN_FRONTMATTER_KEYS = frozenset(
    {
        "date",
        "categories",
        "tags",
        "author",
        "author-email",
        "license",
        "license-url",
        "permalink",
        "permalink-source",
        "lang",
        "trademark",
    }
)


@dataclass(slots=True)
class UpdateIconReport:
    """Outcome of applying edited icon metadata."""

    old_family_id: str
    new_family_id: str
    dest_dir: Path
    moved: bool
    renamed_files: list[str]


def replace_family_id_in_name(name: str, old_id: str, new_id: str) -> str:
    """Rename a file that is the family note or a prefixed variant."""
    if name == old_id or name.startswith((f"{old_id}.", f"{old_id}_")):
        return f"{new_id}{name[len(old_id) :]}"
    return name


def update_icon_note(
    *,
    repo_root: Path,
    family: IconFamily,
    meta: NoteMeta,
    rebuild: bool = True,
) -> UpdateIconReport:
    """Rewrite note YAML and, when needed, rename files and move the note folder."""
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


def _frontmatter_text(
    meta: NoteMeta,
    *,
    extra_categories: list[str],
    trademark: bool,
    extra_frontmatter: dict[str, object],
) -> str:
    categories = [meta.category.strip()] if meta.category.strip() else []
    categories.extend(item for item in extra_categories if item.strip() and item.casefold() != meta.category.casefold())
    lines = [
        "---",
        f"date: {meta.date}" if meta.date.strip() else "date:",
        "categories:",
    ]
    lines.extend(f"  - {item}" for item in categories)
    lines.append("tags:")
    lines.extend(f"  - {tag}" for tag in meta.tags)
    lines.extend(
        [
            f"author: {meta.author}",
            f"author-email: {meta.author_email}",
            f"license: {meta.license}",
            f"license-url: {meta.license_url}",
            f"permalink: {meta.permalink}",
            f"permalink-source: {meta.permalink_source}",
            f"lang: {meta.lang}",
        ]
    )
    if trademark:
        lines.append("trademark: true")
    for key, value in extra_frontmatter.items():
        if key in _KNOWN_FRONTMATTER_KEYS:
            continue
        if isinstance(value, list):
            lines.append(f"{key}:")
            lines.extend(f"  - {item}" for item in value)
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        else:
            lines.append(f"{key}: {value}")
    lines.extend(["---", ""])
    return "\n".join(lines)


def _note_dir_for_family(family: IconFamily, root: Path) -> Path:
    folder = family.folder.strip().replace("\\", "/")
    if not folder or folder in {".", "icons"} or ".." in Path(folder).parts:
        msg = f"Refusing to edit unsafe folder `{family.folder}`"
        raise ValueError(msg)
    note_dir = (root / folder).resolve()
    icons_root = (root / "icons").resolve()
    if not note_dir.is_relative_to(icons_root) or note_dir == icons_root:
        msg = f"Icon folder is outside icons/: {note_dir}"
        raise ValueError(msg)
    if not note_dir.is_dir():
        msg = f"Icon folder not found: {note_dir}"
        raise FileNotFoundError(msg)
    return note_dir


def _rename_family_prefixed_files(note_dir: Path, old_id: str, new_id: str) -> list[str]:
    if old_id == new_id:
        return []
    candidates: list[Path] = []
    for directory in (note_dir, note_dir / "img"):
        if not directory.is_dir():
            continue
        for path in directory.iterdir():
            if not path.is_file():
                continue
            if replace_family_id_in_name(path.name, old_id, new_id) != path.name:
                candidates.append(path)
    renamed: list[str] = []
    for path in sorted(candidates, key=lambda item: len(item.name), reverse=True):
        new_name = replace_family_id_in_name(path.name, old_id, new_id)
        dest = path.with_name(new_name)
        if dest.exists() and dest.resolve() != path.resolve():
            msg = f"Cannot rename `{path.name}` to `{new_name}`: destination exists"
            raise FileExistsError(msg)
        path.rename(dest)
        renamed.append(new_name)
    return renamed


def _replace_first_heading(body: str, title: str) -> str:
    if _H1_RE.search(body):
        return _H1_RE.sub(f"# {title}", body, count=1)
    stripped = body.lstrip("\n")
    return f"# {title}\n\n{stripped}" if stripped else f"# {title}\n"


def _rewrite_note_markdown(
    md_path: Path,
    *,
    meta: NoteMeta,
    extra_categories: list[str],
    trademark: bool,
    old_family_id: str,
    new_family_id: str,
    extra_frontmatter: dict[str, object],
) -> None:
    text = md_path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    body = text[match.end() :] if match is not None else text
    body = _replace_first_heading(body, meta.title)
    if old_family_id and old_family_id != new_family_id:
        body = body.replace(old_family_id, new_family_id)
    front = _frontmatter_text(
        meta,
        extra_categories=extra_categories,
        trademark=trademark,
        extra_frontmatter=extra_frontmatter,
    )
    body = body.lstrip("\n")
    if body and not body.endswith("\n"):
        body += "\n"
    md_path.write_text(front + body, encoding="utf-8")
