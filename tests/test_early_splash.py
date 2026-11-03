"""Tests for the native startup splash shown before Qt imports."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from harrix_swiss_knife.early_splash import (
    AUTO_MINIMIZE_SECONDS,
    TRAY_LOADING_TITLE,
    format_splash_clock,
    splash_logo_path,
    splash_status_lines,
)

_SRC = Path(__file__).resolve().parents[1] / "src"


def test_format_splash_clock() -> None:
    assert format_splash_clock(0) == "00:00"
    assert format_splash_clock(83) == "01:23"
    assert format_splash_clock(3601) == "01:00:01"


def test_tray_loading_title() -> None:
    assert TRAY_LOADING_TITLE == "Harrix Swiss Knife"


def test_splash_logo_path_points_to_app_ico() -> None:
    path = splash_logo_path()
    assert path is not None
    assert path.name == "app.ico"
    assert path.is_file()


def test_splash_status_lines_are_separate() -> None:
    title, status, clock = splash_status_lines(2)
    assert title == "Harrix Swiss Knife"
    assert status == "Loading..."
    assert clock == "00:02"
    assert "Loading" not in title
    assert title not in status


@pytest.mark.skipif(sys.platform != "win32", reason="Native splash is Windows-only")
def test_early_splash_shows_and_closes_window() -> None:
    script = f"""
import sys
import time

sys.path.insert(0, {str(_SRC)!r})
from harrix_swiss_knife.early_splash import close_early_splash, early_splash_hwnd, ensure_early_splash

ensure_early_splash()
hwnd = 0
deadline = time.monotonic() + 2.0
while time.monotonic() < deadline:
    hwnd = early_splash_hwnd()
    if hwnd:
        break
    time.sleep(0.05)
if not hwnd:
    raise SystemExit("splash hwnd was not created")
ensure_early_splash()
if early_splash_hwnd() != hwnd:
    raise SystemExit("second ensure_early_splash replaced the window")
close_early_splash()
if early_splash_hwnd() != 0:
    raise SystemExit("splash hwnd was not cleared")
close_early_splash()
print("ok")
"""
    completed = subprocess.run([sys.executable, "-c", script], check=False, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    assert "ok" in completed.stdout


@pytest.mark.skipif(sys.platform != "win32", reason="Native splash is Windows-only")
def test_early_splash_minimizes_to_toast() -> None:
    script = f"""
import ctypes
import sys
import time
from ctypes import wintypes

sys.path.insert(0, {str(_SRC)!r})
from harrix_swiss_knife.early_splash import (
    close_early_splash,
    early_splash_hwnd,
    ensure_early_splash,
    expand_early_splash,
    is_early_splash_minimized,
    minimize_early_splash,
)

user32 = ctypes.WinDLL("user32", use_last_error=True)

def window_size(hwnd: int) -> tuple[int, int]:
    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise SystemExit("GetWindowRect failed")
    return int(rect.right - rect.left), int(rect.bottom - rect.top)

ensure_early_splash()
hwnd = 0
deadline = time.monotonic() + 2.0
while time.monotonic() < deadline:
    hwnd = early_splash_hwnd()
    if hwnd:
        break
    time.sleep(0.05)
if not hwnd:
    raise SystemExit("splash hwnd was not created")
time.sleep(0.15)
full_w, full_h = window_size(hwnd)
minimize_early_splash()
deadline = time.monotonic() + 2.0
while time.monotonic() < deadline and not is_early_splash_minimized():
    time.sleep(0.05)
if not is_early_splash_minimized():
    raise SystemExit("splash did not minimize")
time.sleep(0.15)
toast_w, toast_h = window_size(hwnd)
if toast_h >= full_h or toast_w >= full_w:
    raise SystemExit(f"toast size not smaller: full={{full_w}}x{{full_h}} toast={{toast_w}}x{{toast_h}}")
expand_early_splash()
deadline = time.monotonic() + 2.0
while time.monotonic() < deadline and is_early_splash_minimized():
    time.sleep(0.05)
if is_early_splash_minimized():
    raise SystemExit("splash did not expand")
time.sleep(0.15)
restored_w, restored_h = window_size(hwnd)
if restored_h < full_h or restored_w < full_w:
    raise SystemExit("splash did not restore full size")
close_early_splash()
print("ok")
"""
    completed = subprocess.run([sys.executable, "-c", script], check=False, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    assert "ok" in completed.stdout


def test_auto_minimize_delay_is_three_seconds() -> None:
    assert AUTO_MINIMIZE_SECONDS == 3.0
