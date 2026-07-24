"""Fuzzy category suggestions from description text and transaction history."""

from __future__ import annotations

import re
from difflib import SequenceMatcher

_DEFAULT_LIMIT = 3
_DEFAULT_MIN_SCORE = 0.55
_DEFAULT_MIN_LENGTH = 3
_MIN_TOKEN_LENGTH = 2
_TOKEN_RE = re.compile(r"[\w]+", re.UNICODE)


def suggest_categories(
    description: str,
    history_pairs: list[tuple[str, str]],
    category_names: list[str],
    *,
    limit: int = _DEFAULT_LIMIT,
    min_score: float = _DEFAULT_MIN_SCORE,
    min_length: int = _DEFAULT_MIN_LENGTH,
) -> list[str]:
    """Return up to `limit` category names suggested for `description`.

    Prefers matches from past `(description, category)` pairs, then fills remaining
    slots by fuzzy-matching against category names. History wins ties.

    """
    query = description.strip().lower()
    if len(query) < min_length:
        return []

    scores: dict[str, tuple[float, int]] = {}

    for past_description, category_name in history_pairs:
        if not category_name:
            continue
        score = _score_texts(query, past_description.strip().lower())
        if score < min_score:
            continue
        _keep_best(scores, category_name, score, priority=0)

    for category_name in category_names:
        if not category_name:
            continue
        score = _score_texts(query, category_name.strip().lower())
        if score < min_score:
            continue
        _keep_best(scores, category_name, score, priority=1)

    ranked = sorted(scores.items(), key=lambda item: (-item[1][0], item[1][1], item[0].lower()))
    return [name for name, _ in ranked[:limit]]


def _keep_best(scores: dict[str, tuple[float, int]], category_name: str, score: float, *, priority: int) -> None:
    previous = scores.get(category_name)
    if previous is None or score > previous[0] or (score == previous[0] and priority < previous[1]):
        scores[category_name] = (score, priority)


def _score_texts(query: str, candidate: str) -> float:
    if not query or not candidate:
        return 0.0
    if query == candidate:
        return 1.0
    if query in candidate or candidate in query:
        contains = 0.85 + 0.15 * (min(len(query), len(candidate)) / max(len(query), len(candidate)))
    else:
        contains = 0.0

    ratio = SequenceMatcher(None, query, candidate).ratio()
    token_score = _token_score(query, candidate)
    return max(ratio, contains, token_score)


def _token_score(query: str, candidate: str) -> float:
    query_tokens = _TOKEN_RE.findall(query)
    candidate_tokens = _TOKEN_RE.findall(candidate)
    if not query_tokens or not candidate_tokens:
        return 0.0

    best = 0.0
    for q_token in query_tokens:
        for c_token in candidate_tokens:
            if len(q_token) < _MIN_TOKEN_LENGTH or len(c_token) < _MIN_TOKEN_LENGTH:
                continue
            if q_token == c_token:
                best = max(best, 0.95)
            elif q_token in c_token or c_token in q_token:
                best = max(best, 0.8)
            else:
                best = max(best, SequenceMatcher(None, q_token, c_token).ratio() * 0.9)
    return best
