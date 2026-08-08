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
  - [⚙️ Method `detach`](#%EF%B8%8F-method-detach)
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
        - `preview_size` (`QSize | None`): Popup size. Defaults to `_PREVIEW_EDGE` square.
        - `parent` (`QObject | None`): Qt parent. Prefer a longer-lived owner than `list_view`.

        """
        # Prefer an owner that outlives the list (e.g. main window) so teardown is ordered.
        super().__init__(parent if parent is not None else list_view)
        self._list_view = list_view
        self._viewport = list_view.viewport()
        self._get_avif_manager = get_avif_manager
        self._preview_size = preview_size or QSize(_PREVIEW_EDGE, _PREVIEW_EDGE)
        self._pending_exercise: str | None = None
        self._shown_exercise: str | None = None
        self._detached = False

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
        self._viewport.setMouseTracking(True)
        self._viewport.installEventFilter(self)
        self._list_view.installEventFilter(self)
        self._list_view.destroyed.connect(self.detach)
        self._viewport.destroyed.connect(self.detach)
        scroll = self._list_view.verticalScrollBar()
        if scroll is not None:
            scroll.valueChanged.connect(self.hide_preview)

    def detach(self, *_args: object) -> None:
        """Remove filters and hide popup; safe during widget teardown."""
        if self._detached:
            return
        self._detached = True
        self._timer.stop()
        self._pending_exercise = None
        self._shown_exercise = None
        self._stop_animation()
        if isValid(self._popup):
            self._popup.hide()
            self._popup.close()

        if isValid(self._viewport):
            self._viewport.removeEventFilter(self)
        if isValid(self._list_view):
            self._list_view.removeEventFilter(self)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        """Track icon hover, dwell delay, and leave/scroll hide."""
        if self._detached or not self._list_alive():
            return False

        event_type = event.type()
        viewport = self._viewport if isValid(self._viewport) else None

        if viewport is not None and obj is viewport and event_type == QEvent.Type.MouseMove:
            self._on_mouse_move(cast("QMouseEvent", event).position().toPoint())
            return False

        if viewport is not None and obj is viewport and event_type in {QEvent.Type.Leave, QEvent.Type.Wheel}:
            self.hide_preview()
            return False

        if obj is self._list_view and event_type == QEvent.Type.Leave:
            self.hide_preview()
            return False

        return super().eventFilter(obj, event)

    def hide_preview(self) -> None:
        """Stop animation and hide the popup."""
        if self._detached:
            return
        self._timer.stop()
        self._pending_exercise = None
        self._shown_exercise = None
        self._stop_animation()
        if isValid(self._popup):
            self._popup.hide()

    def _exercise_at_icon(self, pos: QPoint) -> str | None:
        if not self._list_alive():
            return None
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

    def _list_alive(self) -> bool:
        return isValid(self._list_view) and isValid(self._viewport)

    def _move_popup_to_cursor(self) -> None:
        if not isValid(self._popup):
            return
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
        if not self._list_alive():
            self.detach()
            return

        exercise = self._exercise_at_icon(pos)
        if exercise is None:
            self.hide_preview()
            return

        if exercise == self._shown_exercise and isValid(self._popup) and self._popup.isVisible():
            self._move_popup_to_cursor()
            return

        if exercise == self._pending_exercise and self._timer.isActive():
            return

        self._timer.stop()
        self._stop_animation()
        if isValid(self._popup):
            self._popup.hide()
        self._shown_exercise = None
        self._pending_exercise = exercise
        self._timer.start(_HOVER_DELAY_MS)

    def _show_preview(self) -> None:
        if self._detached or not self._list_alive():
            return
        exercise = self._pending_exercise
        manager = self._get_avif_manager()
        if not exercise or manager is None or not isValid(self._popup) or not isValid(self._label):
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
        if isValid(self._label):
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
- `preview_size` (`QSize | None`): Popup size. Defaults to `_PREVIEW_EDGE` square.
- `parent` (`QObject | None`): Qt parent. Prefer a longer-lived owner than `list_view`.

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
        # Prefer an owner that outlives the list (e.g. main window) so teardown is ordered.
        super().__init__(parent if parent is not None else list_view)
        self._list_view = list_view
        self._viewport = list_view.viewport()
        self._get_avif_manager = get_avif_manager
        self._preview_size = preview_size or QSize(_PREVIEW_EDGE, _PREVIEW_EDGE)
        self._pending_exercise: str | None = None
        self._shown_exercise: str | None = None
        self._detached = False

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
        self._viewport.setMouseTracking(True)
        self._viewport.installEventFilter(self)
        self._list_view.installEventFilter(self)
        self._list_view.destroyed.connect(self.detach)
        self._viewport.destroyed.connect(self.detach)
        scroll = self._list_view.verticalScrollBar()
        if scroll is not None:
            scroll.valueChanged.connect(self.hide_preview)
```

</details>

### ⚙️ Method `detach`

```python
def detach(self, *_args: object) -> None
```

Remove filters and hide popup; safe during widget teardown.

<details>
<summary>Code:</summary>

```python
def detach(self, *_args: object) -> None:
        if self._detached:
            return
        self._detached = True
        self._timer.stop()
        self._pending_exercise = None
        self._shown_exercise = None
        self._stop_animation()
        if isValid(self._popup):
            self._popup.hide()
            self._popup.close()

        if isValid(self._viewport):
            self._viewport.removeEventFilter(self)
        if isValid(self._list_view):
            self._list_view.removeEventFilter(self)
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
        if self._detached or not self._list_alive():
            return False

        event_type = event.type()
        viewport = self._viewport if isValid(self._viewport) else None

        if viewport is not None and obj is viewport and event_type == QEvent.Type.MouseMove:
            self._on_mouse_move(cast("QMouseEvent", event).position().toPoint())
            return False

        if viewport is not None and obj is viewport and event_type in {QEvent.Type.Leave, QEvent.Type.Wheel}:
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
        if self._detached:
            return
        self._timer.stop()
        self._pending_exercise = None
        self._shown_exercise = None
        self._stop_animation()
        if isValid(self._popup):
            self._popup.hide()
```

</details>
