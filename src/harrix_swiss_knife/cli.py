"""Console entry point for Harrix Swiss Knife actions (Click)."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from harrix_swiss_knife.actions.markdown import OnBeautifyMdFolderAndRegenerateGMd


@click.group()
def cli() -> None:
    """Harrix Swiss Knife CLI."""


@cli.group("markdown")
def markdown_group() -> None:
    """Markdown-related commands."""


@markdown_group.command("beautify-regenerate-g-md")
@click.argument(
    "folder",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def markdown_beautify_regenerate_g_md(folder: Path) -> None:
    """Beautify Markdown under FOLDER and regenerate .g.md (same as tray action)."""
    action = OnBeautifyMdFolderAndRegenerateGMd()
    action(folder_path=folder, noninteractive=True)
    if any(line.startswith("❌ Error") for line in action.result_lines):
        sys.exit(1)


def main() -> None:
    """Entry point for ``harrix-swiss-knife-cli``."""
    cli()
