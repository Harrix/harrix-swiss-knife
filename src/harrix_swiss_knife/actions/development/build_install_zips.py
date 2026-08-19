"""Run `install/build-all.bat` and open the folder with generated zip archives."""

from __future__ import annotations

import subprocess
import sys
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.paths import get_project_root

if TYPE_CHECKING:
    from pathlib import Path

BUILD_ALL_BAT_NAME = "build-all.bat"
BUILD_ALL_OPEN_FLAG = "/open"
INSTALL_DIR_NAME = "install"


class OnBuildInstallZips(ActionBase):
    """Run `install/build-all.bat` and open `install/` with the zip archives.

    Runs zip pipeline steps 1-5 (UAC on the first two). After the script
    finishes, Explorer opens `install/` (`install-harrix-swiss-knife.zip` and
    `install-offline-harrix-swiss-knife.zip`). If step 4 asks to close this
    app, Exit is safe: the console window keeps running and still opens the
    folder.

    """

    icon = "🚀"
    title = "Build install zips"
    cli_available = True
    cli_hint = "dev build-install-zips"

    @ActionBase.handle_exceptions("build install zips")
    def execute(self, *args: Any, noninteractive: bool = False, **kwargs: Any) -> None:  # noqa: ARG002
        """Run `install/build-all.bat` then open `install/`."""
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        install_dir = install_folder(get_project_root())
        bat_path = install_dir / BUILD_ALL_BAT_NAME
        if not bat_path.is_file():
            self.add_line(f"❌ `{BUILD_ALL_BAT_NAME}` not found: {bat_path}")
            if not noninteractive:
                self.show_result()
            return

        self._install_dir = install_dir
        self.add_line(f"$ call {BUILD_ALL_BAT_NAME} {BUILD_ALL_OPEN_FLAG}")
        self.add_line(f"Working directory: {install_dir}")
        if noninteractive:
            self._run_build_all(new_console=False)
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("build install zips thread")
    def in_thread(self) -> int:
        """Run the zip pipeline in a visible console window."""
        return self._run_build_all(new_console=True)

    @ActionBase.handle_exceptions("build install zips completion")
    def thread_after(self, result: Any) -> None:
        """Show toast and result after the zip pipeline finishes."""
        code = result if isinstance(result, int) else getattr(self, "_build_exit_code", 1)
        if code == 0:
            self.show_toast("Install zips built")
        else:
            self.show_toast("Install zip build finished (see output)")
        self.show_result()

    def _run_build_all(self, *, new_console: bool) -> int:
        """Run `build-all.bat /open` and return its exit code."""
        install_dir = self._install_dir
        creationflags = 0
        if new_console:
            creationflags = subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP
        try:
            process = subprocess.run(
                build_all_cmd(),
                cwd=str(install_dir),
                check=False,
                creationflags=creationflags,
                shell=False,
            )
        except OSError as exc:
            self.add_line(f"❌ Failed to start `{BUILD_ALL_BAT_NAME}`: {exc}")
            self._build_exit_code = 1
            return 1

        code = int(process.returncode)
        self._build_exit_code = code
        if code == 0:
            self.add_line(f"✅ `{BUILD_ALL_BAT_NAME}` finished. Opened `{install_dir}`.")
        else:
            self.add_line(f"❌ `{BUILD_ALL_BAT_NAME}` stopped with exit code {code}.")
            self.add_line(f"Opened `{install_dir}`.")
        return code


def build_all_cmd() -> list[str]:
    """Return argv that runs `build-all.bat /open` in `install/` (cwd)."""
    return ["cmd.exe", "/c", "call", BUILD_ALL_BAT_NAME, BUILD_ALL_OPEN_FLAG]


def install_folder(project_root: Path) -> Path:
    """Return the `install/` directory under the project root."""
    return project_root / INSTALL_DIR_NAME
