"""Tests for slash flipping."""

from __future__ import annotations

from harrix_swiss_knife.actions.files.flip_slashes import flip_slashes


def test_flip_slashes_swaps_forward_and_back() -> None:
    assert flip_slashes("D:/GitHub/foo") == "D:\\GitHub\\foo"
    assert flip_slashes("D:\\GitHub\\foo") == "D:/GitHub/foo"
    assert flip_slashes("C:/Users\\Name") == "C:\\Users/Name"


def test_flip_slashes_collapses_escaped_backslashes() -> None:
    assert flip_slashes("D:\\\\GitHub\\\\foo") == "D:\\GitHub\\foo"


def test_flip_slashes_keeps_protocol_separators() -> None:
    assert flip_slashes("https://github.com/Harrix/foo") == "https://github.com\\Harrix\\foo"
    assert flip_slashes("https:\\\\github.com\\Harrix\\foo") == "https:\\\\github.com/Harrix/foo"
    assert flip_slashes("https:\\\\") == "https:\\\\"
    assert flip_slashes("foo\\\\:bar/baz") == "foo\\\\:bar\\baz"
