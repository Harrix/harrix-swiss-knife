"""Format VS Code extension sources via Biome."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.common.vscode_extension_path import (
    ensure_node_modules,
    resolve_extension_dir,
    resolve_npm,
    run_npm,
)

if TYPE_CHECKING:
    from pathlib import Path


class OnVscodeFormat(ActionBase):
    """Run Biome format/fix on the Notes Explorer extension (`npm run format`).

    Formats and applies safe fixes under `vscode/harrix-notes-explorer-hsk/`.
    Requires Node.js and npm on PATH. Prefer this before `hsk vscode check`.

    """

    icon = "✨"
    title = "Format VS Code extension"
    cli_available = True
    cli_hint = "vscode format"

    @ActionBase.handle_exceptions("vs code format")
    def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None:
        """Apply Biome write fixes (sync for CLI, background thread for tray)."""
        extension_dir = resolve_extension_dir()
        if extension_dir is None:
            self.add_line("❌ vscode/harrix-notes-explorer-hsk or package.json not found.")
            if not noninteractive:
                self.show_result()
            return

        if resolve_npm() is None:
            self.add_line("❌ npm not found on PATH. Install Node.js, then retry.")
            if not noninteractive:
                self.show_result()
            return

        if noninteractive:
            self._run_biome_format(extension_dir)
            return

        self.folder_path = extension_dir
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("vs code format thread")
    def in_thread(self) -> str | None:
        """Run Biome format in a worker thread for the tray UI."""
        extension_dir = getattr(self, "folder_path", None)
        if extension_dir is None:
            return None
        self._run_biome_format(extension_dir)
        return None

    @ActionBase.handle_exceptions("vs code format thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result dialog after a tray format."""
        failed = any(isinstance(line, str) and line.strip().startswith("❌") for line in self.result_lines)
        self.show_toast(f"{self.title} {'failed' if failed else 'completed'}")
        self.show_result()

    def _run_biome_format(self, extension_dir: Path) -> None:
        """Ensure deps and run ``npm run format``."""
        self.add_line(f"🔵 Starting Biome format in {extension_dir}")

        try:
            install_proc = ensure_node_modules(extension_dir)
        except FileNotFoundError:
            self.add_line("❌ npm not found on PATH. Install Node.js, then retry.")
            return

        if install_proc is not None:
            self.add_line("$ npm ci" if (extension_dir / "package-lock.json").is_file() else "$ npm install")
            output = "\n".join(part for part in (install_proc.stdout.strip(), install_proc.stderr.strip()) if part)
            if output:
                self.add_line(output)
            if install_proc.returncode != 0:
                self.add_line(f"❌ npm install failed (exit code {install_proc.returncode}).")
                return

        self.add_line("$ npm run format")
        process = run_npm(extension_dir, "run", "format")
        output = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
        if output:
            self.add_line(output)

        if process.returncode != 0:
            self.add_line(f"❌ npm run format failed (exit code {process.returncode}).")
        else:
            self.add_line("✅ Biome format completed.")
