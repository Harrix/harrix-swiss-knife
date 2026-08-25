"""Zone and sort identifiers for the snippets overlay."""

from __future__ import annotations

from typing import Literal

ZONE_PHRASE = "phrase"
ZONE_EMOJI = "emoji"
ZONE_SYMBOL = "symbol"
ZONE_COLOR = "color"

ZoneName = Literal["phrase", "emoji", "symbol", "color"]
ZONES: tuple[ZoneName, ...] = (ZONE_PHRASE, ZONE_EMOJI, ZONE_SYMBOL, ZONE_COLOR)

SORT_USED = "used"
SORT_ADDED = "added"
SORT_ALPHA = "alpha"

SortMode = Literal["used", "added", "alpha"]
SORT_MODES: tuple[SortMode, ...] = (SORT_USED, SORT_ADDED, SORT_ALPHA)

DEFAULT_SORT_MODE: SortMode = SORT_ALPHA
SEED_CREATED_AT = "2026-08-25T00:00:00+00:00"
