"""Action for syncing Windows Quick Access pinned folders into Total Commander."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase

# Quick Access ("Home") shell namespace CLSID.
_QUICK_ACCESS_NAMESPACE = "shell:::{679f85cb-0220-4080-b29b-5540cc05aab6}"

# PowerShell that prints "Name<TAB>Path" for pinned Quick Access folders only.
_POWERSHELL_LIST_PINNED = (
    "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8\n"
    "$qa = New-Object -ComObject shell.application\n"
    f'$ns = $qa.Namespace("{_QUICK_ACCESS_NAMESPACE}")\n'
    "foreach ($i in $ns.Items()) {\n"
    '  if ($i.IsFolder -and $i.ExtendedProperty("System.Home.IsPinned")) {\n'
    '    Write-Output ($i.Name + "`t" + $i.Path)\n'
    "  }\n"
    "}\n"
)

_ENTRY_RE = re.compile(r"^\s*(menu|cmd|path)(\d+)\s*=", re.IGNORECASE)
_REDIRECT_RE = re.compile(r"^\s*RedirectSection\s*=\s*(.+?)\s*$", re.IGNORECASE)
_SECTION_RE = re.compile(r"^\s*\[(?P<name>.+?)\]\s*$")


class OnSyncQuickAccessToTotalCommander(ActionBase):
    """Copy Explorer's pinned Quick Access folders into Total Commander's Ctrl+D hotlist.

    Reads folders pinned to Windows Quick Access and merges the missing ones into the
    ``[DirMenu]`` section of Total Commander's ``wincmd.ini`` (the file opened with
    ``Ctrl+D``). Existing hotlist entries are preserved; the action only appends folders
    that are not already present. The path to ``wincmd.ini`` is taken from the
    ``path_totalcmd_ini`` key in ``config.json``.
    """

    icon = "📌"
    title = "Sync Quick Access folders to Total Commander"

    @ActionBase.handle_exceptions("syncing Quick Access to Total Commander")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Merge pinned Quick Access folders into Total Commander's directory hotlist."""
        if not self.get_yes_no_question(
            self.title,
            "Close Total Commander before continuing.\n\n"
            "If it stays open, it will overwrite wincmd.ini on exit and discard the changes.\n\n"
            "Continue?",
            default_yes=False,
        ):
            self.add_line("❌ Cancelled by user.")
            return

        ini_path = Path(str(self.config["path_totalcmd_ini"])).expanduser()
        if not ini_path.is_file():
            self.add_line(f"❌ wincmd.ini not found: {ini_path}")
            self.show_result()
            return

        pinned = self._read_pinned_folders()
        if not pinned:
            self.add_line("❌ No pinned folders found in Quick Access.")
            self.show_result()
            return
        self.add_line(f"Found {len(pinned)} pinned folder(s) in Quick Access.")

        target_path = self._resolve_dirmenu_file(ini_path)
        self.add_line(f"Target [DirMenu] file: {target_path}")

        raw = target_path.read_bytes()
        encoding = self._detect_encoding(raw)
        text = raw.decode(encoding, errors="replace")
        newline = "\r\n" if "\r\n" in text else "\n"
        lines = text.split(newline)

        new_lines, added, skipped = self._merge_dirmenu(lines, pinned)
        if not added:
            self.add_line(f"Nothing to add — all {skipped} pinned folder(s) already present.")
            self.show_toast(f"{self.title}: nothing to add")
            self.show_result()
            return

        target_path.write_bytes(newline.join(new_lines).encode(encoding, errors="replace"))

        self.add_line(f"Added {len(added)} folder(s) to [DirMenu]:")
        for name, path in added:
            self.add_line(f"  ➕ {name} → {path}")  # noqa: RUF001
        if skipped:
            self.add_line(f"Skipped {skipped} folder(s) already present.")
        self.add_line("")
        self.add_line("⚠️ Close Total Commander before running, otherwise it overwrites wincmd.ini on exit.")
        self.show_toast(f"{self.title}: added {len(added)}")
        self.show_result()

    @staticmethod
    def _detect_encoding(raw: bytes) -> str:
        """Guess the text encoding of ``raw`` INI bytes, preserving any BOM on write."""
        if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
            return "utf-16"
        if raw.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError:
            return "mbcs" if os.name == "nt" else "utf-8"
        return "utf-8"

    def _expand_tc_path_variables(self, path: str, ini_path: Path) -> str:
        """Expand Total Commander-specific path variables in *path*."""
        commander_path = str(ini_path.parent)
        expanded = path
        for token in ("%COMMANDER_PATH%", "%commander_path%"):
            expanded = expanded.replace(token, commander_path)
        return os.path.expandvars(expanded)

    @staticmethod
    def _find_section(lines: list[str], name: str) -> tuple[int | None, int]:
        """Return ``(header_index, end_index)`` for the section ``name`` (case-insensitive)."""
        start: int | None = None
        for index, line in enumerate(lines):
            match = _SECTION_RE.match(line)
            if match and match.group("name").strip().lower() == name.lower():
                start = index
                break
        if start is None:
            return None, len(lines)
        end = len(lines)
        for index in range(start + 1, len(lines)):
            if _SECTION_RE.match(lines[index]):
                end = index
                break
        return start, end

    def _merge_dirmenu(
        self, lines: list[str], pinned: list[tuple[str, str]]
    ) -> tuple[list[str], list[tuple[str, str]], int]:
        """Append missing pinned folders to ``[DirMenu]`` and return new lines plus stats."""
        start, end = self._find_section(lines, "DirMenu")
        if start is None:
            lines = [*lines, "[DirMenu]"]
            start, end = len(lines) - 1, len(lines)

        used_indices: set[int] = set()
        existing_paths: set[str] = set()
        for line in lines[start + 1 : end]:
            match = _ENTRY_RE.match(line)
            if not match:
                continue
            used_indices.add(int(match.group(2)))
            if match.group(1).lower() == "cmd":
                value = line.split("=", 1)[1].strip()
                if value.lower().startswith("cd "):
                    existing_paths.add(self._normalize_path(value[3:]))

        next_index = (max(used_indices) + 1) if used_indices else 1
        added: list[tuple[str, str]] = []
        skipped = 0
        new_entries: list[str] = []
        for name, path in pinned:
            if self._normalize_path(path) in existing_paths:
                skipped += 1
                continue
            new_entries.append(f"menu{next_index}={name}")
            new_entries.append(f"cmd{next_index}=cd {path}")
            existing_paths.add(self._normalize_path(path))
            added.append((name, path))
            next_index += 1

        insert_at = end
        while insert_at > start + 1 and not lines[insert_at - 1].strip():
            insert_at -= 1
        merged = [*lines[:insert_at], *new_entries, *lines[insert_at:]]
        return merged, added, skipped

    @staticmethod
    def _normalize_path(path: str) -> str:
        """Return a comparable form of a folder path (case-insensitive, no trailing slash)."""
        return path.strip().strip("\"'").replace("/", "\\").rstrip("\\").lower()

    def _read_pinned_folders(self) -> list[tuple[str, str]]:
        """Return a list of ``(name, path)`` tuples for pinned Quick Access folders."""
        output = h.dev.run_powershell_script(_POWERSHELL_LIST_PINNED) or ""
        folders: list[tuple[str, str]] = []
        for raw_line in output.splitlines():
            line = raw_line.rstrip("\r")
            if "\t" not in line:
                continue
            name, path = line.split("\t", 1)
            name, path = name.strip(), path.strip()
            if name and path:
                folders.append((name, path))
        return folders

    def _resolve_dirmenu_file(self, ini_path: Path) -> Path:
        """Return the file holding ``[DirMenu]`` entries, following ``RedirectSection``."""
        raw = ini_path.read_bytes()
        text = raw.decode(self._detect_encoding(raw), errors="replace")
        newline = "\r\n" if "\r\n" in text else "\n"
        start, end = self._find_section(text.split(newline), "DirMenu")
        if start is None:
            return ini_path
        for line in text.split(newline)[start + 1 : end]:
            match = _REDIRECT_RE.match(line)
            if not match:
                continue
            redirect = self._expand_tc_path_variables(match.group(1), ini_path)
            redirect_path = Path(redirect)
            if not redirect_path.is_absolute():
                redirect_path = ini_path.parent / redirect_path
            if redirect_path.is_file():
                return redirect_path
            self.add_line(f"⚠️ RedirectSection target not found: {redirect_path}")
        return ini_path
