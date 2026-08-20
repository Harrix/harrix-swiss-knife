---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `acl.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `installing_username`](#-function-installing_username)
- [🔧 Function `repair_install_tree_acls`](#-function-repair_install_tree_acls)

</details>

## 🔧 Function `installing_username`

```python
def installing_username() -> str
```

Return the Windows user who launched the elevated installer.

<details>
<summary>Code:</summary>

```python
def installing_username() -> str:
    for key in ("USERNAME", "USER"):
        value = (os.environ.get(key) or "").strip()
        if value:
            return value
    return ""
```

</details>

## 🔧 Function `repair_install_tree_acls`

```python
def repair_install_tree_acls(target: Path, log: OutcomeLog) -> bool
```

Clear read-only, grant Full Control to the installing user, set Medium integrity.

Returns whether every step that was attempted succeeded. Missing tools are logged
and treated as failure without raising.

<details>
<summary>Code:</summary>

```python
def repair_install_tree_acls(target: Path, log: OutcomeLog) -> bool:
    if sys.platform != "win32":
        log.add("skipped", "ACL repair skipped (not Windows)")
        return True
    if not target.exists():
        log.add("failed", f"ACL repair skipped: path missing ({target})")
        return False

    user = installing_username()
    if not user:
        log.add("failed", "ACL repair skipped: USERNAME not set")
        return False

    log.step("Repair folder permissions for the current user")
    log.detail(f"Target: {target}")
    log.detail(f"User: {user}")

    ok = True
    if not _run_cmd(["attrib", "-R", str(target), "/S", "/D"], log, label="attrib -R"):
        ok = False
    grant = ["icacls", str(target), "/grant", f"{user}:(OI)(CI)F", "/T", "/C", "/Q"]
    if not _run_cmd(grant, log, label="icacls /grant"):
        ok = False
    integrity = ["icacls", str(target), "/setintegritylevel", "(OI)(CI)M", "/T", "/C", "/Q"]
    if not _run_cmd(integrity, log, label="icacls /setintegritylevel"):
        # Integrity can fail on some volumes; keep grant result as the main signal.
        log.detail("Medium integrity level could not be set (continuing)")

    if ok:
        log.add("installed", f"Granted Full Control on {target} to {user}")
    else:
        log.add("failed", f"ACL repair incomplete for {target}")
    return ok
```

</details>
