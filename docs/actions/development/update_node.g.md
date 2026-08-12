---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `update_node.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnUpdateNode`](#%EF%B8%8F-class-onupdatenode)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnUpdateNode`

```python
class OnUpdateNode(ActionBase)
```

Update `Node.js` to the latest version via winget.

Upgrades whichever OpenJS Node.js packages are installed via winget
(`OpenJS.NodeJS.LTS` and/or `OpenJS.NodeJS`). Available only on Windows.

<details>
<summary>Code:</summary>

```python
class OnUpdateNode(ActionBase):

    icon = "📥"
    title = "Update Node.js"

    _WINGET_FLAGS: ClassVar[str] = (
        "--source winget --accept-package-agreements --accept-source-agreements --silent --disable-interactivity"
    )

    @ActionBase.handle_exceptions("node.js update")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Update `Node.js` to the latest version via winget."""
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows (winget).")
            self.show_result()
            return
        if not shutil.which("winget"):
            self.add_line("winget was not found on PATH. Install App Installer from Microsoft Store.")
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("node.js update thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        blocks: list[str] = []
        node_version = self._node_version_line()
        if node_version:
            blocks.append(f"=== Current node ===\n{node_version}")

        installed_ids = [package_id for package_id in _NODE_WINGET_IDS if self._winget_package_installed(package_id)]
        if not installed_ids:
            blocks.append(self._explain_no_winget_node(node_version))
            return "\n\n".join(blocks)

        installed_lines = "\n".join(f"- {package_id}" for package_id in installed_ids)
        blocks.append(f"=== Installed winget Node.js package(s) ===\n{installed_lines}")

        summaries: list[str] = []
        for package_id in installed_ids:
            upgrade_out = self._winget_upgrade(package_id)
            blocks.append(f"=== winget upgrade ({package_id}) ===\n{upgrade_out}")
            summaries.append(self._summarize_upgrade_output(package_id, upgrade_out))

        blocks.append("=== Summary ===\n" + "\n".join(summaries))
        return "\n\n".join(blocks)

    @ActionBase.handle_exceptions("node.js update thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        text = result if isinstance(result, str) else str(result)
        lower = text.casefold()
        if "already the latest" in lower:
            toast = "Node.js is already up to date"
        elif "not installed via winget" in lower:
            toast = "Node.js not found via winget (see details)"
        else:
            toast = "Node.js update finished (see details)"
        self.show_toast(toast)
        self.add_line(result)
        self.show_result()

    def _explain_no_winget_node(self, node_version: str) -> str:
        """Build a clear message when no OpenJS Node.js winget package is installed."""
        package_ids = " or ".join(_NODE_WINGET_IDS)
        lines = [
            "=== Summary ===",
            f"Node.js was not found as a winget package with id {package_ids}.",
            (
                'Winget message "No installed package found matching input criteria" '
                "(localized: packages matching the criteria were not found) means "
                "winget does not manage that package id. "
                "It does NOT mean you already have the latest version."
            ),
        ]
        if node_version:
            lines.extend(
                [
                    (
                        f"A `node` binary is still available ({node_version}). "
                        "It was likely installed outside winget "
                        "(installer, nvm, fnm, Chocolatey, etc.)."
                    ),
                    "To let this action update Node.js, install it with winget, for example:",
                    "  winget install -e --id OpenJS.NodeJS.LTS --source winget",
                    "or:",
                    "  winget install -e --id OpenJS.NodeJS --source winget",
                ]
            )
        else:
            lines.extend(
                [
                    "`node` was not found on PATH either.",
                    "Install Node.js with winget, for example:",
                    "  winget install -e --id OpenJS.NodeJS.LTS --source winget",
                ]
            )
        return "\n".join(lines)

    @staticmethod
    def _node_version_line() -> str:
        """Return `node -v` output, or empty string if node is missing."""
        if not shutil.which("node"):
            return ""
        return h.dev.run_command(["node", "-v"]).strip()

    @staticmethod
    def _output_means_already_latest(text: str) -> bool:
        lower = text.casefold()
        return any(marker in lower for marker in _ALREADY_LATEST_MARKERS)

    @staticmethod
    def _output_means_not_installed(text: str) -> bool:
        lower = text.casefold()
        return any(marker in lower for marker in _NO_INSTALLED_MARKERS)

    def _summarize_upgrade_output(self, package_id: str, output: str) -> str:
        """Return a short human-readable status line for one winget upgrade."""
        if self._output_means_already_latest(output):
            return f"{package_id}: already the latest version available in winget."
        if self._output_means_not_installed(output):
            return f"{package_id}: not installed via winget under this id."
        return f"{package_id}: winget upgrade finished (see log above)."

    def _winget_package_installed(self, package_id: str) -> bool:
        """Return whether winget reports `package_id` as installed."""
        cmd = f"winget list -e --id {package_id} --source winget --disable-interactivity"
        output = h.dev.run_command(cmd, is_shell=True)
        if self._output_means_not_installed(output):
            return False
        # Locale-independent: an installed listing includes the exact package id.
        return any(part.casefold() == package_id.casefold() for line in output.splitlines() for part in line.split())

    def _winget_upgrade(self, package_id: str) -> str:
        """Run silent winget upgrade for `package_id`."""
        cmd = f"winget upgrade -e --id {package_id} {self._WINGET_FLAGS}"
        return h.dev.run_command(cmd, is_shell=True)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Update `Node.js` to the latest version via winget.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows (winget).")
            self.show_result()
            return
        if not shutil.which("winget"):
            self.add_line("winget was not found on PATH. Install App Installer from Microsoft Store.")
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        blocks: list[str] = []
        node_version = self._node_version_line()
        if node_version:
            blocks.append(f"=== Current node ===\n{node_version}")

        installed_ids = [package_id for package_id in _NODE_WINGET_IDS if self._winget_package_installed(package_id)]
        if not installed_ids:
            blocks.append(self._explain_no_winget_node(node_version))
            return "\n\n".join(blocks)

        installed_lines = "\n".join(f"- {package_id}" for package_id in installed_ids)
        blocks.append(f"=== Installed winget Node.js package(s) ===\n{installed_lines}")

        summaries: list[str] = []
        for package_id in installed_ids:
            upgrade_out = self._winget_upgrade(package_id)
            blocks.append(f"=== winget upgrade ({package_id}) ===\n{upgrade_out}")
            summaries.append(self._summarize_upgrade_output(package_id, upgrade_out))

        blocks.append("=== Summary ===\n" + "\n".join(summaries))
        return "\n\n".join(blocks)
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        text = result if isinstance(result, str) else str(result)
        lower = text.casefold()
        if "already the latest" in lower:
            toast = "Node.js is already up to date"
        elif "not installed via winget" in lower:
            toast = "Node.js not found via winget (see details)"
        else:
            toast = "Node.js update finished (see details)"
        self.show_toast(toast)
        self.add_line(result)
        self.show_result()
```

</details>
