---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `level_widget.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AudioLevelWidget`](#%EF%B8%8F-class-audiolevelwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `begin_live`](#%EF%B8%8F-method-begin_live)
  - [⚙️ Method `clear`](#%EF%B8%8F-method-clear)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `push_envelope`](#%EF%B8%8F-method-push_envelope)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `set_playback_position`](#%EF%B8%8F-method-set_playback_position)
  - [⚙️ Method `show_overview`](#%EF%B8%8F-method-show_overview)

</details>

## 🏛️ Class `AudioLevelWidget`

```python
class AudioLevelWidget(QWidget)
```

Live scrolling and full-recording waveform display.

<details>
<summary>Code:</summary>

```python
class AudioLevelWidget(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize waveform widget."""
        super().__init__(parent)
        self._mode: Literal["idle", "live", "overview"] = "idle"
        self._live_buckets: deque[tuple[float, float]] = deque(
            [(0.0, 0.0)] * LEVEL_BAR_COUNT,
            maxlen=LEVEL_BAR_COUNT,
        )
        self._overview_pcm = b""
        self._playback_ratio: float | None = None
        self.setMinimumHeight(72)
        self.setVisible(False)

    def begin_live(self) -> None:
        """Switch to scrolling live waveform mode."""
        self._mode = "live"
        self._overview_pcm = b""
        self._playback_ratio = None
        self._live_buckets = deque([(0.0, 0.0)] * LEVEL_BAR_COUNT, maxlen=LEVEL_BAR_COUNT)
        self.setVisible(True)
        self.update()

    def clear(self) -> None:
        """Reset widget to idle state."""
        self._mode = "idle"
        self._overview_pcm = b""
        self._playback_ratio = None
        self._live_buckets = deque([(0.0, 0.0)] * LEVEL_BAR_COUNT, maxlen=LEVEL_BAR_COUNT)
        self.setVisible(False)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Paint live or overview waveform."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        if width <= 0 or height <= 0:
            return

        painter.fillRect(0, 0, width, height, WAVEFORM_BG)
        center_y = height / 2.0
        margin = 8
        half_height = max(4.0, (height - margin * 2) / 2.0)

        for ratio in (0.25, 0.75):
            grid_y = margin + ratio * (height - margin * 2)
            painter.setPen(QPen(WAVEFORM_GRID, 1, Qt.PenStyle.DotLine))
            painter.drawLine(0, int(grid_y), width, int(grid_y))

        painter.setPen(QPen(WAVEFORM_CENTER, 1))
        painter.drawLine(0, int(center_y), width, int(center_y))

        if self._mode == "live":
            buckets = list(self._live_buckets)
            fill_color = WAVEFORM_LIVE_FILL
        elif self._mode == "overview" and self._overview_pcm:
            bucket_count = max(32, width // 2)
            buckets = waveform_buckets_from_pcm(self._overview_pcm, bucket_count)
            fill_color = WAVEFORM_FILL
        else:
            return

        if not buckets:
            return

        path = QPainterPath()
        path.moveTo(0.0, center_y)
        bucket_width = width / len(buckets)
        for index, (_peak_neg, peak_pos) in enumerate(buckets):
            x = index * bucket_width + bucket_width / 2.0
            path.lineTo(x, center_y - peak_pos * half_height)

        last_x = (len(buckets) - 1) * bucket_width + bucket_width / 2.0
        path.lineTo(last_x, center_y)

        for index in range(len(buckets) - 1, -1, -1):
            peak_neg, _peak_pos = buckets[index]
            x = index * bucket_width + bucket_width / 2.0
            path.lineTo(x, center_y - peak_neg * half_height)

        path.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(fill_color)
        painter.drawPath(path)

        painter.setPen(QPen(WAVEFORM_OUTLINE, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        if self._mode == "overview" and self._playback_ratio is not None:
            playhead_x = max(0.0, min(float(width), self._playback_ratio * width))
            painter.setPen(QPen(WAVEFORM_PLAYHEAD, 2))
            painter.drawLine(int(playhead_x), 0, int(playhead_x), height)

    def push_envelope(self, peak_neg: float, peak_pos: float) -> None:
        """Append one live waveform bucket and repaint."""
        if self._mode != "live":
            return
        self._live_buckets.append((peak_neg, peak_pos))
        self.update()

    def resizeEvent(self, event) -> None:  # noqa: ANN001, N802
        """Repaint overview buckets when the widget is resized."""
        super().resizeEvent(event)
        if self._mode == "overview":
            self.update()

    def set_playback_position(self, ratio: float | None) -> None:
        """Set playhead position from 0 to 1, or hide it when `ratio` is `None`."""
        if self._playback_ratio != ratio:
            self._playback_ratio = ratio
            self.update()

    def show_overview(self, pcm_data: bytes) -> None:
        """Show the full recording waveform."""
        self._mode = "overview"
        self._overview_pcm = pcm_data
        self._playback_ratio = None
        self.setVisible(bool(pcm_data))
        self.update()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize waveform widget.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._mode: Literal["idle", "live", "overview"] = "idle"
        self._live_buckets: deque[tuple[float, float]] = deque(
            [(0.0, 0.0)] * LEVEL_BAR_COUNT,
            maxlen=LEVEL_BAR_COUNT,
        )
        self._overview_pcm = b""
        self._playback_ratio: float | None = None
        self.setMinimumHeight(72)
        self.setVisible(False)
```

</details>

### ⚙️ Method `begin_live`

```python
def begin_live(self) -> None
```

Switch to scrolling live waveform mode.

<details>
<summary>Code:</summary>

```python
def begin_live(self) -> None:
        self._mode = "live"
        self._overview_pcm = b""
        self._playback_ratio = None
        self._live_buckets = deque([(0.0, 0.0)] * LEVEL_BAR_COUNT, maxlen=LEVEL_BAR_COUNT)
        self.setVisible(True)
        self.update()
```

</details>

### ⚙️ Method `clear`

```python
def clear(self) -> None
```

Reset widget to idle state.

<details>
<summary>Code:</summary>

```python
def clear(self) -> None:
        self._mode = "idle"
        self._overview_pcm = b""
        self._playback_ratio = None
        self._live_buckets = deque([(0.0, 0.0)] * LEVEL_BAR_COUNT, maxlen=LEVEL_BAR_COUNT)
        self.setVisible(False)
        self.update()
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Paint live or overview waveform.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        if width <= 0 or height <= 0:
            return

        painter.fillRect(0, 0, width, height, WAVEFORM_BG)
        center_y = height / 2.0
        margin = 8
        half_height = max(4.0, (height - margin * 2) / 2.0)

        for ratio in (0.25, 0.75):
            grid_y = margin + ratio * (height - margin * 2)
            painter.setPen(QPen(WAVEFORM_GRID, 1, Qt.PenStyle.DotLine))
            painter.drawLine(0, int(grid_y), width, int(grid_y))

        painter.setPen(QPen(WAVEFORM_CENTER, 1))
        painter.drawLine(0, int(center_y), width, int(center_y))

        if self._mode == "live":
            buckets = list(self._live_buckets)
            fill_color = WAVEFORM_LIVE_FILL
        elif self._mode == "overview" and self._overview_pcm:
            bucket_count = max(32, width // 2)
            buckets = waveform_buckets_from_pcm(self._overview_pcm, bucket_count)
            fill_color = WAVEFORM_FILL
        else:
            return

        if not buckets:
            return

        path = QPainterPath()
        path.moveTo(0.0, center_y)
        bucket_width = width / len(buckets)
        for index, (_peak_neg, peak_pos) in enumerate(buckets):
            x = index * bucket_width + bucket_width / 2.0
            path.lineTo(x, center_y - peak_pos * half_height)

        last_x = (len(buckets) - 1) * bucket_width + bucket_width / 2.0
        path.lineTo(last_x, center_y)

        for index in range(len(buckets) - 1, -1, -1):
            peak_neg, _peak_pos = buckets[index]
            x = index * bucket_width + bucket_width / 2.0
            path.lineTo(x, center_y - peak_neg * half_height)

        path.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(fill_color)
        painter.drawPath(path)

        painter.setPen(QPen(WAVEFORM_OUTLINE, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        if self._mode == "overview" and self._playback_ratio is not None:
            playhead_x = max(0.0, min(float(width), self._playback_ratio * width))
            painter.setPen(QPen(WAVEFORM_PLAYHEAD, 2))
            painter.drawLine(int(playhead_x), 0, int(playhead_x), height)
```

</details>

### ⚙️ Method `push_envelope`

```python
def push_envelope(self, peak_neg: float, peak_pos: float) -> None
```

Append one live waveform bucket and repaint.

<details>
<summary>Code:</summary>

```python
def push_envelope(self, peak_neg: float, peak_pos: float) -> None:
        if self._mode != "live":
            return
        self._live_buckets.append((peak_neg, peak_pos))
        self.update()
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event) -> None
```

Repaint overview buckets when the widget is resized.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event) -> None:  # noqa: ANN001, N802
        super().resizeEvent(event)
        if self._mode == "overview":
            self.update()
```

</details>

### ⚙️ Method `set_playback_position`

```python
def set_playback_position(self, ratio: float | None) -> None
```

Set playhead position from 0 to 1, or hide it when `ratio` is `None`.

<details>
<summary>Code:</summary>

```python
def set_playback_position(self, ratio: float | None) -> None:
        if self._playback_ratio != ratio:
            self._playback_ratio = ratio
            self.update()
```

</details>

### ⚙️ Method `show_overview`

```python
def show_overview(self, pcm_data: bytes) -> None
```

Show the full recording waveform.

<details>
<summary>Code:</summary>

```python
def show_overview(self, pcm_data: bytes) -> None:
        self._mode = "overview"
        self._overview_pcm = pcm_data
        self._playback_ratio = None
        self.setVisible(bool(pcm_data))
        self.update()
```

</details>
