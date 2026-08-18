"""Tests for Vector Icons repo folder choices used by maintenance actions."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.actions.apps.icon_repo import vector_icons_repo_choices


def test_vector_icons_repo_choices_skips_placeholders_and_missing(tmp_path: Path) -> None:
    existing = tmp_path / "Harrix-Vector-Icons"
    existing.mkdir()
    pinned = tmp_path / "other-icons"
    pinned.mkdir()
    choices = vector_icons_repo_choices(
        {
            "path_vector_icons": "<YOUR_GITHUB_FOLDER>/Harrix-Vector-Icons",
            "path_vector_icons_pinned": [str(pinned), str(existing / "missing")],
        }
    )
    assert choices == [str(pinned.resolve())]


def test_vector_icons_repo_choices_includes_main_and_pinned(tmp_path: Path) -> None:
    main = tmp_path / "main"
    extra = tmp_path / "extra"
    main.mkdir()
    extra.mkdir()
    choices = vector_icons_repo_choices(
        {
            "path_vector_icons": str(main),
            "path_vector_icons_pinned": [str(extra), str(main)],
        }
    )
    assert choices == [str(main.resolve()), str(extra.resolve())]
