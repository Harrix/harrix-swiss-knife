---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `tracker_layout_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_tracker_column_surfaces`](#-function-apply_tracker_column_surfaces)
- [🔧 Function `install_tracker_column_chrome`](#-function-install_tracker_column_chrome)
- [🔧 Function `polish_left_field_labels`](#-function-polish_left_field_labels)
- [🔧 Function `quiet_group_box`](#-function-quiet_group_box)
- [🔧 Function `soft_panel_css`](#-function-soft_panel_css)

</details>

## 🔧 Function `apply_tracker_column_surfaces`

```python
def apply_tracker_column_surfaces(host: QWidget, *, soft_panes: Sequence[tuple[QWidget, str]], content_panes: Sequence[tuple[QWidget, str]] = (), quiet_boxes: Iterable[Any] = ()) -> None
```

Paint soft/content panes and quiet GroupBoxes once (caller may theme-bind).

<details>
<summary>Code:</summary>

```python
def apply_tracker_column_surfaces(
    host: QWidget,
    *,
    soft_panes: Sequence[tuple[QWidget, str]],
    content_panes: Sequence[tuple[QWidget, str]] = (),
    quiet_boxes: Iterable[Any] = (),
) -> None:
    _apply_column_surfaces(host, soft_panes=soft_panes, content_panes=content_panes)
    for box in quiet_boxes:
        quiet_group_box(box)
```

</details>

## 🔧 Function `install_tracker_column_chrome`

```python
def install_tracker_column_chrome(host: QWidget, *, soft_panes: Sequence[tuple[QWidget, str]], content_panes: Sequence[tuple[QWidget, str]] = (), quiet_boxes: Iterable[Any] = (), theme_flag: str = '_tracker_column_chrome_theme_bound') -> None
```

Apply soft left/middle panels and quiet GroupBoxes; rebind on theme change.

Args:

- `host` (`QWidget`): Window that owns the panes (theme bind target).
- `soft_panes` (`Sequence[tuple[QWidget, str]]`): Form / list columns with
  soft card fill. Each tuple is `(widget, objectName)`.
- `content_panes` (`Sequence[tuple[QWidget, str]]`): Table / chart columns
  kept transparent. Defaults to empty.
- `quiet_boxes` (`Iterable[Any]`): `QGroupBox` widgets that should lose the
  Fluent title underline. Defaults to empty.
- `theme_flag` (`str`): Attribute name used to bind theme once per host.

<details>
<summary>Code:</summary>

```python
def install_tracker_column_chrome(
    host: QWidget,
    *,
    soft_panes: Sequence[tuple[QWidget, str]],
    content_panes: Sequence[tuple[QWidget, str]] = (),
    quiet_boxes: Iterable[Any] = (),
    theme_flag: str = "_tracker_column_chrome_theme_bound",
) -> None:

    def refresh() -> None:
        apply_tracker_column_surfaces(
            host,
            soft_panes=soft_panes,
            content_panes=content_panes,
            quiet_boxes=quiet_boxes,
        )

    refresh()
    if not getattr(host, theme_flag, False):
        bind_theme(host, refresh)
        setattr(host, theme_flag, True)
```

</details>

## 🔧 Function `polish_left_field_labels`

```python
def polish_left_field_labels(host: Any, pairs: Sequence[tuple[str, str]]) -> None
```

Put muted fixed-width captions to the left of form fields.

Args:

- `host` (`Any`): Window owning the labels.
- `pairs` (`Sequence[tuple[str, str]]`): `(attribute_name, caption)` rows.

<details>
<summary>Code:</summary>

```python
def polish_left_field_labels(host: Any, pairs: Sequence[tuple[str, str]]) -> None:
    for name, text in pairs:
        label = getattr(host, name, None)
        if not isinstance(label, QLabel):
            continue
        label.setText(text)
        label.setStyleSheet(muted_caption_qss())
        label.setMinimumWidth(FIELD_LABEL_WIDTH)
        label.setFixedWidth(FIELD_LABEL_WIDTH)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
```

</details>

## 🔧 Function `quiet_group_box`

```python
def quiet_group_box(group: Any, *, untitled: bool = False) -> None
```

Remove the Fluent GroupBox bottom hairline from a titled section.

<details>
<summary>Code:</summary>

```python
def quiet_group_box(group: Any, *, untitled: bool = False) -> None:
    name = group.objectName() or "groupBox"
    margin_top = "0px" if untitled else "1.2em"
    padding_top = f"{SPACE_XS}px" if untitled else "2px"
    title_rule = (
        f"QGroupBox#{name}::title {{ height: 0px; width: 0px; padding: 0px; margin: 0px; }}" if untitled else ""
    )
    group.setStyleSheet(
        f"""
        QGroupBox#{name} {{
            background: transparent;
            border: none;
            margin-top: {margin_top};
            padding-top: {padding_top};
            padding-bottom: 4px;
            border-radius: 0px;
        }}
        {title_rule}
        """,
    )
```

</details>

## 🔧 Function `soft_panel_css`

```python
def soft_panel_css(host: QWidget) -> str
```

Return the soft entry-column fill used by Finance Transactions.

<details>
<summary>Code:</summary>

```python
def soft_panel_css(host: QWidget) -> str:
    palette = palette_for(host)
    return css(mix(palette.window_bg, palette.card_bg))
```

</details>
