"""Pytest defaults for Harrix Swiss Knife."""

from __future__ import annotations

import os

from harrix_swiss_knife.actions.common.subprocess_run import QT_OFFSCREEN_PLATFORM

# Qt tests must not map real windows (they flash during `hsk py check`).
os.environ.setdefault("QT_QPA_PLATFORM", QT_OFFSCREEN_PLATFORM)
