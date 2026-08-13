---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `add_svgs.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AddSvgResult`](#%EF%B8%8F-class-addsvgresult)
- [🏛️ Class `AddSvgStatus`](#%EF%B8%8F-class-addsvgstatus)
- [🏛️ Class `AddSvgsReport`](#%EF%B8%8F-class-addsvgsreport)
  - [⚙️ Method `summary_lines (property)`](#%EF%B8%8F-method-summary_lines-property)
- [🏛️ Class `SvgJob`](#%EF%B8%8F-class-svgjob)
- [🔧 Function `add_svgs_to_repo`](#-function-add_svgs_to_repo)
- [🔧 Function `append_icon_to_note`](#-function-append_icon_to_note)
- [🔧 Function `build_jobs`](#-function-build_jobs)
- [🔧 Function `discover_source_svgs`](#-function-discover_source_svgs)
- [🔧 Function `ensure_featured_image`](#-function-ensure_featured_image)
- [🔧 Function `ensure_note_scaffold`](#-function-ensure_note_scaffold)
- [🔧 Function `file_sha256`](#-function-file_sha256)
- [🔧 Function `jobs_with_content_collisions`](#-function-jobs_with_content_collisions)
- [🔧 Function `optimize_svg_to`](#-function-optimize_svg_to)
- [🔧 Function `process_job`](#-function-process_job)
- [🔧 Function `resolve_note_dir`](#-function-resolve_note_dir)
- [🔧 Function `unique_variant_name`](#-function-unique_variant_name)

</details>

## 🏛️ Class `AddSvgResult`

```python
class AddSvgResult
```

Outcome of processing one SVG.

<details>
<summary>Code:</summary>

```python
class AddSvgResult:

    source: Path
    family_id: str
    dest: Path | None
    status: AddSvgStatus
    message: str
```

</details>

## 🏛️ Class `AddSvgStatus`

```python
class AddSvgStatus(StrEnum)
```

Result status for one source SVG.

<details>
<summary>Code:</summary>

```python
class AddSvgStatus(StrEnum):

    ADDED = "added"
    REPLACED = "replaced"
    RENAMED = "renamed"
    SKIPPED_SAME = "skipped_same"
    SKIPPED_POLICY = "skipped_policy"
    CREATED_NOTE = "created_note"
    ERROR = "error"
```

</details>

## 🏛️ Class `AddSvgsReport`

```python
class AddSvgsReport
```

Aggregate report for a batch import.

<details>
<summary>Code:</summary>

```python
class AddSvgsReport:

    results: list[AddSvgResult] = field(default_factory=list)
    catalog_rebuilt: bool = False

    @property
    def summary_lines(self) -> list[str]:
        """Human-readable summary lines."""
        counts: dict[str, int] = {}
        for item in self.results:
            counts[item.status.value] = counts.get(item.status.value, 0) + 1
        status_order = (
            AddSvgStatus.ADDED,
            AddSvgStatus.CREATED_NOTE,
            AddSvgStatus.RENAMED,
            AddSvgStatus.REPLACED,
            AddSvgStatus.SKIPPED_SAME,
            AddSvgStatus.SKIPPED_POLICY,
            AddSvgStatus.ERROR,
        )
        lines = [f"Processed {len(self.results)} SVG file(s)."]
        lines.extend(f"- {key.value}: {counts[key.value]}" for key in status_order if counts.get(key.value))
        if self.catalog_rebuilt:
            lines.append("Catalog rebuilt.")
        return lines
```

</details>

### ⚙️ Method `summary_lines (property)`

```python
def summary_lines(self) -> list[str]
```

Human-readable summary lines.

<details>
<summary>Code:</summary>

```python
def summary_lines(self) -> list[str]:
        counts: dict[str, int] = {}
        for item in self.results:
            counts[item.status.value] = counts.get(item.status.value, 0) + 1
        status_order = (
            AddSvgStatus.ADDED,
            AddSvgStatus.CREATED_NOTE,
            AddSvgStatus.RENAMED,
            AddSvgStatus.REPLACED,
            AddSvgStatus.SKIPPED_SAME,
            AddSvgStatus.SKIPPED_POLICY,
            AddSvgStatus.ERROR,
        )
        lines = [f"Processed {len(self.results)} SVG file(s)."]
        lines.extend(f"- {key.value}: {counts[key.value]}" for key in status_order if counts.get(key.value))
        if self.catalog_rebuilt:
            lines.append("Catalog rebuilt.")
        return lines
```

</details>

## 🏛️ Class `SvgJob`

```python
class SvgJob
```

One source SVG mapped to a target note folder.

<details>
<summary>Code:</summary>

```python
class SvgJob:

    source: Path
    family_id: str
    note_dir: Path
    dest_name: str
    dest_path: Path
    source_hash: str
    collision: bool = False
    same_hash: bool = False
```

</details>

## 🔧 Function `add_svgs_to_repo`

```python
def add_svgs_to_repo(source_dir: Path, *, repo_root: Path, collision_policy: CollisionPolicy = 'rename', rebuild: bool = True) -> AddSvgsReport
```

Discover SVGs in `source_dir`, add them into note folders, optionally rebuild catalog.

<details>
<summary>Code:</summary>

```python
def add_svgs_to_repo(
    source_dir: Path,
    *,
    repo_root: Path,
    collision_policy: CollisionPolicy = "rename",
    rebuild: bool = True,
) -> AddSvgsReport:
    report = AddSvgsReport()
    sources = discover_source_svgs(source_dir)
    if not sources:
        report.results.append(
            AddSvgResult(
                source=source_dir,
                family_id="",
                dest=None,
                status=AddSvgStatus.ERROR,
                message=f"No SVG files found in `{source_dir}`",
            )
        )
        return report

    jobs = build_jobs(sources, repo_root=repo_root)
    for job in jobs:
        report.results.extend(process_job(job, repo_root=repo_root, collision_policy=collision_policy))

    if rebuild:
        rebuild_catalog(repo_root)
        report.catalog_rebuilt = True
    return report
```

</details>

## 🔧 Function `append_icon_to_note`

```python
def append_icon_to_note(md_path: Path, svg_name: str) -> None
```

Append an image bullet under `## Icons` when not already listed.

<details>
<summary>Code:</summary>

```python
def append_icon_to_note(md_path: Path, svg_name: str) -> None:
    if not md_path.is_file():
        return
    text = md_path.read_text(encoding="utf-8")
    bullet = f"- ![{Path(svg_name).stem}](img/{svg_name})"
    if f"img/{svg_name}" in text:
        return
    match = _ICONS_SECTION_RE.search(text)
    if match:
        section_body = match.group(2).rstrip()
        new_section = match.group(1) + (section_body + "\n" if section_body else "") + bullet + "\n"
        text = text[: match.start()] + new_section + text[match.end() :]
    elif "## Icons" not in text:
        text = text.rstrip() + f"\n\n## Icons\n\n{bullet}\n"
    else:
        text = text.rstrip() + f"\n{bullet}\n"
    md_path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
```

</details>

## 🔧 Function `build_jobs`

```python
def build_jobs(source_svgs: list[Path], *, repo_root: Path) -> list[SvgJob]
```

Map source SVGs to destination note folders and detect collisions.

<details>
<summary>Code:</summary>

```python
def build_jobs(source_svgs: list[Path], *, repo_root: Path) -> list[SvgJob]:
    icons_dir = Path(repo_root) / "icons"
    jobs: list[SvgJob] = []
    for source in source_svgs:
        family_id = family_id_from_stem(source.stem)
        note_dir = resolve_note_dir(icons_dir, family_id)
        dest_name = source.name
        dest_path = note_dir / "img" / dest_name
        source_hash = file_sha256(source)
        collision = dest_path.is_file()
        same_hash = collision and file_sha256(dest_path) == source_hash
        jobs.append(
            SvgJob(
                source=source,
                family_id=family_id,
                note_dir=note_dir,
                dest_name=dest_name,
                dest_path=dest_path,
                source_hash=source_hash,
                collision=collision,
                same_hash=same_hash,
            )
        )
    return jobs
```

</details>

## 🔧 Function `discover_source_svgs`

```python
def discover_source_svgs(source_dir: Path) -> list[Path]
```

Return sorted SVG files under `source_dir` (non-recursive for top-level packs, recursive otherwise).

Scans recursively, but skips files already inside a target repo `icons/` tree when
`source_dir` itself is that repo root.

<details>
<summary>Code:</summary>

```python
def discover_source_svgs(source_dir: Path) -> list[Path]:
    root = Path(source_dir).resolve()
    if not root.is_dir():
        return []
    icons_marker = root / "icons"
    results: list[Path] = []
    for path in sorted(root.rglob("*.svg")):
        if not path.is_file():
            continue
        # Avoid re-importing from the destination icons tree when user picks the repo root.
        try:
            if icons_marker.is_dir() and path.resolve().is_relative_to(icons_marker.resolve()):
                continue
        except (OSError, ValueError):
            pass
        results.append(path)
    return results
```

</details>

## 🔧 Function `ensure_featured_image`

```python
def ensure_featured_image(note_dir: Path, svg_path: Path) -> None
```

Copy `svg_path` to `featured-image.svg` when featured is missing.

<details>
<summary>Code:</summary>

```python
def ensure_featured_image(note_dir: Path, svg_path: Path) -> None:
    featured = note_dir / "featured-image.svg"
    if featured.is_file():
        return
    featured.write_text(svg_path.read_text(encoding="utf-8"), encoding="utf-8")
```

</details>

## 🔧 Function `ensure_note_scaffold`

```python
def ensure_note_scaffold(note_dir: Path, family_id: str, *, repo_root: Path) -> bool
```

Create note folder + Markdown when missing. Return whether a new note was created.

<details>
<summary>Code:</summary>

```python
def ensure_note_scaffold(note_dir: Path, family_id: str, *, repo_root: Path) -> bool:
    note_dir.mkdir(parents=True, exist_ok=True)
    (note_dir / "img").mkdir(parents=True, exist_ok=True)
    md_path = note_dir / f"{family_id}.md"
    if md_path.is_file():
        return False

    category = category_from_family_id(family_id)
    title = title_from_family_id(family_id)
    tags = tags_from_family_id(family_id)
    tags_yaml = ", ".join(tags)
    today = datetime.now(UTC).date().isoformat()
    permalink = _permalink_for_note(note_dir, family_id, repo_root)
    body = f"""---
date: {today}
categories: [{category}]
tags: [{tags_yaml}]
author: {_AUTHOR}
author-email: {_AUTHOR_EMAIL}
license: CC BY 4.0
license-url: {_LICENSE_URL}
permalink-source: {permalink}
lang: en
---

# {title}

![Featured image](featured-image.svg)

## Icons

"""
    md_path.write_text(body, encoding="utf-8")
    return True
```

</details>

## 🔧 Function `file_sha256`

```python
def file_sha256(path: Path) -> str
```

Return hex SHA-256 of a file.

<details>
<summary>Code:</summary>

```python
def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
```

</details>

## 🔧 Function `jobs_with_content_collisions`

```python
def jobs_with_content_collisions(jobs: list[SvgJob]) -> list[SvgJob]
```

Return jobs where destination exists with a different hash.

<details>
<summary>Code:</summary>

```python
def jobs_with_content_collisions(jobs: list[SvgJob]) -> list[SvgJob]:
    return [job for job in jobs if job.collision and not job.same_hash]
```

</details>

## 🔧 Function `optimize_svg_to`

```python
def optimize_svg_to(source: Path, dest: Path) -> str
```

Optimize `source` SVG into `dest` via `harrix_pylib` SvgOptimizer.

<details>
<summary>Code:</summary>

```python
def optimize_svg_to(source: Path, dest: Path) -> str:
    return h.svg_opt.SvgOptimizer().optimize_file(source, dest)
```

</details>

## 🔧 Function `process_job`

```python
def process_job(job: SvgJob, *, repo_root: Path, collision_policy: CollisionPolicy) -> list[AddSvgResult]
```

Process one SVG job (create note, optimize, place, update Markdown).

<details>
<summary>Code:</summary>

```python
def process_job(
    job: SvgJob,
    *,
    repo_root: Path,
    collision_policy: CollisionPolicy,
) -> list[AddSvgResult]:
    results: list[AddSvgResult] = []
    created = ensure_note_scaffold(job.note_dir, job.family_id, repo_root=repo_root)
    if created:
        results.append(
            AddSvgResult(
                source=job.source,
                family_id=job.family_id,
                dest=job.note_dir / f"{job.family_id}.md",
                status=AddSvgStatus.CREATED_NOTE,
                message=f"Created note `{job.family_id}`",
            )
        )

    img_dir = job.note_dir / "img"
    img_dir.mkdir(parents=True, exist_ok=True)
    dest_path = job.dest_path
    status = AddSvgStatus.ADDED

    if job.same_hash:
        return [
            *results,
            AddSvgResult(
                source=job.source,
                family_id=job.family_id,
                dest=dest_path,
                status=AddSvgStatus.SKIPPED_SAME,
                message=f"Skipped `{job.source.name}` (identical file already in note)",
            ),
        ]

    if job.collision and not job.same_hash:
        if collision_policy == "skip":
            return [
                *results,
                AddSvgResult(
                    source=job.source,
                    family_id=job.family_id,
                    dest=dest_path,
                    status=AddSvgStatus.SKIPPED_POLICY,
                    message=f"Skipped `{job.source.name}` (collision, policy=skip)",
                ),
            ]
        if collision_policy == "rename":
            new_name = unique_variant_name(img_dir, job.source.stem)
            dest_path = img_dir / new_name
            status = AddSvgStatus.RENAMED
        else:
            status = AddSvgStatus.REPLACED

    try:
        optimize_svg_to(job.source, dest_path)
        ensure_featured_image(job.note_dir, dest_path)
        append_icon_to_note(job.note_dir / f"{job.family_id}.md", dest_path.name)
    except (OSError, ValueError, RuntimeError) as exc:
        return [
            *results,
            AddSvgResult(
                source=job.source,
                family_id=job.family_id,
                dest=dest_path,
                status=AddSvgStatus.ERROR,
                message=f"Error for `{job.source.name}`: {exc}",
            ),
        ]

    verb = {
        AddSvgStatus.ADDED: "Added",
        AddSvgStatus.RENAMED: "Added as",
        AddSvgStatus.REPLACED: "Replaced",
    }.get(status, "Wrote")
    results.append(
        AddSvgResult(
            source=job.source,
            family_id=job.family_id,
            dest=dest_path,
            status=status,
            message=f"{verb} `{dest_path.name}` → `{job.family_id}`",
        )
    )
    return results
```

</details>

## 🔧 Function `resolve_note_dir`

```python
def resolve_note_dir(icons_dir: Path, family_id: str) -> Path
```

Return existing note folder for `family_id`, or the nested target path.

<details>
<summary>Code:</summary>

```python
def resolve_note_dir(icons_dir: Path, family_id: str) -> Path:
    nested = note_dir_for_family_id(icons_dir, family_id)
    if nested.is_dir():
        return nested
    flat = Path(icons_dir) / family_id
    if flat.is_dir():
        return flat
    # Search one level of category folders for a matching family folder name.
    try:
        for child in icons_dir.iterdir():
            if not child.is_dir():
                continue
            candidate = child / family_id
            if candidate.is_dir():
                return candidate
    except OSError:
        pass
    return nested
```

</details>

## 🔧 Function `unique_variant_name`

```python
def unique_variant_name(img_dir: Path, stem: str, suffix: str = '.svg') -> str
```

Return a free filename in `img_dir`, preferring `{stem}_new`, then `_new2`, and so on.

<details>
<summary>Code:</summary>

```python
def unique_variant_name(img_dir: Path, stem: str, suffix: str = ".svg") -> str:
    candidate = f"{stem}_new{suffix}"
    if not (img_dir / candidate).exists():
        return candidate
    index = 2
    while True:
        candidate = f"{stem}_new{index}{suffix}"
        if not (img_dir / candidate).exists():
            return candidate
        index += 1
```

</details>
