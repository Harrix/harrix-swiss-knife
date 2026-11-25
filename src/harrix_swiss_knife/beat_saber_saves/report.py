"""Human-readable progress report from Beat Saber `PlayerData.dat`."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# Beat Saber `Rank` enum order (E=0 … SSS=7). Confirmed against LocalLow PlayerData.
_RANK_NAMES: tuple[str, ...] = ("E", "D", "C", "B", "A", "S", "SS", "SSS")
_DIFFICULTY_NAMES: tuple[str, ...] = ("Easy", "Normal", "Hard", "Expert", "Expert+")
_CUSTOM_LEVEL_PREFIX = "custom_level_"
_CUSTOM_HASH_PREVIEW_LEN = 8
_CAMEL_SPLIT_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


@dataclass(frozen=True, slots=True)
class LevelClear:
    """One played difficulty of a level from `levelsStatsData`."""

    level_id: str
    display_name: str
    difficulty: int
    characteristic: str
    max_rank: int
    rank_name: str
    full_combo: bool
    high_score: int
    play_count: int


def format_progress_report(player_data_path: Path) -> str:
    """Return a multiline progress report for the export result / ZIP sidecar."""
    clears, error = load_level_clears(player_data_path)
    if error:
        return f"Progress report unavailable: {error}"
    if not clears:
        return "Progress report: no played levels with a saved score in `PlayerData.dat`."

    fc_count = sum(1 for clear in clears if clear.full_combo)
    lines = [
        "Beat Saber local progress",
        f"Played difficulties: {len(clears)} | Full combo (no misses): {fc_count}",
        "",
        f"{'Rank':<4} {'FC':<3} {'Diff':<9} {'Mode':<12} {'Score':>10}  Song",
        "-" * 72,
    ]
    for clear in clears:
        fc = "yes" if clear.full_combo else "—"
        mode = clear.characteristic if clear.characteristic != "Standard" else "Standard"
        lines.append(
            f"{clear.rank_name:<4} {fc:<3} {_difficulty_name(clear.difficulty):<9} "
            f"{mode:<12} {clear.high_score:>10}  {clear.display_name}"
        )

    by_rank: dict[str, int] = {}
    for clear in clears:
        by_rank[clear.rank_name] = by_rank.get(clear.rank_name, 0) + 1
    rank_summary = ", ".join(f"{name} x{by_rank[name]}" for name in reversed(_RANK_NAMES) if name in by_rank)
    lines.extend(["", f"By rank: {rank_summary}"])
    return "\n".join(lines)


def load_level_clears(player_data_path: Path) -> tuple[list[LevelClear], str]:
    """Parse played level stats from `PlayerData.dat`.

    Returns `(clears, error)`. `clears` is empty when parsing fails (`error` set)
    or when there are no played entries.

    """
    try:
        raw = player_data_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [], str(exc)

    players = data.get("localPlayers")
    if not isinstance(players, list) or not players:
        return [], "`localPlayers` missing or empty"
    player = players[0]
    if not isinstance(player, dict):
        return [], "invalid local player entry"
    stats = player.get("levelsStatsData")
    if not isinstance(stats, list):
        return [], "`levelsStatsData` missing"

    clears: list[LevelClear] = []
    for entry in stats:
        clear = _parse_stat_entry(entry)
        if clear is not None:
            clears.append(clear)

    clears.sort(
        key=lambda item: (
            -item.max_rank,
            0 if item.full_combo else 1,
            item.display_name.casefold(),
            -item.difficulty,
            item.characteristic.casefold(),
        )
    )
    return clears, ""


def _difficulty_name(difficulty: int) -> str:
    if 0 <= difficulty < len(_DIFFICULTY_NAMES):
        return _DIFFICULTY_NAMES[difficulty]
    return f"Diff{difficulty}"


def _display_level_name(level_id: str) -> str:
    if level_id.startswith(_CUSTOM_LEVEL_PREFIX):
        digest = level_id.removeprefix(_CUSTOM_LEVEL_PREFIX)
        if len(digest) > _CUSTOM_HASH_PREVIEW_LEN:
            return f"Custom ({digest[:_CUSTOM_HASH_PREVIEW_LEN]}…)"
        return f"Custom ({digest})"
    spaced = _CAMEL_SPLIT_RE.sub(" ", level_id).replace("_", " ").strip()
    return spaced or level_id


def _parse_stat_entry(entry: object) -> LevelClear | None:
    if not isinstance(entry, dict):
        return None
    play_count = int(entry.get("playCount") or 0)
    high_score = int(entry.get("highScore") or 0)
    full_combo = bool(entry.get("fullCombo"))
    valid_score = bool(entry.get("validScore"))
    if play_count <= 0 and not valid_score and high_score <= 0 and not full_combo:
        return None
    if not valid_score and high_score <= 0 and not full_combo:
        return None

    level_id = str(entry.get("levelId") or "").strip()
    if not level_id:
        return None
    difficulty = int(entry.get("difficulty") or 0)
    characteristic = str(entry.get("beatmapCharacteristicName") or "Standard").strip() or "Standard"
    max_rank = int(entry.get("maxRank") or 0)
    rank_name = f"?{max_rank}" if max_rank < 0 or max_rank >= len(_RANK_NAMES) else _RANK_NAMES[max_rank]

    return LevelClear(
        level_id=level_id,
        display_name=_display_level_name(level_id),
        difficulty=difficulty,
        characteristic=characteristic,
        max_rank=max_rank,
        rank_name=rank_name,
        full_combo=full_combo,
        high_score=high_score,
        play_count=play_count,
    )
