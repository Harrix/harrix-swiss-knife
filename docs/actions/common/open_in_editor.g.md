---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `open_in_editor.py`

## 🔧 Function `open_in_editor`

```python
def open_in_editor(editor: str, workspace: str | Path, file_path: str | Path) -> str
```

Launch an editor with workspace and file as separate argv entries.

Args:

- `editor` (`str`): Editor executable name or path (e.g. `code-insiders`).
- `workspace` (`str | Path`): Workspace file or folder to open.
- `file_path` (`str | Path`): File to open in the editor.
- `timeout` (`float | None`): Subprocess timeout in seconds. Defaults to `120.0`.

Returns:

- `str`: Combined stdout/stderr from the editor process (often empty).

<details>
<summary>Code:</summary>

```python
def open_in_editor(
    editor: str,
    workspace: str | Path,
    file_path: str | Path,
    *,
    timeout: float | None = 120.0,
) -> str:
    editor_cmd = (editor or "").strip()
    if not editor_cmd:
        msg = "Editor executable is empty."
        raise ValueError(msg)

    resolved_editor = shutil.which(editor_cmd) or editor_cmd
    command = [resolved_editor, str(workspace), str(file_path)]
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=timeout,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return f"Editor command timed out after {timeout} seconds"

    output_parts = [(process.stdout or "").strip(), (process.stderr or "").strip()]
    return "\n".join(filter(None, output_parts))
```

</details>
