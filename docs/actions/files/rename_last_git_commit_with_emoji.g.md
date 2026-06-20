---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `rename_last_git_commit_with_emoji.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnRenameLastGitCommitWithEmoji`](#️-class-onrenamelastgitcommitwithemoji)
  - [⚙️ Method `execute`](#️-method-execute)
  - [⚙️ Method `_amend_with_message`](#️-method-_amend_with_message)
  - [⚙️ Method `_apply_keyword_emoji_prefix`](#️-method-_apply_keyword_emoji_prefix)
  - [⚙️ Method `_git_out`](#️-method-_git_out)
  - [⚙️ Method `_git_subprocess`](#️-method-_git_subprocess)
  - [⚙️ Method `_mapped_emojis_sorted`](#️-method-_mapped_emojis_sorted)
  - [⚙️ Method `_mode_add_emoji_last`](#️-method-_mode_add_emoji_last)
  - [⚙️ Method `_mode_rename_by_hash`](#️-method-_mode_rename_by_hash)
  - [⚙️ Method `_mode_rename_last`](#️-method-_mode_rename_last)
  - [⚙️ Method `_push_current_branch`](#️-method-_push_current_branch)
  - [⚙️ Method `_run_rebase_reword`](#️-method-_run_rebase_reword)
  - [⚙️ Method `_subject_has_mapped_emoji_prefix`](#️-method-_subject_has_mapped_emoji_prefix)
  - [⚙️ Method `_write_temp_editor`](#️-method-_write_temp_editor)

</details>

## 🏛️ Class `OnRenameLastGitCommitWithEmoji`

```python
class OnRenameLastGitCommitWithEmoji(ActionBase)
```

Git commit subject: add emoji by keyword, rename last commit, or rename by hash.

Offers three modes after choosing a repository: append emoji to the latest commit only
(unchanged text), set a new message for HEAD (with optional emoji), or reword a commit
by hash via interactive rebase (with optional emoji). Emoji rules match keyword prefixes
in `EMOJI_MAPPING` when the subject does not already start with a mapped emoji.

<details>
<summary>Code:</summary>

```python
class OnRenameLastGitCommitWithEmoji(ActionBase):

    icon = "🎯"
    title = "Git commit message (emoji / rename)…"

    _MODE_CHOICES: ClassVar[list[tuple[str, str, str]]] = [
        ("➕", "Add emoji (last commit)", "_mode_add_emoji_last"),  # noqa: RUF001
        ("✒️", "Rename last commit", "_mode_rename_last"),
        ("🔑", "Rename by hash", "_mode_rename_by_hash"),
    ]

    EMOJI_MAPPING: ClassVar[dict[str, str]] = {
        "Add": "➕",  # noqa: RUF001
        "Create": "➕",  # noqa: RUF001
        "Build": "🚀",
        "Delete": "🗑️",
        "Remove": "🗑️",
        "Docs": "📚",
        "Experiment": "🧪",
        "Fix": "🐞",
        "Modify": "🔧",
        "Move": "🚚",
        "Refactor": "♻️",
        "Rename": "✒️",
        "Replace": "🔄",
        "Style": "✨",
        "Test": "⚗️",
        "Update": "⬆️",
        "Revert": "🔙",
        "Publish": "🚀",
        "Merge": "🔀",
    }

    _SEQUENCE_EDITOR_SCRIPT = r"""import os
import subprocess
import sys
from pathlib import Path


def _resolve(repo: str, ref: str) -> str:
    r = subprocess.run(
        ["git", "-C", repo, "rev-parse", ref],
        capture_output=True,
        text=True,
        check=False,
    )
    return r.stdout.strip() if r.returncode == 0 else ""


def main() -> None:
    repo = os.environ["HARRIX_GIT_REPO"]
    target = os.environ["HARRIX_TARGET_FULL"]
    todo_path = sys.argv[1]
    lines = Path(todo_path).read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    changed = False
    for line in lines:
        parts = line.split(None, 2)
        if len(parts) >= 2 and parts[0] == "pick" and _resolve(repo, parts[1]) == target:
            line = line.replace("pick ", "reword ", 1)
            changed = True
        out.append(line)
    if not changed:
        sys.stderr.write("harrix: could not find pick line for target commit\n")
        raise SystemExit(1)
    Path(todo_path).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
"""

    _MSG_EDITOR_SOURCE = r"""import os
import sys
from pathlib import Path

Path(sys.argv[1]).write_text(os.environ["HARRIX_NEW_SUBJECT"] + "\n", encoding="utf-8")
"""

    @ActionBase.handle_exceptions("Git commit message (emoji / rename)")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Git commit subject: add emoji by keyword, rename last commit, or rename by hash."""
        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_git"], self.config["path_github"]
        )
        if not self.folder_path:
            return

        self.add_line(f"🔵 Processing git repository: {self.folder_path}")

        choices = [(icon, title) for icon, title, _ in self._MODE_CHOICES]
        selected = self.dialogs.get_choice_from_icons("Git commit message", "Choose an action:", choices)
        if not selected:
            return

        method_name = next((m for _, t, m in self._MODE_CHOICES if t == selected), None)
        if not method_name:
            self.add_line(f"❌ Unknown choice: {selected}")
            self.show_result()
            return

        original_cwd = Path.cwd()
        os.chdir(self.folder_path)

        try:
            getattr(self, method_name)(self.folder_path)
        finally:
            os.chdir(original_cwd)

        self.show_result()

    def _amend_with_message(self, folder_path: Path, new_message: str) -> None:
        self.add_line(f"🔄 Amending commit with new message: {new_message}")
        escaped = new_message.replace('"', '\\"')
        out = self._git_out(f'git commit --amend -m "{escaped}"', folder_path)
        self.add_line("✅ Commit amended successfully")
        self.add_line(f"📊 Git output: {out}")

    def _apply_keyword_emoji_prefix(self, subject: str) -> str:
        if self._subject_has_mapped_emoji_prefix(subject):
            return subject
        for keyword, emoji in self.EMOJI_MAPPING.items():
            if subject.startswith(keyword):
                self.add_line(f"🎯 Found keyword '{keyword}', adding emoji {emoji}")
                return f"{emoji} {subject}"
        return subject

    def _git_out(self, cmd: str, cwd: Path) -> str:
        return h.dev.run_command(cmd, cwd=str(cwd))

    @staticmethod
    def _git_subprocess(
        args: list[str],
        cwd: Path,
        *,
        env: dict[str, str] | None = None,
        capture_output: bool = False,
        text: bool = False,
        check: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],  # noqa: S607
            cwd=cwd,
            env=env,
            capture_output=capture_output,
            text=text,
            check=check,
        )

    def _mapped_emojis_sorted(self) -> list[str]:
        emojis: set[str] = set(self.EMOJI_MAPPING.values())

        def _len_str(s: str) -> int:
            return len(s)

        return sorted(emojis, key=_len_str, reverse=True)

    def _mode_add_emoji_last(self, folder_path: Path) -> None:
        result = self._git_out("git log -1 --pretty=format:%s", folder_path)
        if not result.strip():
            self.add_line("❌ No git commits found or not a git repository")
            return

        last_commit_message = result.strip()
        self.add_line(f"📝 Last commit message: {last_commit_message}")

        if self._subject_has_mapped_emoji_prefix(last_commit_message):
            self.add_line("✅ Emoji already present in commit message")
            return

        new_message = None
        for keyword, emoji in self.EMOJI_MAPPING.items():
            if last_commit_message.startswith(keyword):
                new_message = f"{emoji} {last_commit_message}"
                self.add_line(f"🎯 Found keyword '{keyword}', adding emoji {emoji}")
                break

        if not new_message:
            self.add_line("ℹ️ No matching keyword found, no changes needed")  # noqa: RUF001
            return

        self._amend_with_message(folder_path, new_message)
        self._push_current_branch(folder_path)

    def _mode_rename_by_hash(self, folder_path: Path) -> None:
        hash_raw = self.dialogs.get_text_input("Commit hash", "Enter commit hash to reword:", "")
        if hash_raw is None:
            return

        commit_ref = f"{hash_raw}^{{commit}}"
        verify_p = self._git_subprocess(
            ["rev-parse", "--verify", commit_ref],
            folder_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if verify_p.returncode != 0:
            self.add_line(f"❌ Invalid commit: {hash_raw}")
            return

        full_p = self._git_subprocess(
            ["rev-parse", hash_raw],
            folder_path,
            capture_output=True,
            text=True,
            check=False,
        )
        full_hash = full_p.stdout.strip()
        if not full_hash:
            self.add_line("❌ Could not resolve commit hash")
            return

        anc = self._git_subprocess(
            ["merge-base", "--is-ancestor", full_hash, "HEAD"],
            folder_path,
            capture_output=True,
            check=False,
        )
        if anc.returncode != 0:
            self.add_line("❌ That commit is not an ancestor of HEAD on this branch")
            return

        parent_check = self._git_subprocess(
            ["rev-parse", "--verify", f"{full_hash}^"],
            folder_path,
            capture_output=True,
            check=False,
        )
        if parent_check.returncode != 0:
            self.add_line("❌ Cannot reword root commit with this flow (no parent). Use another Git workflow.")
            return

        old_subject = self._git_out(f"git log -1 {full_hash} --pretty=format:%s", folder_path).strip()
        if not old_subject:
            self.add_line("❌ Could not read commit message")
            return

        self.add_line(f"📝 Current message for {full_hash[:7]}: {old_subject}")
        raw = self.dialogs.get_text_input("New message", "New commit message (subject line):", old_subject)
        if raw is None:
            return

        final_subject = self._apply_keyword_emoji_prefix(raw)
        if final_subject != raw:
            self.add_line(f"📝 Message after emoji rule: {final_subject}")

        if not self._run_rebase_reword(folder_path, full_hash, final_subject):
            return
        self._push_current_branch(folder_path)

    def _mode_rename_last(self, folder_path: Path) -> None:
        result = self._git_out("git log -1 --pretty=format:%s", folder_path)
        if not result.strip():
            self.add_line("❌ No git commits found or not a git repository")
            return

        default_subject = result.strip()
        self.add_line(f"📝 Current last commit message: {default_subject}")
        raw = self.dialogs.get_text_input("Rename last commit", "New commit message (subject line):", default_subject)
        if raw is None:
            return

        final_subject = self._apply_keyword_emoji_prefix(raw)
        if final_subject != raw:
            self.add_line(f"📝 Message after emoji rule: {final_subject}")

        self._amend_with_message(folder_path, final_subject)
        self._push_current_branch(folder_path)

    def _push_current_branch(self, folder_path: Path) -> None:
        branch = self._git_out("git rev-parse --abbrev-ref HEAD", folder_path).strip()
        if branch == "HEAD":
            self.add_line("❌ Detached HEAD: cannot push (no current branch name)")
            return
        escaped_branch = branch.replace('"', '\\"')
        out = self._git_out(f'git push origin "{escaped_branch}" --force', folder_path)
        self.add_line(f"✅ Push finished: {out}")

    def _run_rebase_reword(self, folder_path: Path, full_hash: str, new_subject: str) -> bool:
        repo = str(folder_path.resolve())
        seq_script: Path | None = None
        msg_script: Path | None = None
        env = os.environ.copy()
        env["HARRIX_GIT_REPO"] = repo
        env["HARRIX_TARGET_FULL"] = full_hash
        env["HARRIX_NEW_SUBJECT"] = new_subject
        completed: subprocess.CompletedProcess[str] | None = None
        try:
            seq_script = self._write_temp_editor(self._SEQUENCE_EDITOR_SCRIPT)
            msg_script = self._write_temp_editor(self._MSG_EDITOR_SOURCE)
            seq_q = shlex.quote(str(seq_script))
            exe_q = shlex.quote(sys.executable)
            env["GIT_SEQUENCE_EDITOR"] = f"{exe_q} {seq_q}"
            env["GIT_EDITOR"] = f"{exe_q} {shlex.quote(str(msg_script))}"
            parent = f"{full_hash}^"
            completed = self._git_subprocess(
                ["rebase", "-i", parent],
                folder_path,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
        finally:
            if seq_script is not None:
                seq_script.unlink(missing_ok=True)
            if msg_script is not None:
                msg_script.unlink(missing_ok=True)
        if completed is None:
            return False
        if completed.stdout:
            self.add_line(completed.stdout.rstrip())
        if completed.stderr:
            self.add_line(completed.stderr.rstrip())
        if completed.returncode != 0:
            msg = f"❌ git rebase failed (exit {completed.returncode}). Run `git rebase --abort` in the repo if needed."
            self.add_line(msg)
            return False
        self.add_line("✅ Rebase finished; commit message updated")
        return True

    def _subject_has_mapped_emoji_prefix(self, subject: str) -> bool:
        stripped = subject.lstrip()
        return any(stripped.startswith(emoji) for emoji in self._mapped_emojis_sorted())

    def _write_temp_editor(self, source: str) -> Path:
        root = h.dev.get_project_root() / "temp"
        root.mkdir(parents=True, exist_ok=True)
        fd, str_path = tempfile.mkstemp(suffix=".py", prefix="hsk_git_", dir=root)
        os.close(fd)
        path = Path(str_path)
        path.write_text(source, encoding="utf-8")
        return path
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Git commit subject: add emoji by keyword, rename last commit, or rename by hash.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_git"], self.config["path_github"]
        )
        if not self.folder_path:
            return

        self.add_line(f"🔵 Processing git repository: {self.folder_path}")

        choices = [(icon, title) for icon, title, _ in self._MODE_CHOICES]
        selected = self.dialogs.get_choice_from_icons("Git commit message", "Choose an action:", choices)
        if not selected:
            return

        method_name = next((m for _, t, m in self._MODE_CHOICES if t == selected), None)
        if not method_name:
            self.add_line(f"❌ Unknown choice: {selected}")
            self.show_result()
            return

        original_cwd = Path.cwd()
        os.chdir(self.folder_path)

        try:
            getattr(self, method_name)(self.folder_path)
        finally:
            os.chdir(original_cwd)

        self.show_result()
```

</details>

### ⚙️ Method `_amend_with_message`

```python
def _amend_with_message(self, folder_path: Path, new_message: str) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _amend_with_message(self, folder_path: Path, new_message: str) -> None:
        self.add_line(f"🔄 Amending commit with new message: {new_message}")
        escaped = new_message.replace('"', '\\"')
        out = self._git_out(f'git commit --amend -m "{escaped}"', folder_path)
        self.add_line("✅ Commit amended successfully")
        self.add_line(f"📊 Git output: {out}")
```

</details>

### ⚙️ Method `_apply_keyword_emoji_prefix`

```python
def _apply_keyword_emoji_prefix(self, subject: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _apply_keyword_emoji_prefix(self, subject: str) -> str:
        if self._subject_has_mapped_emoji_prefix(subject):
            return subject
        for keyword, emoji in self.EMOJI_MAPPING.items():
            if subject.startswith(keyword):
                self.add_line(f"🎯 Found keyword '{keyword}', adding emoji {emoji}")
                return f"{emoji} {subject}"
        return subject
```

</details>

### ⚙️ Method `_git_out`

```python
def _git_out(self, cmd: str, cwd: Path) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _git_out(self, cmd: str, cwd: Path) -> str:
        return h.dev.run_command(cmd, cwd=str(cwd))
```

</details>

### ⚙️ Method `_git_subprocess`

```python
def _git_subprocess(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _git_subprocess(
        args: list[str],
        cwd: Path,
        *,
        env: dict[str, str] | None = None,
        capture_output: bool = False,
        text: bool = False,
        check: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],  # noqa: S607
            cwd=cwd,
            env=env,
            capture_output=capture_output,
            text=text,
            check=check,
        )
```

</details>

### ⚙️ Method `_mapped_emojis_sorted`

```python
def _mapped_emojis_sorted(self) -> list[str]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _mapped_emojis_sorted(self) -> list[str]:
        emojis: set[str] = set(self.EMOJI_MAPPING.values())

        def _len_str(s: str) -> int:
            return len(s)

        return sorted(emojis, key=_len_str, reverse=True)
```

</details>

### ⚙️ Method `_mode_add_emoji_last`

```python
def _mode_add_emoji_last(self, folder_path: Path) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _mode_add_emoji_last(self, folder_path: Path) -> None:
        result = self._git_out("git log -1 --pretty=format:%s", folder_path)
        if not result.strip():
            self.add_line("❌ No git commits found or not a git repository")
            return

        last_commit_message = result.strip()
        self.add_line(f"📝 Last commit message: {last_commit_message}")

        if self._subject_has_mapped_emoji_prefix(last_commit_message):
            self.add_line("✅ Emoji already present in commit message")
            return

        new_message = None
        for keyword, emoji in self.EMOJI_MAPPING.items():
            if last_commit_message.startswith(keyword):
                new_message = f"{emoji} {last_commit_message}"
                self.add_line(f"🎯 Found keyword '{keyword}', adding emoji {emoji}")
                break

        if not new_message:
            self.add_line("ℹ️ No matching keyword found, no changes needed")  # noqa: RUF001
            return

        self._amend_with_message(folder_path, new_message)
        self._push_current_branch(folder_path)
```

</details>

### ⚙️ Method `_mode_rename_by_hash`

```python
def _mode_rename_by_hash(self, folder_path: Path) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _mode_rename_by_hash(self, folder_path: Path) -> None:
        hash_raw = self.dialogs.get_text_input("Commit hash", "Enter commit hash to reword:", "")
        if hash_raw is None:
            return

        commit_ref = f"{hash_raw}^{{commit}}"
        verify_p = self._git_subprocess(
            ["rev-parse", "--verify", commit_ref],
            folder_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if verify_p.returncode != 0:
            self.add_line(f"❌ Invalid commit: {hash_raw}")
            return

        full_p = self._git_subprocess(
            ["rev-parse", hash_raw],
            folder_path,
            capture_output=True,
            text=True,
            check=False,
        )
        full_hash = full_p.stdout.strip()
        if not full_hash:
            self.add_line("❌ Could not resolve commit hash")
            return

        anc = self._git_subprocess(
            ["merge-base", "--is-ancestor", full_hash, "HEAD"],
            folder_path,
            capture_output=True,
            check=False,
        )
        if anc.returncode != 0:
            self.add_line("❌ That commit is not an ancestor of HEAD on this branch")
            return

        parent_check = self._git_subprocess(
            ["rev-parse", "--verify", f"{full_hash}^"],
            folder_path,
            capture_output=True,
            check=False,
        )
        if parent_check.returncode != 0:
            self.add_line("❌ Cannot reword root commit with this flow (no parent). Use another Git workflow.")
            return

        old_subject = self._git_out(f"git log -1 {full_hash} --pretty=format:%s", folder_path).strip()
        if not old_subject:
            self.add_line("❌ Could not read commit message")
            return

        self.add_line(f"📝 Current message for {full_hash[:7]}: {old_subject}")
        raw = self.dialogs.get_text_input("New message", "New commit message (subject line):", old_subject)
        if raw is None:
            return

        final_subject = self._apply_keyword_emoji_prefix(raw)
        if final_subject != raw:
            self.add_line(f"📝 Message after emoji rule: {final_subject}")

        if not self._run_rebase_reword(folder_path, full_hash, final_subject):
            return
        self._push_current_branch(folder_path)
```

</details>

### ⚙️ Method `_mode_rename_last`

```python
def _mode_rename_last(self, folder_path: Path) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _mode_rename_last(self, folder_path: Path) -> None:
        result = self._git_out("git log -1 --pretty=format:%s", folder_path)
        if not result.strip():
            self.add_line("❌ No git commits found or not a git repository")
            return

        default_subject = result.strip()
        self.add_line(f"📝 Current last commit message: {default_subject}")
        raw = self.dialogs.get_text_input("Rename last commit", "New commit message (subject line):", default_subject)
        if raw is None:
            return

        final_subject = self._apply_keyword_emoji_prefix(raw)
        if final_subject != raw:
            self.add_line(f"📝 Message after emoji rule: {final_subject}")

        self._amend_with_message(folder_path, final_subject)
        self._push_current_branch(folder_path)
```

</details>

### ⚙️ Method `_push_current_branch`

```python
def _push_current_branch(self, folder_path: Path) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _push_current_branch(self, folder_path: Path) -> None:
        branch = self._git_out("git rev-parse --abbrev-ref HEAD", folder_path).strip()
        if branch == "HEAD":
            self.add_line("❌ Detached HEAD: cannot push (no current branch name)")
            return
        escaped_branch = branch.replace('"', '\\"')
        out = self._git_out(f'git push origin "{escaped_branch}" --force', folder_path)
        self.add_line(f"✅ Push finished: {out}")
```

</details>

### ⚙️ Method `_run_rebase_reword`

```python
def _run_rebase_reword(self, folder_path: Path, full_hash: str, new_subject: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _run_rebase_reword(self, folder_path: Path, full_hash: str, new_subject: str) -> bool:
        repo = str(folder_path.resolve())
        seq_script: Path | None = None
        msg_script: Path | None = None
        env = os.environ.copy()
        env["HARRIX_GIT_REPO"] = repo
        env["HARRIX_TARGET_FULL"] = full_hash
        env["HARRIX_NEW_SUBJECT"] = new_subject
        completed: subprocess.CompletedProcess[str] | None = None
        try:
            seq_script = self._write_temp_editor(self._SEQUENCE_EDITOR_SCRIPT)
            msg_script = self._write_temp_editor(self._MSG_EDITOR_SOURCE)
            seq_q = shlex.quote(str(seq_script))
            exe_q = shlex.quote(sys.executable)
            env["GIT_SEQUENCE_EDITOR"] = f"{exe_q} {seq_q}"
            env["GIT_EDITOR"] = f"{exe_q} {shlex.quote(str(msg_script))}"
            parent = f"{full_hash}^"
            completed = self._git_subprocess(
                ["rebase", "-i", parent],
                folder_path,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
        finally:
            if seq_script is not None:
                seq_script.unlink(missing_ok=True)
            if msg_script is not None:
                msg_script.unlink(missing_ok=True)
        if completed is None:
            return False
        if completed.stdout:
            self.add_line(completed.stdout.rstrip())
        if completed.stderr:
            self.add_line(completed.stderr.rstrip())
        if completed.returncode != 0:
            msg = f"❌ git rebase failed (exit {completed.returncode}). Run `git rebase --abort` in the repo if needed."
            self.add_line(msg)
            return False
        self.add_line("✅ Rebase finished; commit message updated")
        return True
```

</details>

### ⚙️ Method `_subject_has_mapped_emoji_prefix`

```python
def _subject_has_mapped_emoji_prefix(self, subject: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _subject_has_mapped_emoji_prefix(self, subject: str) -> bool:
        stripped = subject.lstrip()
        return any(stripped.startswith(emoji) for emoji in self._mapped_emojis_sorted())
```

</details>

### ⚙️ Method `_write_temp_editor`

```python
def _write_temp_editor(self, source: str) -> Path
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _write_temp_editor(self, source: str) -> Path:
        root = h.dev.get_project_root() / "temp"
        root.mkdir(parents=True, exist_ok=True)
        fd, str_path = tempfile.mkstemp(suffix=".py", prefix="hsk_git_", dir=root)
        os.close(fd)
        path = Path(str_path)
        path.write_text(source, encoding="utf-8")
        return path
```

</details>
