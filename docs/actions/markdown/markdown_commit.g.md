---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `markdown_commit.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_commit_message_for_command`](#-function-build_commit_message_for_command)
- [🔧 Function `build_commit_message_for_template`](#-function-build_commit_message_for_template)
- [🔧 Function `format_commit_message`](#-function-format_commit_message)
- [🔧 Function `resolve_git_repo`](#-function-resolve_git_repo)
- [🔧 Function `run_git_commit`](#-function-run_git_commit)
- [🔧 Function `_commit_substitution_values`](#-function-_commit_substitution_values)
- [🔧 Function `_is_git_repo`](#-function-_is_git_repo)

</details>

## 🔧 Function `build_commit_message_for_command`

```python
def build_commit_message_for_command(command_key: str, **field_values: str) -> str | None
```

Return a commit subject for a built-in New Markdown command.

<details>
<summary>Code:</summary>

```python
def build_commit_message_for_command(command_key: str, **field_values: str) -> str | None:
    pattern = _BUILTIN_COMMAND_COMMIT_MESSAGES.get(command_key)
    if not pattern:
        return None
    return format_commit_message(pattern, field_values)
```

</details>

## 🔧 Function `build_commit_message_for_template`

```python
def build_commit_message_for_template(template_name: str, template_config: dict[str, Any], field_values: dict[str, str]) -> str | None
```

Return a commit subject for a markdown_templates entry, or None if unknown.

<details>
<summary>Code:</summary>

```python
def build_commit_message_for_template(
    template_name: str,
    template_config: dict[str, Any],
    field_values: dict[str, str],
) -> str | None:
    pattern = template_config.get("commit_message_template") or _DEFAULT_TEMPLATE_COMMIT_MESSAGES.get(template_name)
    if not pattern:
        return None
    return format_commit_message(str(pattern), field_values)
```

</details>

## 🔧 Function `format_commit_message`

```python
def format_commit_message(pattern: str, field_values: dict[str, str]) -> str
```

Substitute `{Field}` placeholders in a commit message pattern.

<details>
<summary>Code:</summary>

```python
def format_commit_message(pattern: str, field_values: dict[str, str]) -> str:
    values = _commit_substitution_values(field_values)

    def _replace(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        return values.get(key, "")

    message = _COMMIT_PLACEHOLDER_RE.sub(_replace, pattern)
    message = re.sub(r"  +", " ", message)
    return message.strip()
```

</details>

## 🔧 Function `resolve_git_repo`

```python
def resolve_git_repo(target_path: Path, paths_git: list[str]) -> Path | None
```

Find a git repository root that contains `target_path`.

<details>
<summary>Code:</summary>

```python
def resolve_git_repo(target_path: Path, paths_git: list[str]) -> Path | None:
    target = target_path.resolve()
    candidates: list[Path] = []

    for raw in paths_git:
        repo = Path(raw).resolve()
        try:
            target.relative_to(repo)
        except ValueError:
            continue
        candidates.append(repo)

    if candidates:
        candidates.sort(key=lambda path: len(str(path)), reverse=True)
        for repo in candidates:
            if _is_git_repo(repo):
                return repo

    current = target if target.is_dir() else target.parent
    while True:
        if _is_git_repo(current):
            return current
        if current.parent == current:
            break
        current = current.parent
    return None
```

</details>

## 🔧 Function `run_git_commit`

```python
def run_git_commit(repo: Path, message: str, paths_to_add: list[Path]) -> tuple[bool, str]
```

Stage `paths_to_add` relative to `repo` and create a commit.

<details>
<summary>Code:</summary>

```python
def run_git_commit(repo: Path, message: str, paths_to_add: list[Path]) -> tuple[bool, str]:
    repo_resolved = repo.resolve()
    rel_paths: list[str] = []
    for path in paths_to_add:
        if not path.exists():
            continue
        resolved = path.resolve()
        try:
            rel_paths.append(resolved.relative_to(repo_resolved).as_posix())
        except ValueError:
            continue

    if not rel_paths:
        return False, "No files inside the git repository to commit."

    add_proc = subprocess.run(
        ["git", "add", "--", *rel_paths],  # noqa: S607
        cwd=repo_resolved,
        capture_output=True,
        text=True,
        check=False,
    )
    add_output = (add_proc.stdout + "\n" + add_proc.stderr).strip()
    if add_proc.returncode != 0:
        return False, add_output or "git add failed."

    commit_proc = subprocess.run(
        ["git", "commit", "-m", message],  # noqa: S607
        cwd=repo_resolved,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (commit_proc.stdout + "\n" + commit_proc.stderr).strip()
    if commit_proc.returncode != 0:
        return False, output or "git commit failed."
    return True, output
```

</details>

## 🔧 Function `_commit_substitution_values`

```python
def _commit_substitution_values(field_values: dict[str, str]) -> dict[str, str]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _commit_substitution_values(field_values: dict[str, str]) -> dict[str, str]:
    now_local = datetime.now(UTC).astimezone()
    author_english = (field_values.get("Author's name in English") or "").strip()
    author = (field_values.get("Author") or "").strip()
    values = {key: (value or "").strip() for key, value in field_values.items()}
    values["AuthorEnglish"] = author_english or author
    values["Date"] = values.get("Date") or now_local.strftime("%Y-%m-%d")
    return values
```

</details>

## 🔧 Function `_is_git_repo`

```python
def _is_git_repo(path: Path) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _is_git_repo(path: Path) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode == 0 and proc.stdout.strip() == "true"
```

</details>
