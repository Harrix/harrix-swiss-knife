"""Verify VS Code extension code quality via Biome."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.development.vscode_extension_path import (
    ensure_node_modules,
    resolve_extension_dir,
    resolve_npm,
    run_npm,
)


class OnVscodeCheck(ActionBase):
    """Run Biome check on the Notes Explorer extension (`npm run check`).

    Lints and verifies formatting under `vscode/harrix-notes-explorer-hsk/`.
    Requires Node.js and npm on PATH. Prefer `hsk vscode format` first.

    """

    icon = "🔬"
    title = "Check VS Code extension"
    cli_available = True
    cli_hint = "vscode check"

    @ActionBase.handle_exceptions("VS Code check")
    def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None:
        """Run Biome check on the VS Code extension."""
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

        self.add_line(f"🔵 Starting Biome check in {extension_dir}")

        try:
            install_proc = ensure_node_modules(extension_dir)
        except FileNotFoundError:
            self.add_line("❌ npm not found on PATH. Install Node.js, then retry.")
            if not noninteractive:
                self.show_result()
            return

        if install_proc is not None:
            self.add_line("$ npm ci" if (extension_dir / "package-lock.json").is_file() else "$ npm install")
            output = "\n".join(part for part in (install_proc.stdout.strip(), install_proc.stderr.strip()) if part)
            if output:
                self.add_line(output)
            if install_proc.returncode != 0:
                self.add_line(f"❌ npm install failed (exit code {install_proc.returncode}).")
                if not noninteractive:
                    self.show_result()
                return

        self.add_line("$ npm run check")
        process = run_npm(extension_dir, "run", "check")
        output = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
        if output:
            self.add_line(output)

        if process.returncode != 0:
            self.add_line(f"❌ npm run check failed (exit code {process.returncode}).")
        else:
            self.add_line("✅ Biome check completed.")

        if not noninteractive:
            self.show_result()
