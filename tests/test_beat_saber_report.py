"""Tests for Beat Saber PlayerData progress reporting."""

from __future__ import annotations

import json
from pathlib import Path

from harrix_swiss_knife.beat_saber_saves.report import format_progress_report, load_level_clears


def test_load_level_clears_parses_ranks_and_full_combo(tmp_path: Path) -> None:
    player_data = tmp_path / "PlayerData.dat"
    player_data.write_text(
        json.dumps(
            {
                "localPlayers": [
                    {
                        "levelsStatsData": [
                            {
                                "levelId": "EnterSandman",
                                "difficulty": 2,
                                "beatmapCharacteristicName": "Standard",
                                "highScore": 900000,
                                "maxCombo": 100,
                                "fullCombo": True,
                                "maxRank": 6,
                                "validScore": True,
                                "playCount": 2,
                            },
                            {
                                "levelId": "custom_level_ABCDEF0123456789",
                                "difficulty": 4,
                                "beatmapCharacteristicName": "OneSaber",
                                "highScore": 100,
                                "maxCombo": 1,
                                "fullCombo": False,
                                "maxRank": 2,
                                "validScore": True,
                                "playCount": 1,
                            },
                            {
                                "levelId": "UnusedStub",
                                "difficulty": 0,
                                "beatmapCharacteristicName": "Standard",
                                "highScore": 0,
                                "maxCombo": 0,
                                "fullCombo": False,
                                "maxRank": 0,
                                "validScore": False,
                                "playCount": 0,
                            },
                        ]
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    clears, error = load_level_clears(player_data)
    assert error == ""
    assert len(clears) == 2
    assert clears[0].rank_name == "SS"
    assert clears[0].full_combo is True
    assert clears[0].display_name == "Enter Sandman"
    assert clears[1].rank_name == "C"
    assert clears[1].display_name.startswith("Custom (ABCDEF01")

    report = format_progress_report(player_data)
    assert "Full combo (no misses): 1" in report
    assert "Enter Sandman" in report
    assert "SS" in report
