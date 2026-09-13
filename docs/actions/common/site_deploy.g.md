---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `site_deploy.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `deploy_generated_site`](#-function-deploy_generated_site)
- [🔧 Function `is_git_work_tree`](#-function-is_git_work_tree)
- [🔧 Function `should_offer_deploy`](#-function-should_offer_deploy)

</details>

## 🔧 Function `deploy_generated_site`

```python
def deploy_generated_site(html_folder: Path, *, remote_url: str | None = None, remote_name: str = DEPLOY_REMOTE_NAME, branch: str = DEPLOY_BRANCH, commit_message: str = DEPLOY_COMMIT_MESSAGE) -> tuple[bool, str]
```

Commit generated HTML and push it to the production remote.

Args:

- `html_folder` (`Path`): Site output folder (Git work tree).
- `remote_url` (`str | None`): URL for `remote_name`. Added or updated when set.
- `remote_name` (`str`): Git remote name. Defaults to `production`.
- `branch` (`str`): Branch to commit and push. Defaults to `main`.
- `commit_message` (`str`): Commit subject when there are changes.

Returns:

- `tuple[bool, str]`: Success flag and combined log text.

<details>
<summary>Code:</summary>

```python
def deploy_generated_site(
    html_folder: Path,
    *,
    remote_url: str | None = None,
    remote_name: str = DEPLOY_REMOTE_NAME,
    branch: str = DEPLOY_BRANCH,
    commit_message: str = DEPLOY_COMMIT_MESSAGE,
) -> tuple[bool, str]:
    folder = html_folder.expanduser().resolve()
    lines: list[str] = []
    remote = (remote_url or "").strip()

    if not folder.is_dir():
        return False, f"HTML output folder not found: {folder}"

    if not is_git_work_tree(folder):
        if not remote:
            return False, f"Not a Git repository: {folder}"
        if not _log_git(lines, folder, "init", "-b", branch):
            if not _log_git(lines, folder, "init"):
                return False, _join_log(lines)
            if not _log_git(lines, folder, "checkout", "-b", branch):
                return False, _join_log(lines)

    if remote:
        if not _ensure_remote(lines, folder, remote_name, remote):
            return False, _join_log(lines)
    else:
        ok, _current = _git(folder, "remote", "get-url", remote_name)
        if not ok:
            lines.append(f"No deploy remote `{remote_name}` configured.")
            return False, _join_log(lines)

    if not _log_git(lines, folder, "add", "-A"):
        return False, _join_log(lines)

    ok, porcelain = _git(folder, "status", "--porcelain")
    if not ok:
        lines.append(porcelain)
        return False, _join_log(lines)
    if not porcelain.strip():
        lines.append("No changes to commit.")
        return True, _join_log(lines)

    _ensure_git_identity(folder)
    if not _log_git(lines, folder, "-c", "commit.gpgsign=false", "commit", "-m", commit_message):
        return False, _join_log(lines)

    if not _log_git(lines, folder, "push", "-u", remote_name, branch, timeout=_GIT_PUSH_TIMEOUT):
        return False, _join_log(lines)
    lines.append(f"Pushed `{branch}` to `{remote_name}`.")
    return True, _join_log(lines)
```

</details>

## 🔧 Function `is_git_work_tree`

```python
def is_git_work_tree(path: Path) -> bool
```

Return `True` when `path` is a Git working tree.

<details>
<summary>Code:</summary>

```python
def is_git_work_tree(path: Path) -> bool:
    if not path.is_dir():
        return False
    ok, output = _git(path, "rev-parse", "--is-inside-work-tree", timeout=30.0)
    return ok and "true" in output.split()
```

</details>

## 🔧 Function `should_offer_deploy`

```python
def should_offer_deploy(html_folder: Path, deploy_remote: str | None) -> bool
```

Return `True` when the action should ask to publish the generated site.

<details>
<summary>Code:</summary>

```python
def should_offer_deploy(html_folder: Path, deploy_remote: str | None) -> bool:
    remote = (deploy_remote or "").strip()
    return bool(remote) or is_git_work_tree(html_folder)
```

</details>
