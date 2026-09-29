---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `font_preview.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FontPreviewDelegate`](#%EF%B8%8F-class-fontpreviewdelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
- [🔧 Function `clear_font_preview_memory`](#-function-clear_font_preview_memory)
- [🔧 Function `font_preview_cache_dir`](#-function-font_preview_cache_dir)
- [🔧 Function `font_preview_pixmap`](#-function-font_preview_pixmap)
- [🔧 Function `load_font_preview_text`](#-function-load_font_preview_text)

</details>

## 🏛️ Class `FontPreviewDelegate`

```python
class FontPreviewDelegate(QStyledItemDelegate)
```

Paint each font row as family name + sample text in that typeface.

<details>
<summary>Code:</summary>

```python
class FontPreviewDelegate(QStyledItemDelegate):

    def __init__(self, preview_text: str, parent: QWidget | None = None) -> None:
        """Store the sample phrase used for every row."""
        super().__init__(parent)
        self._preview_text = preview_text.strip() or DEFAULT_FONT_PREVIEW_TEXT

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: _ModelIndex) -> None:
        """Draw selection chrome, family label, and cached sample."""
        self.initStyleOption(option, index)
        painter.save()
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(option.rect, option.palette.alternateBase())

        family = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        sample = font_preview_pixmap(family, self._preview_text)
        name_rect = QRect(option.rect.left() + 6, option.rect.top(), 120, option.rect.height())
        sample_rect = QRect(
            name_rect.right() + 6,
            option.rect.top() + max(0, (option.rect.height() - sample.height()) // 2),
            sample.width(),
            sample.height(),
        )
        pen = (
            option.palette.highlightedText().color()
            if option.state & QStyle.StateFlag.State_Selected
            else option.palette.text().color()
        )
        painter.setPen(pen)
        ui_font = QFont(option.font)
        ui_font.setPointSizeF(max(8.0, ui_font.pointSizeF()))
        painter.setFont(ui_font)
        painter.drawText(name_rect, int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft), family)
        painter.drawPixmap(sample_rect.topLeft(), sample)
        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: _ModelIndex) -> QSize:  # noqa: ARG002, N802
        """Return a row tall enough for the sample strip."""
        return QSize(max(option.rect.width(), 360), max(_PREVIEW_HEIGHT + 8, 34))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, preview_text: str, parent: QWidget | None = None) -> None
```

Store the sample phrase used for every row.

<details>
<summary>Code:</summary>

```python
def __init__(self, preview_text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._preview_text = preview_text.strip() or DEFAULT_FONT_PREVIEW_TEXT
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: _ModelIndex) -> None
```

Draw selection chrome, family label, and cached sample.

<details>
<summary>Code:</summary>

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: _ModelIndex) -> None:
        self.initStyleOption(option, index)
        painter.save()
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(option.rect, option.palette.alternateBase())

        family = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        sample = font_preview_pixmap(family, self._preview_text)
        name_rect = QRect(option.rect.left() + 6, option.rect.top(), 120, option.rect.height())
        sample_rect = QRect(
            name_rect.right() + 6,
            option.rect.top() + max(0, (option.rect.height() - sample.height()) // 2),
            sample.width(),
            sample.height(),
        )
        pen = (
            option.palette.highlightedText().color()
            if option.state & QStyle.StateFlag.State_Selected
            else option.palette.text().color()
        )
        painter.setPen(pen)
        ui_font = QFont(option.font)
        ui_font.setPointSizeF(max(8.0, ui_font.pointSizeF()))
        painter.setFont(ui_font)
        painter.drawText(name_rect, int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft), family)
        painter.drawPixmap(sample_rect.topLeft(), sample)
        painter.restore()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self, option: QStyleOptionViewItem, index: _ModelIndex) -> QSize
```

Return a row tall enough for the sample strip.

<details>
<summary>Code:</summary>

```python
def sizeHint(self, option: QStyleOptionViewItem, index: _ModelIndex) -> QSize:  # noqa: ARG002, N802
        return QSize(max(option.rect.width(), 360), max(_PREVIEW_HEIGHT + 8, 34))
```

</details>

## 🔧 Function `clear_font_preview_memory`

```python
def clear_font_preview_memory() -> None
```

Drop in-memory previews (disk files stay until phrase/version changes).

<details>
<summary>Code:</summary>

```python
def clear_font_preview_memory() -> None:
    _memory.clear()
    _memory_order.clear()
```

</details>

## 🔧 Function `font_preview_cache_dir`

```python
def font_preview_cache_dir(preview_text: str) -> Path
```

Return the disk folder for the current preview phrase (and pixel size).

<details>
<summary>Code:</summary>

```python
def font_preview_cache_dir(preview_text: str) -> Path:
    digest = hashlib.sha256(
        f"{_FORMAT_VERSION}|{_PREVIEW_WIDTH}x{_PREVIEW_HEIGHT}|{preview_text}".encode()
    ).hexdigest()[:16]
    return _font_preview_root() / digest
```

</details>

## 🔧 Function `font_preview_pixmap`

```python
def font_preview_pixmap(family: str, preview_text: str | None = None) -> QPixmap
```

Return a cached sample pixmap for `family`, rendering on first use.

<details>
<summary>Code:</summary>

```python
def font_preview_pixmap(family: str, preview_text: str | None = None) -> QPixmap:
    text = (preview_text if preview_text is not None else load_font_preview_text()).strip() or DEFAULT_FONT_PREVIEW_TEXT
    family_key = family.strip() or "Sans Serif"
    cache_key = f"{family_key}\0{text}"
    cached = _memory.get(cache_key)
    if cached is not None and not cached.isNull():
        _touch_memory(cache_key)
        return cached

    path = font_preview_cache_dir(text) / f"{_family_file_stem(family_key)}.png"
    if path.is_file():
        loaded = QPixmap(str(path))
        if not loaded.isNull():
            _store_memory(cache_key, loaded)
            return loaded

    pixmap = _render_preview(family_key, text)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        pixmap.save(str(path), "PNG")
    except OSError:
        logger.debug("Could not save font preview cache for %s", family_key, exc_info=True)
    _store_memory(cache_key, pixmap)
    return pixmap
```

</details>

## 🔧 Function `load_font_preview_text`

```python
def load_font_preview_text() -> str
```

Return the sample phrase from `config.json`, or the default.

<details>
<summary>Code:</summary>

```python
def load_font_preview_text() -> str:
    try:
        raw = h.dev.config_load(get_config_path_str())
    except (FileNotFoundError, OSError, TypeError, ValueError):
        return DEFAULT_FONT_PREVIEW_TEXT
    if not isinstance(raw, dict):
        return DEFAULT_FONT_PREVIEW_TEXT
    text = str(raw.get(_CONFIG_KEY) or "").strip()
    return text or DEFAULT_FONT_PREVIEW_TEXT
```

</details>
