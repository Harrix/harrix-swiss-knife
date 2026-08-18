"""Category suggestions from description text, history, and category labels."""

from __future__ import annotations

import math
import re
from difflib import SequenceMatcher
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

_DEFAULT_LIMIT = 3
_DEFAULT_MIN_SCORE = 0.48
_DEFAULT_MIN_LENGTH = 3
_MIN_TOKEN_LENGTH = 3
_PREFIX_MIN_RATIO = 0.6
_TYPO_MIN_RATIO = 0.72
_TYPO_MIN_LENGTH_RATIO = 0.8
_FREQUENCY_BONUS = 0.04
_TOKEN_RE = re.compile(r"[\w]+", re.UNICODE)


def suggest_categories(
    description: str,
    history_pairs: Sequence[tuple[str, str, int]],
    category_names: Sequence[str],
    *,
    category_aliases: Mapping[str, Sequence[str]] | None = None,
    limit: int = _DEFAULT_LIMIT,
    min_score: float = _DEFAULT_MIN_SCORE,
    min_length: int = _DEFAULT_MIN_LENGTH,
) -> list[str]:
    """Return up to `limit` category names suggested for `description`.

    Prefers close matches to past descriptions (weighted by how often that pair
    was used), then category English/local names. Token prefix and typo-tolerant
    matches are used instead of loose full-string fuzzy matching.

    """
    query = description.strip().lower()
    if len(query) < min_length:
        return []

    allowed = {name for name in category_names if name}
    if not allowed:
        return []

    scores: dict[str, float] = {}
    history_counts: dict[str, int] = {}

    for row in history_pairs:
        category_name = row[1]
        if not category_name or category_name not in allowed:
            continue
        past = str(row[0]).strip().lower()
        count = max(int(row[2]), 1)
        score = _score_texts(query, past)
        if score < min_score:
            continue
        previous = scores.get(category_name, 0.0)
        if score > previous:
            scores[category_name] = score
        history_counts[category_name] = history_counts.get(category_name, 0) + max(count, 1)

    for category_name in allowed:
        aliases = [category_name]
        if category_aliases is not None:
            aliases.extend(category_aliases.get(category_name, ()))
        best_alias = 0.0
        for alias in aliases:
            text = str(alias).strip().lower()
            if not text:
                continue
            best_alias = max(best_alias, _score_texts(query, text))
        if best_alias < min_score:
            continue
        previous = scores.get(category_name, 0.0)
        if best_alias > previous:
            scores[category_name] = best_alias

    ranked = sorted(
        scores.items(),
        key=lambda item: (
            -(item[1] + _FREQUENCY_BONUS * math.log10(1 + history_counts.get(item[0], 0))),
            item[0].lower(),
        ),
    )
    return [name for name, _ in ranked[:limit]]


def _prefix_score(query: str, candidate: str) -> float:
    shorter, longer = (query, candidate) if len(query) <= len(candidate) else (candidate, query)
    if len(shorter) < _MIN_TOKEN_LENGTH or not longer.startswith(shorter):
        return 0.0
    return 0.82 + 0.18 * (len(shorter) / len(longer))


def _score_texts(query: str, candidate: str) -> float:
    if not query or not candidate:
        return 0.0
    if query == candidate:
        return 1.0

    prefix = _prefix_score(query, candidate)
    token_score = _token_score(query, candidate)
    typo = _similar_typo(query, candidate)
    return max(prefix, token_score, typo)


def _similar_typo(left: str, right: str) -> float:
    if min(len(left), len(right)) < _MIN_TOKEN_LENGTH:
        return 0.0
    if min(len(left), len(right)) / max(len(left), len(right)) < _TYPO_MIN_LENGTH_RATIO:
        return 0.0
    ratio = SequenceMatcher(None, left, right).ratio()
    return ratio if ratio >= _TYPO_MIN_RATIO else 0.0


def _token_pair_score(left: str, right: str) -> float:
    if left == right:
        return 1.0
    shorter, longer = (left, right) if len(left) <= len(right) else (right, left)
    if longer.startswith(shorter) and len(shorter) / len(longer) >= _PREFIX_MIN_RATIO:
        return 0.88
    return _similar_typo(left, right)


def _token_score(query: str, candidate: str) -> float:
    query_tokens = [token for token in _TOKEN_RE.findall(query) if len(token) >= _MIN_TOKEN_LENGTH]
    candidate_tokens = [token for token in _TOKEN_RE.findall(candidate) if len(token) >= _MIN_TOKEN_LENGTH]
    if not query_tokens or not candidate_tokens:
        return 0.0

    matched = 0.0
    for q_token in query_tokens:
        best = 0.0
        for c_token in candidate_tokens:
            best = max(best, _token_pair_score(q_token, c_token))
        matched += best
    coverage = matched / len(query_tokens)
    if coverage <= 0.0:
        return 0.0
    return 0.55 + 0.45 * coverage
