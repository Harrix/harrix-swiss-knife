---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `subprocess_run.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `completed_process_output`](#-function-completed_process_output)
- [🔧 Function `run_argv`](#-function-run_argv)
- [🔧 Function `run_argv_output`](#-function-run_argv_output)

</details>

## 🔧 Function `completed_process_output`

```python
def completed_process_output(process: subprocess.CompletedProcess[Any]) -> str
```

Return combined stdout/stderr from a completed process.

<details>
<summary>Code:</summary>

```python
def completed_process_output(process: subprocess.CompletedProcess[Any]) -> str:
    output_parts = [(process.stdout or "").strip(), (process.stderr or "").strip()]
    return "\n".join(filter(None, output_parts))
```

</details>

## 🔧 Function `run_argv`

```python
def run_argv(command: list[str], *, cwd: str | Path | None = None, env: dict[str, str] | None = None, timeout: float | None = DEFAULT_SUBPROCESS_TIMEOUT, check: bool = False) -> subprocess.CompletedProcess[str]
```

Run a command as an argv list with a default timeout.

Args:

- `command` (`list[str]`): Executable and arguments (no shell).
- `cwd` (`str | Path | None`): Working directory. Defaults to `None`.
- `env` (`dict[str, str] | None`): Environment variables. Defaults to `None`.
- `timeout` (`float | None`): Timeout in seconds. Defaults to `300.0`.
- `check` (`bool`): Raise on non-zero exit. Defaults to `False`.

Returns:

- `subprocess.CompletedProcess[str]`: Completed process with text output.

<details>
<summary>Code:</summary>

```python
def run_argv(
    command: list[str],
    *,
    cwd: str | Path | None = None,
    env: dict[str, str] | None = None,
    timeout: float | None = DEFAULT_SUBPROCESS_TIMEOUT,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    if not command:
        msg = "Command list must not be empty."
        raise ValueError(msg)

    executable = shutil.which(command[0]) or command[0]
    argv = [executable, *command[1:]]
    return subprocess.run(
        argv,
        cwd=str(cwd) if cwd is not None else None,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=check,
        timeout=timeout,
        shell=False,
    )
```

</details>

## 🔧 Function `run_argv_output`

```python
def run_argv_output(command: list[str], *, cwd: str | Path | None = None, env: dict[str, str] | None = None, timeout: float | None = DEFAULT_SUBPROCESS_TIMEOUT) -> tuple[int, str]
```

Run argv command and return `(returncode, combined_output)`.

On timeout, returncode is `-1` and output explains the timeout.

<details>
<summary>Code:</summary>

```python
def run_argv_output(
    command: list[str],
    *,
    cwd: str | Path | None = None,
    env: dict[str, str] | None = None,
    timeout: float | None = DEFAULT_SUBPROCESS_TIMEOUT,
) -> tuple[int, str]:
    try:
        process = run_argv(command, cwd=cwd, env=env, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        return -1, f"Command timed out after {exc.timeout} seconds: {' '.join(command)}"
    except OSError as exc:
        return -1, f"Error executing command: {exc}"

    output_parts = [(process.stdout or "").strip(), (process.stderr or "").strip()]
    return process.returncode, "\n".join(filter(None, output_parts))
```

</details>
