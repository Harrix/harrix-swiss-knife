---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `report.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `LevelClear`](#%EF%B8%8F-class-levelclear)
- [🔧 Function `format_progress_report`](#-function-format_progress_report)
- [🔧 Function `load_level_clears`](#-function-load_level_clears)

</details>

## 🏛️ Class `LevelClear`

```python
class LevelClear
```

One played difficulty of a level from `levelsStatsData`.

<details>
<summary>Code:</summary>

```python
class LevelClear:

    level_id: str
    display_name: str
    difficulty: int
    characteristic: str
    max_rank: int
    rank_name: str
    full_combo: bool
    high_score: int
    play_count: int
```

</details>

## 🔧 Function `format_progress_report`

```python
def format_progress_report(player_data_path: Path) -> str
```

Return a multiline progress report for the export result / ZIP sidecar.

<details>
<summary>Code:</summary>

```python
def format_progress_report(player_data_path: Path) -> str:
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
```

</details>

## 🔧 Function `load_level_clears`

```python
def load_level_clears(player_data_path: Path) -> tuple[list[LevelClear], str]
```

Parse played level stats from `PlayerData.dat`.

Returns `(clears, error)`. `clears` is empty when parsing fails (`error` set)
or when there are no played entries.

<details>
<summary>Code:</summary>

```python
def load_level_clears(player_data_path: Path) -> tuple[list[LevelClear], str]:
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
```

</details>
