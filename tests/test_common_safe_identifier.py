"""Tests for SQL identifier validation."""

from __future__ import annotations

import pytest

from harrix_swiss_knife.apps.common.common import _safe_identifier


@pytest.mark.parametrize(
    "identifier",
    ["a", "_x", "table_1", "CamelCase"],
)
def test_safe_identifier_accepts_valid(identifier: str) -> None:
    assert _safe_identifier(identifier) == identifier


@pytest.mark.parametrize(
    "bad",
    ["", "1table", "bad-name", "a.b", "'; DROP--", " spaces "],
)
def test_safe_identifier_rejects_invalid(bad: str) -> None:
    with pytest.raises(ValueError, match="Illegal SQL identifier"):
        _safe_identifier(bad)
