---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exercise_list_hover_preview.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ExerciseListHoverPreview`](#%EF%B8%8F-class-exerciselisthoverpreview)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `hide_preview`](#%EF%B8%8F-method-hide_preview)

</details>

## 🏛️ Class `ExerciseListHoverPreview`

```python
class ExerciseListHoverPreview(QObject)
```

Show an enlarged AVIF animation after dwelling on a list-row icon.

<details>
<summary>Code:</summary>

```python
class ExerciseListHoverPreview(QObject):

    def __init__(
        self,
        list_view: QListView,
        *,
        get_avif_manager: Callable[[], AvifManager | None],
        preview_size: QSize | None = None,
        parent: QObject | None = None,
    ) -> None:
        """Attach hover tracking to `list_view`.

        Args:

        - `list_view` (`QListView`): Exercise list that paints icons on the left.
        - `get_avif_manager` (`Callable`): Returns the current `AvifManager` (may be `None`).
        - `preview_size` (`QSize | None`): Popup size. Defaults to 280×280.
        - `parent` (`QObject | None`): Qt parent. Defaults to `list_view`.

        """
        super().__init__(parent or list_view)
        self._list_view = list_view
        self._get_avif_manager = get_avif_manager
        self._preview_size = preview_size or QSize(_PREVIEW_EDGE, _PREVIEW_EDGE)
        self._pending_exercise: str | None = None
        self._shown_exercise: str | None = None

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._show_preview)

        self._popup = QFrame(
            None,
            Qt.WindowType.ToolTip
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self._popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=True)
        self._popup.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        self._popup.setStyleSheet(
            """
            QFrame {
                background: white;
                border: 1px solid #bdbdbd;
                border-radius: 6px;
            }
            """
        )
        popup_layout = QVBoxLayout(self._popup)
        popup_layout.setContentsMargins(4, 4, 4, 4)
        self._label = QLabel(self._popup)
        self._label.setFixedSize(self._preview_size)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet("background-color: white; border: none;")
        popup_layout.addWidget(self._label)

        self._list_view.setMouseTracking(True)
        viewport = self._list_view.viewport()
        viewport.setMouseTracking(True)
        viewport.installEventFilter(self)
        self._list_view.installEventFilter(self)
        scroll = self._list_view.verticalScrollBar()
        if scroll is not None:
            scroll.valueChanged.connect(self.hide_preview)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        """Track icon hover, dwell delay, and leave/scroll hide."""
        viewport = self._list_view.viewport()
        event_type = event.type()

        if obj is viewport and event_type == QEvent.Type.MouseMove:
            self._on_mouse_move(cast("QMouseEvent", event).position().toPoint())
            return False

        if obj is viewport and event_type in {QEvent.Type.Leave, QEvent.Type.Wheel}:
            self.hide_preview()
            return False

        if obj is self._list_view and event_type == QEvent.Type.Leave:
            self.hide_preview()
            return False

        return super().eventFilter(obj, event)

    def hide_preview(self) -> None:
        """Stop animation and hide the popup."""
        self._timer.stop()
        self._pending_exercise = None
        self._shown_exercise = None
        self._stop_animation()
        self._popup.hide()

    def _exercise_at_icon(self, pos: QPoint) -> str | None:
        index = self._list_view.indexAt(pos)
        if not index.isValid():
            return None

        exercise = index.data(Qt.ItemDataRole.UserRole)
        if not exercise:
            return None

        icon = index.data(Qt.ItemDataRole.DecorationRole)
        if icon is None or (hasattr(icon, "isNull") and icon.isNull()):
            return None

        item_rect = self._list_view.visualRect(index)
        icon_rect = NameLocalListDelegate.list_decoration_rect(
            item_rect,
            self._list_view.iconSize(),
            has_icon=True,
        )
        if not icon_rect.contains(pos):
            return None

        name = str(exercise).strip()
        return name or None

    def _move_popup_to_cursor(self) -> None:
        global_pos = QCursor.pos() + _CURSOR_OFFSET
        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            popup_size = self._popup.sizeHint()
            x = min(global_pos.x(), available.right() - popup_size.width())
            y = min(global_pos.y(), available.bottom() - popup_size.height())
            x = max(x, available.left())
            y = max(y, available.top())
            global_pos = QPoint(x, y)
        self._popup.move(global_pos)

    def _on_mouse_move(self, pos: QPoint) -> None:
        exercise = self._exercise_at_icon(pos)
        if exercise is None:
            self.hide_preview()
            return

        if exercise == self._shown_exercise and self._popup.isVisible():
            self._move_popup_to_cursor()
            return

        if exercise == self._pending_exercise and self._timer.isActive():
            return

        self._timer.stop()
        self._stop_animation()
        self._popup.hide()
        self._shown_exercise = None
        self._pending_exercise = exercise
        self._timer.start(_HOVER_DELAY_MS)

    def _show_preview(self) -> None:
        exercise = self._pending_exercise
        manager = self._get_avif_manager()
        if not exercise or manager is None:
            return
        if manager.get_exercise_avif_path(exercise) is None:
            return

        # Ensure label has a real size before frames are scaled.
        self._label.setFixedSize(self._preview_size)
        self._popup.adjustSize()
        self._move_popup_to_cursor()
        self._popup.show()
        manager.load_exercise_avif(exercise, self._label, AvifLabelKey.LIST_HOVER)
        self._shown_exercise = exercise

    def _stop_animation(self) -> None:
        manager = self._get_avif_manager()
        if manager is None:
            return
        data = manager.avif_data.get(AvifLabelKey.LIST_HOVER)
        if not data:
            return
        timer = data.get("timer")
        if timer is not None:
            timer.stop()
            data["timer"] = None
        data["frames"] = []
        data["current_frame"] = 0
        data["exercise"] = None
        self._label.clear()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, list_view: QListView, *, get_avif_manager: Callable[[], AvifManager | None], preview_size: QSize | None = None, parent: QObject | None = None) -> None
```

Attach hover tracking to `list_view`.

Args:

- `list_view` (`QListView`): Exercise list that paints icons on the left.
- `get_avif_manager` (`Callable`): Returns the current [`AvifManager`](../avif_manager.g.md#%EF%B8%8F-class-avifmanager) (may be `None`).
- `preview_size` (`QSize | None`): Popup size. Defaults to 280×280.
- `parent` (`QObject | None`): Qt parent. Defaults to `list_view`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        list_view: QListView,
        *,
        get_avif_manager: Callable[[], AvifManager | None],
        preview_size: QSize | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent or list_view)
        self._list_view = list_view
        self._get_avif_manager = get_avif_manager
        self._preview_size = preview_size or QSize(_PREVIEW_EDGE, _PREVIEW_EDGE)
        self._pending_exercise: str | None = None
        self._shown_exercise: str | None = None

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._show_preview)

        self._popup = QFrame(
            None,
            Qt.WindowType.ToolTip
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self._popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=True)
        self._popup.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        self._popup.setStyleSheet(
            """
            QFrame {
                background: white;
                border: 1px solid #bdbdbd;
                border-radius: 6px;
            }
            """
        )
        popup_layout = QVBoxLayout(self._popup)
        popup_layout.setContentsMargins(4, 4, 4, 4)
        self._label = QLabel(self._popup)
        self._label.setFixedSize(self._preview_size)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet("background-color: white; border: none;")
        popup_layout.addWidget(self._label)

        self._list_view.setMouseTracking(True)
        viewport = self._list_view.viewport()
        viewport.setMouseTracking(True)
        viewport.installEventFilter(self)
        self._list_view.installEventFilter(self)
        scroll = self._list_view.verticalScrollBar()
        if scroll is not None:
            scroll.valueChanged.connect(self.hide_preview)
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, obj: QObject, event: QEvent) -> bool
```

Track icon hover, dwell delay, and leave/scroll hide.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        viewport = self._list_view.viewport()
        event_type = event.type()

        if obj is viewport and event_type == QEvent.Type.MouseMove:
            self._on_mouse_move(cast("QMouseEvent", event).position().toPoint())
            return False

        if obj is viewport and event_type in {QEvent.Type.Leave, QEvent.Type.Wheel}:
            self.hide_preview()
            return False

        if obj is self._list_view and event_type == QEvent.Type.Leave:
            self.hide_preview()
            return False

        return super().eventFilter(obj, event)
```

</details>

### ⚙️ Method `hide_preview`

```python
def hide_preview(self) -> None
```

Stop animation and hide the popup.

<details>
<summary>Code:</summary>

```python
def hide_preview(self) -> None:
        self._timer.stop()
        self._pending_exercise = None
        self._shown_exercise = None
        self._stop_animation()
        self._popup.hide()
```

</details>
