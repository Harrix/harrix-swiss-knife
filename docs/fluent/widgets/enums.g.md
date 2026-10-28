---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `enums.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MatchMode`](#%EF%B8%8F-class-matchmode)
- [🏛️ Class `MessagePosition`](#%EF%B8%8F-class-messageposition)
- [🏛️ Class `Severity`](#%EF%B8%8F-class-severity)
- [🏛️ Class `SkeletonShape`](#%EF%B8%8F-class-skeletonshape)
- [🏛️ Class `TextRole`](#%EF%B8%8F-class-textrole)
- [🏛️ Class `TextStyle`](#%EF%B8%8F-class-textstyle)
- [🏛️ Class `Trend`](#%EF%B8%8F-class-trend)

</details>

## 🏛️ Class `MatchMode`

```python
class MatchMode(Enum)
```

How [`FluentAutoComplete`](inputs.g.md#%EF%B8%8F-class-fluentautocomplete) matches suggestions.

<details>
<summary>Code:</summary>

```python
class MatchMode(Enum):

    CONTAINS = "contains"
    PREFIX = "prefix"
    SUFFIX = "suffix"
    REGEX = "regex"
```

</details>

## 🏛️ Class `MessagePosition`

```python
class MessagePosition(Enum)
```

Where a floating message bar appears inside its host window.

<details>
<summary>Code:</summary>

```python
class MessagePosition(Enum):

    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
```

</details>

## 🏛️ Class `Severity`

```python
class Severity(Enum)
```

Semantic color of badges, tags, and info bars.

<details>
<summary>Code:</summary>

```python
class Severity(Enum):

    ACCENT = "accent"
    SUCCESS = "success"
    CAUTION = "caution"
    CRITICAL = "critical"
    NEUTRAL = "neutral"
```

</details>

## 🏛️ Class `SkeletonShape`

```python
class SkeletonShape(Enum)
```

Placeholder shape for [`FluentSkeleton`](display.g.md#%EF%B8%8F-class-fluentskeleton).

<details>
<summary>Code:</summary>

```python
class SkeletonShape(Enum):

    TEXT = "text"
    CIRCLE = "circle"
    RECTANGLE = "rectangle"
```

</details>

## 🏛️ Class `TextRole`

```python
class TextRole(Enum)
```

Color role of a Fluent label.

<details>
<summary>Code:</summary>

```python
class TextRole(Enum):

    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    ACCENT = "accent"
    DISABLED = "disabled"
```

</details>

## 🏛️ Class `TextStyle`

```python
class TextStyle(Enum)
```

Fluent type ramp entries: (scale, weight).

<details>
<summary>Code:</summary>

```python
class TextStyle(Enum):

    CAPTION = (TYPE_CAPTION, QFont.Weight.Normal)
    BODY = (TYPE_BODY, QFont.Weight.Normal)
    BODY_STRONG = (TYPE_BODY, QFont.Weight.DemiBold)
    BODY_LARGE = (TYPE_BODY_LARGE, QFont.Weight.Normal)
    SUBTITLE = (TYPE_SUBTITLE, QFont.Weight.DemiBold)
    TITLE = (TYPE_TITLE, QFont.Weight.DemiBold)
    TITLE_LARGE = (TYPE_TITLE_LARGE, QFont.Weight.DemiBold)
    DISPLAY = (TYPE_DISPLAY, QFont.Weight.DemiBold)
```

</details>

## 🏛️ Class `Trend`

```python
class Trend(Enum)
```

Direction shown on a stat card.

<details>
<summary>Code:</summary>

```python
class Trend(Enum):

    UP = "up"
    DOWN = "down"
    FLAT = "flat"
```

</details>
