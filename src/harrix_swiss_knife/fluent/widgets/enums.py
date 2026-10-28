"""Enumerations shared by the Fluent widget modules."""

from __future__ import annotations

from enum import Enum

from PySide6.QtGui import QFont

from harrix_swiss_knife.fluent.tokens import (
    TYPE_BODY,
    TYPE_BODY_LARGE,
    TYPE_CAPTION,
    TYPE_DISPLAY,
    TYPE_SUBTITLE,
    TYPE_TITLE,
    TYPE_TITLE_LARGE,
)


class MatchMode(Enum):
    """How `FluentAutoComplete` matches suggestions."""

    CONTAINS = "contains"
    PREFIX = "prefix"
    SUFFIX = "suffix"
    REGEX = "regex"


class MessagePosition(Enum):
    """Where a floating message bar appears inside its host window."""

    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"


class Severity(Enum):
    """Semantic color of badges, tags, and info bars."""

    ACCENT = "accent"
    SUCCESS = "success"
    CAUTION = "caution"
    CRITICAL = "critical"
    NEUTRAL = "neutral"


class SkeletonShape(Enum):
    """Placeholder shape for `FluentSkeleton`."""

    TEXT = "text"
    CIRCLE = "circle"
    RECTANGLE = "rectangle"


class TextRole(Enum):
    """Color role of a Fluent label."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    ACCENT = "accent"
    DISABLED = "disabled"


class TextStyle(Enum):
    """Fluent type ramp entries: (scale, weight)."""

    CAPTION = (TYPE_CAPTION, QFont.Weight.Normal)
    BODY = (TYPE_BODY, QFont.Weight.Normal)
    BODY_STRONG = (TYPE_BODY, QFont.Weight.DemiBold)
    BODY_LARGE = (TYPE_BODY_LARGE, QFont.Weight.Normal)
    SUBTITLE = (TYPE_SUBTITLE, QFont.Weight.DemiBold)
    TITLE = (TYPE_TITLE, QFont.Weight.DemiBold)
    TITLE_LARGE = (TYPE_TITLE_LARGE, QFont.Weight.DemiBold)
    DISPLAY = (TYPE_DISPLAY, QFont.Weight.DemiBold)


class Trend(Enum):
    """Direction shown on a stat card."""

    UP = "up"
    DOWN = "down"
    FLAT = "flat"
