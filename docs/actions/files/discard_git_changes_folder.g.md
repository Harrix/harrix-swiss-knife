---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `discard_git_changes_folder.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnDiscardGitChangesFolder`](#%EF%B8%8F-class-ondiscardgitchangesfolder)
  - [⚙️ Method `discard_git_changes_common`](#%EF%B8%8F-method-discard_git_changes_common)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)
- [🔧 Function `find_git_repos`](#-function-find_git_repos)
- [🔧 Function `git_porcelain`](#-function-git_porcelain)
- [🔧 Function `git_run`](#-function-git_run)
- [🔧 Function `is_git_repo`](#-function-is_git_repo)

</details>

## 🏛️ Class `OnDiscardGitChangesFolder`

```python
class OnDiscardGitChangesFolder(ActionBase)
```

Discard uncommitted changes in all Git repos inside a selected folder.

Finds Git repositories that are either the selected folder itself or its
immediate child directories. For each repository runs `git reset --hard HEAD`
and `git clean -fd` (tracked changes discarded; untracked files/folders removed;
ignored files such as `.venv` are kept).

Typical use: a parent folder like `D:/Dropbox/Notes` that contains several
sibling Git projects (`Notes`, `Notes-Diaries`, …).

<details>
<summary>Code:</summary>

```python
class OnDiscardGitChangesFolder(ActionBase):

    icon = "↩️"
    title = "Discard uncommitted git changes in …"
    cli_available = True
    cli_hint = "file discard-git-changes"

    def discard_git_changes_common(self) -> None:
        """Discard uncommitted changes in every Git repo under `folder_path`."""
        if self.folder_path is None:
            return

        repos = find_git_repos(self.folder_path)
        if not repos:
            self.add_line(f"❌ No git repositories found in {self.folder_path}")
            return

        self.add_line(f"🔵 Found {len(repos)} git repository(ies) under {self.folder_path}")
        for repo in repos:
            self._discard_one_repo(repo)

    @ActionBase.handle_exceptions("discarding uncommitted git changes")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Discard uncommitted changes in all Git repos inside a selected folder."""
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                self.title,
            )
            return

        if folder_path is not None:
            self.folder_path = Path(folder_path).resolve()
        else:
            self.folder_path = self.dialogs.get_folder_with_choice_option(
                self.config["paths_notes"], self.config["path_notes"]
            )
        if not self.folder_path:
            return

        repos = find_git_repos(self.folder_path)
        if not repos:
            self.add_line(f"❌ No git repositories found in {self.folder_path}")
            if not noninteractive:
                self.show_result()
            return

        if not noninteractive:
            repo_list = "\n".join(f"  • {repo}" for repo in repos)
            if not self.dialogs.get_yes_no_question(
                self.title,
                "This will permanently discard uncommitted changes "
                f"in {len(repos)} repository(ies):\n\n{repo_list}\n\n"
                "Runs `git reset --hard HEAD` and `git clean -fd` in each.\n\n"
                "Continue?",
                default_yes=False,
            ):
                self.add_line("❌ Cancelled by user.")
                return

        if noninteractive:
            self.add_line(f"🔵 Starting discard for path: {self.folder_path}")
            self.discard_git_changes_common()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("discarding uncommitted git changes thread")
    def in_thread(self) -> str | None:
        """Execute discard in a worker thread."""
        self.discard_git_changes_common()
        return f"{self.title} completed"

    @ActionBase.handle_exceptions("discarding uncommitted git changes thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result dialog after the worker finishes."""
        self.show_toast(f"{self.title} completed")
        self.show_result()

    def _discard_one_repo(self, repo: Path) -> None:
        dirty = git_porcelain(repo).strip()
        if not dirty:
            self.add_line(f"⚪ {repo.name}: clean (no uncommitted changes)")
            return

        self.add_line(f"🔵 {repo.name}: discarding uncommitted changes…")
        reset_p = git_run(repo, "reset", "--hard", "HEAD")
        if reset_p.returncode != 0:
            self.add_line(f"❌ {repo.name}: git reset failed: {reset_p.stderr.strip() or reset_p.stdout}")
            return

        clean_p = git_run(repo, "clean", "-fd")
        if clean_p.returncode != 0:
            self.add_line(f"❌ {repo.name}: git clean failed: {clean_p.stderr.strip() or clean_p.stdout}")
            return

        self.add_line(f"✅ {repo.name}: discarded uncommitted changes")
```

</details>

### ⚙️ Method `discard_git_changes_common`

```python
def discard_git_changes_common(self) -> None
```

Discard uncommitted changes in every Git repo under `folder_path`.

<details>
<summary>Code:</summary>

```python
def discard_git_changes_common(self) -> None:
        if self.folder_path is None:
            return

        repos = find_git_repos(self.folder_path)
        if not repos:
            self.add_line(f"❌ No git repositories found in {self.folder_path}")
            return

        self.add_line(f"🔵 Found {len(repos)} git repository(ies) under {self.folder_path}")
        for repo in repos:
            self._discard_one_repo(repo)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, **_kwargs: Any) -> None
```

Discard uncommitted changes in all Git repos inside a selected folder.

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                self.title,
            )
            return

        if folder_path is not None:
            self.folder_path = Path(folder_path).resolve()
        else:
            self.folder_path = self.dialogs.get_folder_with_choice_option(
                self.config["paths_notes"], self.config["path_notes"]
            )
        if not self.folder_path:
            return

        repos = find_git_repos(self.folder_path)
        if not repos:
            self.add_line(f"❌ No git repositories found in {self.folder_path}")
            if not noninteractive:
                self.show_result()
            return

        if not noninteractive:
            repo_list = "\n".join(f"  • {repo}" for repo in repos)
            if not self.dialogs.get_yes_no_question(
                self.title,
                "This will permanently discard uncommitted changes "
                f"in {len(repos)} repository(ies):\n\n{repo_list}\n\n"
                "Runs `git reset --hard HEAD` and `git clean -fd` in each.\n\n"
                "Continue?",
                default_yes=False,
            ):
                self.add_line("❌ Cancelled by user.")
                return

        if noninteractive:
            self.add_line(f"🔵 Starting discard for path: {self.folder_path}")
            self.discard_git_changes_common()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute discard in a worker thread.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        self.discard_git_changes_common()
        return f"{self.title} completed"
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and result dialog after the worker finishes.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

## 🔧 Function `find_git_repos`

```python
def find_git_repos(root: Path) -> list[Path]
```

Return Git repos: `root` itself if it is a repo, else its immediate child repos.

<details>
<summary>Code:</summary>

```python
def find_git_repos(root: Path) -> list[Path]:
    root = root.resolve()
    if not root.is_dir():
        return []

    if is_git_repo(root):
        return [root]

    try:
        children = sorted(root.iterdir(), key=lambda p: p.name.lower())
    except OSError:
        return []

    return [child for child in children if child.is_dir() and not child.name.startswith(".") and is_git_repo(child)]
```

</details>

## 🔧 Function `git_porcelain`

```python
def git_porcelain(repo: Path) -> str
```

Return `git status --porcelain` output for `repo`.

<details>
<summary>Code:</summary>

```python
def git_porcelain(repo: Path) -> str:
    proc = git_run(repo, "status", "--porcelain")
    return proc.stdout if proc.returncode == 0 else ""
```

</details>

## 🔧 Function `git_run`

```python
def git_run(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]
```

Run a Git command in `cwd` and return the completed process.

<details>
<summary>Code:</summary>

```python
def git_run(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],  # noqa: S607
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
```

</details>

## 🔧 Function `is_git_repo`

```python
def is_git_repo(path: Path) -> bool
```

Return whether `path` is inside a Git work tree rooted at `path`.

<details>
<summary>Code:</summary>

```python
def is_git_repo(path: Path) -> bool:
    if not (path / ".git").exists():
        return False
    proc = git_run(path, "rev-parse", "--is-inside-work-tree")
    return proc.returncode == 0 and proc.stdout.strip() == "true"
```

</details>
