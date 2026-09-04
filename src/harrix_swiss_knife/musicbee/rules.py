"""Declarative Stream playlist rules."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.musicbee.paths import normalize_path_key, path_is_under

if TYPE_CHECKING:
    from harrix_swiss_knife.musicbee.index import FileIndex

KNOWN_RULE_TYPES = frozenset({"restrict_folder", "ensure_subset", "union", "rebuild_remainder"})


@dataclass
class RuleWarning:
    """A skipped or incomplete rule application."""

    message: str


def apply_rules(
    playlists: dict[str, list[str]],
    rules: list[dict[str, Any]],
    *,
    placeholders: dict[str, str],
    file_index: FileIndex,
) -> list[RuleWarning]:
    """Apply `rules` in order, mutating `playlists` (name → tracks)."""
    warnings: list[RuleWarning] = []
    for raw in rules:
        if not isinstance(raw, dict):
            warnings.append(RuleWarning("Skipped a non-object rule"))
            continue
        rule = expand_rule_placeholders(raw, placeholders)
        kind = str(rule.get("type") or "").strip()
        if kind not in KNOWN_RULE_TYPES:
            warnings.append(RuleWarning(f"Unknown rule type: {kind or '(empty)'}"))
            continue
        if kind == "restrict_folder":
            warnings.extend(_restrict_folder(playlists, rule))
        elif kind == "ensure_subset":
            warnings.extend(_ensure_subset(playlists, rule))
        elif kind == "union":
            warnings.extend(_union(playlists, rule))
        else:
            warnings.extend(_rebuild_remainder(playlists, rule, file_index))
    return warnings


def expand_rule_placeholders(rule: dict[str, Any], values: dict[str, str]) -> dict[str, Any]:
    """Replace `{music_root}` / `{stream_root}` in string fields of `rule`."""
    expanded: dict[str, Any] = {}
    for key, value in rule.items():
        if isinstance(value, str):
            expanded[key] = value.format_map(values)
        elif isinstance(value, list):
            expanded[key] = [item.format_map(values) if isinstance(item, str) else item for item in value]
        else:
            expanded[key] = value
    return expanded


def matching_playlist_names(names: list[str], pattern: str) -> list[str]:
    """Return playlist names matching a glob `pattern`."""
    return [name for name in names if fnmatch.fnmatch(name, pattern)]


def _dedupe_preserve(paths: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for path in paths:
        key = normalize_path_key(path)
        if key in seen:
            continue
        seen.add(key)
        result.append(path)
    return result


def _ensure_subset(playlists: dict[str, list[str]], rule: dict[str, Any]) -> list[RuleWarning]:
    source = str(rule.get("source") or "")
    target = str(rule.get("target") or "")
    if source not in playlists or target not in playlists:
        return [RuleWarning(f"ensure_subset skipped (missing playlist): {source} → {target}")]
    present = {normalize_path_key(path) for path in playlists[target]}
    extra = [path for path in playlists[source] if normalize_path_key(path) not in present]
    if extra:
        playlists[target] = _dedupe_preserve([*playlists[target], *extra])
    return []


def _rebuild_remainder(
    playlists: dict[str, list[str]],
    rule: dict[str, Any],
    file_index: FileIndex,
) -> list[RuleWarning]:
    name = str(rule.get("playlist") or "")
    folder = str(rule.get("from_folder") or "")
    exclude_pattern = str(rule.get("exclude_playlists") or "")
    if name not in playlists:
        return [RuleWarning(f"rebuild_remainder skipped (missing playlist): {name}")]
    if not folder:
        return [RuleWarning("rebuild_remainder skipped (from_folder is empty)")]
    excluded: set[str] = set()
    for other in matching_playlist_names(list(playlists), exclude_pattern):
        if other == name:
            continue
        excluded.update(normalize_path_key(path) for path in playlists[other])
    remainder = [
        str(item.path)
        for item in sorted(file_index.files, key=lambda item: normalize_path_key(item.path))
        if path_is_under(item.path, Path(folder)) and normalize_path_key(item.path) not in excluded
    ]
    playlists[name] = remainder
    return []


def _restrict_folder(playlists: dict[str, list[str]], rule: dict[str, Any]) -> list[RuleWarning]:
    pattern = str(rule.get("playlists") or "")
    folder = str(rule.get("folder") or "")
    if not pattern or not folder:
        return [RuleWarning("restrict_folder skipped (playlists or folder is empty)")]
    names = matching_playlist_names(list(playlists), pattern)
    if not names:
        return [RuleWarning(f"restrict_folder matched no playlists: {pattern}")]
    for name in names:
        playlists[name] = [path for path in playlists[name] if path_is_under(path, folder)]
    return []


def _union(playlists: dict[str, list[str]], rule: dict[str, Any]) -> list[RuleWarning]:
    target = str(rule.get("target") or "")
    sources = [str(item) for item in (rule.get("sources") or [])]
    if target not in playlists:
        return [RuleWarning(f"union skipped (missing target): {target}")]
    missing = [name for name in sources if name not in playlists]
    if missing:
        return [RuleWarning(f"union skipped (missing sources): {', '.join(missing)}")]
    merged: list[str] = []
    for name in sources:
        merged.extend(playlists[name])
    playlists[target] = _dedupe_preserve(merged)
    return []
