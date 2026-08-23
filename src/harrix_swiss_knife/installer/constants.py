"""Shared constants for the Windows GUI installer."""

from __future__ import annotations

# Trailer at end of frozen EXE: [zip bytes][uint64 LE length][b"HSK1"]
OVERLAY_MAGIC = b"HSK1"
OVERLAY_TRAILER_SIZE = 12  # 8 bytes length + 4 bytes magic

ONLINE_EXE_NAME = "harrix-swiss-knife-online.exe"
OFFLINE_EXE_NAME = "harrix-swiss-knife-offline-for-personal-use.exe"
OFFLINE_PERSONAL_USE_NOTE = "This offline installer is for personal use only."

STUB_EXE_NAME = "harrix-swiss-knife-installer-stub.exe"


def installer_window_title(mode: str) -> str:
    """Return the installer window title for online or offline mode."""
    if mode == "offline":
        return "Harrix Swiss Knife — Offline Installer (for personal use)"
    return "Harrix Swiss Knife — Online Installer"


def offline_install_welcome_kind() -> str:
    """Return the install-source phrase shown on the offline welcome page."""
    return "offline bundle, for personal use"


REPO_NAMES = ("harrix-pylib", "harrix-pyssg", "harrix-swiss-knife")
HSK_REPO_NAME = "harrix-swiss-knife"
MEDIA_EXE_NAMES = ("ffmpeg.exe", "avifenc.exe", "avifdec.exe")

GIT_WINGET_ID = "Git.Git"
UV_WINGET_ID = "astral-sh.uv"
VSCODE_WINGET_ID = "Microsoft.VisualStudioCode"

UV_WINDOWS_ZIP = "uv-x86_64-pc-windows-msvc.zip"
VSCODE_URL = "https://update.code.visualstudio.com/latest/win32-x64-user/stable"
VSCODE_EXE_NAME = "VSCodeSetup-x64-latest.exe"
GIT_EXE_NAME = "Git-latest-64-bit.exe"

# VS Code Python extension (Marketplace id) bundled as VSIX for offline installs.
VSCODE_PYTHON_EXTENSION_ID = "ms-python.python"
VSCODE_EXTENSIONS_DIR_NAME = "vscode-extensions"

GITHUB_UA = "Harrix-Swiss-Knife/1.0 (Python; installer)"
LIBAVIF_ZIP_NAME = "windows-artifacts.zip"
FFMPEG_ZIP_NAME = "ffmpeg-master-latest-win64-gpl.zip"

# Bump when PyInstaller flags or stub entry imports change (forces stub rebuild).
STUB_SPEC_VERSION = "9"
